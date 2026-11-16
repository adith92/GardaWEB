"""
ONVIF Camera Controller
Handles ONVIF discovery, device management, PTZ movement, and preset controls.
"""
import logging
from typing import Optional, Tuple, List, Dict, Any

try:
    from onvif import ONVIFCamera
except ImportError:
    ONVIFCamera = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ONVIFController")


class ONVIFController:
    def __init__(self):
        self.camera: Optional[ONVIFCamera] = None
        self.media_service = None
        self.ptz_service = None
        self.imaging_service = None
        self.device_service = None
        self.profile = None
        self.profile_token: Optional[str] = None
        self.is_connected = False
        self.ip = ""
        self.port = 8899

    def connect(self, ip: str, port: int, username: str = "admin", password: str = "") -> Tuple[bool, str]:
        """
        Connect to the ONVIF service on the camera.
        Returns: (success: bool, message: str)
        """
        if ONVIFCamera is None:
            return False, "Library 'onvif-zeep' belum terinstall."

        self.ip = ip
        self.port = port
        try:
            logger.info(f"Connecting to ONVIF {ip}:{port} user='{username}'...")
            self.camera = ONVIFCamera(
                ip,
                port,
                username,
                password,
                no_cache=True
            )

            # Initialize services
            self.media_service = self.camera.create_media_service()
            profiles = self.media_service.GetProfiles()

            if not profiles or len(profiles) == 0:
                return False, "Tidak ditemukan Video Profile pada kamera ini."

            self.profile = profiles[0]
            self.profile_token = self.profile.token
            logger.info(f"ONVIF Connected! Active Profile: {self.profile.Name} (Token: {self.profile_token})")

            # Initialize PTZ if available
            try:
                self.ptz_service = self.camera.create_ptz_service()
                logger.info("PTZ Service initialized successfully.")
            except Exception as e:
                logger.warning(f"PTZ Service not available on this device: {e}")
                self.ptz_service = None

            # Initialize Imaging if available
            try:
                self.imaging_service = self.camera.create_imaging_service()
            except Exception:
                self.imaging_service = None

            self.is_connected = True
            return True, f"Terkoneksi ke ONVIF Profile '{self.profile.Name}'"

        except Exception as e:
            self.is_connected = False
            err_msg = str(e)
            logger.error(f"ONVIF connection error: {err_msg}")
            return False, f"Gagal konek ONVIF ({ip}:{port}): {err_msg}"

    def disconnect(self):
        self.camera = None
        self.media_service = None
        self.ptz_service = None
        self.imaging_service = None
        self.profile = None
        self.profile_token = None
        self.is_connected = False

    def get_stream_uri(self) -> Optional[str]:
        """Fetch RTSP stream URI using ONVIF Media Service."""
        if not self.is_connected or not self.media_service or not self.profile_token:
            return None
        try:
            req = self.media_service.create_type("GetStreamUri")
            req.ProfileToken = self.profile_token
            req.StreamSetup = {
                "Stream": "RTP-Unicast",
                "Transport": {"Protocol": "RTSP"}
            }
            res = self.media_service.GetStreamUri(req)
            uri = res.Uri
            # Ensure IP is replaced if camera reports 0.0.0.0 or internal IP
            if "0.0.0.0" in uri or "127.0.0.1" in uri:
                uri = uri.replace("0.0.0.0", self.ip).replace("127.0.0.1", self.ip)
            return uri
        except Exception as e:
            logger.error(f"Failed to get stream URI: {e}")
            return None

    def continuous_move(self, pan: float = 0.0, tilt: float = 0.0, zoom: float = 0.0) -> Tuple[bool, str]:
        """
        Move camera continuously in direction (pan, tilt, zoom).
        pan: -1.0 (Left) to +1.0 (Right)
        tilt: -1.0 (Down) to +1.0 (Up)
        zoom: -1.0 (Wide) to +1.0 (Tele)
        """
        if not self.is_connected or not self.ptz_service or not self.profile_token:
            return False, "PTZ tidak tersedia atau kamera belum terkoneksi."

        try:
            req = self.ptz_service.create_type("ContinuousMove")
            req.ProfileToken = self.profile_token
            req.Velocity = {
                "PanTilt": {"x": pan, "y": tilt},
                "Zoom": {"x": zoom}
            }
            self.ptz_service.ContinuousMove(req)
            return True, "Moving"
        except Exception as e:
            logger.error(f"ContinuousMove failed: {e}")
            return False, str(e)

    def stop_move(self) -> Tuple[bool, str]:
        """Stop all PTZ movements."""
        if not self.is_connected or not self.ptz_service or not self.profile_token:
            return False, "PTZ tidak aktif."

        try:
            req = self.ptz_service.create_type("Stop")
            req.ProfileToken = self.profile_token
            req.PanTilt = True
            req.Zoom = True
            self.ptz_service.Stop(req)
            return True, "Stopped"
        except Exception as e:
            logger.error(f"Stop failed: {e}")
            return False, str(e)

    def relative_move(self, pan: float, tilt: float, zoom: float = 0.0) -> Tuple[bool, str]:
        """Move camera by a relative step."""
        if not self.is_connected or not self.ptz_service or not self.profile_token:
            return False, "PTZ tidak aktif."

        try:
            req = self.ptz_service.create_type("RelativeMove")
            req.ProfileToken = self.profile_token
            req.Translation = {
                "PanTilt": {"x": pan, "y": tilt},
                "Zoom": {"x": zoom}
            }
            self.ptz_service.RelativeMove(req)
            return True, "Step Move"
        except Exception as e:
            logger.error(f"RelativeMove failed: {e}")
            return False, str(e)

    def get_presets(self) -> List[Dict[str, Any]]:
        """Get list of stored PTZ presets."""
        if not self.is_connected or not self.ptz_service or not self.profile_token:
            return []

        try:
            res = self.ptz_service.GetPresets(self.profile_token)
            presets = []
            for p in res:
                presets.append({
                    "token": p.token,
                    "name": getattr(p, "Name", f"Preset {p.token}")
                })
            return presets
        except Exception as e:
            logger.error(f"Failed to get presets: {e}")
            return []

    def goto_preset(self, preset_token: str) -> Tuple[bool, str]:
        """Move camera to preset."""
        if not self.is_connected or not self.ptz_service or not self.profile_token:
            return False, "PTZ tidak aktif."

        try:
            req = self.ptz_service.create_type("GotoPreset")
            req.ProfileToken = self.profile_token
            req.PresetToken = preset_token
            self.ptz_service.GotoPreset(req)
            return True, f"Menuju preset {preset_token}"
        except Exception as e:
            logger.error(f"GotoPreset failed: {e}")
            return False, str(e)

    def set_preset(self, preset_name: str) -> Tuple[bool, str]:
        """Save current position as a preset."""
        if not self.is_connected or not self.ptz_service or not self.profile_token:
            return False, "PTZ tidak aktif."

        try:
            req = self.ptz_service.create_type("SetPreset")
            req.ProfileToken = self.profile_token
            req.PresetName = preset_name
            res = self.ptz_service.SetPreset(req)
            token = getattr(res, "PresetToken", preset_name)
            return True, f"Preset '{preset_name}' tersimpan (token: {token})"
        except Exception as e:
            logger.error(f"SetPreset failed: {e}")
            return False, str(e)

    def send_auxiliary_command(self, command: str) -> Tuple[bool, str]:
        """
        Send ONVIF auxiliary command (commonly used for IR light, white LED, wiper, etc.)
        Example commands: 'tt:Wiper|On', 'tt:IRLamp|On', 'tt:IRLamp|Off', 'tt:Aux1|On'
        """
        if not self.is_connected or not self.ptz_service or not self.profile_token:
            return False, "PTZ tidak aktif."

        try:
            req = self.ptz_service.create_type("SendAuxiliaryCommand")
            req.ProfileToken = self.profile_token
            req.AuxiliaryData = command
            res = self.ptz_service.SendAuxiliaryCommand(req)
            return True, f"Auxiliary command '{command}' sent."
        except Exception as e:
            logger.warning(f"Auxiliary command failed: {e}")
            return False, str(e)
