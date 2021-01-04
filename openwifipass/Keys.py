from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519


class SessionKeys:
    def __init__(self):
        self.private = x25519.X25519PrivateKey.generate()
        self.public = self.private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
        )
