import logging
import struct
import time
from uuid import UUID

from bluepy.btle import ADDR_TYPE_RANDOM, DefaultDelegate, Peripheral

from .GrantorHandler import GrantorHandler

logger = logging.getLogger(__name__)

PWSGATTServiceUUID = UUID("9FA480E0496745429390D343DC5D04AE")
PWSGATTCharacteristicUUID = UUID("AF0BADB15B9943CD917AA77BC549E3CC")


# Reconstructs the mechanism used by Apple in the password sharing process
class WPNearbyReadDelegate(DefaultDelegate):
    state = 0

    # Current state of frame reception, ether:
    # - False: the last frame was fully recived, ready for a new frame.
    # - True: the expectedPayloadLength is still larger as the length of the
    #         recived data, waiting for more data.
    openFrame = False

    # WPNearby payload
    payload = []

    # The expected length of the full WPNearby frame. This length is given in
    # the first 2 bytes of a new frame.
    expectedPayloadLength = 0

    def __init__(self, grantorHandler):
        DefaultDelegate.__init__(self)
        self.pwsHandler = grantorHandler

    def handleNotification(self, _, data):
        # If we have an open frame, append data and check if package is complete
        if self.openFrame:
            self.payload += data

        # Received data without an open frame, so we open a new frame with this data
        else:
            # calculate the expected package size from the first 2 bytes
            expLenBytes = data[0:2]
            expLenBytes += b"\x00\x00"
            expected = struct.unpack("<L", expLenBytes)[0]

            # set self.payload to the payload part of the recived data
            self.payload = data[2:]

            self.openFrame = True
            self.expectedPayloadLength = expected

        logger.debug(
            f"Data for frame {len(self.payload)} of {self.expectedPayloadLength} bytes"
        )

        # If the size of the recived data equals the given package size (first 2 bytes in first package), all package data has been recived
        if len(self.payload) >= self.expectedPayloadLength:
            self.openFrame = False

            # frameType is the first byte/ service type the second
            frameType = self.payload[0]
            # serviceType = self.payload[1]
            data = self.payload[2:]

            # check if frameType is 0x18 (PWS1)
            if frameType == 24 and self.state == 0:
                self.state = 1
                self.pwsHandler.receivePWS2(data)
                return

            # check if frameType is 0x13 (M2)
            if frameType == 19 and self.state == 1:
                self.state = 2
                self.pwsHandler.receiveM2(data)
                return

            if frameType == 19 and self.state == 2:
                self.state = 3
                self.pwsHandler.receiveM4(data)
                return

            if frameType == 6 and self.state == 3:
                self.pwsHandler.receivePWS4(data)
                return

            logger.warning("Received unknown frame")


def startPWS(addr, ssid, psk):
    logger.info(f"Connect to device {addr}")

    grantorHandler = GrantorHandler(ssid, psk)

    # Init Peripheral, connect to it an set read delegate
    peripheral = Peripheral(addr, ADDR_TYPE_RANDOM)
    peripheral.setDelegate(WPNearbyReadDelegate(grantorHandler))

    pwsService = peripheral.getServiceByUUID(PWSGATTServiceUUID)
    pwsCharacteristic = pwsService.getCharacteristics(
        forUUID=PWSGATTCharacteristicUUID
    )[0]
    logger.debug(f"PWS characteristic: {pwsCharacteristic.getHandle()}")
    grantorHandler.pwsCharacteristic = pwsCharacteristic

    time.sleep(0.5)

    # Subscribe to the PWS characteristics by sending 0x0200 to pwsCharacteristic Handle+1 (Todo clean uo and check if it is always +1)
    peripheral.writeCharacteristic(
        pwsCharacteristic.getHandle() + 2, b"\x01\x00", withResponse=True
    )

    grantorHandler.sendPWS1()

    while peripheral.waitForNotifications(2):
        pass

    peripheral.disconnect()

    logger.info("Wi-Fi Password Sharing completed")
