from ctypes import *
import datetime
import ctypes
import os
from sys import getwindowsversion

sub20dll = cdll.LoadLibrary("C:/Windows/System32/sub20")
sub_get_serial_number = sub20dll.sub_get_serial_number
sub_get_serial_number.argtypes = [c_int, c_char_p, c_int]

sub_open = sub20dll.sub_open
sub_open.argtypes = [c_int]

sub_close = sub20dll.sub_open
sub_close.argtypes = [c_int]

MAX_BUFF_SZ = 64
MAX_FREQ = 444444
class MdioFrameRec(Structure):
    _fields_ = [
        ("op", ctypes.c_int),
        ("port_addr", ctypes.c_int),
        ("dev_addr", ctypes.c_int),
        ("data", ctypes.c_int)]

sub_mdio_xfer_ex = sub20dll.sub_mdio_xfer_ex
sub_mdio_xfer_ex.argtypes = [c_int, c_int, c_int, POINTER(MdioFrameRec)]

class MdioDrivers:
    """MDIO UI driver functions"""

    __MDIO_OP_ADDR = 0
    __MDIO_OP_WRITE = 1
    __MDIO_OP_READ_INC =2
    __MDIO_OP_READ = 3
    __mdio_readWriteBufSize = 2
    __mdio_readWriteSingleBuf = 1

    # MDIO registers

    REG_MOD_GEN_CONTROL_B010 = 0xB010
    REG_MOD_STATE_B016 = 0xB016
    REG_MOD_UPGRADE_DATA_B04C = 0xB04C
    REG_MOD_UPGRADE_CTRL_B04D = 0xB04D
    REG_MOD_EXT_FN_B050 = 0xB050
    REG_MOD_UP_STAT_B051 = 0xB051
    REG_BULK_DATA_TO_MOD_BC00 = 0xBC00

    # MDIO register
    RMASK_B04C_UPGRADE_RDY = 0x8000
    RMASK_B04D_NOOP = 0x0000
    RMASK_B04D_DOWNLOAD_START = 0x1000
    RMASK_B04D_DOWNLOAD_COMPLET = 0x2000
    RMASK_B04D_RUN_A = 0x3000
    RMASK_B04D_RUN_B = 0x4000
    RMASK_B04D_ABORT_DOWNLD = 0x5000
    RMASK_B04D_CPY_AtoB = 0x6000
    RMASK_B04D_CPY_BtoA = 0x7000
    RMASK_B04D_COMMIT_A = 0x8000
    RMASK_B04D_COMMIT_B = 0x9000
    RMASK_B050_READY = 0x8000
    RMASK_B050_CMD_ERR = 0x4000
    RMASK_B051_CMD_STAT_MASK = 0xC000
    RMASK_B051_CMD_STAT_IDLE = 0x0000
    RMASK_B051_CMD_STAT_SUCCESS = 0x4000
    RMASK_B051_CMD_STAT_PROG = 0x8000
    RMASK_B051_CMD_STAT_FAIL = 0xC000
    RMASK_B051_ERR_MASK = 0x007f
    RMASK_B051_ERR_NONE = 0x0000
    RMASK_B051_ERR_CRC_IMAGE = 0x0001
    RMASK_B051_ERR_LEN_IMAGE = 0x0002
    RMASK_B051_ERR_FLASH_WT = 0x0003
    RMASK_B051_ERR_BAD_IMAGE = 0x0004
    RMASK_BO51_IMAGE_RUN = ((1 << 12) & 0xffff)
    RMASK_B051_IMGA_STAT_MASK = ((3 << 10) & 0xffff)
    RMASK_B051_IMGA_STAT_VALID = ((1 << 10) & 0xffff)
    RMASK_B051_IMGB_STAT_MASK = ((3 << 8) & 0xffff)
    RMASK_B051_IMGB_STAT_VALID = ((1 << 8) & 0xffff)
    RMASK_BO51_IMAGE_COMMITTED = ((1 << 7) & 0xffff)

    # Error Resp
    ERROR_RESP = {"NONE": "OK",
                  "MDIO_OPEN": "Unable to open sub20 port",
                  "OPEN_FILE": "Unable to open file",
                  "MDIO_READ": "Unable to read from module",
                  "MDIO_WRITE": "Unable to write to module",
                  "WRITE_BUSY": "Mudule still processing a write command",
                  "UPGRADE_BUSY": "Upgrade in progress",
                  "MDIO_ERROR": "MDIO protocol error",
                  "MDIO_WRONG_STATE": "MDIO module in wrong upgrade state",
                  "MDIO_UPDATE_COMPLETE": "Firmware upgrade completed",
                  "MDIO_INVALID_IMAGE": "Invalid Image",
                  "MDIO_UP_STAT_CRC": "FW Update CRC error",
                  "MDIO_UP_STAT_LEN": "FW Update bulk data length error",
                  "MDIO_UP_STAT_WT": "FW Update flash write error",
                  "MDIO_UP_STATUS_BAD": "FW Update bad image",
                  "MDIO_UP_STATUS_UNKNOWN": "FW Update Unknown status in 0xB051",
                  "MDIO_COMMITTED": "Already Committed"}

    def __init__(self):
        self.mdio_portAddr = 0  # 5
        self.mdio_devAddr = 1
        self.mdio_channel = 1
        self.mdio_current_reg_addr = 0
        self.dev_id = 0
        self.logging_to_display_enabled = False
        self.logging_to_file_enabled = False
        self.log_file_handle = 0
        self.errno = 0

        # Setup the MDIO frame structure for the drives suplied by SUB-20 manufacturers
        elems = (MdioFrameRec * MdioDrivers.__mdio_readWriteBufSize)()
        self.mdio_frames = ctypes.cast(elems, POINTER(MdioFrameRec))

    # port_address - Mdio port address
    # dev_addr - MDIO Device address
    # mdio_channel - There are 2 MDIO channels in on the SUB20. We use channel 1
    # Channel 0 does not seem to work.

    def mdio_init(self, port_addr, dev_addr, mdio_channel):
        self.mdio_portAddr = port_addr
        self.mdio_devAddr = dev_addr
        self.mdio_channel = mdio_channel

        if (self.mdio_open() != 0):
            print("SUB20 device id is: {0}   ERROR: {1}".format(self.dev_id, self.mdio_get_error_description()))

        s2 = create_string_buffer(67)
        sub_get_serial_number(self.dev_id, s2, 67)
        print("\nSerial Number:", s2.value.decode("utf-8"))
        self.mdio_close()

    # ! may have more than 1 SUB-20 connecteded to the PC.
    def mdio_open(self, portNum=0):
        # Open SUB-20 port.
        self.dev_id = sub20dll.sub_open(portNum)
        self.errno = c_int.in_dll(sub20dll, "sub_errno")
        # print "[sub20RegBridgeClass.py] debug -> dev_id:", self.__dev_id
        if (self.dev_id == 0):
            #raise "MDIO_READ"
            print("TN: Dev_ID Error")
            return self.errno.value
        else:
            return 0

    def mdio_close(self):
        sub20dll.sub_close(self.dev_id)

    # Write MDIO register.
    # reg_addr a 16 bit hex word
    # value - The value to write to the module's register.

    def mdio_write(self, reg_addr, value):
        self.mdio_frames[0].op = MdioDrivers.__MDIO_OP_ADDR
        self.mdio_frames[0].port_addr = self.mdio_portAddr
        self.mdio_frames[0].dev_addr = self.mdio_devAddr
        self.mdio_frames[0].data = reg_addr
        self.mdio_current_reg_addr = reg_addr

        self.mdio_frames[1].op = MdioDrivers.__MDIO_OP_WRITE
        self.mdio_frames[1].port_addr = self.mdio_portAddr
        self.mdio_frames[1].dev_addr = self.mdio_devAddr
        self.mdio_frames[1].data = value

        success = sub_mdio_xfer_ex(self.dev_id, 1, MdioDrivers.__mdio_readWriteBufSize, self.mdio_frames)

        if (self.logging_to_file_enabled):
            logLine = 'wt,' + hex(reg_addr) + ',' + hex(value)
            self.mdio_log_writeline(logLine)

        if (self.logging_to_display_enabled):
            print("wt {0} = {1}".format(hex(reg_addr), hex(value)))

        if (success != 0):
            raise "MDIO_WRITE:"

        return success

    # Write a value to a register but wait until the 'MDIO write ready' bit in
    # MDIO register 0xB050. Throw an exception if not ready

    def mdio_write_when_ready(self, reg_addr, value, timeout):
        endT = startT = datetime.datetime.now()
        delta_ms = int((endT - startT).total_seconds() * 1000)

        # wait until ready for write
        readVal = [0]
        success = self.mdio_read(MdioDrivers.REG_MOD_EXT_FN_B050, readVal)
        if (success != 0):
            # raise "MDIO_READ"
            success = 1
            return success
        while (((readVal[0] & MdioDrivers.RMASK_B050_READY) == 0) and (delta_ms < timeout)):
            success = self.mdio_read(MdioDrivers.REG_MOD_EXT_FN_B050, readVal)
            if (success != 0):
                # raise "MDIO_READ"
                success = 1
                return success

            endT = datetime.datetime.now()
            delta_ms = int((endT - startT).total_seconds() * 1000)

        if ((readVal[0] & MdioDrivers.RMASK_B050_READY) == 0):
            # raise "WRITE_BUSY"
            success = 1  # not successful
        else:
            # do the-write
            success = self.mdio_write(reg_addr, value)
            if (success != 0):
                # raise "MDIO_WRITE"
                success = 1
                return success

        return success

    # Read from a register but wait until the 'MDIO write ready' bit in
    # MDIO register 0xB050. Throw an exception if not ready.
    # Good when waiting for the previous write to complete its request before
    # reading a register such as status as an example.    #
    #
    #    reg_addr a 16 bit hex word
    # OUT
    #    value - [list] The value to read from the module's register.
    #
    #
    # RETURN: The error status response. 0 = success. The error number (errorno) can be read
    #         to get further details on the error (see sub20-man.pdf).
    #

    def mdio_read_when_prev_write_complete(self, reg_addr, value, timeout):
        endT = startT = datetime.datetime.now()
        delta_ms = int((endT - startT).total_seconds() * 1000)

        # wait until ready for write
        readVal = [0]
        success = self.mdio_read(MdioDrivers.REG_MOD_EXT_FN_B050, readVal)
        if (success != 0):
            # raise "MDIO_READ"
            success = 1
            return success
        while (((readVal[0] & MdioDrivers.RMASK_B050_READY) == 0) and (delta_ms < timeout)):
            success = self.mdio_read(MdioDrivers.REG_MOD_EXT_FN_B050, readVal)
            if (success != 0):
                # raise "MDIO_READ"
                success = 1
                return success

            endT = datetime.datetime.now()
            delta_ms = int((endT - startT).total_seconds() * 1000)

        if ((readVal[0] & MdioDrivers.RMASK_B050_READY) == 0):
            # raise "WRITE_BUSY"
            success = 1  # not successful
        else:
            success = self.mdio_read(reg_addr, value)

        return success

    # Read a value to a MDIO register on the module. An error status is returned in the event
    # that SUB-20 fails
    #
    # IN:
    #    reg_addr a 16 bit hex word
    # OUT:
    #    value (list) - The value to write to the module's register.
    #
    # RETURN: The error status response. 0 = success. The error number (errorno) can be read
    #         to get further details on the error (see sub20-man.pdf).
    #

    def mdio_read(self, reg_addr, value):
        self.mdio_frames[0].op = MdioDrivers.__MDIO_OP_ADDR
        self.mdio_frames[0].port_addr = self.mdio_portAddr
        self.mdio_frames[0].dev_addr = self.mdio_devAddr
        self.mdio_frames[0].data = reg_addr
        self.mdio_current_reg_addr = reg_addr

        self.mdio_frames[1].op = MdioDrivers.__MDIO_OP_READ
        self.mdio_frames[1].port_addr = self.mdio_portAddr
        self.mdio_frames[1].dev_addr = self.mdio_devAddr
        self.mdio_frames[1].data = 0xffff

        success = sub_mdio_xfer_ex(self.dev_id, 1, MdioDrivers.__mdio_readWriteBufSize, self.mdio_frames)
        # read the value from the register
        value[0] = self.mdio_frames[1].data

        if (self.logging_to_file_enabled):
            logLine = 'rd,' + hex(reg_addr) + ',' + hex(value[0])
            self.mdio_log_writeline(logLine)

        if (self.logging_to_display_enabled):
            print("rd {0} = {1}".format(hex(reg_addr), hex(value[0])))

        if (success != 0):
            raise "MDIO_READ"

        return success

    # Read a value of the current MDIO register then incremment the address on the module to current address +1.
    # Subsequent read or readInc will read the next register.
    # An error status is returned in the event that SUB-20 fails
    #
    # OUT:
    #    value (list)- The value to write to the module's register.
    #
    # RETURN: The error status response. 0 = success. The error number (errorno) can be read
    #         to get further details on the error (see sub20-man.pdf).
    #
    def mdio_read_then_inc(self, value):

        self.mdio_frames[0].op = MdioDrivers.__MDIO_OP_READ_INC
        self.mdio_frames[0].port_addr = self.mdio_portAddr
        self.mdio_frames[0].dev_addr = self.mdio_devAddr
        self.mdio_frames[0].data = 0xffff

        success = sub_mdio_xfer_ex(self.dev_id, 1, MdioDrivers.__mdio_readWriteSingleBuf, self.mdio_frames)
        # read the value from the register
        value[0] = self.mdio_frames[0].data

        if (self.logging_to_file_enabled):
            logLine = 'rl,' + ',' + hex(value[0])
            self.mdio_log_writeline(logLine)

        if (self.logging_to_display_enabled):
            print("rl {0} = {1}".format(hex(self.mdio_current_reg_addr), hex(value[0])))

        self.mdio_current_reg_addr += 1  # MDIO increments counter after the read.
        if (success != 0):
            raise "MDIO_READ:"
        return success

    # Read the error number. The error number (errorno) can be read
    # to get further details on the error (see sub20-man.pdf).
    #
    # RETURN the error number
    def mdio_get_error_number(self):
        return self.errno.value

    # Read the error number and return the description of the error.
    # The error number (errorno) can be read from the SUB20 drivers.
    # To get further details on the error (see sub20-man.pdf).
    #
    # RETURN a string with a description of the last error
    def mdio_get_error_description(self):
        errorDisc = sub20dll.sub_strerror(self.errno.value)
        return ctypes.cast(errorDisc, c_char_p).value

    # Get the last MDIO address that was written/ read from.
    #
    # RETURN the current address
    #
    def mdio_get_current_reg_addr(self):
        return self.mdio_current_reg_addr

    # Print logging to standard out. Logging logs the MDIO messaging sent to the
    # module
    #
    # IN:
    #    enabled - True if want logging
    #
    def mdio_enable_logging(self, enabled):
        if (enabled):
            self.logging_to_display_enabled = True
        else:
            self.logging_to_display_enabled = False

    # Open the log file to log MDIO commands
    def mdio_log_open(self):

        if (self.logging_to_file_enabled):
            print("MDIO log file currently open")
            return

        fileName = './logs/mdioLogs__' + datetime.datetime.today().strftime('%m%d%y_%H%M%S') + '.csv'

        self.log_file_handle = open(fileName, "wb+")
        logline = "Date,Time,ms, CMD, Addr, Value" + os.linesep
        self.logging_to_file_enabled = True
        self.log_file_handle.write(logline)
        print("MDIO log file opened")

    # Close logs
    def mdio_log_close(self):
        if (self.logging_to_file_enabled):
            self.logging_to_file_enabled = False
            self.log_file_handle.close()
            print("MDIO log file closed")
        else:
            print("MDIO log file NOT opened")

    # Write a CSV file to the MDIO log fine
    # format:-
    #
    #    date:        date (added in function)
    #    time:        time stamp (added in function).
    #    ms:          ms componant of time (added in function).
    #    CMD:         rd/wt/rl/addr
    #    address:     read/Write address
    #    value:       value read/written
    #    Carriage return added in function
    #
    # IN:
    #    logLine - parameters to write as a list.
    #
    def mdio_log_writeline(self, logLine):
        logLine = datetime.datetime.now().strftime('%m-%d-%Y,%H:%M:%S,%f') + ',' + logLine + os.linesep
        self.log_file_handle.write(logLine)
        # self.__logFileHandle.write(os.linesep)

    def MdioReg_modState(self):
        readValue = [0]
        modState = []
        state = {
            '0x80': 'txTurnOff',
            '0x40': 'fault',
            '0x20': 'ready',
            '0x8': 'txOff',
            '0x4': 'hiPwrUp',
            '0x2': 'loPwr',
            '0x1': 'init',
        }

        self.mdio_read(self.REG_MOD_STATE_B016, readValue)
        modState.append(hex(readValue[0]))
        modState.append(state[hex(readValue[0])])
        return modState

    def MdioReg_modGenControl(self, setState):
        readValue = [0]
        # self.value = self.MdioReg_modState()
        value = self.mdio_read(self.REG_MOD_STATE_B016, readValue)

        self.state = {
            'softModReset': {'mask': 0x8000, 'state': None, 'pState': None},
            'modLoPwr': {'mask': 0x4000, 'state': None, 'pState': None},
            'txDisable': {'mask': 0x2000, 'state': None, 'pState': None},
            'prgCntrl3': {'mask': 0x1000, 'state': None, 'pState': None},
            'prgCntrl2': {'mask': 0x800, 'state': None, 'pState': None},
            'prgCntrl1': {'mask': 0x400, 'state': None, 'pState': None},
            'glbAlm': {'mask': 0x200, 'state': None, 'pState': None},
            'procReset': {'mask': 0x100, 'state': None, 'pState': None},
            'txDisPinState': {'mask': 0x20, 'state': None, 'pState': None},
            'modLoPwrPinState': {'mask': 0x10, 'state': None, 'pState': None},
            'prgCntrl3PinState': {'mask': 0x8, 'state': None, 'pState': None},
            'prgCntrl2PinState': {'mask': 0x4, 'state': None, 'pState': None},
            'prgCntrl1PinState': {'mask': 0x2, 'state': None, 'pState': None},
        }

        if setState == 'softModReset':
            writeValue = self.state['softModReset']['mask']
            print(hex(writeValue))

        elif setState == 'modLoPwr':
            writeValue = self.state['modLoPwr']['mask']
            print(hex(writeValue))

        elif setState == 'clrModLoPwr':
            # readBuf = [0]
            val = value & (0xffff - self.state['modLoPwr']['mask'])
            writeValue = val

        elif setState == 'txDisable':
            writeValue = self.state['txDisable']['mask']
            print(hex(writeValue))

        self.mdio_write(self.REG_MOD_GEN_CONTROL_B010, writeValue)

class I2CDevice:
    def __init__(self):
        self.sDev = None
        self.sHandle = None

    def sub20Init(self):
        self.sdev = sub20dll.sub_find_devices(self.sDev)
        while(self.sDev != 0):
            self.sDev = sub20dll.sub_find_devices(self.sDev)
            self.sHandle = sub20dll.sub_open(self.sdev)

        if not self.sHandle:
            raise "Unable to open i2c device"

    def subGetSerialNumber(self):
        if not self.sHandle:
            raise "Device was not opened"
        rx_buf_sz = MAX_BUFF_SZ
        rx_buf = create_string_buffer(rx_buf_sz)
        resp = sub2dll.sub_get_serial_number(self.sHandle, rx_buf, rx_buf_sz)
        if(resp < 0):
            raise "Error in reading the Serial Number"
        return rx_buf.value.decode('UTF-8')

    def subI2CFreq(self, freq=0):
        if not self.sHandle:
            raise "Device was not opened"

        if freq > MAX_FREQ:
            raise ValueError("Maximum Frequency Exceeded")

        freqResponse = c_int(freq)
        sub20dll.sub_i2c_freq(self.sHandle, freqResponse)
        return freqResponse.value

    def subI2CRead(self, devAddr, regAddr, buffSz):
        if not self.sHandle:
            raise "Device was not opened"

        regAddSz =1
        rxBuff = create_string_buffer(buffSz)
        resp = sub20dll.sub_i2c_read(self.sHandle, devAddr, regAddr, regAddSz, rxBuff, buffSz)
        if resp:
            raise "Device error in read"

        return rx_buf

    def subI2CWrite(self, devAddr, regAddr, dataToWrite):
        if not self.sHandle:
            raise "Device was not opened"

        regAddrSz =1
        txBuffSz = len(dataToWrite)
        txBuff = create_string_buffer(dataToWrite)
        resp = sub20dll.sub_i2c_write(self.sHandle, devAddr, regAddr, regAddSz, txBuff, txBuffSz)
        if resp:
            raise "Device error to write"








