class OPACK:
    @staticmethod
    def encode(object_):
        return bytes(OPACKEncode().encode(object_))

    @staticmethod
    def decode(data):
        return OPACKDecode(data).parse()


class OPACKDecodeError(Exception):
    pass


class OPACKEncodeError(Exception):
    pass


class OPACKDecode:
    def __init__(self, data):
        self.data = data
        self.position = 0

    def readBytes(self, bytesCount):
        posFrom = self.position
        posTo = self.position + bytesCount
        self.position += bytesCount
        return self.data[posFrom:posTo]

    def parse(self):
        dataTypes = {
            0x01: self.parseTrue,
            0x02: self.parseFalse,
            0x05: self.parseUUID,
            0x06: self.parseDate,
            0x35: self.parseFloat32,
            0x36: self.parseFloat64,
            0xDF: self.parseArrayEndless,
            0xEF: self.parseDictEndless,
        }
        type_ = self.readBytes(1)[0]
        method = dataTypes.get(type_)
        if not method:
            if type_ >= 0x08 and type_ <= 0x2F:
                return type_ - 0x08
            if type_ >= 0x30 and type_ <= 0x33:
                return self.parseIntX(type_ - 0x30 + 1)
            if type_ >= 0x40 and type_ <= 0x60:
                return self.parseStringWithLength(type_ - 0x40)
            if type_ >= 0x61 and type_ <= 0x64:
                return self.parseStringX(type_ - 0x60)
            if type_ >= 0x70 and type_ <= 0x90:
                return self.parseDataWithLength(type_ - 0x70)
            if type_ >= 0x91 and type_ <= 0x94:
                return self.parseDataX(type_ - 0x90)
            if type_ >= 0xD0 and type_ <= 0xDE:
                return self.parseArray(type_ - 0xD0 + 1)
            if type_ >= 0xE0 and type_ <= 0xEE:
                return self.parseDict(type_ - 0xE0 + 1)
            raise OPACKDecodeError(f"Unknown type {type_}")
        else:
            return method()

    def parseTrue(self):
        return True

    def parseFalse(self):
        return False

    def parseUUID(self):
        return self.readBytes(4)

    def parseDate(self):
        self.position += 4
        return None  # TODO

    def parseIntX(self, length):
        data = self.readBytes(length)
        return int.from_bytes(data, byteorder="big")

    def parseFloat32(self):
        self.position += 4
        return None  # TODO

    def parseFloat64(self):
        self.position += 8
        return None  # TODO

    def parseStringX(self, length):
        return self.parseDataX(length).decode("utf-8", "strict")

    def parseStringWithLength(self, length):
        return self.parseDataWithLength(length).decode("utf-8", "strict")

    def parseDataX(self, length):
        data = self.readBytes(length)
        dataLength = int.from_bytes(data, byteorder="big")
        return self.parseDataWithLength(dataLength)

    def parseDataWithLength(self, length):
        return self.readBytes(length)

    def parseArray(self, count):
        outArray = []
        for _ in range(1, count):
            outArray.append(self.parse())
        return outArray

    def parseArrayEndless(self):
        outArray = []
        while True:
            outArray.append(self.parse())
            if self.position <= len(self.data):
                break
            if self.data[(self.position + 1)] == 0x03:
                self.position += 1
                break
        return outArray

    def parseDict(self, count):
        outDict = {}
        for _ in range(1, count):
            key = self.parse()
            value = self.parse()
            outDict[key] = value
        return outDict

    def parseDictEndless(self, _):
        outDict = {}
        while True:
            key = self.parse()
            value = self.parse()
            outDict[key] = value
            if self.position <= len(self.data):
                break
            if self.data[(self.position + 1)] == 0x03:
                self.position += 1
                break
        return outDict


class OPACKEncode:
    def encode(self, object_):
        types = {
            bool: self.encodeBool,
            int: self.encodeInt,
            # TODO add float
            str: self.encodeString,
            bytes: self.encodeData,
            list: self.encodeArray,
            dict: self.encodeDict,
            # TODO add date
            # TODO add UUID
        }
        type_ = type(object_)
        method = types.get(type_)
        if method:
            return method(object_)
        else:
            raise OPACKEncodeError(f"Unsupported type {type_}")

    def encodeBool(self, value):
        if value:
            return [0x01]
        else:
            return [0x02]

    def encodeInt(self, value):
        if value < 0x27:
            return [value + 0x08]
        for i in range(0, 4):
            if value < pow(2, 8 * (i + 1)):
                data = list(value.to_bytes(i + 1, byteorder="big"))
                data.insert(0, 0x30 + i)
                return data
        raise OPACKEncodeError(f"Failed to encode {value} (type int)")

    def encodeString(self, value):
        length = len(value)
        if length <= 0x20:
            data = list(value.encode(encoding="UTF-8", errors="strict"))
            data.insert(0, length + 0x40)
            return data
        for i in range(0, 4):
            if length < pow(2, 8 * (i + 1)):
                data = list(length.to_bytes(i + 1, byteorder="big"))
                data.insert(0, 0x61 + i)
                data.extend(list(value.encode(encoding="UTF-8", errors="strict")))
                return data
        raise OPACKEncodeError(f"Failed to encode {value} (type string)")

    def encodeData(self, value):
        length = len(value)
        if length <= 0x20:
            data = list(value)
            data.insert(0, length + 0x70)
            return data
        for i in range(0, 4):
            if length < pow(2, 8 * (i + 1)):
                data = list(length.to_bytes(i + 1, byteorder="big"))
                data.insert(0, 0x91 + i)
                data.extend(list(value))
                return data
        raise OPACKEncodeError(f"Failed to encode {value} (type bytes)")

    def encodeArray(self, value):
        length = len(value)
        if length < 0x0F:
            data = [length + 0xD0]
            for entry in value:
                data.extend(self.encode(entry))
            return data
        else:
            data = [0xDF]
            for entry in value:
                data.extend(self.encode(entry))
            data.append(0x03)
            return data

    def encodeDict(self, value):
        length = len(value)
        if length < 0x0F:
            data = [length + 0xE0]
            for key, v in value.items():
                data.extend(self.encode(key))
                data.extend(self.encode(v))
            return data
        else:
            data = [0xEF]
            for key, v in value.items():
                data.extend(self.encode(key))
                data.extend(self.encode(v))
            data.append(0x03)
            return data
