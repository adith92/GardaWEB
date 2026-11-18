"""Bounded, opt-in, private-LAN CCTV discovery for Windows and Linux.

No credentials, default-password checks, exploit probes, or camera configuration writes.
Open ports alone are NOT proof that a particular service or camera exists.
"""
from __future__ import annotations

import ipaddress
import os
import re
import socket
import subprocess
import threading
import time
import uuid
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

import psutil

RFC1918 = tuple(ipaddress.ip_network(c) for c in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))
INITIAL_PORTS = (21, 23, 80, 554, 8080, 8554, 8899, 1111, 8888)
EXTRA_PORTS = (443, 1234, 1235, 6666, 7777, 10055, 10067)
MAX_HOSTS = 512
MAX_WORKERS = 48
SERVICE_HINTS = {
    21: "ftp_candidate", 23: "telnet_candidate", 80: "http_candidate",
    443: "https_candidate", 554: "rtsp_candidate", 8080: "http_candidate",
    8554: "rtsp_candidate", 8899: "onvif_candidate", 1111: "mjpeg_candidate",
    8888: "media_candidate", 1234: "vendor_candidate", 1235: "vendor_candidate",
    6666: "vendor_candidate", 7777: "vendor_candidate",
    10055: "p2p_candidate", 10067: "p2p_candidate",
}


def private_ip(address: ipaddress.IPv4Address) -> bool:
    """Use RFC1918, not ipaddress.is_private (includes other reserved blocks)."""
    return any(address in block for block in RFC1918)


def network_interfaces() -> list[dict]:
    """Enumerate actual UP IPv4 network interfaces; trim huge LANs to host /24 scan suggestions."""
    stats = psutil.net_if_stats()
    results: list[dict] = []
    seen = set()
    for nic, addresses in psutil.net_if_addrs().items():
        if nic not in stats or not stats[nic].isup:
            continue
        for a in addresses:
            if a.family != socket.AF_INET or not a.netmask:
                continue
            try:
                address = ipaddress.IPv4Address(a.address)
                network = ipaddress.IPv4Network(f"{a.address}/{a.netmask}", strict=False)
            except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
                continue
            if not private_ip(address) or network.prefixlen == 32:
                continue
            suggestion = network if network.num_addresses <= MAX_HOSTS + 2 else ipaddress.IPv4Network(f"{address}/24", strict=False)
            if (str(network), str(address)) in seen:
                continue
            seen.add((str(network), str(address)))
            results.append({"interface": nic, "ip": str(address), "network": str(network),
                            "suggested_cidr": str(suggestion), "source": "local_interface"})
    return sorted(results, key=lambda x: (x["interface"], x["ip"]))


def allowed_network(cidr: str, interfaces: list[dict], target_ip: str | None = None,
                    explicit_allowlist: str = "") -> tuple[ipaddress.IPv4Network, list[str]]:
    """Reject external/unroutable and remote LAN targets and broad sweeps."""
    try:
        network = ipaddress.IPv4Network(cidr, strict=True)
    except (ValueError, TypeError) as exc:
        raise ValueError("CIDR must be a canonical IPv4 network, e.g. 192.168.1.0/24") from exc
    if network.num_addresses > MAX_HOSTS + 2 or network.prefixlen >= 32:
        raise ValueError("Network scan scope must include 2..512 addresses (use a /24 for large LANs)")
    if not all(private_ip(address) for address in (network.network_address, network.broadcast_address)):
        raise ValueError("Only RFC1918 private IPv4 LANs may be scanned")
    local = [ipaddress.IPv4Network(x["network"]) for x in interfaces]
    if not any(network.subnet_of(parent) for parent in local):
        raise ValueError("Network is not on an active local IPv4 interface")
    if explicit_allowlist.strip():
        try:
            allowed = [ipaddress.IPv4Network(x.strip(), strict=False) for x in explicit_allowlist.split(",") if x.strip()]
        except ValueError as exc:
            raise ValueError("GARDA_SCAN_ALLOWED_CIDRS contains invalid network") from exc
        if not any(network.subnet_of(entry) for entry in allowed):
            raise ValueError("Network not listed in GARDA_SCAN_ALLOWED_CIDRS")
    excluded = [x["ip"] for x in interfaces]
    if target_ip:
        try:
            host = ipaddress.IPv4Address(target_ip)
        except (ValueError, TypeError) as exc:
            raise ValueError("Invalid target IPv4 address") from exc
        if host not in network or host in (network.network_address, network.broadcast_address):
            raise ValueError("Target is outside the selected LAN or is broadcast/network address")
        if str(host) in excluded:
            raise ValueError("Scanning the application's host is disabled")
    return network, excluded


def _safe_label(raw: bytes) -> str:
    text = raw.decode("latin-1", "replace")
    # Only retain innocuous first-line / Server header metadata, never whole response bodies.
    first = text.splitlines()[0] if text.splitlines() else ""
    server = next((line for line in text.splitlines() if line.lower().startswith("server:")), "")
    out = server if server else first
    return re.sub(r"[^\w ./;:()=,+-]", "", out)[:110]


def probe_port(ip: str, port: int, timeout: float = 0.35) -> dict | None:
    """TCP handshake and optionally a bounded, read-only identification request."""
    try:
        with socket.create_connection((ip, port), timeout=timeout) as sock:
            sock.settimeout(min(timeout, 0.35))
            banner = b""
            evidence = "tcp_connect"
            if port in (554, 8554):
                sock.sendall((f"OPTIONS rtsp://{ip}:{port}/ RTSP/1.0\r\nCSeq: 1\r\nUser-Agent: GARDA-LAB\r\n\r\n").encode("ascii"))
            elif port in (80, 8080, 1111, 8899, 8888):
                sock.sendall((f"HEAD / HTTP/1.0\r\nHost: {ip}\r\nConnection: close\r\n\r\n").encode("ascii"))
            if port in (21, 23, 554, 8554, 80, 8080, 1111, 8899, 8888):
                try:
                    banner = sock.recv(1024)
                except (socket.timeout, OSError):
                    pass
            label = _safe_label(banner)
            kind = SERVICE_HINTS.get(port, "unidentified")
            if port in (554, 8554) and banner.startswith(b"RTSP/"):
                kind, evidence = "rtsp_confirmed", "rtsp_options_response"
            elif port == 21 and banner.startswith(b"220"):
                kind, evidence = "ftp_confirmed", "ftp_greeting"
            elif port in (80, 8080, 1111, 8899, 8888) and banner.startswith(b"HTTP/"):
                kind, evidence = "http_confirmed", "http_head_response"
                if b"mjpg-streamer" in banner.lower():
                    kind = "mjpg_streamer_confirmed"
            # ONVIF is never confirmed merely because TCP 8899 accepted a connection.
            return {"port": port, "hint": kind, "evidence": evidence, "banner": label}
    except (OSError, TimeoutError):
        return None


def arp_cache() -> dict[str, str]:
    """Best-effort passive ARP cache; no privileged discovery or third-party Nmap needed."""
    try:
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=2, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return {}
    found: dict[str, str] = {}
    for line in result.stdout.splitlines():
        ips = re.findall(r"(?<![0-9.])(?:\d{1,3}\.){3}\d{1,3}(?![0-9.])", line)
        mac = re.search(r"(?<![0-9a-f])(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}(?![0-9a-f])", line, re.I)
        if not mac:
            continue
        for ip in ips:
            try:
                parsed = ipaddress.IPv4Address(ip)
            except ValueError:
                continue
            if private_ip(parsed):
                found[ip] = mac.group().lower().replace("-", ":")
    return found


def discover_onvif(interface_ip: str, cidr: ipaddress.IPv4Network, timeout: float = 1.0) -> set[str]:
    """Optional ONVIF WS-Discovery multicast probe, bounded responses and no auth."""
    transaction = str(uuid.uuid4())
    payload = ("<?xml version='1.0'?>"
               "<s:Envelope xmlns:s='http://www.w3.org/2003/05/soap-envelope' "
               "xmlns:a='http://schemas.xmlsoap.org/ws/2004/08/addressing' "
               "xmlns:d='http://schemas.xmlsoap.org/ws/2005/04/discovery'>"
               "<s:Header><a:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe"
               "</a:Action><a:MessageID>uuid:" + transaction + "</a:MessageID>"
               "<a:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</a:To></s:Header>"
               "<s:Body><d:Probe/></s:Body></s:Envelope>").encode("utf-8")
    results: set[str] = set()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(interface_ip))
            sock.bind((interface_ip, 0))
            sock.settimeout(0.2)
            sock.sendto(payload, ("239.255.255.250", 3702))
            until = time.monotonic() + timeout
            while time.monotonic() < until and len(results) < 64:
                try:
                    raw, source = sock.recvfrom(12288)
                except socket.timeout:
                    continue
                source_ip = ipaddress.IPv4Address(source[0])
                if source_ip not in cidr:
                    continue
                try:
                    root = ET.fromstring(raw)
                    if root.find(".//{http://schemas.xmlsoap.org/ws/2005/04/discovery}ProbeMatches") is not None:
                        results.add(str(source_ip))
                except ET.ParseError:
                    pass
    except (OSError, ValueError):
        pass  # Windows firewall/adapter may block multicast: do not falsely mark it unsupported.
    return results


def scan_network(cidr: str, mode: str = "quick", target_ip: str | None = None,
                 interfaces: list[dict] | None = None,
                 probe: Callable[[str, int], dict | None] = probe_port,
                 enable_ws: bool = True) -> dict:
    """Two-stage bounded scan. Extended mode probes listed vendor ports on responding hosts."""
    interfaces = network_interfaces() if interfaces is None else interfaces
    network, own_ips = allowed_network(cidr, interfaces, target_ip, os.getenv("GARDA_SCAN_ALLOWED_CIDRS", ""))
    if mode not in ("quick", "extended"):
        raise ValueError("Mode must be quick or extended")
    hosts = [target_ip] if target_ip else [str(ip) for ip in network.hosts() if str(ip) not in own_ips]
    if not hosts:
        raise ValueError("No permitted remote hosts in this network")
    started = time.monotonic()
    observed: dict[str, list[dict]] = {}

    def stage(work: list[tuple[str, int]]):
        if not work:
            return
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(probe, ip, port): (ip, port) for ip, port in work}
            for future in as_completed(futures):
                ip, port = futures[future]
                try:
                    finding = future.result()
                except Exception:
                    finding = None
                if finding:
                    observed.setdefault(ip, []).append(finding)

    stage([(ip, port) for ip in hosts for port in INITIAL_PORTS])
    if mode == "extended":
        stage([(ip, port) for ip in sorted(observed) for port in EXTRA_PORTS])
    ws_matches: set[str] = set()
    if enable_ws:
        for interface in interfaces:
            if network.subnet_of(ipaddress.IPv4Network(interface["network"])):
                ws_matches.update(discover_onvif(interface["ip"], network))
    macs = arp_cache()
    devices = []
    for ip in sorted(set(observed) | ws_matches, key=ipaddress.IPv4Address):
        ports = sorted(observed.get(ip, []), key=lambda x: x["port"])
        hints = {entry["hint"] for entry in ports}
        confirmed = ip in ws_matches or "rtsp_confirmed" in hints or "mjpg_streamer_confirmed" in hints
        possible = confirmed or any(p["port"] in (554, 8554, 8899, 1111, 6666, 7777, 8888) for p in ports)
        devices.append({"ip": ip, "mac": macs.get(ip), "open_ports": ports,
                        "onvif_ws_discovery": ip in ws_matches,
                        "classification": "camera_evidence" if confirmed else "possible_camera" if possible else "other_device",
                        "flags": [name for name, port in (("ftp_port_open", 21), ("telnet_port_open", 23)) if any(p["port"] == port for p in ports)]})
    return {"network": str(network), "mode": mode, "target_ip": target_ip,
            "devices": devices, "host_count": len(hosts),
            "duration_seconds": round(time.monotonic()-started, 2),
            "cautions": ["Unresponsive hosts may still exist (ICMP is not required or used)",
                         "ONVIF PTZ/RTSP video paths require credentialed capability tests",
                         "Do not equate port 23 with successful Telnet shell access"]}


class ScanManager:
    """One scan at a time, asynchronous to API requests, with encrypted SQLite results."""
    def __init__(self, store, scanner=scan_network):
        self.store, self.scanner = store, scanner
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None

    def start(self, cidr: str, mode: str = "quick", target_ip: str | None = None) -> str:
        # Validate before allocating job; local interface inventory must not be client-supplied.
        allowed_network(cidr, network_interfaces(), target_ip, os.getenv("GARDA_SCAN_ALLOWED_CIDRS", ""))
        if mode not in ("quick", "extended"):
            raise ValueError("Unsupported mode")
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError("A LAN scan is already running")
            scan_id = self.store.create_scan(cidr, mode, target_ip)
            self._thread = threading.Thread(target=self._run, args=(scan_id, cidr, mode, target_ip), daemon=True)
            self._thread.start()
            return scan_id

    def _run(self, scan_id: str, cidr: str, mode: str, target_ip: str | None):
        try:
            self.store.finish_scan(scan_id, "running", {"devices": [], "message": "Scanning private LAN"})
            result = self.scanner(cidr, mode=mode, target_ip=target_ip)
            self.store.finish_scan(scan_id, "completed", result)
        except Exception as exc:
            self.store.finish_scan(scan_id, "failed", {"error": type(exc).__name__, "message": "Scan failed; review local interface and firewall"})

    def close(self) -> bool:
        # A running background scan may still use Store. Return False to keep DB
        # alive until process exit rather than closing it out from under the thread.
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=6)
        return not (thread and thread.is_alive())
