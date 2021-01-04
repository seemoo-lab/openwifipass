from openwifipass.OPACK import OPACK


def test_encode_decode_dict():
    data = {"pf": 266256}
    encoded = OPACK.encode(data)
    decoded_data = OPACK.decode(encoded)

    assert data == decoded_data
