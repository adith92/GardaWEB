import socket
import threading
import time
from unittest.mock import patch

import pytest
from garda_ai.network import NetworkScanner, probe, scope

LOCAL = [{"network": "192.168.1.0/24"}]

@pytest.mark.parametrize("target,ports", [("8.8.8.8", "80"), ("192.168.2.1", "80"),
    ("192.168.0.0/16", "80"), ("192.168.1.0/24", "1-65535"),
    ("192.168.1.1", "0"), ("192.168.1.1", "65536"), ("192.168.1.1", "90-80")])
def test_rejects_invalid_scopes(target, ports):
    with pytest.raises(ValueError): scope(target, ports, LOCAL)

def test_full_scan_only_single_host():
    hosts, ports = scope("192.168.1.14", "1-65535", LOCAL)
    assert hosts == ["192.168.1.14"] and len(ports) == 65535

def test_real_tcp_listener():
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0)); server.listen()
        port = server.getsockname()[1]
        assert probe(("127.0.0.1", port))["port"] == port
    assert probe(("127.0.0.1", port)) is None

def test_cancel_preserves_partial_results_and_prevents_overlap():
    scanner = NetworkScanner()
    gate = threading.Event()
    def slow(item):
        gate.wait(2)
        return {"ip": item[0], "port": item[1], "hint": "test"}
    with patch("garda_ai.network.interfaces", return_value=LOCAL), patch("garda_ai.network.probe", side_effect=slow):
        scanner.start("192.168.1.14", "1-100")
        with pytest.raises(RuntimeError): scanner.start("192.168.1.14", "80")
        scanner.cancel(); gate.set(); scanner.thread.join(3)
    result = scanner.snapshot()
    assert result["status"] == "cancelled" and result["completed"] <= 64
    assert len(result["results"]) == result["completed"]
