from openwifipass import __version__
from codecs import open
from os.path import abspath, dirname, join
from setuptools import find_packages, setup

this_dir = abspath(dirname(__file__))
with open(join(this_dir, "README.md"), encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="OpenWifiPass",
    version=__version__,
    python_requires=">=3.6",
    description="An open Apple Wi-Fi Password Sharing implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://owlink.org",
    project_urls={
        "Source": "https://github.com/seemoo-lab/openwifipass",
    },
    author="The Open Wireless Link Project",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="cli",
    packages=find_packages(exclude=["docs"]),
    install_requires=[
        "bluepy",
        "cryptography",
        "hkdf",
        "pycryptodomex",
    ],
    entry_points={
        "console_scripts": [
            "openwifipass=openwifipass.__main__:main",
        ],
    },
)
