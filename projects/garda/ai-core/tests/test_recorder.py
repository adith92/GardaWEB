from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import hashlib
import json
import threading

import pytest
from fastapi.testclient import TestClient
from garda_ai.api import create_app
from garda_ai.gateway import install_web
from garda_ai.recorder import Recorder, engine_config, prepare_storage
from garda_ai.tls import provision_tls


def test_recommended_is_default_and_full_requires_explicit_profile(tmp_path):
    app=create_app(tmp_path, unified=True,lab_no_login=True)
    with TestClient(app) as client:
        csrf=client.get('/api/v1/auth/me').json()['csrf']
        headers={'X-GARDA-CSRF':csrf}
        with patch.object(app.state.unified.scanner,'start',return_value={'status':'running'}) as start:
            client.post('/api/v1/network/scan',json={'target':'192.168.1.15','ports':'1-65535'},headers=headers)
            assert start.call_args.args[1]!='1-65535'
            client.post('/api/v1/network/scan',json={'target':'192.168.1.15','profile':'full'},headers=headers)
            assert start.call_args.args[1]=='1-65535'
        assert client.post('/api/v1/network/scan',json={'target':'192.168.1.15','profile':'oops'},headers=headers).status_code==422


def test_engine_uses_loopback_and_separate_part_retention_policy(tmp_path):
    config=engine_config(tmp_path,1)
    assert config['apiAddress'].startswith('127.0.0.1:')
    assert config['rtspAddress'].startswith('127.0.0.1:')
    assert config['playbackAddress'].startswith('127.0.0.1:')
    assert config['pathDefaults']['recordDeleteAfter']=='1d'
    assert config['pathDefaults']['recordPartDuration']=='1s'
    assert config['pathDefaults']['recordMaxPartSize']=='8M'
    assert config['pathDefaults']['sourceOnDemand'] is False


def test_storage_refuses_to_adopt_existing_unowned_video(tmp_path):
    (tmp_path/'video').mkdir()
    (tmp_path/'video'/'personal.txt').write_text('preserve')
    with pytest.raises(ValueError):prepare_storage(tmp_path)
    assert (tmp_path/'video'/'personal.txt').read_text()=='preserve'


def test_low_disk_pauses_and_resumes_without_deleting_files(tmp_path):
    runtime=SimpleNamespace(lock=threading.RLock(),records={'CAM-01':{'url':'rtsp://private-secret@192.168.1.15/live'}})
    recorder=Recorder(tmp_path,runtime)
    recorder.storage=prepare_storage(tmp_path/'managed')
    calls=[]
    def request(method,path,payload=None):
        calls.append((method,path,payload))
        return {'items':[{'name':'CAM-01','ready':True,'bytesReceived':1000}]} if method=='GET' else {}
    recorder._request=request
    with patch('garda_ai.recorder.shutil.disk_usage',return_value=SimpleNamespace(total=100*1024**3,free=1)):
        recorder.reconcile()
    assert recorder.snapshot()['disk_paused']
    assert recorder.applied['CAM-01']['record'] is False
    with patch('garda_ai.recorder.shutil.disk_usage',return_value=SimpleNamespace(total=100*1024**3,free=30*1024**3)):
        recorder.reconcile()
    assert recorder.applied['CAM-01']['record'] is True
    assert 'private-secret' not in json.dumps(recorder.snapshot())


def test_binary_tampering_blocks_launch(tmp_path,monkeypatch):
    binary=tmp_path/'engine';binary.write_bytes(b'expected')
    monkeypatch.setenv('GARDA_NVR_BINARY_SHA256',hashlib.sha256(b'expected').hexdigest())
    recorder=Recorder(tmp_path,SimpleNamespace(),binary=binary,directory=tmp_path/'managed')
    binary.write_bytes(b'corrupted')
    with pytest.raises(ValueError,match='fingerprint'):recorder.start()


def test_gateway_single_origin_keeps_api_guards_and_unknown_routes(tmp_path):
    web=tmp_path/'web';web.mkdir();(web/'index.html').write_text('<h1>Workspace</h1>')
    app=create_app(tmp_path/'data',unified=True)
    install_web(app,web)
    with TestClient(app) as client:
        assert client.get('/workspace').status_code==200
        assert client.get('/garda-api/api/v1/cameras').status_code==401
        assert client.get('/garda-api/api/no-such-route').status_code==404
        assert client.get('/no-such.js').status_code==404


def test_tls_ca_is_persistent_and_cert_contains_lan_ip(tmp_path):
    from cryptography import x509
    import ipaddress
    first=provision_tls(tmp_path,'192.168.1.3')
    identity=Path(first['ca']).read_bytes()
    second=provision_tls(tmp_path,'192.168.1.4')
    assert Path(second['ca']).read_bytes()==identity
    cert=x509.load_pem_x509_certificate(Path(second['cert']).read_bytes())
    san=cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    assert ipaddress.ip_address('192.168.1.4') in san.get_values_for_type(x509.IPAddress)


def test_nvr_recording_control_uses_csrf_and_persists(tmp_path):
    app=create_app(tmp_path,unified=True,lab_no_login=True)
    with TestClient(app) as client:
        s=app.state.unified
        s.runtime.save('CAM-01','Test','rtsp://user:secret@192.168.1.15/live','presence','off')
        assert client.put('/api/v1/nvr/cameras/CAM-01/recording',json={'enabled':False}).status_code==403
        csrf=client.get('/api/v1/auth/me').json()['csrf']
        assert client.put('/api/v1/nvr/cameras/CAM-01/recording',json={'enabled':False},headers={'X-GARDA-CSRF':csrf}).status_code==200
        assert s.runtime.records['CAM-01']['recording_enabled'] is False
        assert b'secret' not in (tmp_path/'cameras.encrypted').read_bytes()
