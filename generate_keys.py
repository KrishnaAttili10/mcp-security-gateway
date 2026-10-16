from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


BASE_DIR = Path(__file__).resolve().parent

PRIVATE_KEY_PATH = BASE_DIR / "private_key.pem"
PUBLIC_KEY_PATH = BASE_DIR / "public_key.pem"


def generate_keys():
    # Don't accidentally overwrite existing keys
    if PRIVATE_KEY_PATH.exists() or PUBLIC_KEY_PATH.exists():
        print("RSA keys already exist. Skipping generation.")
        return

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    PRIVATE_KEY_PATH.write_bytes(private_key_bytes)
    PUBLIC_KEY_PATH.write_bytes(public_key_bytes)

    print("RSA key pair generated successfully!")
    print("Private key:", PRIVATE_KEY_PATH.name)
    print("Public key:", PUBLIC_KEY_PATH.name)


if __name__ == "__main__":
    generate_keys()