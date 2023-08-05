#!/usr/local/bin/python
"""
simple example for pyusb module
"""

import sys
#sys.path[:0]=['/usr/local/lib/python2.6/dist-packages']

import usb, usb.core,usb.util
from usb import ENDPOINT_IN, REQ_GET_DESCRIPTOR, DT_STRING, TYPE_STANDARD, RECIP_DEVICE
from usb import *
from usbids import *
init_usbids()

#/* from USB 2.0 spec and updates */
USB_DT_DEVICE_QUALIFIER	 = 0x06
USB_DT_OTHER_SPEED_CONFIG = 0x07
USB_DT_OTG = 0x09
USB_DT_DEBUG = 0x0a
USB_DT_INTERFACE_ASSOCIATION = 0x0b

#/* convention suggested by common class spec */
USB_DT_CS_INTERFACE = 0x24
USB_DT_CS_ENDPOINT = 0x25
USB_CLASS_VIDEO = 0x0e

def get_string_descriptor(dev, desc_index, langid=0x0409, length=255):
    b=dev.ctrl_transfer(usb.ENDPOINT_IN | usb.TYPE_STANDARD |usb.RECIP_DEVICE, #bmRequestType
                        REQ_GET_DESCRIPTOR,  # bRequest
                        (DT_STRING << 8) | desc_index, # wValue
                        langid, # wIndex
                        length, # data_or_wLength
                        1000)
    if (b[1] != DT_STRING):#b[1] is a datatype
        raise IO_ERROR
    if (b[0] > length):
        raise IO_ERROR # b[0] holds size of return data+2?

    return b[2:].tostring().decode() # return unicode string

def get_langid(dev):
    # desc_index = 0 return a list of lang id 
    r=dev.ctrl_transfer(usb.ENDPOINT_IN | usb.TYPE_STANDARD |usb.RECIP_DEVICE,
                        REQ_GET_DESCRIPTOR, 
                        (DT_STRING << 8) | 0 , # index=0 means langid
                        0, #langid = 0
                        255, # data_or_wLength
                        1000)
    langid=r[2] | (r[3]<<8)
    return langid

def get_string_descriptor_ascii(dev, desc_index, length=255):
    if desc_index == 0:
        raise USBError("Invalid Parameter")
    langid=get_langid(dev)
    b=dev.ctrl_transfer(usb.ENDPOINT_IN | usb.TYPE_STANDARD |usb.RECIP_DEVICE,
                        REQ_GET_DESCRIPTOR, 
                        (DT_STRING << 8) | desc_index,
                        langid, length, 5000)
    if (b[1] != DT_STRING):#b[1] is a datatype
        raise IOERROR
    if (b[0] > length):
        raise IOERROR # b[0] holds size of return data+2?
    return b[2::2].tostring()

def find_tmc_device():
    """
    pBase/Sub/Protcol=0xfe/0x03/0x00 for TMC 0x01 for USB488
    """
    def is_usbtmc(d):
        for cfg in d:
            if (usb.util.find_descriptor(cfg, bInterfaceClass=0xfe, bInterfaceSubClass=3) != None):
                return True
        
    devs=usb.core.find(find_all=True,
                       custom_match=is_usbtmc
                       ) #
    return devs


DeviceClassDict={
#    usb.CLASS_APPLICATION:"Application",
    usb.CLASS_AUDIO:"Audio",
    usb.CLASS_COMM:"Comunication",
    usb.CLASS_DATA:"Data",
#    usb.CLASS_DIAGNOSITC:"Diagnostic",
    usb.CLASS_HID:"HID",
    usb.CLASS_HUB:"HUB",
#    usb.CLASS_IMAGE:"Image",
    usb.CLASS_MASS_STORAGE:"Mass Storage",
#    usb.CLASS_WIRELESS:"Wireless",
#    usb.CLASS_VIDEO:"Video",
    usb.CLASS_VENDOR_SPEC:"Vendor Specific",
#    usb.CLASS_SMART_CARD:"Smart Card",
#    usb.CLASS_SECURITY:"Security",
#    usb.CLASS_PHYSICAL:"Physical",
    usb.CLASS_PER_INTERFACE:"Per interface",
    usb.CLASS_PRINTER:"Printer",
    usb.CLASS_VENDOR_SPEC:"Vendor specific",
#    usb.CLASS_MISC:"Miscellaneous"
    }


def show_device(dev):
    print "\nidVendor/idProducet:%04x/%04x"%(dev.idVendor, dev.idProduct)
    try:
        print "Manufacturer/Product name/Serial Number: %s/%s/%s"%(
            usb.util.get_string(dev,255,dev.iManufacturer),
            usb.util.get_string(dev,255,dev.iProduct),
            usb.util.get_string(dev,255,dev.iSerialNumber) if dev.iSerialNumber <> 0 else "")
    except:
        try:
            print "Manufacturer/Product name: %s/%s"%(
                get_string_descriptor_ascii(dev,dev.iManufacturer),
                get_string_descriptor_ascii(dev,dev.iProduct))
        except:
            print "Manufacturer/Product name: %s/%s"%(vendors.get(dev.idVendor,""),
                                                      products.get((dev.idVendor,dev.idProduct),"NA"))
    print "USB Version:% 4x"%dev.bcdUSB
    print "Device Class/SubClass/Protocol:%s/%s/%s"%(
        usb_classes.get(dev.bDeviceClass, "%02X"%dev.bDeviceClass),
        usb_subclasses.get((dev.bDeviceClass, dev.bDeviceSubClass), "%02X"%dev.bDeviceSubClass),
        protocols.get((dev.bDeviceClass,dev.bDeviceSubClass,dev.bDeviceProtocol), "%02X"%dev.bDeviceProtocol))
    print "Max Packet Size:%d"%dev.bMaxPacketSize0
    print "device Release:% 4x"%dev.bcdDevice
    print "number of configurations:%d"%dev.bNumConfigurations

def show_config(dev,cnf):
    print "Configuration #:%d"%cnf.bConfigurationValue
    print "\tNumber of Interfaces:%d"%cnf.bNumInterfaces

    try:
        print "\tConfiguration String %s"%usb.util.get_string(dev,255,cnf.iConfiguration)
    except:
        try:
            print "\tConfiguration String %s"%get_string_descriptor_ascii(dev,cnf.iConfiguration)
        except:
            pass
    print "\tAttributes:",
    c=cnf.bmAttributes
    #if (c & 0x80):print "1,",
    if (c & 0x40): 
        print "Self Powered,",
    else:
        print "Bus Powered,",
    if (c & 0x20):
        print "Remote wakeup",
    else:
        print "Local wakeup",
    print ""
    print "\tMax Power: %d mA"%(2*cnf.bMaxPower)

def show_interface(dev,cnf,intf):
    print "\tInterface #%d"%intf.bInterfaceNumber
    print "\t\tAltenate Setting:%d"%intf.bAlternateSetting
    print "\t\tnumber of endpoint:%d"%intf.bNumEndpoints
    print "\t\tInterface class/protocol: %s/%s/%s"%(
        usb_classes.get(intf.bInterfaceClass,"%02x"%intf.bInterfaceClass),
        usb_subclasses.get((intf.bInterfaceClass,intf.bInterfaceSubClass),
                           "%02x"%intf.bInterfaceSubClass),
        protocols.get((intf.bInterfaceClass,intf.bInterfaceSubClass,intf.bInterfaceProtocol),"%02x"%intf.bInterfaceProtocol))
    try:
        print "\t\tinterface description:\"%s\""%get_string_descriptor_ascii(dev,intf.iInterface)
    except:
        pass

def show_endpoint(dev,cnf,intf,ep):
    print "\t\tEnd point Address:%d"%ep.bEndpointAddress
    c=ep.bmAttributes
    print "\t\t\tAttributes",
    tp=c&usb.ENDPOINT_TYPE_MASK
    if(tp == usb.ENDPOINT_TYPE_CONTROL):
        print "Control,",
    elif (tp ==usb.ENDPOINT_TYPE_ISOCHRONOUS):
        print "Isochronous,",
    elif(tp==usb.ENDPOINT_TYPE_BULK):
        print "Bulk,",
    elif(tp ==usb.ENDPOINT_TYPE_INTERRUPT):
        print "Interrupt,",
    sync=(c&12)>>2
    if (sync == 0):
        print "No sync,",
    elif(sync == 1):
        print "Async,",
    elif(sync == 2):
        print "Adaptive,",
    elif(sync == 3):
        print "Sync,",
    usage=(c&48)>>4
    if (usage == 0):
        print "Data endpoint"
    elif(usage == 1):
        print "Feedback endpoint"
    elif(usage ==2):
        print "Subordinate Feedback endpoint"
    elif(usage == 3):
        print "Reserved"
    print "\t\t\tMaxPacketSize:%d"%ep.wMaxPacketSize
    print "\t\t\tPolling interval:%d"%ep.bInterval

def LS():
    for dev in usb.core.find(True):
        show_device(dev)
        for cnf in dev:
            show_config(dev,cnf)
            for intf in cnf:
                show_interface(dev,cnf,intf)
                for ep  in intf:
                    show_endpoint(dev,cnf,intf,ep)

def lsusb():
    print "dev rel./ idVendor/idProduct Manufacture/Product (Serial Number) "
    for dev in usb.core.find(True):
        print "%04x\t"%dev.bcdDevice,
        print "%04x:%04x"%(dev.idVendor, dev.idProduct),
        try:
            print "%s /"%get_string_descriptor_ascii(dev,dev.iManufacturer),
        except:
            print "%s /"%vendors.get(dev.idVendor,"NA"),
        try:
            print "%s"%get_string_descriptor_ascii(dev,dev.iProduct),
        except:
            print "%s"%products.get((dev.idVendor,dev.idProduct),"NA"),
        try:
            print "\t(%s)"%get_string_descriptor_ascii(dev,dev.iSerialNumber),
            #print "\t(%s)"%usb.util.get_string(dev,255,dev.iSerialNumber)
        except:
            print "",
        finally:
            print 

if __name__ == "__main__":
    import getopt,sys
    
    opts,argv=getopt.getopt(sys.argv[1:],"lL")
    opts=dict(opts)
    if ("-l" in opts or "-L" in opts):
        LS()
    else:
        lsusb()
