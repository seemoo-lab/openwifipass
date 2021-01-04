import hashlib
import logging

from bluepy.btle import DefaultDelegate, Scanner

from .TLV8 import TLV8Box

# Password Sharing advertisment frame layout
# | 0  1  | 2     | 3  4  5  | 6  7  8  | 9  10 11    | 12 13 14    | 15 16 17    | 18 19 20    | 21 22 23 | 24     |
# | ----- | ----- | -------- | -------- | ----------- | ----------- | ----------- | ----------- | -------- | ------ |
# | 4c 00 | 0f    | 11 c0 08 | 55 eb 84 | 4b 60 e5    | 89 f9 12    | f4 4d cd    | e1 0d aa    | 10 02 5b | 0c     |
# | apple | pws   | const    | id       | mail        | phone       | appleID     | wifi SSID   | const    | const  |
# | const | const |          |          | sha256[0:3] | sha256[0:3] | sha256[0:3] | sha256[0:3] |          |        |

logger = logging.getLogger(__name__)

BLE_MANUFACTURER_DATA = 255
BLE_COMPANY_ID_APPLE = bytes.fromhex("4c00")
BLE_APPLE_PWS_TYPE = 0x0F


class PWSScanner(DefaultDelegate):
    def __init__(self, ssid):
        DefaultDelegate.__init__(self)
        self.result = None
        ssidHash = hashlib.sha256()
        ssidHash.update(ssid.encode())
        self.ssidHash = ssidHash.digest()

    def getPWSTLV(self, data):
        company_id = data[:2]
        if company_id != BLE_COMPANY_ID_APPLE:
            return None
        tlv8Dict = TLV8Box.decodeFromData(data[2:]).toDict()
        logger.debug(f"Apple advertisement {tlv8Dict}")
        return tlv8Dict.get(0x0F)

    def isSSIDInTLV(self, tlv):
        return tlv[-3:] == self.ssidHash[:3]

    def handleDiscovery(self, scanEntry, _isNewDev, _isNewData):
        for (adtype, _, value) in scanEntry.getScanData():
            if adtype == BLE_MANUFACTURER_DATA:
                data = bytes.fromhex(value)
                pwsTLV = self.getPWSTLV(data)
                if pwsTLV is not None:
                    if self.isSSIDInTLV(pwsTLV):
                        self.result = scanEntry

    def scan(self):
        """
        Scans for PWS advertisements with the given SSID and returns the first match
        """
        logger.info("Start scanning...")
        scanner = Scanner().withDelegate(self)
        scanner.clear()
        scanner.start(passive=True)
        while self.result is None:
            scanner.process(0.1)
        logger.info(f"SSID match in PWS advertisement from {self.result.addr}")
        scanner.stop()
        # return and clear result
        result = self.result
        self.result = None
        return result
