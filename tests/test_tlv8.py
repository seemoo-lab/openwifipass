from openwifipass.TLV8 import TLV8Box


def test_tlv8box_decode_encode():
    encoded = bytes.fromhex("4401ff4402ffff")
    decoded = TLV8Box.decodeFromData(encoded)

    assert encoded == decoded.encode()
