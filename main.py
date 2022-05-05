from CAN_ProgrammerAPI import CAN_Programmer
import CAN_Macro

if __name__=='__main__':
    canprogrammer=CAN_Programmer(channel='COM10',debug=False)
    # if canprogrammer.CAN_ProgrammerChangeBaudRate(CAN_ProgrammerBootloaderCMD.DATA_BAUDRATE_500_0):
    #     print("Baud Rate Changed")
    # else:
    #     print('BaudRate Change failed. Exiting Now...')
    #     exit()
    # if canprogrammer.CAN_ProgrammerInitiliseOTAReequest(CMD=CAN_Macro.CMD_OTA_REQUEST,DATA=CAN_Macro.DATA_OTA_REQUEST):
    #     print("OTA Request accepted.")
    # else:
    #     print('OTA Request Failed.Exiting Now...')
    #     exit()
    # if canprogrammer.CAN_ProgrammerChangeBaudRate(CAN_ProgrammerBootloaderCMD.DATA_BAUDRATE_125_0):
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
    # # if canprogrammer.CAN_ProgrammerFullChipErase():
    # #     print("Full CHIP Erase succesful")
    # if canprogrammer.CAN_ProgrammerSectorErase(addr=0x8000000,no_of_sectors=19):
    #     print("Sector Erase succesful")
    # if canprogrammer.CAN_ProgrammerWriteMemory("C:/GURU/vecmocon/VIM/ivec_bootloader-application/ivec-bootloader/build/ivec-bootloader.bin",addr=0x8000000):
    #     print("Flashing Succesful")
    #     # if canprogrammer.CAN_ProgrammerJumpToAddress(addr=0x08000000):
    #     #     print("Jumping Succesful")
    # else:
    #     print('Flashing Failed')
    # with open('C:/GURU/vecmocon/VIM/ivec-application/Scripts/CAN_Programmer/write.bin','wb') as writefile:
    #     writefile.write(canprogrammer.CAN_ProgrammerReadMemory(addr=0x8000000,no_of_bytes=38636))
    #     print("file written")

    while True:
        msg=canprogrammer.CAN_ProgrammerPollForData(1)
        if msg:
            print(f"ID:{hex(msg.arbitration_id)}    DATA:{msg.data} DLC:{msg.dlc}")
        
