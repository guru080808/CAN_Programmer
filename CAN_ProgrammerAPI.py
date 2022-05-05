from socket import timeout
from unittest.mock import sentinel
import can
import time
from datetime import datetime
import CAN_Macro


class CAN_Programmer:
    def __init__(self, channel: str, debug: bool) -> None:
        '''
        channel=COMx

        '''
        self.__canBus = can.interface.Bus(bustype='serial', channel=channel)
        f = open(
            "C:/GURU/vecmocon/VIM/ivec-application/Scripts/CAN_Programmer/CANProgrammer.log", 'w')
        f.close()
        self.DebugEnable = debug

    def MODULE_DEBUG(self, data_to_print):
        if self.DebugEnable:
            print(time.time(), datetime.now().strftime(
                    "%H:%M:%S"), data_to_print)
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
            f"-------Sending CAN packet with id:{hex(ID)} data:{bytes(DATA)} DLC:{DLC}--------")
        try:
            message = can.Message(arbitration_id=ID, is_extended_id=False,
                                  data=DATA, dlc=DLC)
            self.__canBus.send(message, timeout=0.2)
            retCode = 1
        except Exception as e:
            self.MODULE_DEBUG(f"Exception:{e} while sending can message")
        return retCode

    def CAN_ProgrammerWaitForAck(self, CMD):
        whiletimeout = time.time()
        state = CAN_Macro.BOOTLOADER_ERROR
        while time.time()-whiletimeout < 6:
            msg = self.__canBus.recv(1)
            if msg and msg.arbitration_id == CMD:
                self.MODULE_DEBUG(
                    f"Message:ID:{hex(msg.arbitration_id)},bytes:{msg.data},DLC:{msg.dlc}")
                if CMD == CAN_Macro.CMD_ACK:
                    state = CAN_Macro.BOOTLOADER_OK
                    break
                elif msg.data[0] == CAN_Macro.CMD_ACK:
                    state = CAN_Macro.BOOTLOADER_OK
                    break

        return state

    def CAN_ProgrammerPollForCMDData(self, CMD, timeout: float,):
        data = b''
        data_counts = 0
        data_end = 0
        whiletimeout = time.time()
        while time.time()-whiletimeout < timeout:
            msg = self.__canBus.recv(1)
            if msg and msg.arbitration_id == CMD:
                data += msg.data
                data_counts += msg.dlc
                if msg.data[0:1] == CAN_Macro.CMD_ACK:
                    break
            else:
                break
        self.MODULE_DEBUG(
            f"Message:ID:{hex(CMD)},bytes:{data},DLC:{data_counts}")
        data_dict = {
            'data': data,
            'total_bytes': data_counts
        }
        return data_dict

    def CAN_ProgrammerPollForData(self, timeout: float):
        msg = self.__canBus.recv(timeout)
        return msg

    def CAN_ProgrammerGetID(self) -> str:
        dev_ID = ''
        temp = b''
        if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_GET_ID) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_GET_ID) == CAN_Macro.BOOTLOADER_OK:
            data_dict = self.CAN_ProgrammerPollForCMDData(
                timeout=0.5, CMD=CAN_Macro.CMD_GET_ID)
            if data_dict['total_bytes'] and data_dict['data'][-1] == CAN_Macro.CMD_ACK:
                temp = data_dict['data'][0:data_dict['total_bytes']-1]
                dev_ID = hex(int.from_bytes(temp, 'big', signed=False))
        return dev_ID

    def CAN_ProgrammerGetVersion(self) -> str:
        dev_VER = ''
        temp = b''
        if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_GET_VERSION) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_GET_VERSION) == CAN_Macro.BOOTLOADER_OK:
            data_dict = self.CAN_ProgrammerPollForCMDData(
                timeout=0.5, CMD=CAN_Macro.CMD_GET_VERSION)
            if data_dict['total_bytes'] and data_dict['data'][-1] == CAN_Macro.CMD_ACK:
                temp = hex(data_dict['data'][0])
                dev_VER = temp
        return dev_VER

    def CAN_ProgrammerInitiliseBootloader(self, wait=0):
        '''
        Send Sync Cmd to bootloader to intilise CAN mode
        wait(in seconds)>=time of bootloader mode entered-time of OTA request ACK NOTE:this delay is to ensure that device is in bootloader mode before sending SYNC request
        '''
        time.sleep(wait)
        retCode = 0
        if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_ACK) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_ACK) == CAN_Macro.BOOTLOADER_OK:
            retCode = 1
        return retCode

    def CAN_ProgrammerInitiliseOTAReequest(self, CMD, DATA):
        '''
        Sends command to CAN bus for OTA request and waits for ACK on same CMD ID with 
        DLC=1 and data=CAN_Macro.CMD_ACK and ACK must be recievd within 1 sec
        '''
        if self.CAN_ProgrammerSendCmd(CMD=CMD, data=[DATA]):
            self.MODULE_DEBUG("OTA Request Sent. Waiting for ACK...")
            if self.CAN_ProgrammerWaitForAck(CMD=CMD) == CAN_Macro.BOOTLOADER_OK:
                return 1
        return 0

    def CAN_ProgrammerChangeBaudRate(self, BAUDRATE):
        if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_BAUDRATE, data=[BAUDRATE, CAN_Macro.DATA_BAUDRATE_125_1]):
            self.MODULE_DEBUG(
                "BAUDRATE Change Request Sent. Waiting for ACK...")
            if self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_BAUDRATE):
                return 1
        return 0

    def CAN_ProgrammerFullChipErase(self):
        if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_ERASE, data=[0xff]):
            self.MODULE_DEBUG("Starting CHIP Erase. Waiting for ACK...")
            if self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_ERASE):
                if self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_ERASE):
                    return 1
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
                if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_ERASE, data=[no_of_sectors-1]) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_ERASE):
                    SectorsPending = no_of_sectors
                    TotalErasingRequests = int(
                        no_of_sectors/8) + (0 if no_of_sectors % 256 == 0 else 1)
                    for i in range(TotalErasingRequests):
                        DATA = [i*8+j for j in range(8)]
                        if SectorsPending < 9:
                            DATA = [j+i*8 for j in range(SectorsPending)]
                        self.MODULE_DEBUG(
                            f"Starting Sector Erase: {DATA} out of {no_of_sectors}")
                        if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_ERASE, data=DATA) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_ERASE):
                            SectorsPending -= 8
                            if SectorsPending <= 0 and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_ERASE):
                                return 1
                        else:
                            self.MODULE_DEBUG(f"Sector {i} failed to Erase")
                            return 0

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
                        f"request:{i} out of {TotalRequest} Pending:{TempLen} out of Totallen:{Totalen}")

                    if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_WRITEMEMORY, data=ADDR) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_WRITEMEMORY):
                        SentLen = 0
                        while TempLen:
                            self.MODULE_DEBUG(f"Sentlen:{SentLen}")
                            if SentLen >= TempLen or SentLen >= 256:
                                self.MODULE_DEBUG("Waiting for double ack")
                                if not self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_WRITEMEMORY):
                                    print(
                                        f"Double ACK Not Received Sentlen:{SentLen}  Request:{i} out of {TotalRequest}   ADDR:{ADDR}")
                                    return 0
                                else:
                                    TempLen -= 256
                                    break
                            if self.CAN_ProgrammerSendCmd(CMD=0x04, data=bindata[256*i+SentLen:256*i+SentLen+8]) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_WRITEMEMORY):
                                SentLen += 8
                            else:
                                print(
                                    f"ACK Not Received Sentlen:{SentLen}  Request:{i} out of {TotalRequest}   ADDR:{ADDR}")
                                return 0
                        # time.sleep(0.100)
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
                        f"request:{i} out of {TotalRequest-1} Pending:{ReadBytesPending} out of Totallen:{Totalen}")

                    if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_READ_MEMORY, data=ADDR) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_READ_MEMORY):
                        data_dict=self.CAN_ProgrammerPollForCMDData(CMD=CAN_Macro.CMD_READ_MEMORY,timeout=1)
                        if data_dict['data'][-1]==CAN_Macro.CMD_ACK:
                            ReadBuf+=data_dict['data'][0:-1]
                            ReadBytesPending-=256
                        else:
                            self.MODULE_DEBUG(f"ACK not found in data   Request:{i} out of {TotalRequest} Pending:{ReadBytesPending} out of Totallen:{Totalen}")
                            return ReadBuf


        return ReadBuf

    def CAN_ProgrammerJumpToAddress(self, addr: int):
        ADDR = bytearray(addr.to_bytes(4, 'big'))
        if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_GO, data=ADDR) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_GO):
            return 1
        return 0

    def CAN_ProgrammerFlashWriteUnprotect(self):
        if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_WRITEOUT_UNPROTECT) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_WRITEOUT_UNPROTECT):
            return 1
        return 0

    def CAN_ProgrammerFlashWriteprotect(self):
        if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_WRITEOUT_PROTECT) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_WRITEOUT_PROTECT):
            return 1
        return 0

    def CAN_ProgrammerFlashReadUnprotect(self):
        if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_READOUT_UNPROTECT) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_READOUT_UNPROTECT):
            return 1
        return 0

    def CAN_ProgrammerFlashReadprotect(self):
        if self.CAN_ProgrammerSendCmd(CMD=CAN_Macro.CMD_READOUT_PROTECT) and self.CAN_ProgrammerWaitForAck(CMD=CAN_Macro.CMD_READOUT_PROTECT):
            return 1
        return 0
