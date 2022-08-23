from src.CAN_ProgrammerAPI import CAN_Programmer
from UI.CAN_ProgrammerUI import Ui_MainWindow
from util import CAN_Macro
from UI.app_setup import APP_Setup
from PyQt5 import QtWidgets, QtGui
import sys
import time
if __name__=='__main__':
    # APP=APP_Setup(True)

    canprogrammer=CAN_Programmer(debug_level=3)
    canprogrammer.CAN_ProgrammerSetPort('COM10')
    # if canprogrammer.CAN_ProgrammerInitiliseOTAReequest(CMD=CAN_Macro.CMD_OTA_REQUEST,DATA=CAN_Macro.DATA_OTA_REQUEST):
    #     print("OTA Request accepted.")
    # else:
    #     print('OTA Request Failed.Exiting Now...')
    #     exit()
    # if canprogrammer.CAN_ProgrammerChangeBaudRate(CAN_Macro.DATA_BAUDRATE_500_0):
    #     print("Baud Rate Changed")
    # else:
    #     print('BaudRate Change failed. Exiting Now...')
    #     exit()
    
    # if canprogrammer.CAN_ProgrammerChangeBaudRate(CAN_Macro.DATA_BAUDRATE_500_0):
    #     print("Baud Rate Changed")
    # else:
    #     print('BaudRate Change failed. Exiting Now...')
    #     exit()
    # if canprogrammer.CAN_ProgrammerInitiliseBootloader(0.3):
    #     print("CAN Bootloader Initilised. Device is ready to recive commands")
    # else:
    #     print('Bootloader Init Request Failed. Exiting Now...')
    #     exit()
 
    # print("DeviceID:",canprogrammer.CAN_ProgrammerGetID())
    # print("BootloaderVersion:",canprogrammer.CAN_ProgrammerGetVersion())
    # if canprogrammer.CAN_ProgrammerFullChipErase():
    #     print("Full CHIP Erase succesful")
    # # if canprogrammer.CAN_ProgrammerSectorErase(addr=0x8000000,no_of_sectors=19):
    # # #     print("Sector Erase succesful")
    # if canprogrammer.CAN_ProgrammerWriteMemory("C:/GURU/vecmocon/VIM/ivec_bootloader-application/ivec-bootloader/build/ivec-bootloader.bin",addr=0x8000000):
    #     print("Flashing Succesful")
    # #     # if canprogrammer.CAN_ProgrammerJumpToAddress(addr=0x08000000):
    # #     #     print("Jumping Succesful")
    # # else:
    # #     print('Flashing Failed')
    # # with open('C:/GURU/vecmocon/VIM/ivec-application/Scripts/CAN_Programmer/write.bin','wb') as writefile:
    # #     writefile.write(canprogrammer.CAN_ProgrammerReadMemory(addr=0x8000000,no_of_bytes=38636))
    # #     print("file written")
    DATA=[0,0,0xff,0xff,0x23,0x00,0xff,0xc1]
    # CFFC169
    # canprogrammer.CAN_ProgrammerSendCmd(CMD=0x10,data=DATA,dlc=8)
    t_start=time.time()
    while True:
        if time.time()-t_start>5:
            t_start=time.time()
            print("Sending message")
            canprogrammer.CAN_ProgrammerSendCmd(0x12,data=DATA,dlc=8)
        msg=canprogrammer.CAN_ProgrammerPollForData(1)
        if msg:
            print(f"ID:{hex(msg.arbitration_id)}    DATA:{msg.data} DLC:{msg.dlc}")
            if msg.arbitration_id==0xCFFC169:
                print("Sending ack")
                canprogrammer.CAN_ProgrammerSendCmd(0xCFFC123,data=DATA,dlc=8)

