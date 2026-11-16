"""No LAN traffic in these tests: all probes and interfaces are mocked."""
import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from garda_vision import api
from garda_vision.core import Camera
from garda_vision.scanner import allowed_network, scan_network
from garda_vision.storage import Store

INTERFACES = [{"interface": "Ethernet", "ip": "192.168.50.5", "network": "192.168.50.0/24",
               "suggested_cidr": "192.168.50.0/24", "source": "local_interface"}]


def test_scope_enforcement():
    assert str(allowed_network("192.168.50.0/24", INTERFACES)[0]) == "192.168.50.0/24"
    for bad in ("8.8.8.0/24", "192.168.51.0/24", "192.168.50.0/16", "127.0.0.0/24", "192.168.50.2/24"):
        with pytest.raises(ValueError):
            allowed_network(bad, INTERFACES)
    with pytest.raises(ValueError):
        allowed_network("192.168.50.0/24", INTERFACES, target_ip="192.168.50.5")
    with pytest.raises(ValueError):
        allowed_network("192.168.50.0/24", INTERFACES, explicit_allowlist="192.168.10.0/24")


def test_two_stage_results_and_security_flags(monkeypatch):
    monkeypatch.setenv("GARDA_SCAN_ALLOWED_CIDRS", "192.168.50.0/24")
    monkeypatch.setattr("garda_vision.scanner.arp_cache", lambda: {"192.168.50.14": "ea:aa:bb:cc:dd:ee"})
    requests = []

    def probe(ip, port):
        requests.append((ip, port))
        if ip == "192.168.50.14" and port in (23, 1111, 8899, 6666):
            return {"port": port, "hint": "mjpg_streamer_confirmed" if port == 1111 else "onvif_candidate",
                    "evidence": "http_head_response" if port == 1111 else "tcp_connect", "banner": ""}
        return None

    result = scan_network("192.168.50.0/24", mode="extended", target_ip="192.168.50.14",
                          interfaces=INTERFACES, probe=probe, enable_ws=False)
    assert result["host_count"] == 1
    assert result["devices"][0]["ip"] == "192.168.50.14"
    assert result["devices"][0]["classification"] == "camera_evidence"
    assert "telnet_port_open" in result["devices"][0]["flags"]
    assert ("192.168.50.14", 6666) in requests
    assert all(ip == "192.168.50.14" for ip, _ in requests)


def test_rbac_confirmation_async_scan_and_encrypted_persistence(monkeypatch):
    for role in ("VIEWER", "OPERATOR", "ADMIN"):
        monkeypatch.setenv(f"GARDA_{role}_TOKEN", role.lower() * 12)
    monkeypatch.setenv("GARDA_NETWORK_SCAN_ENABLED", "1")
    monkeypatch.setenv("GARDA_SCAN_ALLOWED_CIDRS", "192.168.50.0/24")
    monkeypatch.setattr("garda_vision.scanner.network_interfaces", lambda: INTERFACES)
    monkeypatch.setattr(api, "network_interfaces", lambda: INTERFACES)

    class FakeVision:
        enable_face_id = False

    def fake_scan(cidr, mode="quick", target_ip=None):
        return {"network": cidr, "mode": mode, "devices": [{"ip": "192.168.50.14", "open_ports": []}]}

    with TemporaryDirectory() as d:
        db_path = Path(d) / "lab.sqlite"
        store = Store(str(db_path), Fernet.generate_key().decode())
        app = api.build_app({"LAB": Camera("LAB", "LAB", "GARDA_CAM_LAB")}, store, FakeVision(), scan_engine=fake_scan)
        with TestClient(app) as client:
            admin = {"Authorization": "Bearer " + os.environ["GARDA_ADMIN_TOKEN"]}
            viewer = {"Authorization": "Bearer " + os.environ["GARDA_VIEWER_TOKEN"]}
            payload = {"cidr": "192.168.50.0/24", "mode": "extended", "target_ip": "192.168.50.14", "confirm_authorized": True}
            assert client.get("/api/v1/network/interfaces").status_code == 401
            assert client.get("/api/v1/network/interfaces", headers=viewer).status_code == 403
            assert client.post("/api/v1/network/scans", json=payload, headers=viewer).status_code == 403
            assert client.post("/api/v1/network/scans", json={**payload, "confirm_authorized": False}, headers=admin).status_code == 422
            assert client.post("/api/v1/network/scans", json={**payload, "cidr": "8.8.8.0/24"}, headers=admin).status_code == 422
            res = client.post("/api/v1/network/scans", json=payload, headers=admin)
            assert res.status_code == 202, res.text
            scan_id = res.json()["scan_id"]
            for _ in range(30):
                result = client.get(f"/api/v1/network/scans/{scan_id}", headers=admin)
                if result.json()["status"] == "completed":
                    break
                time.sleep(0.02)
            assert result.json()["status"] == "completed"
            assert result.json()["result"]["devices"][0]["ip"] == "192.168.50.14"
            assert client.get(f"/api/v1/network/scans/{scan_id}", headers=viewer).status_code == 403
            assert client.get("/api/v1/network/scans", headers=admin).status_code == 200
            assert b"192.168.50.14" not in db_path.read_bytes()  # encrypted scan payload
        store.close()
        assert b"192.168.50.14" not in db_path.read_bytes()  # SQLite main file after checkpoint


def test_scan_disabled_by_default(monkeypatch):
    for role in ("VIEWER", "OPERATOR", "ADMIN"):
        monkeypatch.setenv(f"GARDA_{role}_TOKEN", role.lower() * 12)
    monkeypatch.delenv("GARDA_NETWORK_SCAN_ENABLED", raising=False)
    with TemporaryDirectory() as d:
        store = Store(str(Path(d) / "db.sqlite"), Fernet.generate_key().decode())
        app = api.build_app({}, store, object())
        with TestClient(app) as client:
            admin = {"Authorization": "Bearer " + os.environ["GARDA_ADMIN_TOKEN"]}
            assert client.post("/api/v1/network/scans", headers=admin,
                json={"cidr": "192.168.50.0/24", "confirm_authorized": True}).status_code == 403
        store.close()
