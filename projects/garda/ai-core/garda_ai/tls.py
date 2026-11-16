"""Persistent site-local CA and server certificate; verification remains enabled in clients."""
import datetime
import ipaddress
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID


def provision_tls(root, host):
    address = ipaddress.ip_address(host)
    if not address.is_private or address.is_unspecified or address.is_multicast:
        raise ValueError("Use the server LAN or loopback IP")
    root = Path(root) / "tls"
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    ca_file, key_file = root/"site-ca.pem", root/"site-ca.key"
    now = datetime.datetime.now(datetime.timezone.utc)
    if ca_file.exists() != key_file.exists():
        raise ValueError("Incomplete site CA: restore its private key and certificate")
    if ca_file.is_file():
        key = serialization.load_pem_private_key(key_file.read_bytes(), password=None)
        ca = x509.load_pem_x509_certificate(ca_file.read_bytes())
    else:
        key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,"GARDA Internal Site CA")])
        ca = x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-datetime.timedelta(days=1)).not_valid_after(now+datetime.timedelta(days=3650)).add_extension(x509.BasicConstraints(ca=True,path_length=0),True).add_extension(x509.KeyUsage(True,False,False,False,False,True,True,False,False),True).sign(key,hashes.SHA256())
        ca_file.write_bytes(ca.public_bytes(serialization.Encoding.PEM))
        key_file.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
        key_file.chmod(0o600)
    server_key = rsa.generate_private_key(public_exponent=65537,key_size=3072)
    cert = x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,"GARDA Local Server")])).issuer_name(ca.subject).public_key(server_key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-datetime.timedelta(days=1)).not_valid_after(now+datetime.timedelta(days=365)).add_extension(x509.BasicConstraints(False,None),True).add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),False).add_extension(x509.SubjectAlternativeName([x509.IPAddress(address),x509.IPAddress(ipaddress.ip_address("127.0.0.1")),x509.DNSName("localhost")]),False).sign(key,hashes.SHA256())
    (root/"server.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    (root/"server.key").write_bytes(server_key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
    (root/"server.key").chmod(0o600)
    return {"host":host,"cert":str((root/"server.pem").resolve()),"key":str((root/"server.key").resolve()),"ca":str(ca_file.resolve())}
