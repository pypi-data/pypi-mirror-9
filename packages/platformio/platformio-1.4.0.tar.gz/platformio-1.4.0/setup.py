# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from platform import system

from setuptools import find_packages, setup

from platformio import (__author__, __description__, __email__, __license__,
                        __title__, __url__, __version__)

setup(
    name=__title__,
    version=__version__,
    description=__description__,
    long_description=open("README.rst").read(),
    author=__author__,
    author_email=__email__,
    url=__url__,
    license=__license__,
    install_requires=[
        "click>=3.0",
        "pyserial",
        "requests>=2.4.0",
        # "SCons"
    ] + (["colorama"] if system() == "Windows" else []),
    packages=find_packages(),
    package_data={"platformio": ["projectconftpl.ini", "boards/*.json"]},
    entry_points={
        "console_scripts": [
            "platformio = platformio.__main__:main"
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Compilers"
    ],
    keywords=("builder library manager atmel avr sam freescale kinetis nordic "
              "nrf51 nxp lpc st stm32 ti msp430 tiva teensy arduino mbed "
              "libopencm3")
)
