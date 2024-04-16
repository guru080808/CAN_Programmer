import sys
from src.CAN_ProgrammerAPI import CAN_Programmer
from src.CAN_ProgrammerAPI import CAN_Programmer
from UI.CAN_ProgrammerUI import Ui_MainWindow
from util import CAN_Macro
from UI.app_setup import APP_Setup
from PyQt5 import QtWidgets, QtGui
import can.interfaces.serial
import time
import argparse,os

def FLASH_mode(addr,filepath,comport,debuglevel):
    print("Flash mode")
    print("Checking address now...")
    try:
        if '0x' in addr:
            ADDR=int(addr,16)
        else:
            ADDR=int(addr)
    except:
        print("Address not ok:",addr)
        sys.exit()

    addr_range=range(0x08000000,0x0807FFFF+1)
    if ADDR not in addr_range:
        print(f"Address:{hex(ADDR)} is not in range {hex(addr_range[0])}-{hex(addr_range[-1])}")
        sys.exit()
    print("Address check pass")
    print("Checking file ")
    if not os.path.exists(filepath):
        print("Filepath does not exist:",filepath)
        sys.exit()
    print("Filepath check pass")
    if debuglevel is None or int(debuglevel)<=0:
        debuglevel='1'
    canprogrammer=CAN_Programmer(debug_level=int(debuglevel) if int(debuglevel)<=CAN_Macro.DEBUG_LVL_3 else CAN_Macro.DEBUG_LVL_3)
    canprogrammer.CAN_ProgrammerSetPort(comport)
    if canprogrammer.CAN_ProgrammerChangeBaudRate(CAN_Macro.DATA_BAUDRATE_500_0):
        print("Baud Rate Changed")
    else:
        print('BaudRate Change failed. Exiting Now...')
        sys.exit()
    whiletimeout=time.time()
    while True:
        if canprogrammer.CAN_ProgrammerInitiliseOTAReequest(CMD=CAN_Macro.CMD_OTA_REQUEST,DATA=CAN_Macro.DATA_OTA_REQUEST):
            print("OTA Request accepted.")
            break
        elif time.time()-whiletimeout>20:
            print('OTA Request Failed.Exiting Now...')
            time.sleep(0.3)
            sys.exit()

    time.sleep(1)
    if canprogrammer.CAN_ProgrammerChangeBaudRate(CAN_Macro.DATA_BAUDRATE_125_0):
        print("Baud Rate Changed")
    else:
        print('BaudRate Change failed. Exiting Now...')
        sys.exit()
    time.sleep(1)
    if canprogrammer.CAN_ProgrammerInitiliseBootloader(0.3):
        print("CAN Bootloader Initilised. Device is ready to recive commands")
    else:
        print('Bootloader Init Request Failed. Exiting Now...')
        sys.exit()
    time.sleep(1)
    if canprogrammer.CAN_ProgrammerSetBaudRate(4):
            print("Baud Rate Changed")
    else:
        print('BaudRate Change failed. Exiting Now...')
        sys.exit()
    time.sleep(1)
    dev_id=canprogrammer.CAN_ProgrammerGetID()
    time.sleep(1)
    dev_ver=canprogrammer.CAN_ProgrammerGetVersion()
    print("DeviceID:",dev_id)
    print("BootloaderVersion:",dev_ver)
    # if canprogrammer.CAN_ProgrammerFullChipErase():
    #     print("Full CHIP Erase succesful")
    # if not dev_ver:
    #     print("Unable to fetch device version. Exiting now...")
    #     sys.exit()
    FILESIZE=os.path.getsize(filepath)
    PagesToClear=int((FILESIZE)/2048) + (1 if (FILESIZE)%2048!=0 else 0)
    if ADDR==0x807f000:
        PagesToClear=2
    time.sleep(1)
    if canprogrammer.CAN_ProgrammerSectorErase(addr=ADDR,no_of_sectors=PagesToClear):
        print("Sector Erase succesful")
        time.sleep(1)
        if canprogrammer.CAN_ProgrammerWriteMemory(filepath,addr=ADDR):
            print("Flashing Succesful")
        else:
            print("Flashing failed...")
    else:
        print('Erasing Failed')
    return

def DEBUGLOGS_mode(comport,filepath):
    print("Debug logs mode")
    canprogrammer=CAN_Programmer(debug_level=1)
    canprogrammer.CAN_ProgrammerSetPort(comport)
    if canprogrammer.CAN_ProgrammerChangeBaudRate(CAN_Macro.DATA_BAUDRATE_500_0):
        print("Baud Rate Changed")
    else:
        print('BaudRate Change failed. Exiting Now...')
        sys.exit()
    heartbeattimer=time.time()
    mstr=''
    if not os.path.exists(filepath):
        f=open(filepath,'w')
        f.write(f"File created at:{time.ctime(time.time())}")
        f.close()
    f=open(filepath,'a')
    f.write(f"\n--------------- Starting new logs at:{time.ctime(time.time())}-------------- \n")
    f.close()
    while True:
        if time.time()-heartbeattimer>2:
            heartbeattimer=time.time()
            cmd=0x14fffc20
            DATA=[0]
            DLC=len(DATA)
            canprogrammer.CAN_ProgrammerSendCmd(CMD=cmd,data=DATA,dlc=DLC)
        msg=canprogrammer.CAN_ProgrammerPollForData(1)
        try:
            if  msg.arbitration_id == 0x69:
                mstr += msg.data.decode('utf-8') 
                if '\n' in mstr:
                    f=open(filepath,'a')
                    outstr=f"|{time.ctime(time.time())}|{mstr.encode('utf-16')}|\n"
                    f.write(outstr)
                    f.close()
                    print(outstr)
                    mstr = ""
            else:
                print("rx : {}".format(msg))
        except Exception as e:
            # print("exception",e)
            pass
    return

print("Entering CAN programmer...")
parser = argparse.ArgumentParser(description='CAN programmer')

parser.add_argument('-a', action="store", dest='ADDR')
parser.add_argument('-f', action="store", dest='FILEPATH')
parser.add_argument('-p', action="store", dest='COMPORT')
parser.add_argument('-m', action="store", dest='MODE')
parser.add_argument('-v', action="store", dest='DEBUGLEVEL')
args = parser.parse_args()
if args.FILEPATH== None or args.COMPORT == None or args.MODE==None:
    print("Please specify arguments")
    sys.exit()
print("args:",args.ADDR, args.FILEPATH, args.COMPORT,args.MODE,args.DEBUGLEVEL)
if(args.MODE=='FLASH'):
    if args.ADDR==None:
        print("Please specify arguments")
        sys.exit()
    FLASH_mode(args.ADDR, args.FILEPATH, args.COMPORT,args.DEBUGLEVEL)
elif args.MODE=='DEBUGLOGS':
    DEBUGLOGS_mode(args.COMPORT,args.FILEPATH)
