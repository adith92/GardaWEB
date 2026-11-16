# Configuration manager for CleanTV Camera Controller
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "camera_config.json")

DEFAULT_CONFIG = {
    "ip": "192.168.18.249",
    "onvif_port": 8899,
    "rtsp_port": 1234,
    "rtsp_port_2": 1235,
    "ptz_port": 7777,
    "telnet_port": 23,
    "rtsp_path": "/",
    "view_mode": "dual_v",
    "username": "admin",
    "password": "",
    "ptz_step": 30,
    "auto_connect": False,
    "rtsp_transport": "tcp",
    "snapshots_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots"),
    "recordings_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings"),
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception as e:
            print(f"Failed to load config: {e}")
    return DEFAULT_CONFIG.copy()


def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Failed to save config: {e}")
        return False
