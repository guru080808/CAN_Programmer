from PyQt5 import QtWidgets, QtGui
import threading
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from UI.CAN_ProgrammerUI import Ui_MainWindow
import time,os
import sys,serial.tools.list_ports
from src.CAN_ProgrammerAPI import CAN_Programmer
from util.CAN_Macro import CMD_OTA_REQUEST,DATA_OTA_REQUEST,DATA_BAUDRATE_125_0,DATA_BAUDRATE_500_0,PASS,FAIL,DATA_BAUDRATE_250_0,CMD_ACK




class APP_Setup:
    def __init__(self,AppEnable=False) -> None:
        self.canprogrammer=CAN_Programmer(APP_Object=self,APP_Enable=AppEnable, debug_level=3)
        self.MainUI = Ui_MainWindow()
        self.setup()
        self.App_Run()

    def App_Run(self):
        self.MainWindow.show()
        sys.exit(self.app.exec_())

    def setup(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.MainUI.setupUi(MainWindow=self.MainWindow)
        ports_list=[]
        for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
            ports_list.append(port)
        self.MainUI.verbosity_box.addItems([str(i) for i in range(4)])
        self.MainUI.Bitrate_box.addItems([str(i) for i in range(1,5)])
        self.MainUI.pageno_box.addItems([str(i) for i in range(0,256)])
        self.MainUI.PORT_list.addItems(ports_list)
        self.MainUI.Setport_btn.clicked.connect(self.BUTTON_RequestSetComPort)
        self.MainUI.RequestOTA_btn.clicked.connect(self.BUTTON_RequestOta)
        self.MainUI.SYNC_btn.clicked.connect(self.BUTTON_RequestSync)
        self.MainUI.Erase_btn.clicked.connect(self.BUTTON_RequestErase)
        self.MainUI.Flash_btn.clicked.connect(self.BUTTON_RequestFlash)
        self.MainUI.ChooseFile_btn.clicked.connect(self.BUTTON_RequestChooseFile)
        self.MainUI.SetBitrate_btn.clicked.connect(self.BUTTON_RequestSetBitRate)
        self.MainUI.verbosity_box.currentTextChanged.connect(self.BOX_ChangeVerbosityLvl)
        self.MainUI.ClearLogs_btn.clicked.connect(self.BUTTON_RequestClearLogs)
        return

    def APP_ShowLogs(self,log:str):
        self.MainUI.Logs_op.append(f"{time.time()}: {log}")
        return

    def APP_SetProgress(self,val:int):
        val_to_update=val
        if val==PASS:
            val_to_update=100
            self.MainUI.progressBar.setStyleSheet("QProgressBar::chunk "
                  "{"
                    "background-color: green;"
                  "}")
        elif val==FAIL:
            val_to_update=100
            self.MainUI.progressBar.setStyleSheet("QProgressBar::chunk "
                  "{"
                    "background-color: red;"
                  "}")
        self.MainUI.progressBar.setValue(val_to_update)
        return

    def BOX_ChangeVerbosityLvl(self):
        self.canprogrammer.CAN_ProgrammerSetVerbosityLvl(int(self.MainUI.verbosity_box.currentText()))
        return

    def BUTTON_RequestClearLogs(self):
        self.MainUI.Logs_op.clear()
        return
    def BUTTON_RequestOta(self):
        self.APP_ShowLogs("OTA Request Initated")
        whiletimeout=time.time()
        if self.canprogrammer.CAN_ProgrammerChangeBaudRate(BAUDRATE=DATA_BAUDRATE_250_0):
            while time.time()-whiletimeout<10:
                if self.canprogrammer.CAN_ProgrammerInitiliseOTAReequest(CMD=CMD_ACK,DATA=DATA_OTA_REQUEST):
                    # self.canprogrammer.CAN_ProgrammerChangeBaudRate(BAUDRATE=DATA_BAUDRATE_125_0)
                    break
                time.sleep(0.100)


        return 

    def BUTTON_RequestSync(self):
        if self.canprogrammer.CAN_ProgrammerInitiliseBootloader():
            self.MainUI.BootVer_op.clear()
            self.MainUI.PID_op.clear()
            self.MainUI.PID_op.append(self.canprogrammer.CAN_ProgrammerGetID())
            self.MainUI.BootVer_op.append(self.canprogrammer.CAN_ProgrammerGetVersion())
        return

    def BUTTON_RequestFlash(self):
        ADDR_temp='0' if self.MainUI.Address_ip.toPlainText() =='' else self.MainUI.Address_ip.toPlainText()
        FILENAME=self.MainUI.ChooseFile_ip.toPlainText()
        if '0x' in ADDR_temp:
            ADDR=int(ADDR_temp,16)
        else:
            ADDR=int(ADDR_temp)
        
        addr_range=range(0x08000000,0x0807FFFF+1)
        if ADDR not in addr_range:
            self.APP_ShowLogs(f"Address:{hex(ADDR)} is not in range {hex(addr_range[0])}-{hex(addr_range[-1])}")
            return
        if not os.path.isfile(FILENAME):
            self.APP_ShowLogs(f"Filename:{FILENAME} not found")
            return
        FILESIZE=os.path.getsize(FILENAME)
        PagesToClear=int((FILESIZE)/2048) + (1 if (FILESIZE)%2048!=0 else 0)
        flashTime=time.time()
        if 1 or self.canprogrammer.CAN_ProgrammerSectorErase(addr=ADDR,no_of_sectors= PagesToClear):
            self.APP_ShowLogs(f"{hex(ADDR)}-{hex(ADDR+FILESIZE)} Erased. Flashing Now...")
            if self.canprogrammer.CAN_ProgrammerWriteMemory(filepath=FILENAME,addr=ADDR):
                self.APP_ShowLogs(f"Succesfully flashed...")
                self.canprogrammer.CAN_ProgrammerJumpToAddress(0x08007000)
                exit()
                if self.MainUI.verify_chkbox.isChecked():
                    self.APP_ShowLogs(f"Verifying Now...")
                    READ_BUF=self.canprogrammer.CAN_ProgrammerReadMemory(addr=ADDR,no_of_bytes=FILESIZE)
                    if READ_BUF:
                        with open(FILENAME,'rb') as binfile:
                            COMPARE_BUF=binfile.read()
                            if COMPARE_BUF==READ_BUF:
                                self.APP_ShowLogs(f"Verification Passed")
                                self.APP_SetProgress(PASS)
                            else:
                                self.APP_ShowLogs(f"Verification Failed.    Input file size:{len(COMPARE_BUF)}  Flash Read File Size:{len(READ_BUF)}")
                                self.APP_SetProgress(FAIL)
                    else:
                        self.APP_ShowLogs(f"Verification failed...Unable to read Flash")
                        self.APP_SetProgress(FAIL)
                else:
                    self.APP_SetProgress(PASS)

            else:
                self.APP_ShowLogs(f"Flashing failed...")
                self.APP_SetProgress(FAIL)
        else:
            self.APP_ShowLogs(f"Unable to Erase")
            self.APP_SetProgress(FAIL)
        flashTime=time.time()-flashTime
        self.APP_ShowLogs(f"Time took to flash:{flashTime}")         
        return 

    def BUTTON_RequestErase(self):
        if self.MainUI.MassErase_chkbox.isChecked():
            self.canprogrammer.CAN_ProgrammerFullChipErase()
        else:
            page_no=int(self.MainUI.pageno_box.currentText())
            ADDR=int(0x08000000)+(page_no*2048)
            print("Erasing page no:",page_no, hex(ADDR))
            if self.canprogrammer.CAN_ProgrammerSectorErase(addr=ADDR,no_of_sectors= 1):
                self.APP_ShowLogs(f"{hex(ADDR)} Erased.")

        return 

    def BUTTON_RequestChooseFile(self):
        file_dialog = QtWidgets.QFileDialog(self.MainUI.centralwidget)
        self.MainUI.ChooseFile_ip.clear()
        fileName, _ = file_dialog.getOpenFileName()
        if '.bin' in fileName:
            self.MainUI.ChooseFile_ip.append(fileName)

        return 

    def BUTTON_RequestSetComPort(self):
        port=self.MainUI.PORT_list.currentText()
        self.APP_ShowLogs(f"Connecting to port:{port}")
        retCode=self.canprogrammer.CAN_ProgrammerSetPort(port)
        if retCode:
            self.APP_ShowLogs(f"Connection to port:{port} succesful")
        else:
            self.APP_ShowLogs(f"Connection to port:{port} failed")
        
        # if self.canprogrammer.CAN_ProgrammerInitiliseOTAReequest(CMD=CMD_OTA_REQUEST,DATA=DATA_OTA_REQUEST):
        self.canprogrammer.CAN_ProgrammerChangeBaudRate(BAUDRATE=DATA_BAUDRATE_250_0)
        #         if self.canprogrammer.CAN_ProgrammerInitiliseBootloader():
        #             self.MainUI.BootVer_op.clear()
        #             self.MainUI.PID_op.clear()
        #             self.MainUI.PID_op.append(self.canprogrammer.CAN_ProgrammerGetID())
        #             self.MainUI.BootVer_op.append(self.canprogrammer.CAN_ProgrammerGetVersion())
        return 

    def BUTTON_RequestSetBitRate(self):
        bitrate=int(self.MainUI.Bitrate_box.currentText())
        self.canprogrammer.CAN_ProgrammerSetBaudRate(bitrate)
        return

