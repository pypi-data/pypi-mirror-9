#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
PyUSBTMC:python module to handle USB-TMC(Test and Measurement class)　devices.
It requires pyusb module and libusb or openusb libraries.
(C) 2012, Noboru Yamamot, Accl. Lab, KEK, JAPAN
contact: noboru.yamamoto_at_kek.jp
"""

import struct,array,time
import usb
from usb import USBError
from usb.core import *
from usb.util import *
import usb.control as usbctrl

from lsusb import show_endpoint

# fro USB-TMC table2
class USBTMC_MsgID:
    DEV_DEP_MSG_OUT = 1
    REQUEST_DEV_DEP_MSG_IN = 2
    DEV_DEP_MSG_IN = 2
    VENDOR_SPECIFIC_OUT = 126
    REQUEST_VENDOR_SPECIFIC_IN = 127
    VENDOR_SPECIFIC_IN = 127
    TRIGGER = 128 # for USB488

Mandatory_LANGID=0x0409 # English,United State
#
USBTMC_bInterfaceClass=254 #0xfe
USBTMC_bInterfaceSubClass=3 # usbtmc
USBTMC_bInterfaceProtocol=0 
USB488_bInterfaceSubClass=1

# from usbtmc.h
# Size of driver internal IO buffer. Must be multiple of 4 and at least as
# large as wMaxPacketSize (which is usually 512 bytes). 
USBTMC_SIZE_DEFAULT = 4096
#USBTMC_SIZE_IOBUFFER = 32768*10
USBTMC_SIZE_IOBUFFER = 64*1024
USBTMC_DEFAULT_TIMEOUT = 1000 #msec
USBTMC_MAX_READS_TO_CLEAR_BULK_IN = 100

#USB2.0 Specification
# #8.1 Byte/Bit Ordering
# Bits are sent out onto the bus least-significant bit (LSb) first, 
# followed by the next LSb, through to the mostsignificant
# bit (MSb) last. 
# Multiple byte fields in standard descriptors, requests, and 
# responses are interpreted as and moved over the
# bus in little-endian order, i.e., LSB to MSB.
#NY memo:
# it means 'use "<" in pack/unpack of struct module.'

def find_tmc_devices():
    """
    pBase/Sub/Protcol=0xfe/0x03/(0x00 for TMC, 0x01 for USB488)
    This function returns a list of usb devices but not usbtmc devices.
    """
    def is_usbtmc(d):
        for cfg in d:
            # USBTMC_bInterfaceClass = 0xfe, USBTMC_bInterfaceSubClass = 3
            # strictry speaking, TMC or USB488 devices will be selected
            if (usb.util.find_descriptor(cfg, bInterfaceClass=0xfe, bInterfaceSubClass=3) != None):
                return True
        return False

    devs=usb.core.find(find_all=True, custom_match=is_usbtmc) 
    return devs # a list of usb.core.Device

# Table11 Bulk-IN protocol error
class USBTMCError(USBError):
    pass

class USBTMC_BulkInError(USBTMCError):
    pass

# 
class usbtmc_dev_capabilities:
    def __init__(self):
        self.interface_capabilities=""
        self.device_capabilities=""
        self.usb488_interface_capabilities=""
        self.usb488_device_capabilities=""

class usbtmc_attribute:
    def __init__(self):
        self.attribute=0
        self.value=0
        
# USBTMC status values/USBTMC Table 16
class USBTMC_Status:
    SUCCESS = 0x01
    PENDING = 0x02
    FAILED = 0x80
    TRANSFER_NOT_IN_PROGRESS = 0x81
    SPLIT_NOT_IN_PROGRESS = 0x82
    SPLIT_IN_PROGRESS = 0x83
    # only fo USB488
    #INTERRUPT_IN_BUSY=0x20
    
    @classmethod
    def msg(cls,i):
        if (i == cls.SUCCESS):
            return "Success"
        elif (i == cls.PENDING):
            return "Pending"
        elif (i == cls.FAILED):
            return "Failed"
        elif (i == cls.TRANSFER_NOT_IN_PROGRESS):
            return "Transfer not in progress"
        elif (i == cls.SPLIT_NOT_IN_PROGRESS):
            return "Split not in progress"
        elif (i == cls.SPLIT_IN_PROGRESS):
            return "Split in progress"
        return "Reserved"
#
class IEEE488_Status_Byte_Reg:
    def __init__(self,byte):
        self.OPER=(byte&0x80)>>7
        self.RQS_MSS=(byte&0x40)>>6
        self.ESB=(byte&0x20)>>5
        self.MAV=(byte&0x10)>>4
        self.MSG=(byte&0x04)>>2
        self.USR=(byte&0x02)>>1
        self.TRG=(byte&0x01)>>0

class USB488_Status(USBTMC_Status):
    INTERRUPT_IN_BUSY=0x20
    
    def __init__(self, bytes):
        self.USBTMC_status=bytes[0]
        self.bTag=bytes[1]
        self.SBR=IEEE488_Status_Byte_Reg(bytes[2])
        
    @classmethod
    def msg(cls,i):
        if (i == cls.INTERRUPT_IN_BUSY):
            return "Interrupt in busy"
        else:
            return USBTMC_Status.msg(i)

#USBTMC requests values/USBTMC Table 15
class USBTMC_REQUEST:
    INITIATE_ABORT_BULK_OUT = 1
    CHECK_ABORT_BULK_OUT_STATUS = 2
    INITIATE_ABORT_BULK_IN = 3
    CHECK_ABORT_BULK_IN_STATUS = 4
    INITIATE_CLEAR = 5
    CHECK_CLEAR_STATUS = 6
    GET_CAPABILITIES = 7
    INDICATOR_PULSE = 64

class USB488_REQUEST(USBTMC_REQUEST):# USB488 Table 9
    READ_STATUS_BYTE=128
    REN_CONTROL=160
    GOTO_LOCAL=161
    LOCAL_LOCKOUT=162

class StandardFeature:# usb2.0 table 9-6
    DEVICE_REMOTE_WAKEUP=1
    ENDPOINT_HALT=0
    TEST_MODE=2

class SREmask:
    OPER = 1<<7
    ESB = 1<<5
    MAV = 1<<4
    MSG = 1<<2
    USR = 1<<1
    TRG = 1<<0

class USBTMC_device:
    #
    @classmethod
    def find_all(cls):
        usbdevs=find_tmc_devices()
        return [cls(dev) for dev in usbdevs]

    def __init__(self,device):
        # usb device
        self.device=device
        if self.device.is_kernel_driver_active(0):
            self.device.detach_kernel_driver(0)
        self.device.set_configuration()
        self.device.set_interface_altsetting()
        
        for cnf in self.device:
            for intf in cnf:
                #check if this device has TMC/USB488 interface             
                if ((intf.bInterfaceClass == USBTMC_bInterfaceClass) and
                    (intf.bInterfaceSubClass == USBTMC_bInterfaceSubClass)):
                    self.__init_data__()
                    self.getendpoints(cnf, intf)
                    self.get_capabilities()
                    return
        raise USBError,"the device is not TMC/USB488 Class"

    def __init_data__(self):
        self.last_write_bTag=0
        self.last_read_bTag=0
        self.eof=0
        self.retry_buf=""
        self.timeout=USBTMC_DEFAULT_TIMEOUT
        self.term_char_enabled=False
        self.term_char="\n"
        self.fread=0
        self.auto_abort=False
        self.add_nl_on_read=True
        self.add_nl_on_write=True

    def __del__(self):
        if self.device :
            try:
                del self.device
            finally:
                self.device=None

    def getendpoints(self,cnf, intf):
        self.intf=intf
        #intf.set_altsetting()
        #self.setting=self.intf.get_active_setting()
        num_endpoints=self.intf.bNumEndpoints
        if (num_endpoints < 2):
            raise USBError
        #endpoints
        self.bulk_in=None  #intf[0] normally
        self.bulk_out=None #intf[1]
        self.intr_in=None  #intf[2]
        
        for ep in intf:
            attr=ep.bmAttributes
            direction=ep.bEndpointAddress & usb.ENDPOINT_DIR_MASK
            ep_type=attr & usb.ENDPOINT_TYPE_MASK
            #show_endpoint(self.device, self.intf.configuration,self.intf,ep)
            if (ep_type == usb.ENDPOINT_TYPE_BULK):
                if (direction == usb.ENDPOINT_IN):
                    self.bulk_in=ep
                elif (direction == usb.ENDPOINT_OUT):
                    self.bulk_out=ep
            elif (ep_type == usb.ENDPOINT_TYPE_INTERRUPT):
                if (direction == usb.ENDPOINT_IN):
                    self.intr_in = ep
        if (self.bulk_in and self.bulk_out):
            return
        else:
            raise USBError,"TMC device must have both Bulk-In and Bulk-out endpoints."

    def isUSB488(self):
        if (self.intf.bInterfaceProtocol == 1):
            return True
        else:
            return False

    def usb_get_status(self,recipient=None):
        return  usb.control.get_status(self.device,recipient)

    def reset(self):
        return self.device.reset()
    
    def ask0(self, cmd="*IDN?\n", requestSize=4096,
             termChar="\n",termCharFlag=True, io_timeout=1000):
        """ 
        A name borrowed from PyVISA module 
        return value: tuple of (data size, binary array of data)
        """
        self.device_write(cmd)
        return self.read0(io_timeout=io_timeout
                         , termChar=termChar,flag=termCharFlag
                         , requestSize=requestSize)

    def ask(self, cmd="*IDN?\n", requestSize=4096, 
             termChar="\n",termCharFlag=True,io_timeout=1000):
        """ 
        A name borrowed from PyVISA module 
        now return value as string. Old behaviour is available as ask0
        """
        self.device_write(cmd)
        data=self.read(io_timeout=io_timeout
                         , termChar=termChar, flag=termCharFlag
                         , requestSize=requestSize)
        return data

    askS=ask
    
    def read(self,requestSize=4096, io_timeout=1000
             , lock_timeout=0, flag=False, termChar=None):
        """
        returns values as string. Old behaviour is now available as read0
        """
        data=array.array('B') # null array
        ndata=0
        eom=False
        rsize=min(USBTMC_SIZE_IOBUFFER, requestSize)
        termCharFlag=(True if (flag and (termChar !=None)) else False)
        while (not eom) and (ndata < requestSize):
            resp=self.device_read( rsize, termCharFlag=termCharFlag, 
                                   termchar=termChar, timeout=io_timeout)
            ndata += resp.TransferSize
            #data  += resp.data
            data.extend(resp.data)
            eom = resp.eom
        
        return data.tostring()

    # for compatibility
    readS=read

    def read0(self,requestSize=4096, io_timeout=1000
              , lock_timeout=0, flag=False, termChar=None):
        """
        returns values as tuple of (data size, binary array data)
        """
        data=array.array('B') # null array
        ndata=0
        eom=False
        rsize=min(USBTMC_SIZE_IOBUFFER,requestSize)
        termCharFlag=(True if (flag and (termChar !=None)) else False)
        while (not eom) and (ndata < requestSize):
            resp=self.device_read(rsize, termCharFlag=termCharFlag,
                                  termchar=termChar,timeout=io_timeout)
            ndata += resp.TransferSize
            #data  += resp.data
            data.extend(resp.data)
            eom = resp.eom
        return (ndata,data)

    def write(self, cmd="*IDN?\n"):
        return self.device_write(cmd)

    def device_write(self,  message):
        remaining=len(message)
        while (remaining > 0):
            # bulk_out message includes 12bytes usbtmc header.
            if ((remaining + 12 ) < USBTMC_SIZE_IOBUFFER):# do we need it in python?
                eom=True
                transferSize=remaining # can send all remaining data
            else:
                eom=False
                transferSize=USBTMC_SIZE_IOBUFFER-12 # send data as much as possible
            t,h=mkDevDepMSGOUTHeader(transferSize, eom=eom)
            if ((transferSize % 4) == 0):
                command="%s%s"%(h,message[:transferSize])
            else:# padding data for 4bytes boundary
                command="%s%s%s"%(h,message[:transferSize],(4-(transferSize % 4))*'\0')
            command=array.array('B',command)
            #print "device_write:",command,len(command),transferSize
            try:
                self.bulk_out.write(command)
                self.last_write_bTag=t
            except:
                self.abort_bulk_out() # is it reasonable?
            message=message[transferSize:]
            remaining=len(message)
        return 

    def device_read(self, transferSize=USBTMC_SIZE_DEFAULT, 
                    termCharFlag=False, termchar="\n", timeout=None):
        # bulkin header size = 12 standard headr
        #                    + 4bytes for Deivce Responce (msgID, TransferSize, termChar, eom)
        ndata=0
        btag,buf=mkReqDevDepMSGINHeader(transferSize, termCharFlag, termchar)
        buf=array.array('B',buf) # convert string to byte array
        #print "ReqHeader:",buf,len(buf),'transferSize:',transferSize
        try:
            self.bulk_out.write(buf)
        except:
            self.abort_bulk_out()
            return 
        self.last_write_bTag=btag
        # add 12+4 for usb header size (NY, 2015.1.21)
        raw_resp=self.bulk_in.read(transferSize+16, timeout = timeout)
        resp=DevDep_Responce(raw_resp)
        self.last_read_bTag=resp.bTag
        #print "responce:",resp.TransferSize, resp.TermChar,resp.eom,
        #print transferSize-resp.TransferSize
        return resp

    def vender_write(self,message):
        """
        Vender specific bulk write method. Should be 
        """
        raise USBTMCError("Not Implemented")

    def vender_read(self,maxsize=None):
        raise USBTMCError("Not Implemented")

    def check_SRQ(self):
        rv=self.intr_in.read(self.intr_in.wMaxPacketSize, timeout=self.intr_in.bInterval)
        sb=Interrupt_IN_Data(rv)
        # assert(sb.bTag == 0x1) for SRQ
        return sb

    # class standard control messages
    """ctrl_transfer(self, bmRequestType, bRequest, 
                     wValue=0, wIndex=0, data_or_wLength=None, timeout=None) 
    unbound usb.core.Device method
    Do a control transfer on the endpoint 0.
    
    This method is used to issue a control transfer over the
    endpoint 0(endpoint 0 is required to always be a control endpoint).
    
    The parameters bmRequestType, bRequest, wValue and wIndex are the
    same of the USB Standard Control Request format.
    
    Control requests may or may not have a data payload to write/read.
    In cases which it has, the direction bit of the bmRequestType
    field is used to infere the desired request direction. For
    host to device requests (OUT), data_or_wLength parameter is
    the data payload to send, and it must be a sequence type convertible
    to an array object. In this case, the return value is the number of data
    payload written. For device to host requests (IN), data_or_wLength
    is the wLength parameter of the control request specifying the
    number of bytes to read in data payload. In this case, the return
    value is the data payload read, as an array object."""

    def abort_bulk_out(self):
        rv=self.device.ctrl_transfer(
            usb.util.build_request_type(CTRL_IN, CTRL_TYPE_CLASS, CTRL_RECIPIENT_ENDPOINT),
            #usb.ENDPOINT_IN | usb.TYPE_CLASS|usb.RECIP_ENDPOINT, # bmRequest type
            USBTMC_REQUEST.INITIATE_ABORT_BULK_OUT,
            self.last_write_bTag,
            self.bulk_out.bEndpointAddress,
            data_or_wLength=2,
            timeout=self.timeout)
        if (rv[0] == USBTMC_Status.SUCCESS):
            rv=self.check_abort_bulk_out_status()
            while(rv[0] == USBTMC_Status.PENDING):
                rv=self.check_abort_bulk_out_status()
            if (rv[0] == USBTMC_Status.SUCCESS):
                self.clear_bulk_out_halt()
            return rv
        elif (rv[0] == USBTMC_Status.TRANSFER_NOT_IN_PROGRESS):
                raise USBTMCError("Transfer not in progress")
        else:
            raise USBTMCError("Initiate abort_bulk_out failed")

    def check_abort_bulk_out_status(self):
        # usb.control.get_status(self.device, self.bulk_out.bEndpointAddress)
        rv=self.device.ctrl_transfer(
            build_request_type(CTRL_IN, CTRL_TYPE_CLASS, CTRL_RECIPIENT_ENDPOINT),
            USBTMC_REQUEST.CHECK_ABORT_BULK_OUT_STATUS, # CHECK_STATUS
            0,
            self.bulk_out.bEndpointAddress,
            data_or_wLength=8,
            timeout=self.timeout)
        return rv
    
    def clear_bulk_out_halt(self):#USBTMC 3.2.2.4
        #usb.control.clear_feature(self.device,usb.ENDPOINT_HALT,self.bulk_out.bEndpointAddress)
        rv=self.device.ctrl_transfer(
            build_request_type(CTRL_OUT, CTRL_TYPE_STANDARD, CTRL_RECIPIENT_ENDPOINT),
            usb.REQ_CLEAR_FEATURE, # Clear feature request
            usbctrl.ENDPOINT_HALT, # Feature ENDPOINT_HALT
            self.bulk_out.bEndpointAddress,
            data_or_wLength=None,# Although we don't really want data this time
            timeout=self.timeout)
        if(rv==None):
            print "USBTMC: usb_control_msg returned None\n"

        return rv

    def abort_bulk_in(self):
        rv=self.device.ctrl_transfer(
            build_request_type( CTRL_IN, CTRL_TYPE_CLASS, CTRL_RECIPIENT_ENDPOINT), # bmRequest type
            USBTMC_REQUEST.INITIATE_ABORT_BULK_IN, # INITIATE_ABORT
            self.last_read_bTag, # Last transaction's bTag value
            self.bulk_in.bEndpointAddress, # Endpoint
            2, # Number of characters to read
            self.timeout); # Timeout in miliseconds
        if (rv[0] == USBTMC_Status.SUCCESS):
            rv=self.check_abort_bulk_in_status()
            while(rv[0] == USBTMC_Status.PENDING):
                rv=self.check_abort_bulk_int_status()
            return rv
        elif (rv[0] == USBTMC_Status.TRANSFER_NOT_IN_PROGRESS):
            return
        elif (rv[0] == USBTMC_Status.FAILED):
            return 
        else:
            raise USBTMCError("Initiate abort_bulk_in failed %d"%rv[0])
        
    def check_abort_bulk_in_status(self):
        n=0
        max_size=self.bulk_in.wMaxPacketSize
        # clear buffer 
        while(1):
            rv=self.bulk_in.read(USBTMC_SIZE_IOBUFFER, self.default_timeout)
            n +=1
            if (len(rv) < max_size): #receive a short packet. 
                break 
            elif  (n >= USBTMC_MAX_READ_TO_CLEAR_BULK_IN):
                raise USBTMCError("Couldn't clear device buffer "
                                  "within %d cycles\n"%USBTMC_MAX_READ_TO_CLEAR_BULK_IN)

        rv=self.device.ctrl_transfer(
            build_request_type(CTRL_IN, CTRL_TYPE_CLASS,
                               CTRL_RECIPIENT_ENDPOINT), # bmRequest type
            USBTMC_REQUEST.CHECK_ABORT_BULK_IN_STATUS, # CHECK_STATUS
            0, # Reserved
            self.bulk_in.bEndpointAddress, # Endpoint
            0x08, # Number of characters to read
            self.timeout)  # Timeout (jiffies)
        return rv

    def clear_bulk_in_halt(self):#USBTMC 3.3.2.4/4.1.1.2
        # rv=usb.control.clear_feature(self.device, usb.control.ENDPOINT_HALT,
        #                              self.bulk_in.bEndpointAddress)
        rv=self.device.ctrl_transfer(        
            build_request_type(CTRL_OUT, CTRL_TYPE_STANDARD,
                               CTRL_RECIPIENT_ENDPOINT), # bmRequest type
            usb.REQ_CLEAR_FEATURE, # Clear feature request
            usbctrl.ENDPOINT_HALT, # Feature ENDPOINT_HALT
            self.bulk_in.bEndpointAddress,
            None, # Although we don't really want data this time
            self.timeout)
        return rv

    #
    def clear(self):
        rv=self.device.ctrl_transfer(        
            build_request_type(CTRL_IN, CTRL_TYPE_CLASS,
                               CTRL_RECIPIENT_INTERFACE), # bmRequest type
            USBTMC_REQUEST.INITIATE_CLEAR, # INITIATE_CLEAR
            0, # Interface number (always zero for USBTMC)
            0, # Reserved
            1, # Number of characters to read
            self.timeout) # Timeout (jiffies)
        if (rv[0] == USBTMC_Status.SUCCESS):
            rv=self.check_clear_status()
            n=0
            while (rv[0] == USBTMC_Status.PENDING):
                rv=self.check_clear_status()
                n+=1
                if n > 1000:
                    raise USBTMCError("clear status: too many iteration")
            return
        return rv

    def check_clear_status(self):
        rv=self.device.ctrl_transfer(        
            build_request_type(CTRL_IN, CTRL_TYPE_CLASS,
                               CTRL_RECIPIENT_INTERFACE), # bmRequest type
            USBTMC_REQUEST.CHECK_CLEAR_STATUS, # INITIATE_CLEAR
            0, # Interface number (always zero for USBTMC)
            0, # Reserved
            2, # Number of characters to read
            self.timeout)
        return rv

    def get_capabilities(self):
        # see Table 36- Get_Capabilities setup packet
        b=self.device.ctrl_transfer(
            build_request_type(CTRL_IN, CTRL_TYPE_CLASS,
                               CTRL_RECIPIENT_INTERFACE), # bmRequest type
            USBTMC_REQUEST.GET_CAPABILITIES,
            wValue=0x0000,wIndex=0,
            data_or_wLength=0x0018,
            timeout=self.timeout)
        if (b[0] == USBTMC_Status.SUCCESS):
            self.capabilities = USBTMC_Capabilities(b)
            return self.capabilities

    def indicator_pulse(self):
        if self.capabilities.indicator_pulse:
            # see Table 38- Indicator_pulse setup packet            
            b=self.device.ctrl_transfer(
                build_request_type(CTRL_IN, CTRL_TYPE_CLASS,
                                   CTRL_RECIPIENT_INTERFACE), # bmRequest type
                USBTMC_REQUEST.INDICATOR_PULSE,
                data_or_wLength=0x0001,
                timeout=self.timeout)
        else:
            raise USBError,"INDICATOR_PULSE is not supported on this device"

class USB488_device(USBTMC_device):
    #mandatory commands
    def CLS(self):
        self.write("*CLS\n")

    def ESE(self,query=False):
        if query:
            return self.ask("*ESE?\n")
        else:
            self.write("*ESE\n")

    def ESR(self):
        return self.ask("*ESQ?\n")

    def IDN(self):
        return self.ask("*IDN?\n")

    def OPC(self,query=False):
        if query:
            return self.ask("*OPC?\n")
        else:
            self.write("*OPC\n")
    def RST(self):
        return self.ask("*RST?\n")

    def SRE(self,mask=None):
        if mask == None:
            return self.ask("*SRE?\n")
        else:
            self.write("*SRE %d\n"%mask)

    def STB(self):
        return self.ask("*STB?\n")
    
    def TRG(self):
        self.write("*TRG\n")

    def TST(self):
        return self.ask("*TST?\n")

    def WAI(self):
        self.write("*WAI\n")
    
    # optional commands

    def CAL(self):
        return self.ask("*CAL?\n")

    def DDT(self,query=False):
        if query:
            return self.ask("*DDT?\n")
        else:
            self.write("*DDT\n")

    def DMC(self):
        self.write("*DMC\n")

    def EMC(self,query=False):
        if query:
            return self.ask("*EMC?\n")
        else:
            self.write("*EMC\n")
    def GMC(self):
        return self.ask("*GMC?\n")

    def LMC(self):
        return self.ask("*LMC?\n")

    def LRN(self):
        return self.ask("*LRN?\n")

    def PSC(self,query=False):
        if query:
            return self.ask("*PSC?\n")
        else:
            self.write("*PSC\n")

    def PUD(self):
        self.write("*PUD\n")

    def RCL(self):
        self.write("*RCL\n")

    def RDT(self,query=False):
        if query:
            return self.ask("*RDT?\n")
        else:
            self.write("*RDT")

    def RMC(self):
        self.write("*RMC\n")

    def SAV(self):
        self.write("*SAV\n")

    def SAD(self):
        self.write("*SDS")
    #
    def OPT(self):
        return self.ask("*OPT?\n")

    def TER(self):
        return self.ask("*TER?\n")
    #
    def RemoteEnable(self,enable=True):#Table 15
        if enable:
            b=self.device.ctrl_transfer(
                build_request_type(CTRL_IN, CTRL_TYPE_CLASS,
                                   CTRL_RECIPIENT_INTERFACE), # bmRequest type
                USB488_REQUEST.REN_CONTROL,
                wValue= 1, # should I use struct? to avoide endianess
                wIndex= 0, # Interface number (always zero for USBTMC)
                data_or_wLength=0x1,
                timeout=self.timeout)
        else:
            b=self.device.ctrl_transfer(
                build_request_type(CTRL_IN, CTRL_TYPE_CLASS,
                                   CTRL_RECIPIENT_INTERFACE), # bmRequest type
                USB488_REQUEST.REN_CONTROL,
                wValue= 0, # should I use struct? to avoide endianess
                wIndex= 0, # Interface number (always zero for USBTMC)
                data_or_wLength=0x1,
                timeout=self.timeout)

        return b #USBTMC_Status

    def LocalLockOut(self):
        b=self.device.ctrl_transfer(
            build_request_type(CTRL_IN, CTRL_TYPE_CLASS,
                               CTRL_RECIPIENT_INTERFACE), # bmRequest type
            USB488_REQUEST.LOCAL_LOCKOUT,
            wValue= 0, # tabel 19
            wIndex= 0, # Interface number (always zero for USBTMC)
            data_or_wLength=0x0001,
            timeout=self.timeout)
        return b #USBTMC_Status

    def GoToLocal(self):
        b=self.device.ctrl_transfer(
            build_request_type(CTRL_IN, CTRL_TYPE_CLASS,
                               CTRL_RECIPIENT_INTERFACE), # bmRequest type
            USB488_REQUEST.GOTO_LOCAL,
            wValue= 0, # should I use struct? to avoide endianess
            wIndex= 0, # Interface number (always zero for USBTMC)
            data_or_wLength=0x0001,
            timeout=self.timeout)
        return b #USBTMC_Status

    def Read_Status_Byte(self):
        # see Table 9,
        b=self.device.ctrl_transfer(
            build_request_type(CTRL_IN, CTRL_TYPE_CLASS,
                               CTRL_RECIPIENT_INTERFACE), # bmRequest type
            USB488_REQUEST.READ_STATUS_BYTE,
            wValue=bTag.next()&0x7f,
            wIndex= 0, # Interface number (always zero for USBTMC)
            data_or_wLength=0x0003,# USB2.0 specification, section 9.3.5
            timeout=self.timeout)
        print b
        if self.intr_in:
            sb=USB488_Status(b)
            bytes=self.intr_in.read(self.intr_in.wMaxPacketSize, self.intr_in.bInterval)
            sb.SBR=Interrupt_IN_Data(bytes).SBR
            return sb
        else:
            return USB488_Status(b)

    def GetExecuteTrigger(self):
        self.TRG()
    
    def SelectedDeviceClear(self):#table 26
        self.clear()
    
    # @classmethod
    # def DeviceClear(cls):
    #     for ent in cls.instances():
    #         ent.clear()

    def DCL(self):
        self.write("*DCL\n")

    # @classmethod
    # def LockOut(cls):
    #     for ent in cls.instances():
    #         ent.RemoteEnable()
    #         ent.LocalLockOut()

class USBTMC_Capabilities:
    def __init__(self,bytes):
        self.bcdUSBTMC="0x%.2x%.2x"%(bytes[3],bytes[2])
        if (bytes[4]&0x4):
            self.indicator_pulse=True
        else:
            self.indicator_pulse=False

        if (bytes[4]&0x2):
            self.talk_only=True
        else:
            self.talk_only=False

        if (bytes[4]&0x1):
            self.listen_only=True
        else:
            self.listen_only=False
        if (bytes[5] &0x1):
            self.termchar_enable=True
        else:
            self.termchar_enable=False
        if(len(bytes) > 12):
            self.bcdUSB488="0x%.2x%.2x"%(bytes[13],bytes[12])
            if bytes[14]&0x4:
                self.USB488=True
            else:
                self.USB488=False
            if bytes[14]&0x2:
                self.REN_CONTROL=True
            else:
                self.REN_CONTROL=False
            if bytes[14]&0x1:
                self.TRIGGER=True
            else:
                self.TRIGGER=False
            if bytes[15]&0x8:
                self.SCPI=True
            else:
                self.SCPI=False
            if bytes[15]&0x4:
                self.SR1=True
            else:
                self.SR1=False
            if bytes[15]&0x2:
                self.RL1=True
            else:
                self.RL1=False
            if bytes[15]&0x1:
                self.DT1=True
            else:
                self.DT1=False

    def __str__(self):
        msg=""
        if self.indicator_pulse:
            msg +="indicator pulse,"
        if self.talk_only:
            msg +="talk only,"
        if self.listen_only:
            msg +="listen only,"
        if self.termchar_enable:
            msg +="termchar enable"
        return msg

# bTag generator
class bTag:
    __lastbtag=0
    @classmethod
    def next(cls):
        cls.__lastbtag=( (cls.__lastbtag + 1) & 0xff
                         if (cls.__lastbtag < 0xff) else 1)
        return cls.__lastbtag
    @classmethod
    def last(cls):
        return cls.__lastbtag

def mkCommonHeader(msgid):
    btag=bTag.next()
    h="%1c%1c%1c\0"%(msgid&0xff, btag, (~btag)&0xff)
    return (btag,h)

def mkDevDepMSGOUTHeader(tsize, eom=False):
    btag,h=mkCommonHeader(USBTMC_MsgID.DEV_DEP_MSG_OUT)
    if eom:
        h="%s%1c%1c%1c%1c\1\0\0\0"%(h,
                                    tsize & 0xff,
                                    (tsize>>8) & 0xff,
                                    (tsize>>16) & 0xff,
                                    (tsize>>24) & 0xff)
    else:
        h="%s%1c%1c%1c%1c\0\0\0\0"%(h,
                                    tsize & 0xff,
                                    (tsize>>8) & 0xff,
                                    (tsize>>16) & 0xff,
                                    (tsize>>24) & 0xff)
    return (btag,h)

def mkReqDevDepMSGINHeader(tsize,TermCharEnable, TermChar='\n'):
    btag,h=mkCommonHeader(USBTMC_MsgID.DEV_DEP_MSG_IN)
    if TermCharEnable:
        h="%s%1c%1c%1c%1c\2%1c\0\0"%(h,
                                     tsize & 0xff,
                                     (tsize>>8) & 0xff,
                                     (tsize>>16) & 0xff,
                                     (tsize>>24) & 0xff,
                                     TermChar)
    else:
        h="%s%1c%1c%1c%1c\0%1c\0\0"%(h,
                                     tsize & 0xff,
                                     (tsize>>8) & 0xff,
                                     (tsize>>16) & 0xff,
                                     (tsize>>24) & 0xff,
                                     TermChar)
    return (btag,h)
    

def mkVendorSpecMSGOUTHeader(tsize):
    btag,h=mkCommonHeader(USBTMC_MsgID.VENDOR_SPECIFIC_OUT)
    h="%s%1c%1c%1c%1c\0\0\0\0"%(h,
                                tsize & 0xff,
                                (tsize>>8) & 0xff,
                                (tsize>>16) & 0xff,
                                (tsize>>24) & 0xff
                                )
    return (btag,h)

def mkReqVendorSpecMSGINHeader(tsize):
    btag,h=mkCommonHeader(USBTMC_MsgID.VENDOR_SPECIFIC_IN)
    h="%s%1c%1c%1c%1c\0\0\0\0"%(h,
                                tsize & 0xff,
                                (tsize>>8) & 0xff,
                                (tsize>>16) & 0xff,
                                (tsize>>24) & 0xff
                                )
    return (btag,h)
        
class BulkIn_Header:
    """
    convert return value header to structure
    """
    def __init__(self,bytes):
        self.msgID=bytes[0]
        self.bTag=bytes[1]
        self.bTagInverse=bytes[2]
        self.resMsg=bytes[4:12]
        try:
            self.data=bytes[12:]
        except:
            self.data=None

class DevDep_Responce(BulkIn_Header):
    def __init__(self,bytes):
        BulkIn_Header.__init__(self, bytes)
        if self.msgID <> USBTMC_MsgID.DEV_DEP_MSG_IN :
            raise TypeError
        #self.TransferSize=struct.unpack("<l",self.resMsg[:4])[0]
        self.TransferSize = ( self.resMsg[0]+
                             (self.resMsg[1]<<8)+
                             (self.resMsg[2]<<16)+
                             (self.resMsg[3]<<24))
        self.TermChar=(self.resMsg[4]>>1)&0x1
        self.eom=self.resMsg[4]&0x1

class VendorSpec_Responce(BulkIn_Header):
    def __init__(self,bytes):
        BulkIn_Header.__init__(self, bytes)
        if self.msgID <> USBTMC_MsgID.VENDOR_SPECIFIC_IN :
            raise TypeError
        self.TransferSize = (self.resMsg[0]+
                             (self.resMsg[1]<<8)+
                             (self.resMsg[2]<<16)+
                             (self.resMsg[3]<<24))
#
class Interrupt_IN_Data:# Table 6, USB488
    def __init__(self, bytes):
        self.SBR=None
        self.statusBytes=None
        if (bytes[0] & 0x80):# USB488
            self.bTag=bytes[0]&0x7f # 0x01 for SRQ responce or bTag_id for READ_Status
            self.SBR=IEEE488_Status_Byte_Reg(bytes[1])
        elif (bytes[0] & 0x40): # vendor specific
            self.statusBytes=bytes[1:]
        else:
            self.statusBytes=bytes[1:]
#
def test():
    #import usb.core, usb.util,usb.backend,usb.backend.libusb1
    #dev=usb.core.find(idVendor=0x0957, idProduct=0x0407)
    #    dev=usb.core.find(backend=usb.backend.libusb10.get_backend()
    #                      , idVendor=0x0957 # Agilent
    #                      , idProduct=0x1724)
    # dev=usb.core.find( backend=usb.backend.libusb10.get_backend()
    #                    , idVendor=0x0699 # Tektronix 0x02, 0x81, 0x83
    #                    , idProduct=0x0407) #DPO4K
    # dev=usb.core.find(idVendor=0x0699 # Tektronix 
    #, idProduct=0x0347) #AFG3022 address 0x1,0x82,0x83
    usbdevs=find_tmc_devices() # 
    if usbdevs == None:
        return
    usbdev=usbdevs[0]
    #tmcdev=USBTMC_device(dev)
    tmcdev=USB488_device(usbdev)
    #print "Clear:",tmcdev.clear()
    #print "ClearStatsu:",tmcdev.check_clear_status()
    try:
        try:
            tmcdev.device_write("*IDN?\n")
        except:
            tmcdev.abort_bulk_out()
        r=tmcdev.device_read(4096)
        print r.bTag,r.eom,r.msgID,r.TransferSize,r.data.tostring()
        if (tmcdev.device.idVendor == 1689): #0x0699
            tmcdev.device_write(":DATE?\n")
            r=tmcdev.device_read(4096)
            print r.bTag,r.eom,r.msgID,r.TransferSize,r.data.tostring()
            #tmcdev.write("DAT:ENC ASCI\n")
            tmcdev.write("DAT:ENC SRP\n") # 0-255 or 0-16K
            tmcdev.write("DAT:SOU CH1\n")
            tmcdev.write("WFMO:BYT_N 1\n")
            #tmcdev.write(":CURVE?")
            #w=tmcdev.read(2000020)
        elif (tmcdev.device.idVendor == 2391) : #0x0957
            tmcdev.device_write(":WAV:POINTS?\n")
            r=tmcdev.device_read(4096)
            print r.bTag,r.eom,r.msgID,r.TransferSize,r.data.tostring()
    finally:
        print "Done"
        return tmcdev

def DSO6K_test(dev=None):
    import Gnuplot
    if not dev:
        dev=test()
    print
    dev.write(":STOP;:SINGLE;:WAV:POINTS:MODE MAX;:WAV:POINTS 50000;")
    n,d=dev.ask("*IDN?;")
    print d.tostring()
    maker,model,sn,vers=d.tostring().split(",")
    dev.write(":WAV:SOURCE CH1;\n")
    dev.write(":WAV:POINTS 100000;\n")
    n,d=dev.ask(":WAV:POINTS?\n")
    print "WAV:POINT =",d.tostring()
    n,wf=dev.ask(":WAV:DATA?",requestSize=20000000)
    print "size of waveform",n

    dev.write(":WAV:SOURCE CH2;\n")
    n,wf2=dev.ask(":WAV:DATA?",requestSize=20000000)

    gp=Gnuplot.Gnuplot()
    gp.title("Python USBTMC module example \\n from %s"%model)
    hl=int(wf[1:2].tostring())+2
    gp.plot(wf[hl:-2][::10],wf2[hl:-2][::10])
    x0=wf[-1]
    return dev

def DSO6K_test_pylab(dev=None):
    import pylab
    if not dev:
        dev=test()
    print
    dev.write(":STOP;:SINGLE;:WAV:POINTS:MODE MAX;:WAV:POINTS 50000;")
    n,d=dev.ask("*IDN?;")
    print d.tostring()
    maker,model,sn,vers=d.tostring().split(",")
    dev.write(":WAV:SOURCE CH1;\n")
    dev.write(":WAV:POINTS 100000;\n")
    n,d=dev.ask(":WAV:POINTS?\n")
    print "WAV:POINT =",d.tostring()
    n,wf=dev.ask(":WAV:DATA?",requestSize=20000000)
    print "size of waveform",n

    dev.write(":WAV:SOURCE CH2;\n")
    n,wf2=dev.ask(":WAV:DATA?",requestSize=20000000)

    pylab.clf()
    pylab.title("Python USBTMC module example from %s"%model)
    hl=int(wf[1:2].tostring())+2
    pylab.xlabel("points")
    pylab.ylabel("signal")
    pylab.plot(range(0,n-hl-2,10),wf[hl:-2][::10], range(0,n-hl-2,10),pylab.array(wf2[hl:-2][::10])-127.)
    pylab.show(False)
    x0=wf[-1]
    return dev

def DPO4K_test():
    import pylab,time
    dev=test()
    print
    dev.write("DAT:ENC ASCI\n")
    dev.write("DAT:ENC SRP\n") # 0-255 or 0-16K
    dev.write("DAT:SOU CH1\n")
    dev.write("WFMO:BYT_N 1\n")
    s=time.time()
    dev.write("CURVE?")
    n,wf=dev.read(2000020)
    e=time.time()
    print "read ",n,"bytes in",e-s,"seconds", n/(e-s),"bytes/second"
    pylab.clf()
    hl=int(wf[1:2].tostring())+2
    pylab.xlabel("points")
    pylab.ylabel("signal")
    pylab.title("Waveform from DPO4034B")
    pylab.plot(wf[hl:-1][::100])
    pylab.show(False)
    return dev

def SL1K_test():
    import pylab
    dev=test()
    print
    print dev.ask(":DATA?\n")[1].tostring()
    print dev.ask(":ACQ?\n")[1].tostring()
    print dev.ask(":WAV?\n")[1].tostring()
    print dev.ask(":TRIG?\n")[1].tostring()
    print dev.ask(":MEAS?\n")[1].tostring()
    print dev.ask(":ALARM?\n")[1].tostring()
    print dev.ask(":CONTROL?\n")[1].tostring()
    print dev.ask(":CHAN1?\n")[1].tostring()
    res=dev.ask(":WAV:LENGTH?")[1].tostring()
    dev.write("WAV:FORMAT BYTE\n")
    dev.write("WAV:TRACE 1\n")
    #dev.write(":DATA:FRAW?\n")
    dev.write(":STOP\n")
    dev.write(":WAV:SEND?\n")
    n,wf=dev.read(2000020)
    pylab.clf()
    hl=int(wf[1:2].tostring())+2
    nd=int(wf[2:hl].tostring())
    pylab.plot(wf[hl:nd])
    pylab.xlabel("points")
    pylab.ylabel("signal")
    pylab.title("Waveform from Yokogawa SL1000")
    return dev

def AFG3K_test():
    import pylab,time
    devs=find_tmc_devices() # 
    if devs == None:
        return
    dev=USB488_device(devs[0])
    dev.write("*RST\n");time.sleep(3); print dev.IDN()[1].tostring()
    AFG3K_setup_test(dev)

def AFG3K_setup_test(dev):
    import pylab
    #'Set CH1 output parameters
    dev.write ("FUNCTION SIN\n") #Set output waveform SIN
    dev.write ("FREQUENCY 10E3\n") #Set frequency 10kHz
    dev.write ("VOLTAGE:AMPLITUDE 2.00\n") #Set amplitude 2Vpp
    dev.write ("VOLTAGE:OFFSET 1.00\n") #Set offset 1V
    dev.write ("PHASE:ADJUST 0DEG\n") #Set phase 0degree
    #Set CH2 output parameters
    dev.write ("SOURCE2:FUNCTION SIN\n") #Set output waveform SIN
    dev.write ("SOURCE2:FREQUENCY 10E3\n") #Set frequency 10kHz
    dev.write ("SOURCE2:VOLTAGE:AMPLITUDE 1.00\n") #Set amplitude 1Vpp
    dev.write ("SOURCE2:VOLTAGE:OFFSET 0.00\n") #Set offset 0V
    dev.write ("SOURCE2:PHASE:ADJUST 90DEG\n") #Set phase 90degrees
    n,wf=dev.ask("DATA:DATA? EMEM\n")
    hl=int(wf[1:2].tostring())+2
    nd=int(wf[2:hl].tostring())
    pylab.plot(wf[hl:nd])
    pylab.xlabel("points")
    pylab.ylabel("signal")
    pylab.title("EMEM data from Tektronix AFG3000 series")
    #Save settings and output on
    #dev.write ("*SAV 1\n") #Save settings to Setup1
    #dev.write ("*RCL 1\n") #Recall settings from Setup1
    return dev
