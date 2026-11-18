"""
GARDA Desktop - Unified Camera Hardware & ONVIF Client
Supports:
1. CleanTV / GARDA Embedded ONVIF & REST Daemon (Port 8899: /api/status, /api/ptz, /api/led, ONVIF SOAP)
2. WS-Discovery Multicast Scanner (UDP 3702)
3. Direct Native Binary PTZ Protocol (Port 7777 TCP 32-byte packet)
4. Telnet Hardware Fallback (Port 23)
"""
import json
import socket
import time
import urllib.request
import urllib.error
import logging
from typing import Tuple, Dict, Any, List

logger = logging.getLogger("GardaClient")


class SriHomeClient:
    """
    Unified client for GARDA / CleanTV Provisioned Dual-Lens Cameras.
    Communicates via Port 8899 (ONVIF + REST API) and Port 7777 (Native PTZ).
    """
    # Port 7777 PTZ Opcodes
    CMD_LEFT = 0x40       # '@'
    CMD_RIGHT = 0x41      # 'A'
    CMD_DOWN = 0x42       # 'B'
    CMD_UP = 0x43         # 'C'
    CMD_RESET = 0x44      # 'D' - Self calibration / center
    CMD_CRUISE = 0x47     # 'G' - Auto 360 cruise
    CMD_TRACKING = 0x48   # 'H' - Auto human motion tracking
    CMD_MANUAL = 0x49     # 'I' - Stop auto tracking / manual mode

    def __init__(self, ip: str = "192.168.18.249", onvif_port: int = 8899, ptz_port: int = 7777, telnet_port: int = 23):
        self.ip = ip
        self.onvif_port = onvif_port
        self.ptz_port = ptz_port
        self.telnet_port = telnet_port
        self.is_connected = False
        self.onvif_active = False
        self.white_light_on = False
        self.ir_light_on = False
        self.tracking_on = False
        self.cruise_on = False

    def check_connection(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Verify connectivity to ONVIF/REST daemon (8899) and Native PTZ (7777)."""
        telemetry = {}
        # 1. Check Port 8899 REST API (/api/status)
        ok_api, data = self.get_telemetry()
        if ok_api:
            self.onvif_active = True
            self.is_connected = True
            telemetry = data
            return True, f"ONVIF & REST Daemon Aktif ({self.ip}:{self.onvif_port})", telemetry

        # 2. Fallback check Port 7777 Native PTZ
        try:
            with socket.socket() as s:
                s.settimeout(1.5)
                s.connect((self.ip, self.ptz_port))
            self.is_connected = True
            return True, f"Native PTZ Terhubung ({self.ip}:{self.ptz_port})", telemetry
        except Exception as e:
            self.is_connected = False
            return False, f"Gagal terhubung ke {self.ip}: {e}", telemetry

    def get_telemetry(self) -> Tuple[bool, Dict[str, Any]]:
        """Query GET /api/status on port 8899."""
        url = f"http://{self.ip}:{self.onvif_port}/api/status"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
                data = json.loads(raw)
                self.onvif_active = True
                return True, data
        except Exception as e:
            return False, {"error": str(e)}

    def get_onvif_device_info(self) -> Tuple[bool, Dict[str, str]]:
        """Send ONVIF SOAP GetDeviceInformation request to port 8899."""
        url = f"http://{self.ip}:{self.onvif_port}/onvif/device_service"
        soap_body = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">'
            '<s:Body xmlns:tds="http://www.onvif.org/ver10/device/wsdl">'
            '<tds:GetDeviceInformation/>'
            '</s:Body></s:Envelope>'
        ).encode("utf-8")
        try:
            req = urllib.request.Request(
                url,
                data=soap_body,
                headers={"Content-Type": "application/soap+xml; charset=utf-8"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                xml = resp.read().decode("utf-8", errors="ignore")
                info = {}
                for tag in ["Manufacturer", "Model", "FirmwareVersion", "SerialNumber", "HardwareId"]:
                    open_tag = f"<tds:{tag}>"
                    close_tag = f"</tds:{tag}>"
                    start = xml.find(open_tag)
                    end = xml.find(close_tag)
                    if start != -1 and end != -1:
                        info[tag] = xml[start + len(open_tag):end]
                return True, info
        except Exception as e:
            return False, {"error": str(e)}

    @staticmethod
    def discover_onvif_lan(timeout: float = 1.5) -> List[str]:
        """Broadcast WS-Discovery UDP 3702 Probe to find ONVIF cameras on LAN."""
        probe = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope" '
            'xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" '
            'xmlns:wsd="http://schemas.xmlsoap.org/ws/2005/04/discovery">'
            '<Header>'
            '<wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action>'
            '<wsa:MessageID>urn:uuid:garda-discovery-probe-01</wsa:MessageID>'
            '<wsa:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</wsa:To>'
            '</Header>'
            '<Body><wsd:Probe/></Body></Envelope>'
        ).encode("utf-8")

        found_ips = []
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(0.4)
        try:
            for target in ["239.255.255.250", "192.168.18.255", "192.168.18.249", "192.168.18.250"]:
                try:
                    s.sendto(probe, (target, 3702))
                except Exception:
                    pass
            start = time.time()
            while time.time() - start < timeout:
                try:
                    data, addr = s.recvfrom(4096)
                    ip = addr[0]
                    if ip not in found_ips:
                        found_ips.append(ip)
                except socket.timeout:
                    break
        except Exception:
            pass
        finally:
            s.close()
        return found_ips

    def _post_api(self, path: str) -> Tuple[bool, str]:
        """Call POST /api/... on port 8899."""
        url = f"http://{self.ip}:{self.onvif_port}{path}"
        try:
            req = urllib.request.Request(url, data=b"", method="POST")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                return True, resp.read().decode("utf-8", errors="ignore").strip()
        except Exception as e:
            return False, str(e)

    def send_ptz_packet(self, opcode: int, step: int = 30) -> Tuple[bool, str]:
        """Send a 32-byte binary PTZ packet to port 7777."""
        try:
            pkt = bytearray(32)
            pkt[0] = 0xAA
            pkt[1] = opcode & 0xFF
            pkt[2] = step & 0xFF
            pkt[3] = (step >> 8) & 0xFF
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1.5)
                sock.connect((self.ip, self.ptz_port))
                sock.sendall(pkt)
                res = sock.recv(32)
            if res and res[0] == 0xBB:
                return True, "OK (0xBB)"
            return False, "Kamera mengembalikan respons PTZ tidak valid"
        except Exception as e:
            return False, str(e)

    def move_left(self, step: int = 30) -> Tuple[bool, str]:
        ok, msg = self.send_ptz_packet(self.CMD_LEFT, step)
        if not ok:
            return self._post_api("/api/ptz?dir=left")
        return ok, msg

    def move_right(self, step: int = 30) -> Tuple[bool, str]:
        ok, msg = self.send_ptz_packet(self.CMD_RIGHT, step)
        if not ok:
            return self._post_api("/api/ptz?dir=right")
        return ok, msg

    def move_up(self, step: int = 30) -> Tuple[bool, str]:
        ok, msg = self.send_ptz_packet(self.CMD_UP, step)
        if not ok:
            return self._post_api("/api/ptz?dir=up")
        return ok, msg

    def move_down(self, step: int = 30) -> Tuple[bool, str]:
        ok, msg = self.send_ptz_packet(self.CMD_DOWN, step)
        if not ok:
            return self._post_api("/api/ptz?dir=down")
        return ok, msg

    def center_position(self) -> Tuple[bool, str]:
        """Move to center position x=515, y=70 via ONVIF/REST API."""
        ok, msg = self._post_api("/api/ptz?dir=center")
        if ok:
            return True, "Posisi Tengah (x=515, y=70)"
        return self.reset_calibrate()

    def reset_calibrate(self) -> Tuple[bool, str]:
        """Trigger camera PTZ self-calibration / center homing."""
        return self.send_ptz_packet(self.CMD_RESET, 0)

    def set_tracking(self, enable: bool) -> Tuple[bool, str]:
        """Enable or disable AI Human Motion Auto-Tracking."""
        opcode = self.CMD_TRACKING if enable else self.CMD_MANUAL
        ok, msg = self.send_ptz_packet(opcode, 0)
        if ok:
            self.tracking_on = enable
        return ok, msg

    def set_cruise(self, enable: bool) -> Tuple[bool, str]:
        """Enable or disable 360-degree cruise scan."""
        opcode = self.CMD_CRUISE if enable else self.CMD_MANUAL
        ok, msg = self.send_ptz_packet(opcode, 0)
        if ok:
            self.cruise_on = enable
        return ok, msg

    def execute_shell_cmd(self, cmd: str) -> Tuple[bool, str]:
        """Execute a shell command via passwordless Telnet port 23."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2.0)
                sock.connect((self.ip, self.telnet_port))
                time.sleep(0.12)
                payload = f"{cmd}\nexit\n".encode("utf-8")
                sock.sendall(payload)
                time.sleep(0.18)
                out = sock.recv(2048).decode("utf-8", errors="ignore")
            return True, out.strip()
        except Exception as e:
            return False, str(e)

    def set_white_light(self, enable: bool) -> Tuple[bool, str]:
        """Turn White Light Spotlight ON or OFF via REST API + PWM."""
        mode = "white_on" if enable else "white_off"
        ok, msg = self._post_api(f"/api/led?mode={mode}")
        if not ok:
            # Preserve owner-requested Telnet hardware fallback in lab testing.
            ok, msg = self.execute_shell_cmd(
                "echo 1 > /var/white_light" if enable else "rm -f /var/white_light"
            )
        if ok:
            self.white_light_on = enable
        return ok, f"Spotlight Putih {'ON' if enable else 'OFF'}" if ok else f"Spotlight gagal: {msg}"

    def set_ir_light(self, enable: bool) -> Tuple[bool, str]:
        """Turn IR Night Vision LED ON or OFF via REST API (/api/led) & GPIO 44."""
        mode = "ir_on" if enable else "ir_off"
        ok, msg = self._post_api(f"/api/led?mode={mode}")
        if not ok:
            val = "1" if enable else "0"
            ok, msg = self.execute_shell_cmd(f"/app/gpio_output.sh 44 {val}")
        if ok:
            self.ir_light_on = enable
        return ok, f"IR Night Vision {'ON' if enable else 'OFF'}" if ok else f"IR gagal: {msg}"

    def set_ircut_filter(self, night_mode: bool) -> Tuple[bool, str]:
        """Switch IR-Cut optical filter between Day (GPIO 39) and Night (GPIO 40)."""
        mode = "ircut_night" if night_mode else "ircut_day"
        ok, msg = self._post_api(f"/api/led?mode={mode}")
        if ok:
            return True, f"IR-Cut Filter: {'Night (Mode Malam)' if night_mode else 'Day (Mode Siang)'}"
        return False, msg
