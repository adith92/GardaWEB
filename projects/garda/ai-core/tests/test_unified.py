import hashlib
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from garda_ai.api import create_app
from garda_ai.config import load_config
from garda_ai.providers import model_file
from garda_ai.runtime import checked_rtsp
from garda_ai.updates import ReleaseCache


class UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"GARDA_COOKIE_SECURE": "0"})
        self.env.start()
        self.app = create_app(self.temp.name, unified=True)
        self.service = self.app.state.unified
        self.service.identity.add_user("admin", "a-strong-test-password", "admin")
        self.service.identity.add_user("viewer", "another-test-password", "viewer")
        self.client = TestClient(self.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.env.stop()
        self.temp.cleanup()

    def login(self, user="admin", password="a-strong-test-password"):
        result = self.client.post("/api/v1/auth/login", json={"username": user, "password": password})
        self.assertEqual(result.status_code, 200)
        return result.json()

    def test_anonymous_requests_cannot_access_catalog_or_preview(self):
        for path in ("/api/v1/cameras", "/api/v1/events", "/api/v1/providers", "/api/events",
                     "/api/v1/cameras/CAM-01/preview.jpg", "/api/v1/updates/fold/manifest.json"):
            self.assertEqual(self.client.get(path).status_code, 401, path)

    def test_eight_slots_never_claim_online_without_fresh_frame(self):
        self.login()
        result = self.client.get("/api/v1/cameras").json()
        self.assertEqual(len(result["cameras"]), 8)
        self.assertFalse(result["capacity_validated"])
        self.assertTrue(all(not c["online"] and not c["configured"] for c in result["cameras"]))
        self.assertEqual(self.client.get("/api/v1/cameras/CAM-01/preview.jpg").status_code, 503)

    def test_csrf_origin_role_and_legacy_read_permissions(self):
        actor = self.login()
        data = {"name": "Gate", "rtsp_url": "rtsp://user:private-camera-password@192.168.1.22:1234/"}
        self.assertEqual(self.client.put("/api/v1/cameras/CAM-01", json=data).status_code, 403)
        headers = {"X-GARDA-CSRF": actor["csrf"], "Origin": "https://untrusted.example"}
        self.assertEqual(self.client.put("/api/v1/cameras/CAM-01", json=data, headers=headers).status_code, 403)
        self.assertEqual(self.client.post("/api/v1/auth/login", json={"username":"admin","password":"anything"},
                                         headers={"Origin":"https://untrusted.example"}).status_code, 403)
        viewer = self.login("viewer", "another-test-password")
        self.assertEqual(self.client.get("/api/v1/cameras").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/events").status_code, 403)
        self.assertEqual(self.client.get("/api/events").status_code, 403)
        self.assertEqual(self.client.put("/api/v1/cameras/CAM-01", json=data,
            headers={"X-GARDA-CSRF": viewer["csrf"]}).status_code, 403)

    def test_camera_secret_encrypted_and_not_returned_or_audited(self):
        actor = self.login()
        secret = "rtsp://user:private-camera-password@192.168.1.22:1234/"
        response = self.client.put("/api/v1/cameras/CAM-01", json={"name":"Gate","rtsp_url":secret},
                                   headers={"X-GARDA-CSRF":actor["csrf"]})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(secret, response.text)
        self.assertNotIn(secret, self.client.get("/api/v1/cameras").text)
        data = (Path(self.temp.name)/"cameras.encrypted").read_bytes()
        self.assertNotIn(b"private-camera-password", data)
        audit = self.service.store.db.execute("SELECT action,source FROM access_audit").fetchall()
        self.assertNotIn("private-camera-password", str(audit))

    def test_session_revoke_and_expiry(self):
        actor = self.login()
        token = actor["access_token"]
        self.assertEqual(self.client.post("/api/v1/auth/logout", headers={"X-GARDA-CSRF":actor["csrf"]}).status_code,200)
        self.assertEqual(self.client.get("/api/v1/cameras", headers={"Authorization":"Bearer "+token}).status_code,401)
        actor = self.login()
        self.service.identity.sessions[self.service.identity.digest(actor["access_token"])]["expires"] = time.time()-1
        self.assertEqual(self.client.get("/api/v1/auth/me").status_code,401)

    def test_login_throttles_and_never_persists_password(self):
        for _ in range(5):
            self.assertEqual(self.client.post("/api/v1/auth/login", json={"username":"admin","password":"wrong"}).status_code,401)
        self.assertEqual(self.client.post("/api/v1/auth/login", json={"username":"admin","password":"wrong"}).status_code,429)
        self.assertNotIn(b"a-strong-test-password", (Path(self.temp.name)/"identity.db").read_bytes())

    def test_search_and_evidence_authorization(self):
        actor = self.login()
        self.service.store.add_event("CAM-01", "Gate", "plate", .9, "B1234ABC")
        self.service.store.add_event("CAM-02", "Door", "face", .8, face_label="Reference One")
        self.assertEqual(self.client.get("/api/v1/events?q=B1234").json()["count"],1)
        self.assertEqual(self.client.get("/api/v1/events?q=Reference").json()["count"],1)
        self.assertEqual(self.client.get("/api/v1/events?q=' OR 1=1 --").json()["count"],0)
        self.assertEqual(self.client.get("/api/v1/events/bad/photos/wrong").status_code,404)
        response=self.client.post("/api/v1/faces/enroll", data={"label":"One","reference":"lab-test"},
            files={"image":("test.jpg", b"invalid", "image/jpeg")}, headers={"X-GARDA-CSRF":actor["csrf"]})
        self.assertIn(response.status_code,(422,503))

    def test_provider_catalog_does_not_initialize_or_claim_accuracy(self):
        self.login()
        records=self.client.get("/api/v1/providers").json()["providers"]
        self.assertEqual({r["id"] for r in records},{"sface","deepface","insightface","fastalpr","paddleocr"})
        self.assertTrue(all(r["state"]=="not_loaded" and not r["hardware_validated"] for r in records))
        self.assertEqual(self.service.runtime.providers.instances,{})


class LocalAdminTests(unittest.TestCase):
    def test_initial_lab_enters_admin_without_credentials_and_keeps_csrf(self):
        with tempfile.TemporaryDirectory() as d:
            app = create_app(d, unified=True, lab_no_login=True)
            with TestClient(app) as client:
                actor = client.get("/api/v1/auth/me").json()
                self.assertEqual(actor["role"], "admin")
                self.assertTrue(actor["lab_no_login"])
                self.assertEqual(client.get("/health").json()["auth_mode"], "local_admin")
                for path in ("/api/v1/cameras", "/api/v1/providers", "/api/v1/events", "/api/events"):
                    self.assertEqual(client.get(path).status_code, 200, path)
                data = {"name":"Lab camera", "rtsp_url":"rtsp://192.168.1.22:1234/"}
                self.assertEqual(client.put("/api/v1/cameras/CAM-01", json=data).status_code, 403)
                self.assertEqual(client.put("/api/v1/cameras/CAM-01", json=data,
                    headers={"X-GARDA-CSRF":actor["csrf"]}).status_code, 200)
                self.assertEqual(client.put("/api/v1/cameras/CAM-01", json=data,
                    headers={"X-GARDA-CSRF":actor["csrf"],"Origin":"https://untrusted.example"}).status_code, 403)

    def test_local_admin_is_explicitly_scoped_to_the_unified_mode(self):
        with tempfile.TemporaryDirectory() as d:
            app = create_app(d, unified=True)
            with TestClient(app) as client:
                self.assertEqual(client.get("/api/v1/auth/me").status_code, 401)
                self.assertEqual(client.get("/health").json()["auth_mode"], "named_sessions")


class ConfigurationAndAssetsTests(unittest.TestCase):
    def test_provision_validates_download_and_preserves_template_key(self):
        import io
        from garda_ai.provision import provision_opencv
        content=b"synthetic model for provisioning test"
        model={"env":"GARDA_TEST_MODEL","directory":"test","file":"test.onnx",
               "size":len(content),"sha256":hashlib.sha256(content).hexdigest(),"license":"test"}
        def response(url,timeout=0):return io.BytesIO(b"test notice" if url.endswith("LICENSE") else content)
        with tempfile.TemporaryDirectory() as d,patch("garda_ai.provision.MODELS",(model,)),patch("urllib.request.urlopen",response):
            root=Path(d)
            provision_opencv(root)
            key=(root/"face.key").read_bytes()
            self.assertEqual((root/"models/test.onnx").read_bytes(),content)
            provision_opencv(root)
            self.assertEqual((root/"face.key").read_bytes(),key)

    def test_provision_rejects_corrupted_bytes_without_partial_model(self):
        import io
        from garda_ai.provision import provision_opencv
        model={"env":"GARDA_TEST_MODEL","directory":"test","file":"test.onnx",
               "size":5,"sha256":"0"*64,"license":"test"}
        with tempfile.TemporaryDirectory() as d,patch("garda_ai.provision.MODELS",(model,)),patch("urllib.request.urlopen",lambda *a,**k:io.BytesIO(b"wrong")):
            root=Path(d)
            with self.assertRaises(ValueError):provision_opencv(root)
            self.assertFalse((root/"models/test.onnx").exists())
            self.assertEqual(list((root/"models").glob("*.part")),[])

    def test_camera_vault_restores_without_disclosing_credentials(self):
        from garda_ai.runtime import Runtime
        from garda_ai.storage import EventStore
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);store=EventStore(root)
            runtime=Runtime(root,store)
            secret="rtsp://test:runtime-only@192.168.1.22:554/"
            runtime.save("CAM-01","Gate",secret,"presence","off")
            runtime.close()
            restored=Runtime(root,store)
            self.assertEqual(restored.records["CAM-01"]["url"],secret)
            self.assertTrue(restored.cameras()[0]["configured"])
            self.assertNotIn("runtime-only",json.dumps(restored.cameras()))
            self.assertIsNone(restored.preview("CAM-01"))
            restored.close();store.close()

    def test_paddle_adapter_reads_detector_crops_and_returns_scores(self):
        import numpy as np
        from types import SimpleNamespace
        from garda_ai.providers import Plates
        engine=object.__new__(Plates)
        engine.name="paddleocr"
        box=SimpleNamespace(x1=10,y1=20,x2=80,y2=40)
        engine.base=SimpleNamespace(engine=SimpleNamespace(predict=lambda frame:[SimpleNamespace(detection=SimpleNamespace(bounding_box=box))]))
        class OCR:
            def predict(self,crop):
                self.shape=crop.shape
                return [SimpleNamespace(json={"res":{"rec_texts":["B 1234 ABC"],"rec_scores":[.93]}})]
        engine.ocr=OCR()
        found=engine.detect(np.zeros((100,120,3),dtype=np.uint8))
        self.assertEqual(found[0].text,"B1234ABC")
        self.assertAlmostEqual(found[0].confidence,.93)
        self.assertLess(engine.ocr.shape[0],100)

    def test_eight_camera_config_and_stream_count_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"config.json"
            rows=[{"id":f"C{i}","rtsp_env":f"GARDA_CAM_{i:02}"} for i in range(8)]
            values={row["rtsp_env"]:"rtsp://127.0.0.1/" for row in rows}
            path.write_text(json.dumps({"cameras":rows}))
            with patch.dict(os.environ,values):
                self.assertEqual(len(load_config(path).cameras),8)
            path.write_text(json.dumps({"cameras":rows*7}))
            with patch.dict(os.environ,values), self.assertRaises(ValueError):
                load_config(path)

    def test_reject_public_targets_and_verify_model_checksum(self):
        for value in ("rtsp://8.8.8.8/", "rtsp://example.org/", "file:///private", "rtsp://169.254.169.254/"):
            with self.assertRaises(ValueError): checked_rtsp(value)
        self.assertEqual(checked_rtsp("rtsp://192.168.1.14:1234/"),"rtsp://192.168.1.14:1234/")
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"model.onnx";path.write_bytes(b"test model only")
            values={"GARDA_TEST_MODEL":str(path),"GARDA_TEST_MODEL_SHA256":"0"*64}
            with patch.dict(os.environ,values),self.assertRaises(RuntimeError):model_file("GARDA_TEST_MODEL")
            values["GARDA_TEST_MODEL_SHA256"]=hashlib.sha256(path.read_bytes()).hexdigest()
            with patch.dict(os.environ,values):self.assertEqual(model_file("GARDA_TEST_MODEL"),path.resolve())


class ReleaseRelayTests(unittest.TestCase):
    def test_github_redirect_drops_auth_and_checks_package(self):
        payload=b"synthetic test package"; seen=[]
        def handler(request):
            seen.append((request.url.host, request.headers.get("Authorization")))
            if request.url.host=="api.github.com":
                return httpx.Response(302,headers={"Location":"https://release-assets.githubusercontent.com/test.apk"})
            return httpx.Response(200,content=payload)
        original=httpx.Client
        def client(**kwargs):return original(transport=httpx.MockTransport(handler),**kwargs)
        entry={"assetId":1,"sha256":hashlib.sha256(payload).hexdigest(),"sizeBytes":len(payload)}
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,{"GARDA_GITHUB_READ_TOKEN":"server-secret"}),patch("garda_ai.updates.httpx.Client",client):
            result=ReleaseCache(Path(d)).fetch(entry)
            self.assertEqual(result.read_bytes(),payload)
        self.assertEqual(seen[0][1],"Bearer server-secret")
        self.assertIsNone(seen[1][1])

    def test_untrusted_redirect_and_wrong_checksum_leave_no_package(self):
        original=httpx.Client
        for bad_redirect in (True, False):
            def handler(request):
                return httpx.Response(302,headers={"Location":"https://untrusted.example/package.apk"}) if bad_redirect else httpx.Response(200,content=b"wrong")
            def client(**kwargs):return original(transport=httpx.MockTransport(handler),**kwargs)
            with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{"GARDA_GITHUB_READ_TOKEN":"server-secret"}),patch("garda_ai.updates.httpx.Client",client):
                with self.assertRaises(ValueError):ReleaseCache(Path(d)).fetch({"assetId":1,"sha256":"0"*64,"sizeBytes":5})
                self.assertEqual(list(Path(d).glob("*.apk")),[])
                self.assertEqual(list(Path(d).glob("*.part")),[])


if __name__ == "__main__":unittest.main()
