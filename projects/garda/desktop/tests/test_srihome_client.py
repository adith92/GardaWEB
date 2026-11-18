"""GARDA desktop camera control: truthful command results; lab Telnet fallback remains."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

path = Path(__file__).resolve().parents[1] / "srihome_client.py"
spec = importlib.util.spec_from_file_location("garda_desktop_srihome_tested", path)
client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client_module)
SriHomeClient = client_module.SriHomeClient


class CameraControlTests(unittest.TestCase):
    def setUp(self):
        self.client = SriHomeClient("192.168.1.20")

    def test_failed_lights_do_not_report_success(self):
        with patch.object(self.client, "_post_api", return_value=(False, "offline")):
            with patch.object(self.client, "execute_shell_cmd", return_value=(False, "offline")):
                self.assertFalse(self.client.set_white_light(True)[0])
                self.assertFalse(self.client.set_ir_light(True)[0])
        self.assertFalse(self.client.white_light_on)
        self.assertFalse(self.client.ir_light_on)

    def test_rest_success_avoids_telnet(self):
        with patch.object(self.client, "_post_api", return_value=(True, "OK")):
            with patch.object(self.client, "execute_shell_cmd") as shell:
                self.assertTrue(self.client.set_white_light(True)[0])
                self.assertTrue(self.client.set_ir_light(True)[0])
                shell.assert_not_called()

    def test_telnet_hardware_fallback_preserved(self):
        with patch.object(self.client, "_post_api", return_value=(False, "REST absent")):
            with patch.object(self.client, "execute_shell_cmd", return_value=(True, "done")):
                self.assertTrue(self.client.set_white_light(True)[0])
                self.assertTrue(self.client.set_ir_light(True)[0])

    def test_unexpected_ptz_ack_fails_not_pass(self):
        with patch.object(client_module.socket, "socket") as factory:
            factory.return_value.__enter__.return_value.recv.return_value = b"bad"
            ok, detail = self.client.send_ptz_packet(self.client.CMD_UP)
        self.assertFalse(ok)
        self.assertIn("tidak valid", detail)


if __name__ == "__main__":
    unittest.main()
