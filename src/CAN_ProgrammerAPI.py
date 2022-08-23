from socket import timeout
from unittest.mock import sentinel
import can
import time
from datetime import datetime
from util.CAN_Macro import *


class CAN_Programmer:
    def __init__(self,APP_Object=None, debug_level=0,APP_Enable=0) -> None:
        '''
        channel=COMx

        '''
        self.Debuglvl = debug_level
        self.AppEnable=APP_Enable
        self.AppObject=APP_Object
        f = open(
            "C:/GURU/vecmocon/VIM/ivec-application/Scripts/CAN_Programmer/CANProgrammer.log", 'w')
        f.close()
        

    def CAN_ProgrammerSetPort(self,channel)->int:
        retCode=0
        try:
            self.__canBus = can.interface.Bus(bustype='serial', channel=channel)
            retCode=1
            self.MODULE_DEBUG(f'{channel} connected',DEBUG_LVL_1)
        except Exception as e:
            retCode=0
            self.MODULE_DEBUG(f'{channel} failed with exeption {e}',DEBUG_LVL_0)
        return retCode

    def CAN_ProgrammerSetVerbosityLvl(self,verbosityLvl):
        self.Debuglvl=verbosityLvl
        return 

    def MODULE_DEBUG(self, data_to_print,debug_level=0):
        data_print=0
        data_log=0
        if self.Debuglvl>=debug_level:
            data_print=1
            if self.Debuglvl==3:
                data_log=1

        if data_print:
            print(time.time(), data_to_print)
            if self.AppEnable:
                self.AppObject.APP_ShowLogs(f'{time.time()}:-{data_to_print}')

        if data_log:
            with open("C:/GURU/vecmocon/VIM/ivec-application/Scripts/CAN_Programmer/CANProgrammer.log", 'a') as logfile:
                logfile.write(f"\n{time.time()}--{data_to_print}")
        return

    def CAN_ProgrammerAddCallback(self, callback):
        listener = can.Listener()
        listener.on_message_received = callback
        self.__notifier = can.Notifier(self.__canBus, [listener])
        self.__listeners = [listener]

    def CAN_ProgrammerSendCmd(self, CMD, data=[0], dlc=0):
        retCode = 0
        ID = CMD
        DATA = data
        DLC = len(data)
        if dlc:
            DLC = dlc
        self.MODULE_DEBUG(
            f"-------Sending CAN packet with id:{hex(ID)} data:{bytes(DATA)} DLC:{DLC}--------",DEBUG_LVL_3)
        try:
            message = can.Message(arbitration_id=ID, is_extended_id=True,
                                  data=DATA, dlc=DLC)
            self.__canBus.send(message, timeout=0.2)
            retCode = 1
        except Exception as e:
            self.MODULE_DEBUG(f"Exception:{e} while sending can message")
        return retCode

    def CAN_ProgrammerWaitForAck(self, CMD,delay=6):
        whiletimeout = time.time()
        state = BOOTLOADER_ERROR
        while time.time()-whiletimeout < delay:
            msg = self.__canBus.recv(0.1)
            if msg and msg.arbitration_id == CMD:
                self.MODULE_DEBUG(
                    f"Message:ID:{hex(msg.arbitration_id)},bytes:{msg.data},DLC:{msg.dlc}",DEBUG_LVL_3)
                if CMD == CMD_ACK:
                    state = BOOTLOADER_OK
                    break
                elif msg.data[0] == CMD_ACK:
                    self.MODULE_DEBUG("ACK Recievd",DEBUG_LVL_3)
                    state = BOOTLOADER_OK
                    break

        return state

    def CAN_ProgrammerPollForCMDData(self, CMD, timeout: float):
        data = b''
        data_counts = 0
        whiletimeout = time.time()
        while time.time()-whiletimeout < timeout:
            msg = self.__canBus.recv(0.1)
            if msg and msg.arbitration_id == CMD:
                data += msg.data
                data_counts += msg.dlc
                if msg.data[0:1] == CMD_ACK:
                    break
            else:
                break
        self.MODULE_DEBUG(
            f"Message:ID:{hex(CMD)},bytes:{data},DLC:{data_counts}",DEBUG_LVL_3)
        data_dict = {
            'data': data,
            'total_bytes': data_counts
        }
        return data_dict

    def CAN_ProgrammerPollForData(self, timeout: float):
        msg = self.__canBus.recv(timeout)
        self.MODULE_DEBUG(msg,DEBUG_LVL_3)
        return msg

    def CAN_ProgrammerGetID(self) -> str:
        dev_ID = ''
        temp = b''
        self.MODULE_DEBUG('Getting Product ID',DEBUG_LVL_1)
        if self.CAN_ProgrammerSendCmd(CMD=CMD_GET_ID) and self.CAN_ProgrammerWaitForAck(CMD=CMD_GET_ID) == BOOTLOADER_OK:
            data_dict = self.CAN_ProgrammerPollForCMDData(
                timeout=0.5, CMD=CMD_GET_ID)
            if data_dict['total_bytes'] and data_dict['data'][-1] == CMD_ACK:
                temp = data_dict['data'][0:data_dict['total_bytes']-1]
                dev_ID = hex(int.from_bytes(temp, 'big', signed=False))
                self.MODULE_DEBUG(f'DeviceID:{dev_ID}',DEBUG_LVL_1)
        return dev_ID

    def CAN_ProgrammerGetVersion(self) -> str:
        dev_VER = ''
        temp = b''
        self.MODULE_DEBUG('Getting Bootloader Version',DEBUG_LVL_1)
        if self.CAN_ProgrammerSendCmd(CMD=CMD_GET_VERSION) and self.CAN_ProgrammerWaitForAck(CMD=CMD_GET_VERSION) == BOOTLOADER_OK:
            data_dict = self.CAN_ProgrammerPollForCMDData(
                timeout=0.5, CMD=CMD_GET_VERSION)
            if data_dict['total_bytes'] and data_dict['data'][-1] == CMD_ACK:
                temp = hex(data_dict['data'][0])
                dev_VER = temp
                self.MODULE_DEBUG(f'Device Ver:{dev_VER}',DEBUG_LVL_1)
        return dev_VER

    def CAN_ProgrammerInitiliseBootloader(self, wait=0):
        '''
        Send Sync Cmd to bootloader to intilise CAN mode
        wait(in seconds)>=time of bootloader mode entered-time of OTA request ACK NOTE:this delay is to ensure that device is in bootloader mode before sending SYNC request
        '''
        time.sleep(wait)
        retCode = 0
        self.MODULE_DEBUG("Connecting with ST Bootloader",DEBUG_LVL_1)
        if self.CAN_ProgrammerSendCmd(CMD=CMD_ACK) and self.CAN_ProgrammerWaitForAck(CMD=CMD_ACK) == BOOTLOADER_OK:
            self.MODULE_DEBUG("Connected.Device is ready to recieve commands",DEBUG_LVL_1)
            retCode = 1
        else:
                self.MODULE_DEBUG("ACK Not Recived",DEBUG_LVL_1)
        return retCode

    def CAN_ProgrammerInitiliseOTAReequest(self, CMD, DATA):
        '''
        Sends command to CAN bus for OTA request and waits for ACK on same CMD ID with 
        DLC=1 and data=CMD_ACK and ACK must be recievd within 1 sec
        '''
        if type(DATA) is int and self.CAN_ProgrammerSendCmd(CMD=CMD, data=[DATA]):
            self.MODULE_DEBUG("OTA Request Sent. Waiting for ACK...",DEBUG_LVL_1)
            if self.CAN_ProgrammerWaitForAck(CMD=CMD,delay=0.1) == BOOTLOADER_OK:
                self.MODULE_DEBUG("ACK Recived",DEBUG_LVL_1)
                return 1
            else:
                self.MODULE_DEBUG("ACK Not Recived",DEBUG_LVL_1)
        return 0

    def CAN_ProgrammerChangeBaudRate(self, BAUDRATE):
        if self.CAN_ProgrammerSendCmd(CMD=CMD_BAUDRATE, data=[BAUDRATE, DATA_BAUDRATE_125_1]):
            self.MODULE_DEBUG(
                "BAUDRATE Change Request Sent. Waiting for ACK...",DEBUG_LVL_1)
            if self.CAN_ProgrammerWaitForAck(CMD=CMD_BAUDRATE):
                self.MODULE_DEBUG("ACK Recived",DEBUG_LVL_1)
                return 1
            else:
                self.MODULE_DEBUG("ACK Not Recived",DEBUG_LVL_1)
        return 0

    def CAN_ProgrammerFullChipErase(self):
        if self.CAN_ProgrammerSendCmd(CMD=CMD_ERASE, data=[0xff]):
            self.MODULE_DEBUG("Starting CHIP Erase. Waiting for ACK...",DEBUG_LVL_1)
            if self.CAN_ProgrammerWaitForAck(CMD=CMD_ERASE):
                if self.CAN_ProgrammerWaitForAck(CMD=CMD_ERASE):
                    self.MODULE_DEBUG("CHIP Erased",DEBUG_LVL_1)
                    return 1
            else:
                self.MODULE_DEBUG("ACK Not Recived",DEBUG_LVL_1)
        return 0

    def CAN_ProgrammerSectorErase(self, addr=0, no_of_sectors=0):
        if addr:
            TotalSize = 524288
            EndAddr = 0x0807FFFF
            StartAddr = 0x08000000
            Range_H = 0x08000000
            Range_L = 0x08000000
            Range_Size = 2048
            SectorofAddr = None
            for i in range(256):
                Range_L = Range_H
                Range_H = Range_H+Range_Size
                if addr >= Range_L and addr < Range_H:
                    SectorofAddr = i
                    break
            if SectorofAddr is not None and no_of_sectors < 255:
                if self.CAN_ProgrammerSendCmd(CMD=CMD_ERASE, data=[no_of_sectors-1]) and self.CAN_ProgrammerWaitForAck(CMD=CMD_ERASE):
                    SectorsPending = no_of_sectors
                    TotalErasingRequests = int(
                        no_of_sectors/8) + (0 if no_of_sectors % 256 == 0 else 1)
                    for i in range(TotalErasingRequests):
                        DATA = [SectorofAddr+i*8+j for j in range(8)]
                        if SectorsPending < 9:
                            DATA = [SectorofAddr+j+i*8 for j in range(SectorsPending)]
                        self.MODULE_DEBUG(
                            f"Starting Sector Erase: {DATA} out of {no_of_sectors}",DEBUG_LVL_2)
                        if self.CAN_ProgrammerSendCmd(CMD=CMD_ERASE, data=DATA) and self.CAN_ProgrammerWaitForAck(CMD=CMD_ERASE):
                            SectorsPending -= 8
                            if SectorsPending <= 0 and self.CAN_ProgrammerWaitForAck(CMD=CMD_ERASE):
                                self.MODULE_DEBUG(f"Erasing Succesful",DEBUG_LVL_2)
                                return 1
                        else:
                            self.MODULE_DEBUG(f"Sector {i} failed to Erase",DEBUG_LVL_2)
                            return 0
                else:
                    self.MODULE_DEBUG("ACK Not Recievd",DEBUG_LVL_2)
        return 0

    def CAN_ProgrammerWriteMemory(self, filepath: str, addr: int):
        retCode = 1
        try:
            with open(filepath, mode="rb") as binfile:
                bindata = binfile.read()
                TempLen = Totalen = len(bindata)
                TotalRequest = int(Totalen/256) + \
                    (0 if Totalen % 256 == 0 else 1)
                for i in range(TotalRequest):
                    ADDR = bytearray(addr.to_bytes(4, 'big'))
                    ADDR.append(0)
                    if TempLen > 256:
                        ADDR[4] = 255
                        addr += 256
                    else:
                        ADDR[4] = TempLen-1
                        addr += TempLen

                    self.MODULE_DEBUG(
                        f"request:{i} out of {TotalRequest} Pending:{TempLen} out of Totallen:{Totalen}",DEBUG_LVL_2)

                    if self.CAN_ProgrammerSendCmd(CMD=CMD_WRITEMEMORY, data=ADDR) and self.CAN_ProgrammerWaitForAck(CMD=CMD_WRITEMEMORY):
                        SentLen = 0
                        while TempLen:
                            if SentLen >= TempLen or SentLen >= 256:
                                if not self.CAN_ProgrammerWaitForAck(CMD=CMD_WRITEMEMORY):
                                    print(
                                        f"ACK Not Received Sentlen:{SentLen}  Request:{i} out of {TotalRequest}   ADDR:{ADDR}",DEBUG_LVL_2)
                                    return 0
                                else:
                                    TempLen -= 256
                                    break
                            if self.CAN_ProgrammerSendCmd(CMD=0x04, data=bindata[256*i+SentLen:256*i+SentLen+8]) and self.CAN_ProgrammerWaitForAck(CMD=CMD_WRITEMEMORY):
                                SentLen += 8
                            else:
                                print(
                                    f"ACK Not Received Sentlen:{SentLen}  Request:{i} out of {TotalRequest}   ADDR:{ADDR}",DEBUG_LVL_2)
                                return 0
                        time.sleep(0.100)
                    else:
                        return 0
        except Exception as e:
            print("Exception: ", e)
            retCode = 0
        return retCode

    def CAN_ProgrammerReadMemory(self,addr:int,no_of_bytes):
        ReadBuf=b''
        ReadBytesPending = Totalen = no_of_bytes
        TotalRequest = int(Totalen/256) + \
            (0 if Totalen % 256 == 0 else 1)
        if addr:
            for i in range(TotalRequest):
                    ADDR = bytearray(addr.to_bytes(4, 'big'))
                    ADDR.append(0)
                    if ReadBytesPending > 256:
                        ADDR[4] = 255
                        addr += 256
                    else:
                        ADDR[4] = ReadBytesPending-1
                        addr += ReadBytesPending

                    self.MODULE_DEBUG(
                        f"request:{i} out of {TotalRequest-1} Pending:{ReadBytesPending} out of Totallen:{Totalen}",DEBUG_LVL_2)

                    if self.CAN_ProgrammerSendCmd(CMD=CMD_READ_MEMORY, data=ADDR) and self.CAN_ProgrammerWaitForAck(CMD=CMD_READ_MEMORY):
                        data_dict=self.CAN_ProgrammerPollForCMDData(CMD=CMD_READ_MEMORY,timeout=2)
                        if data_dict['data'][-1]==CMD_ACK:
                            ReadBuf+=data_dict['data'][0:-1]
                            ReadBytesPending-=256
                        else:
                            self.MODULE_DEBUG(f"ACK not found in data   Request:{i} out of {TotalRequest} Pending:{ReadBytesPending} out of Totallen:{Totalen}",DEBUG_LVL_2)
                            return ReadBuf


        return ReadBuf

    def CAN_ProgrammerJumpToAddress(self, addr: int):
        ADDR = bytearray(addr.to_bytes(4, 'big'))
        self.MODULE_DEBUG(f"Jumping to Address:{addr}",DEBUG_LVL_1)
        if self.CAN_ProgrammerSendCmd(CMD=CMD_GO, data=ADDR) and self.CAN_ProgrammerWaitForAck(CMD=CMD_GO):
            self.MODULE_DEBUG(f"Jumping to Address:{addr} Succesful",DEBUG_LVL_1)
            return 1
        else:
            self.MODULE_DEBUG(f"Jumping to Address:{addr} Failed",DEBUG_LVL_1)
        return 0

    def CAN_ProgrammerFlashWriteUnprotect(self):
        if self.CAN_ProgrammerSendCmd(CMD=CMD_WRITEOUT_UNPROTECT) and self.CAN_ProgrammerWaitForAck(CMD=CMD_WRITEOUT_UNPROTECT):
            return 1
        return 0

    def CAN_ProgrammerFlashWriteprotect(self):
        if self.CAN_ProgrammerSendCmd(CMD=CMD_WRITEOUT_PROTECT) and self.CAN_ProgrammerWaitForAck(CMD=CMD_WRITEOUT_PROTECT):
            return 1
        return 0

    def CAN_ProgrammerFlashReadUnprotect(self):
        if self.CAN_ProgrammerSendCmd(CMD=CMD_READOUT_UNPROTECT) and self.CAN_ProgrammerWaitForAck(CMD=CMD_READOUT_UNPROTECT):
            return 1
        return 0

    def CAN_ProgrammerFlashReadprotect(self):
        if self.CAN_ProgrammerSendCmd(CMD=CMD_READOUT_PROTECT) and self.CAN_ProgrammerWaitForAck(CMD=CMD_READOUT_PROTECT):
            return 1
        return 0

    def CAN_ProgrammerSetBaudRate(self,bitrate):
        if self.CAN_ProgrammerSendCmd(CMD=CMD_SET_SPEED,data=[bitrate]) and self.CAN_ProgrammerWaitForAck(CMD=CMD_SET_SPEED):
            if bitrate==1:
                CANUSBbitrate=DATA_BAUDRATE_125_0
            elif bitrate==2:
                CANUSBbitrate=DATA_BAUDRATE_250_0
            elif bitrate==3:
                CANUSBbitrate=DATA_BAUDRATE_500_0
            elif bitrate==4:
                CANUSBbitrate=DATA_BAUDRATE_1000_0
            if self.CAN_ProgrammerChangeBaudRate(BAUDRATE=CANUSBbitrate):
                if self.CAN_ProgrammerWaitForAck(CMD=CMD_SET_SPEED):
                    return 1
        return 0