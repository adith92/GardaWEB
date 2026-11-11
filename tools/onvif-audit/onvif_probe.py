#!/usr/bin/env python3
"""GARDA read-only LAN ONVIF diagnostic (no firmware changes)."""
import argparse
import getpass
import json
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_HOSTS = ("192.168.18.232", "192.168.18.233")
DEFAULT_PORTS = (80, 8899, 8080, 8000, 2020)
NETWORK_PORTS = (80, 443, 554, 8554, 8899, 8080, 8000, 2020)


def tcp_open(host: str, port: int, timeout: float = 1.2) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def error_summary(exc: Exception) -> str:
    # Avoid printing SOAP payloads/URLs, which could contain credentials.
    return type(exc).__name__


def onvif_probe(host: str, port: int, username: str, password: str) -> dict:
    from onvif import ONVIFClient

    record = {"port": port, "device_service": False}
    client = ONVIFClient(host=host, port=port, username=username or None,
                         password=password or None, timeout=5)
    device = client.devicemgmt()
    details = device.GetDeviceInformation()
    record["device_service"] = True
    record["manufacturer"] = str(getattr(details, "Manufacturer", ""))
    record["model"] = str(getattr(details, "Model", ""))
    record["firmware_version"] = str(getattr(details, "FirmwareVersion", ""))

    try:
        media = client.media()
        profiles = media.GetProfiles()
        record["media_profiles"] = []
        for p in profiles:
            token = str(getattr(p, "token", ""))
            item = {"name": str(getattr(p, "Name", "")), "has_token": bool(token)}
            try:
                stream = media.GetStreamUri(
                    ProfileToken=token,
                    StreamSetup={"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}},
                )
                item["rtsp_uri_available"] = bool(getattr(stream, "Uri", None))
                # Do not print returned URLs: may contain credentials or tokens.
            except Exception as exc:
                item["rtsp_uri_error"] = error_summary(exc)
            record["media_profiles"].append(item)
        try:
            record["audio_input_count"] = len(media.GetAudioSources())
        except Exception as exc:
            record["audio_input_error"] = error_summary(exc)
    except Exception as exc:
        record["media_error"] = error_summary(exc)

    try:
        ptz = client.ptz()
        record["ptz_configuration_count"] = len(ptz.GetConfigurations())
    except Exception as exc:
        record["ptz_error"] = error_summary(exc)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="GARDA read-only ONVIF camera lab probe")
    parser.add_argument("--hosts", nargs="+", default=list(DEFAULT_HOSTS))
    parser.add_argument("--user", default="adith92", help="camera username; never put a password on the CLI")
    parser.add_argument("--ports", type=int, nargs="+", default=list(DEFAULT_PORTS))
    parser.add_argument("--output", default="garda_onvif_report.json")
    args = parser.parse_args()
    try:
        from onvif import ONVIFClient  # noqa: F401
    except ImportError:
        print("Install dependency first: python3 -m pip install onvif-python", file=sys.stderr)
        return 2

    pwd = getpass.getpass("Camera password (hidden; not saved): ")
    report = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "read_only": True, "cameras": []}
    for host in args.hosts:
        entry = {"host": host, "open_tcp_ports": [], "onvif": None, "probe_errors": []}
        print(f"Checking {host} ...", flush=True)
        entry["open_tcp_ports"] = [p for p in NETWORK_PORTS if tcp_open(host, p)]
        for port in args.ports:
            if port not in entry["open_tcp_ports"]:
                continue
            try:
                entry["onvif"] = onvif_probe(host, port, args.user, pwd)
                print(f"  ONVIF service found on TCP {port}", flush=True)
                break
            except Exception as exc:
                entry["probe_errors"].append({"port": port, "error_type": error_summary(exc)})
        if entry["onvif"] is None:
            print("  No verified ONVIF service on tested ports", flush=True)
        report["cameras"].append(entry)
    Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved: {args.output}. No credentials, RTSP URLs, or serial numbers stored.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
