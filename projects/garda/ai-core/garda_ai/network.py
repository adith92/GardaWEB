"""Bounded built-in TCP discovery, shared by all five clients. No external binary."""
from __future__ import annotations

import ipaddress
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import islice, product

import psutil

PRIVATE = tuple(ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))
DEFAULT_PORTS = "21,23,80,443,554,1111,1234,1235,6666,7777,8000,8080,8554,8888,8899,10055,10067"
HINTS = {21: "FTP?", 23: "Telnet?", 80: "HTTP?", 443: "HTTPS?", 554: "RTSP?",
         1111: "MJPEG?", 8000: "ONVIF/vendor?", 8080: "HTTP?", 8554: "RTSP?", 8899: "ONVIF?"}


def interfaces():
    found = []
    stats = psutil.net_if_stats()
    for name, entries in psutil.net_if_addrs().items():
        if name not in stats or not stats[name].isup:
            continue
        for entry in entries:
            if entry.family != socket.AF_INET or not entry.netmask:
                continue
            address = ipaddress.ip_address(entry.address)
            if not any(address in block for block in PRIVATE):
                continue
            network = ipaddress.ip_network(f"{address}/{entry.netmask}", strict=False)
            suggested = network if network.prefixlen >= 24 else ipaddress.ip_network(f"{address}/24", strict=False)
            found.append({"name": name, "ip": str(address), "network": str(network), "suggested": str(suggested)})
    return found


def scope(target, ports, local):
    try:
        network = ipaddress.IPv4Network(target.strip(), strict=False)
    except (ValueError, AttributeError):
        raise ValueError("Masukkan IPv4 atau subnet CIDR yang valid")
    if not any(network.subnet_of(block) for block in PRIVATE):
        raise ValueError("Hanya LAN IPv4 privat yang dapat dipindai")
    if network.num_addresses > 256:
        raise ValueError("Maksimal satu subnet /24 per pemindaian")
    if not any(network.subnet_of(ipaddress.IPv4Network(item["network"])) for item in local):
        raise ValueError("Target harus berada pada interface LAN server yang aktif")
    selected = set()
    try:
        for part in ports.split(","):
            span = part.strip().split("-")
            if len(span) not in (1, 2):
                raise ValueError()
            first, last = int(span[0]), int(span[-1])
            if not 1 <= first <= last <= 65535:
                raise ValueError()
            selected.update(range(first, last + 1))
    except (ValueError, AttributeError):
        raise ValueError("Port harus 1–65535; contoh 80,443,554 atau 1-65535")
    hosts = list(network.hosts())
    if not selected or len(hosts) * len(selected) > 65535:
        raise ValueError("Maksimal 65535 koneksi; pilih satu IP untuk full port scan")
    return [str(ip) for ip in hosts], sorted(selected)


def probe(item):
    ip, port = item
    try:
        with socket.create_connection((ip, port), timeout=0.25):
            return {"ip": ip, "port": port, "hint": HINTS.get(port, "Layanan belum diketahui")}
    except OSError:
        return None


class NetworkScanner:
    def __init__(self):
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.thread = None
        self.state = {"status": "idle", "completed": 0, "total": 0, "results": [], "source": "server"}

    def snapshot(self):
        with self.lock:
            return {**self.state, "results": list(self.state["results"])}

    def start(self, target, ports):
        hosts, numbers = scope(target, ports, interfaces())
        with self.lock:
            if self.thread and self.thread.is_alive():
                raise RuntimeError("Pemindaian sebelumnya masih berjalan")
            self.stop.clear()
            self.state = {"status": "running", "target": target, "completed": 0,
                          "total": len(hosts)*len(numbers), "results": [], "truncated": False, "source": "server"}
            self.thread = threading.Thread(target=self._run, args=(hosts, numbers), daemon=True)
            self.thread.start()
        return self.snapshot()

    def cancel(self):
        self.stop.set()
        return self.snapshot()

    def _run(self, hosts, numbers):
        until = time.monotonic() + 300
        tasks = product(hosts, numbers)
        status = "completed"
        try:
            with ThreadPoolExecutor(max_workers=64) as pool:
                while True:
                    if self.stop.is_set():
                        status = "cancelled"
                        break
                    if time.monotonic() > until:
                        status = "timed_out"
                        break
                    batch = list(islice(tasks, 64))
                    if not batch:
                        break
                    for result in pool.map(probe, batch):
                        with self.lock:
                            self.state["completed"] += 1
                            if result:
                                if len(self.state["results"]) < 1000:
                                    self.state["results"].append(result)
                                else:
                                    self.state["truncated"] = True
        except Exception:
            status = "failed"
        finally:
            with self.lock:
                self.state["status"] = status
