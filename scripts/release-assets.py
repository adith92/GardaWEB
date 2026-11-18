"""Verify package inventory from downloaded bytes, then produce OTA metadata/checksums."""
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path
from cryptography.hazmat.primitives import hashes as crypto_hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import pkcs12
import base64

root = Path(sys.argv[1])
expected = ["GARDA-Web-0.14.0.zip", "GARDA-Windows-x64-0.14.0.exe", "GARDA-macOS-arm64-0.14.0.dmg",
            "GARDA-Ubuntu-x64-0.14.0.deb", "GARDA-Linux-x64-0.14.0.AppImage",
            "GARDA-FOLD-0.14.0.apk", "GARDA-Standard-0.14.0.apk",
            "GARDA-Server-Windows-x64-0.14.0.zip", "GARDA-Server-Ubuntu-x64-0.14.0.zip"]
for name in expected:
    assert (root/name).is_file() and (root/name).stat().st_size > 1000, name + " missing/empty"
hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.iterdir()) if p.is_file()}
(root/"SHA256SUMS.txt").write_text("".join(f"{v}  {k}\n" for k,v in hashes.items()))
tag = os.environ.get('GARDA_RELEASE_TAG') or os.environ['GITHUB_REF_NAME']
url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/releases?per_page=100"
request = urllib.request.Request(url, headers={"Authorization": "Bearer "+os.environ['GH_TOKEN'], "Accept": "application/vnd.github+json"})
with urllib.request.urlopen(request) as response:
    releases = json.load(response)
    release = next(r for r in releases if r['tag_name'] == tag)
    assets = {a['name']:a for a in release['assets']}
manifest = {}
for channel, name, package in [("fold",expected[5],"org.foldview.cctv"),("standard",expected[6],"org.garda.cctv.standard")]:
    manifest[channel] = {"assetId": assets[name]['id'], "sha256": hashes[name], "sizeBytes": (root/name).stat().st_size,
                         "packageName": package, "versionName": "0.14.0", "versionCode": 18}
(root/"updates.json").write_text(json.dumps(manifest, indent=2)+"\n")
hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.iterdir())
          if p.is_file() and p.name not in {'SHA256SUMS.txt', 'SHA256SUMS.sig', 'GARDA-Release-PublicKey.pem'}}
(root/"SHA256SUMS.txt").write_text("".join(f"{v}  {k}\n" for k,v in hashes.items()))
key, certificate, _ = pkcs12.load_key_and_certificates(base64.b64decode(os.environ['GARDA_RELEASE_PFX_B64']),
    os.environ['GARDA_RELEASE_PFX_PASSWORD'].encode())
assert certificate.fingerprint(crypto_hashes.SHA256()).hex() == '9bea20396a3ab4d749f3335c4e852ae56473a52c37b07634ece8bba623b51019'
payload = (root/'SHA256SUMS.txt').read_bytes()
signature = key.sign(payload, padding.PKCS1v15(), crypto_hashes.SHA256())
certificate.public_key().verify(signature, payload, padding.PKCS1v15(), crypto_hashes.SHA256())
(root/'SHA256SUMS.sig').write_bytes(signature)
(root/'GARDA-Release-PublicKey.pem').write_bytes(certificate.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
print(json.dumps({"verified_packages": expected, "hashes": hashes},indent=2))
