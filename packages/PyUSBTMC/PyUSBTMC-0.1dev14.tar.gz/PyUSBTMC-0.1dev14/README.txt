PyUSBTMC
================

PyUSBTMC:python module to handle USB-TMC(Test and Measurement class)　devices.
It requires pyusb module and libusb or openusb libraries.

(C) 2012-2015, Noboru Yamamot, Accl. Lab, KEK, JAPAN
contact: noboru.yamamoto_at_kek.jp

rev.0.1d14:
  remove reset in __init__ of USBTMC_device. It breaks everything for the device from Tektronix.
  bring back mkDevDepMSGOUTHeader  to older version.

 
