"""Verify package inventory from downloaded bytes, then produce OTA metadata/checksums."""
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

root = Path(sys.argv[1])
expected = ["GARDA-Web-0.13.0.zip", "GARDA-Windows-x64-0.13.0.exe", "GARDA-macOS-arm64-0.13.0.dmg",
            "GARDA-Ubuntu-x64-0.13.0.deb", "GARDA-Linux-x64-0.13.0.AppImage",
            "GARDA-FOLD-0.13.0.apk", "GARDA-Standard-0.13.0.apk"]
for name in expected:
    assert (root/name).is_file() and (root/name).stat().st_size > 1000, name + " missing/empty"
hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.iterdir()) if p.is_file()}
(root/"SHA256SUMS.txt").write_text("".join(f"{v}  {k}\n" for k,v in hashes.items()))
url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/releases/tags/{os.environ['GITHUB_REF_NAME']}"
request = urllib.request.Request(url, headers={"Authorization": "Bearer "+os.environ['GH_TOKEN'], "Accept": "application/vnd.github+json"})
with urllib.request.urlopen(request) as response:
    assets = {a['name']:a for a in json.load(response)['assets']}
manifest = {}
for channel, name, package in [("fold",expected[5],"org.foldview.cctv"),("standard",expected[6],"org.garda.cctv.standard")]:
    manifest[channel] = {"assetId": assets[name]['id'], "sha256": hashes[name], "sizeBytes": (root/name).stat().st_size,
                         "packageName": package, "versionName": "0.13.0", "versionCode": 17}
(root/"updates.json").write_text(json.dumps(manifest, indent=2)+"\n")
print(json.dumps({"verified_packages": expected, "hashes": hashes},indent=2))
