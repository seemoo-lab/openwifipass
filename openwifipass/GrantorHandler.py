import hashlib
import logging

import hkdf
from Cryptodome.Cipher import ChaCha20_Poly1305
from cryptography.hazmat.primitives.asymmetric import x25519

from .Keys import SessionKeys
from .OPACK import OPACK
from .TLV8 import TLV8, TLV8Box

logger = logging.getLogger(__name__)


class GrantorHandler:
    def __init__(self, ssid, psk):
        self.session_keys = SessionKeys()
        self.shared_secret = None
        self.ssid = ssid
        self.psk = psk

    # Currently the data is not split into chunks if too large, since the giving device never exceeds this limit
    def send(self, frameType, body):
        data = bytearray()
        data.append(frameType)
        data.append(0x07)
        data += bytearray(body)

        dataLength = len(data)
        payload = []
        payload.append(dataLength)
        payload.append(0x00)
        payload += data
        self.pwsCharacteristic.write(bytes(payload), withResponse=True)

    def sendPWS1(self):
        logger.info("Send PWS1")
        opack_bytes = OPACK.encode(
            {
                "sid": b"\x01\x02\x03\x04",
                "shv": "1476.17",
            }
        )
        self.send(0x17, opack_bytes)

    def receivePWS2(self, _data):
        logger.info("Receive PWS2")
        self.sendM1()

    def sendM1(self):
        logger.info("Send M1")
        logger.debug(f"Session key: {self.session_keys.public}")
        tlv8_bytes = TLV8Box(
            [TLV8(0x03, self.session_keys.public), TLV8(0x06, b"\x01")]
        ).encode()
        opack_bytes = OPACK.encode(
            {
                "pf": "1052676",
                "pd": tlv8_bytes,
            }
        )
        self.send(0x12, opack_bytes)

    def receiveM2(self, data):
        logger.info("Receive M2")

        pvDict = OPACK.decode(data)
        tlv = TLV8Box.decodeFromData(pvDict["pd"]).toDict()
        searching_device_pub_key = x25519.X25519PublicKey.from_public_bytes(
            bytes(tlv[0x03])
        )
        self.shared_secret = self.session_keys.private.exchange(
            searching_device_pub_key
        )

        hkdf_inst = hkdf.Hkdf(
            "Pair-Verify-Encrypt-Salt".encode(), self.shared_secret, hash=hashlib.sha512
        )
        key = hkdf_inst.expand("Pair-Verify-Encrypt-Info".encode(), 32)

        encryptedData = bytes(tlv[0x05])[:-16]
        authKey = bytes(tlv[0x05])[-16:]
        nonce = "PV-Msg02".encode()

        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        plainData = cipher.decrypt_and_verify(encryptedData, authKey)
        plainTLV = TLV8Box.decodeFromData(plainData).toDict()

        # plainTLV contains authentication data:
        # {
        #    9: Signature over public keys of grantor and requestor
        #   10: Apple ID certificate (NSDataCompressed)
        #   20: Apple ID validation record (NSDataCompressed)
        # }
        logger.debug(f"Identity TLV: {plainTLV}")

        self.sendM3()

    def sendM3(self):
        logger.info("Send M3")

        hkdf_inst = hkdf.Hkdf(
            "Pair-Verify-Encrypt-Salt".encode(), self.shared_secret, hash=hashlib.sha512
        )
        key = hkdf_inst.expand("Pair-Verify-Encrypt-Info".encode(), 32)

        nonce = "PV-Msg03".encode()
        payload = bytes()
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        _ciphertext, authTag = cipher.encrypt_and_digest(payload)

        tlv8_bytes = TLV8Box([TLV8(0x05, authTag), TLV8(0x06, b"\x03")]).encode()

        opack_bytes = OPACK.encode(
            {
                "pd": tlv8_bytes,
            }
        )
        self.send(0x13, opack_bytes)

    def receiveM4(self, _data):
        logger.info("Receive M4")
        self.sendPWS3()

    def sendPWS3(self):
        logger.info("Send PWS3")

        hkdf_inst = hkdf.Hkdf(
            "WriteKeySalt".encode(), self.shared_secret, hash=hashlib.sha512
        )
        key = hkdf_inst.expand("WriteKeyInfo".encode(), 32)

        opack_bytes = OPACK.encode(
            {
                "op": 5,
                "nw": self.ssid,
                "psk": self.psk,
            }
        )

        aad = bytes(b"\x06\x07")
        nonce = bytes(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        cipher.update(aad)
        encryptedData, authTag = cipher.encrypt_and_digest(opack_bytes)
        encryptedData += authTag

        self.send(0x06, encryptedData)

    def receivePWS4(self, _data):
        logger.info("Receive PWS4")
