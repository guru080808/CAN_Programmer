
from src.CAN_ProgrammerAPI import CAN_Programmer
from UI.CAN_ProgrammerUI import Ui_MainWindow
from util import CAN_Macro
from UI.app_setup import APP_Setup
from PyQt5 import QtWidgets, QtGui
import sys
import time
import numpy as np
import msvcrt
import cantools
from canlib import kvadblib
import random
if __name__ == '__main__':
    # APP=APP_Setup(True)

    canprogrammer = CAN_Programmer(debug_level=3)
    # canprog
    canprogrammer.CAN_ProgrammerSetPort('COM226')
    if canprogrammer.CAN_ProgrammerChangeBaudRate(CAN_Macro.DATA_BAUDRATE_500_0):
        print("Baud Rate Changed")
    else:
        print('BaudRate Change failed. Exiting Now...')
        exit()
    # if canprogrammer.CAN_ProgrammerChangeBaudRateType2(CAN_Macro.DATA_BAUDRATE_250_0):
    #     print("Baud Rate Changed")
    # else:
    #     print('BaudRate Change failed. Exiting Now...')
    #     exit()

    def relay_action(relay_no, action):
        IOT_PIN_MAPPING = {
            "1": [2, 1],
            "2": [2, 0],
            "3": [1, 7],
            "4": [1, 6],
            "5": [1, 5],
            "6": [1, 4],
            "7": [1, 3],
            "8": [1, 2],
            "9": [1, 1],
            "10": [1, 0]
        }
        idx = relay_no
        import can
        port = IOT_PIN_MAPPING[str(idx)][0]
        pin = IOT_PIN_MAPPING[str(idx)][1]
        TURN_ON = 1
        TURN_OFF = 0
        send_action = TURN_ON if action else TURN_OFF
        ACK = 0x79
        ack_rcvd = 0

        try:
            can_packet = [2, ACK, port, pin, send_action]
            bit_change = [1, ACK, 12]
            msg = can.Message(arbitration_id=0x33, dlc=5, data=can_packet)
            canprogrammer.CAN_ProgrammerSendCmd(0x33, can_packet, dlc=5)
            recv_msg = canprogrammer.CAN_ProgrammerPollForData(1)
            if recv_msg:
                # print(recv_msg)
                if recv_msg.arbitration_id == 0x33 and recv_msg.data[0] == ACK:
                    ack_rcvd = 1
                    print("ack recvd")
        except Exception as e:
            print("Exception:", e)
        pass
        return ack_rcvd
    t_start1 = time.time()
    # t_start2=time.time()
    i = 0
    # for i in range(1,11):
    #     relay_action(i,0)
    # time.sleep(2)
    # for i in range(1,11):
    #     relay_action(i,1)
    # relay=1
    # relay_action(relay,1)
    TEC_IDs=[]
    db = cantools.database.load_file("C:/Users/gurpa/Downloads/Tec_CAN_13Mar24_ByteWise.dbc")    
    with kvadblib.Dbc( filename="C:/Users/gurpa/Downloads/Tec_CAN_13Mar24_ByteWise.dbc") as kdbc:
        kstr = ""
        global keys
        global can_data
        kstr += "CPU_Time"
        for message in kdbc:
            TEC_IDs.append((message.id))
    while True:
        # if time.time()-t_start2 > 40 :
        #     relay_action(relay,0)
        #     relay=relay+1
        #     relay_action(relay,1)

        #     t_start2=time.time()
        if time.time()-t_start1 >3 and 1:
            for can_id in TEC_IDs:
                can_packet=[random.randint(0,255) for i in range(8)]
                canprogrammer.CAN_ProgrammerSendCmd(can_id, data=can_packet, dlc=8)
                time.sleep(0.050)
            t_start1=time.time()
            continue
            daly_soc_can_id = (0x18 << 24) | (
                0x90 << 16) | (0x40 << 8) | (0x01 << 0)
            soc = 50 * 10
            txdata = [0, 0, 0, 0, 0, 0, 0, 0]
            txdata[7] = soc & 0xff
            txdata[6] = (soc >> 8) & 0xff

            imei_data = []
            imei_data.append(0x00FDC5 & 0xff)
            imei_data.append((0x00FDC5 >> 8) & 0xff)
            imei_data.append((0x00FDC5 >> 16) & 0xff)
            imei_id = 0x1cea6969

            cmd_id_usb = 0x33
            cmd_id_ex = 0x34
            cmd_gpio_write = [2, 0x79, 1, 11, 0, 0, 0, 0xb5]
            cmd_gpio_read = [3, 0x79, 1, 11, 0, 0, 0, 0xb5]
            cmd_bootloader = [5, 0x79, 0, 0, 0, 0, 0, 0xb5]
            cmd_bitrate_change_usb = [1, 0x79, CAN_Macro.DATA_BAUDRATE_500_0]

            can_id = daly_soc_can_id
            can_packet = txdata
            # continue
            def h():
                if canprogrammer.CAN_ProgrammerChangeBaudRate(CAN_Macro.DATA_BAUDRATE_250_0):
                    print("Baud Rate Changed")
                else:
                    print('BaudRate Change failed. Exiting Now...')
                return 0
        
            print("Sending message:", hex(can_id))
            # for i in range(0x18ff0240,0x18ff0240):
            canprogrammer.CAN_ProgrammerSendCmd(can_id, data=can_packet, dlc=8)
                # time.sleep(0.010)
            # exit()
            # while True:
            #     time.sleep(0.1)
            #     if canprogrammer.CAN_ProgrammerInitiliseOTAReequest(0x32,1):
            #         break
            while 0 and time.time()-t_start1<50:
                msg = canprogrammer.CAN_ProgrammerPollForData(0.001)
                if msg and msg.arbitration_id == 0x6934 or 0:
                    print("Starting bootprocess")
                    # if canprogrammer.CAN_ProgrammerChangeBaudRate(CAN_Macro.DATA_BAUDRATE_25_0):
                    #     print("Baud Rate Changed")
                    # else:
                    #     print('BaudRate Change failed. Exiting Now...')

                    if canprogrammer.CAN_ProgrammerInitiliseBootloader(0.3):
                        print(
                            "CAN Bootloader Initilised. Device is ready to recive commands")
                    else:
                        print('Bootloader Init Request Failed. Exiting Now...')
                        exit(h())

                    print("DeviceID:", canprogrammer.CAN_ProgrammerGetID())
                    print("BootloaderVersion:",
                            canprogrammer.CAN_ProgrammerGetVersion())
                    canprogrammer.CAN_ProgrammerJumpToAddress(0x08007000)
                    exit(h())
                t_start1=time.time()
            
            # exit()
            t_start1=time.time()
        msg = canprogrammer.CAN_ProgrammerPollForData(0.001)
        # try:

        #     if  msg.arbitration_id == 0x69:
        #         mstr += msg.data.decode('utf-8')
        #         if '\n' in mstr:
        #             print(mstr)
        #             mstr = ""
        #     else:
        #         print("rx : {}".format(msg))
        # except Exception as e:
        #     print("exception",e)
        #     pass
        # print(msg_rcvd,msg_sent)
        # if msvcrt.kbhit():
        #     msg_rcvd=0
        if msg:
            # print(time.ctime(time.time()),': ',hex(msg.arbitration_id>>16 &0xff) ,' ',hex(msg.arbitration_id &0xff))
            print(
                f"ID:{hex(msg.arbitration_id)}    DATA:{msg.data},{[i for i in msg.data]} DLC:{msg.dlc}")
            if (msg.arbitration_id == 0x1cebff69 or msg.arbitration_id == 0x1cecff69) and msg.data[0] == 4:
                print("dID rcvd:", int.from_bytes(
                    msg.data[1:], byteorder='little'))
            if msg.arbitration_id == 0x34:
                print("Cmd Id rcvd:", msg.data)
            if msg.arbitration_id == 0xCFFC169:
                print("Sending ack")
                canprogrammer.CAN_ProgrammerSendCmd(
                    0xCFFC123, data=DATA, dlc=8)
