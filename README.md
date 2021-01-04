# OpenWifiPass

An open source implementation of the grantor role in Apple's Wi-Fi Password Sharing protocol.

## Disclaimer

OpenWifiPass is experimental software and is the result of reverse engineering efforts by the [Open Wireless Link](https://owlink.org) project.
The code serves solely documentary and educational purposes. It is *untested* and *incomplete*.
For example, the code **does not verify the identity of the requestor**. So, do not use this implementation with sensitive Wi-Fi credentials.
OpenWifiPass is not affiliated with or endorsed by Apple Inc.

## Requirements

**Hardware:** Bluetooth Low Energy radio, e.g., Raspberry Pi 4

**OS:** Linux (due to the `bluepy` dependency)

## Install

Clone this repository and install it:

```bash
git clone git@github.com/seemoo-lab/openwifipass.git
pip3 install ./openwifipass
```

## Run

Run `openwifipass` to share Wi-Fi credentials (`SSID` and `PSK`) with *any* requestor (we need super user privileges to use the Bluetooth subsystem):

```bash
sudo -E python3 -m openwifipass --ssid <SSID> --psk <PSK>
```

A successful run of the protocol would look as follows:
```
pi@raspberrypi:~/openwifipass $ sudo -E python3 -m openwifipass --ssid OWL --psk SuperSecretPassword
Start scanning...
SSID match in PWS advertisement from aa:bb:cc:dd:ee:ff
Connect to device aa:bb:cc:dd:ee:ff
Send PWS1
Receive PWS2
Send M1
Receive M2
Send M3
Receive M4
Send PWS3
Receive PWS4
Wi-Fi Password Sharing completed
```

## OPACK

This projects contains a reusable OPACK (de)serializer. Read [OPACK.md](OPACK.md) for more information.

## Authors

* Jannik Lorenz

## Publications

* Milan Stute, Alexander Heinrich, Jannik Lorenz, and Matthias Hollick. **Disrupting Continuity of Apple’s Wireless Ecosystem Security: New Tracking, DoS, and MitM Attacks on iOS and macOS Through Bluetooth Low Energy, AWDL, and Wi-Fi.** *30th USENIX Security Symposium (USENIX Security ’21)*, August 11–13, 2021, Vancouver, B.C., Canada. *To appear*.
* Jannik Lorenz. **Wi-Fi Sharing for All: Reverse Engineering and Breaking the Apple Wi-Fi Password Sharing Protocol.** Bachelor thesis, *Technical University of Darmstadt*, March 2020.

## License

OpenWifiPass is licensed under the [**GNU General Public License v3.0**](LICENSE).
