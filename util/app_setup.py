from PyQt5 import QtWidgets, QtGui
from UI.CAN_ProgrammerUI import Ui_MainWindow
import time
import sys,serial.tools.list_ports
from src.CAN_ProgrammerAPI import CAN_Programmer
from util.CAN_Macro import CMD_OTA_REQUEST,DATA_OTA_REQUEST

PASS=101
FAIL=102
canprogrammer=CAN_Programmer(channel='COM10',debug=1)


MainUI = Ui_MainWindow()
def APP_ShowLogs(log:str):
    MainUI.Logs_op.append(f"{time.time()}: {log}")
    return

def APP_UpdateStatus(val:int):
    if val==0:
        MainUI.CmdStatus_bar.setStyleSheet("QProgressBar::chunk "
                          "{"
                          "background-color: yellow;"
                          "}")
    elif val==PASS:
        MainUI.CmdStatus_bar.setStyleSheet("QProgressBar::chunk "
                          "{"
                          "background-color: green;"
                          "}")
        val=100
    elif val==FAIL:
        MainUI.CmdStatus_bar.setStyleSheet("QProgressBar::chunk "
                          "{"
                          "background-color: red;"
                          "}")
        val=100
    MainUI.CmdStatus_bar.setValue(val)
    
    return

def BUTTON_RequestOta():
    APP_ShowLogs("OTA Request Initated")
    APP_UpdateStatus(0)
    canprogrammer.CAN_ProgrammerSendCmd(CMD_OTA_REQUEST,data=[DATA_OTA_REQUEST])
    

    return 

def BUTTON_RequestResetUI():
    return 

def BUTTON_RequestResetStatus():
    return 

def BUTTON_RequestPid():
    return

def BUTTON_RequestSync():
    return

def BUTTON_RequestFlash():
    return 

def BUTTON_RequestErase():
    return 

def BUTTON_RequestChooseFile():
    return 

def BUTTON_RequestSetComPort():
    port=MainUI.PORT_list.currentText()
    APP_ShowLogs(f"Connecting to port:{port}")
    APP_UpdateStatus(0)
    retCode=canprogrammer.CAN_ProgrammerSetPort(port)
    if retCode:
        APP_UpdateStatus(PASS)
        APP_ShowLogs(f"Connection to port:{port} succesful")
    else:
        APP_UpdateStatus(FAIL)
        APP_ShowLogs(f"Connection to port:{port} failed")
    
    return 


def APP_SetupUI(MainUI:Ui_MainWindow):
    MainUI.RequestOTA_btn.clicked.connect(BUTTON_RequestOta)
    MainUI.RequestPID_btn.clicked.connect(BUTTON_RequestPid)
    MainUI.RESET_btn.clicked.connect(BUTTON_RequestResetUI)
    MainUI.SYNC_btn.clicked.connect(BUTTON_RequestSync)
    MainUI.Erase_btn.clicked.connect(BUTTON_RequestErase)
    MainUI.Flash_btn.clicked.connect(BUTTON_RequestFlash)
    MainUI.ResetStatus_btn.clicked.connect(BUTTON_RequestResetStatus)
    MainUI.ChooseFile_btn.clicked.connect(BUTTON_RequestChooseFile)
    return

def CAN_ProgrammerSetupAndRunUI(app_setup=False):
    if app_setup:
        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()
        MainUI.setupUi(MainWindow=MainWindow)
        ports_list=[]
        for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
            ports_list.append(port)
        MainUI.PORT_list.addItems(ports_list)
        MainWindow.show()
        MainUI.Setport_btn.clicked.connect(BUTTON_RequestSetComPort)
        APP_SetupUI(MainUI)
        

        sys.exit(app.exec_())