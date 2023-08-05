#!/usr/bin/env python
"""
"""
import os,platform,re

from distutils.core import setup,Extension
rev="$Revision: 0.1dev08 $"
sysname=platform.system()

setup(name="PyUSBTMC",
      version=rev[11:-2],
      author="Noboru Yamamoto, KEK, JAPAN",
      author_email = "Noboru.YAMAMOTO@kek.jp",
      description ="Python module to control USBTMC/USB488 from python",
      long_description=""" Python module to control USBTMC/USB488 from python.
It requires pyusb module and libusb (or openusb) library to run. 
Although it is still in the development stage, it can read/write data from/to the devices.""",
      platforms="tested on MacOSX10.7",
      url="http://www-acc.kek.jp/EPICS_Gr/products/PyUSBTMC-0.1dev05.tar.gz",
      py_modules=["PyUSBTMC","lsusb","usbids",],
      data_files=[("/usr/share/misc",['usb.ids'])]
      )

