import argparse
import logging
import sys

from .Connection import startPWS
from .Scanner import PWSScanner


# Search until we found one pws advertisment frame
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--ssid", help="The Wi-Fi name (SSID)", required=True)
    parser.add_argument(
        "-k", "--psk", help="The Wi-Fi pre-shared key (PSK)", required=True
    )
    parser.add_argument(
        "-d", "--debug", help="Enable debug messages", action="store_true"
    )
    args = parser.parse_args(sys.argv[1:])

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    scanResult = PWSScanner(args.ssid).scan()
    startPWS(scanResult.addr, args.ssid, args.psk)


if __name__ == "__main__":
    main()
