class TLV8:
    def __init__(self, type_, data):
        self.type_ = type_
        self.payload = data
        self.length = len(data)

    def encode(self):
        data = [self.type_]
        data.append(self.length)
        data.extend(list(self.payload))
        return bytes(data)

    def __str__(self):
        return "TLV8(type: {}, length: {}, payload: {})".format(
            self.type_, self.length, self.payload
        )


class TLV8Box:
    def __init__(self, tlv8s):
        self.tlv8s = tlv8s

    def encode(self):
        data = []
        for tlv8 in self.tlv8s:
            data.extend(tlv8.encode())
        return bytes(data)

    def toDict(self):
        dict_ = {}
        for tlv in self.tlv8s:
            if not dict_.get(tlv.type_):
                dict_[tlv.type_] = bytearray()
            dict_[tlv.type_] += bytearray(tlv.payload)
        return dict_

    def __str__(self):
        out = "TLB8Box [\n"
        for tlv8 in self.tlv8s:
            out += "  {} \n".format(tlv8)
        out += "]"
        return out

    @staticmethod
    def decodeFromData(data):
        tlv8s = []
        position = 0
        while True:
            if position + 2 >= len(data):
                break
            type_ = data[position]
            length = data[position + 1]
            payload = data[position + 2 : position + 2 + length]
            position += 2 + length
            tlv8s.append(TLV8(type_, payload))
        return TLV8Box(tlv8s)
