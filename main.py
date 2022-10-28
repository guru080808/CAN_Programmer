from src.CAN_ProgrammerAPI import CAN_Programmer
from UI.CAN_ProgrammerUI import Ui_MainWindow
from util import CAN_Macro
from UI.app_setup import APP_Setup
from PyQt5 import QtWidgets, QtGui
import sys
import time
if __name__=='__main__':
    APP=APP_Setup(True)

    canprogrammer=CAN_Programmer(debug_level=1)
    canprogrammer.CAN_ProgrammerSetPort('COM29')
    if canprogrammer.CAN_ProgrammerChangeBaudRate(CAN_Macro.DATA_BAUDRATE_500_0):
        print("Baud Rate Changed")
    else:
        print('BaudRate Change failed. Exiting Now...')
        exit()
    whiletimeout=time.time()
    # while True:
    #     if canprogrammer.CAN_ProgrammerInitiliseOTAReequest(CMD=CAN_Macro.CMD_OTA_REQUEST,DATA=CAN_Macro.DATA_OTA_REQUEST):
    #         print("OTA Request accepted.")
    #     elif time.time()-whiletimeout>10:
    #         print('OTA Request Failed.Exiting Now...')
    #         time.sleep(0.3)
    #         exit()

    
    # if canprogrammer.CAN_ProgrammerChangeBaudRate(CAN_Macro.DATA_BAUDRATE_125_0):
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
    DATA=[1,2,3,4,5,6,7,8]
    # CFFC169
    # canprogrammer.CAN_ProgrammerSendCmd(CMD=0x10,data=DATA,dlc=8)
    ID_LIST=[0x18900140,0x18910140,0x18920140,0x18930140,0x18940140,0x18950140,0x18960140,0x18970140,0x18980140]
    i=0
    shift=0
    t_start1=time.time()
    t_start=time.time()
    # canprogrammer.CAN_ProgrammerSendCmd(0x18d90140,data=DATA,dlc=8) 
    mstr=''
    while True:
        if time.time()-t_start>3:
            t_start=time.time()
            print("Sending message")
            canprogrammer.CAN_ProgrammerSendCmd(0x14fffc20,data=DATA,dlc=8) 
        msg=canprogrammer.CAN_ProgrammerPollForData(0.1)
        try:
            
            if  msg.arbitration_id == 0x69:
                mstr += msg.data.decode('utf-8') 
                if '\n' in mstr:
                    print(mstr)
                    mstr = ""
            else:
                print("rx : {}".format(msg))
        except Exception as e:
            # print("exception",e)
            pass
        # if msg:
        #     print(f"ID:{hex(msg.arbitration_id)}    DATA:{msg.data} DLC:{msg.dlc}")
        #     if msg.arbitration_id==0xCFFC169:
        #         print("Sending ack")
        #         canprogrammer.CAN_ProgrammerSendCmd(0xCFFC123,data=DATA,dlc=8)

