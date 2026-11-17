"""Host-only ONVIF protocol smoke tests; NOT a camera/firmware test."""
import os
import socket
import subprocess
import time
import unittest
import urllib.request
import xml.etree.ElementTree as ET

PORT = 18899
NS = {"d": "http://www.onvif.org/ver10/device/wsdl",
      "m": "http://www.onvif.org/ver10/media/wsdl",
      "tt": "http://www.onvif.org/ver10/schema"}

class OnvifDaemonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.process = subprocess.Popen(
            ["./foldview_onvifd", "--ip", "127.0.0.1",
             "--http-port", str(PORT), "--main-port", "1234",
             "--sub-port", "1235"],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        time.sleep(0.25)
        if cls.process.poll() is not None:
            raise RuntimeError("native daemon did not start: " + cls.process.stderr.read().decode())

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        try:
            cls.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            cls.process.kill()

    def soap(self, op):
        body = ('<?xml version="1.0"?>'
                '<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"'
                ' xmlns:tds="http://www.onvif.org/ver10/device/wsdl"'
                ' xmlns:trt="http://www.onvif.org/ver10/media/wsdl">'
                '<s:Body>' + op + '</s:Body></s:Envelope>')
        request = urllib.request.Request(
            f"http://127.0.0.1:{PORT}/onvif/device_service",
            data=body.encode(), method="POST",
            headers={"Content-Type":"application/soap+xml"})
        with urllib.request.urlopen(request, timeout=3) as response:
            self.assertEqual(response.status, 200)
            return ET.fromstring(response.read())

    def test_device_information(self):
        response = self.soap("<tds:GetDeviceInformation/>")
        self.assertEqual(response.find(".//d:Model", NS).text,
                         "FH8852V201 FOLDVIEW prototype")

    def test_capabilities_and_media_endpoint(self):
        response = self.soap("<tds:GetCapabilities/>")
        addresses = [el.text for el in response.findall(".//tt:XAddr", NS)]
        self.assertIn(f"http://127.0.0.1:{PORT}/onvif/media_service", addresses)

    def test_profiles_and_main_rtsp(self):
        resp = self.soap("<trt:GetProfiles/>")
        profiles = resp.findall(".//m:Profiles", NS)
        self.assertEqual({p.attrib.get("token") for p in profiles},
                         {"Profile_Main", "Profile_Sub"})
        main = self.soap("<trt:GetStreamUri><trt:ProfileToken>Profile_Main</trt:ProfileToken></trt:GetStreamUri>")
        self.assertEqual(main.find(".//tt:Uri", NS).text,
                         "rtsp://127.0.0.1:1234/")
        sub = self.soap("<trt:GetStreamUri><trt:ProfileToken>Profile_Sub</trt:ProfileToken></trt:GetStreamUri>")
        self.assertEqual(sub.find(".//tt:Uri", NS).text,
                         "rtsp://127.0.0.1:1235/")

    def test_invalid_content_length_does_not_kill_daemon(self):
        # Invalid length must be rejected without poisoning later clients.
        with socket.create_connection(("127.0.0.1", PORT), timeout=3) as sock:
            sock.sendall(b"POST /onvif/device_service HTTP/1.1\r\n"
                         b"Content-Length: 42invalid\r\n\r\n")
            sock.shutdown(socket.SHUT_WR)
            self.assertEqual(sock.recv(1024), b"")
        self.assertIsNone(self.process.poll())
        self.test_device_information()

    def test_discovery_message_id_not_reflected_as_xml(self):
        request = ('<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"'
                   ' xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery">'
                   '<s:Header><a:MessageID xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing">'
                   'urn:uuid:bad&amp;escape</a:MessageID></s:Header>'
                   '<s:Body><d:Probe/></s:Body></s:Envelope>').encode()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(3)
            sock.sendto(request, ("127.0.0.1", 3702))
            payload, _ = sock.recvfrom(8192)
        root = ET.fromstring(payload)
        self.assertIsNotNone(root)
        self.assertNotIn(b"bad&amp;escape", payload)
        self.assertIn(b"urn:uuid:unknown", payload)

    def test_discovery_probe(self):
        request = ('<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"'
                   ' xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery">'
                   '<s:Header><a:MessageID xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing">'
                   'urn:uuid:unit-test</a:MessageID></s:Header>'
                   '<s:Body><d:Probe/></s:Body></s:Envelope>').encode()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(3)
            sock.sendto(request, ("127.0.0.1", 3702))
            payload, _ = sock.recvfrom(8192)
        self.assertIn(b"ProbeMatches", payload)
        ET.fromstring(payload)

if __name__ == "__main__":
    unittest.main()
