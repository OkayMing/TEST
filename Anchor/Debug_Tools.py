#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import asyncio
import sys
import io
import os
import struct
import time
import base64
import socket
import re
import socket
from PyQt5.QtWidgets import QPushButton,QGridLayout,QCheckBox,QSpacerItem,QTextBrowser,QLabel,QSizePolicy,QApplication,QLineEdit,QWidget,QTextEdit,QVBoxLayout,QHBoxLayout,QComboBox,QFileDialog,QProgressBar
from PyQt5.QtCore import Qt,QThread,pyqtSignal,QSize,QRect
from PyQt5.QtGui import QIcon,QTextCursor
from Restoreip_Tool import Resip_Tool
from Link_Tools import get_port_list,open_port,uart_read


from LOGO_png import LOGO_png as logo

__version__ = "V0.0.1"


class Debug_Thread(QThread):
    stateSignal = pyqtSignal(int)
    textSignal = pyqtSignal(str)
    def __init__(self, _port_name, baudRate=115200):
        super(Debug_Thread, self).__init__()

        self._port_name = _port_name
        self._baudRate = baudRate
        self._stop = False

    def my_stop(self):
        self._stop = True
        self.textSignal.emit("正在关闭串口！" + '\r\n')

    def send(self, data):
        if (self._port != None):
            self._port.write(data)
        else:
            self.textSignal.emit("请先打开串口！" + '\r\n')

    def run(self):
        try:
            self._port = open_port(self._port_name)
            self._port.baudrate = int(self._baudRate)
        except Exception:
            self.textSignal.emit("串口" + self._port_name + "打开失败，请检查串口是否被占用！~" + '\r\n')
            self.stateSignal.emit(1)
            return

        self.stateSignal.emit(0)
        self.textSignal.emit("打开串口成功！！！" + '\r\n')

        self._port.setRTS(False)
        self._port.setDTR(False)

        while(True):
            if self._stop :
                break

            self.result = uart_read(self._port)
            if(len(self.result) > 1): 
                self.textSignal.emit(self.result)
            time.sleep(0.1)

        self._port.close()
        self._port = None

        self.stateSignal.emit(1)


class Debug_UDP_Thread(QThread):
    udpstateSignal = pyqtSignal(int)
    udptextSignal = pyqtSignal(str)
    def __init__(self,_ip_port,BUFSIZE = 1024):
        super(Debug_UDP_Thread, self).__init__()

        self._ip_port = _ip_port
        self._BUFSIZE = BUFSIZE
        self._stop = False
        self.udp_flag = 0


    def my_stop(self):
        self._stop = True
        self.udptextSignal.emit("正在关闭连接！" + '\r\n')


    def send(self,data):
        if self.udp_flag == 1:
            self.client.sendto(data,(self._ip_port,5000))
        else:
            self.udptextSignal.emit('请先进行设备连接！' + '\r\n')

    def run(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client.bind(('',5000))
            self.udp_flag = 1
        except Exception:
            self.udptextSignal.emit('网口连接失败，请检查' + '\r\n')
            self.udpstateSignal.emit(1)
            return

        self.udpstateSignal.emit(0)
        self.udptextSignal.emit('网口连接成功！' + '\r\n')

        while (True):
            if self._stop == True:
                break
            try:
                self.client.setblocking(0)
                self.data, server_addr = self.client.recvfrom(int(self._BUFSIZE))
            except BlockingIOError:
                self.data = ''
            if len(self.data) > 1:
                self.data = self.data.decode('utf-8')
                self.udptextSignal.emit(self.data)
            time.sleep(0.1)

        self.client.close()
        self.client = None

        self.udpstateSignal.emit(1)


class Debug_Tools(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.mThread = None
        self.uThread = None
        self.connect_code = 0
        Resip_win = Resip_Tool()
        self.setWindowTitle("ESWIN UWB配置工具 " + __version__)

        # if not os.path.exists('aithinker.png'):
        #     tmp = open('aithinker.png', 'wb+')
        #     tmp.write(base64.b64decode(logo))
        #     tmp.close()

        self.setStyleSheet("QPushButton:hover{background-color:rgb(3, 54, 129)}QPushButton{background-color:rgb(7, 71, 166)}\n"
"QPushButton{font-family:\'宋体\';font-size:15px;color:white;}")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_9 = QHBoxLayout()
        self.connect_mode = QPushButton('切换串口连接')
        self.connect_mode.setMinimumSize(QSize(117,31))
        self.horizontalLayout_9.addWidget(self.connect_mode)
        #网口连接选项
        self.widget = QWidget()
        self.widget.setObjectName("widget")
        self.widget.setMinimumSize(QSize(677,53))
        self.widget.setMaximumSize(QSize(16777215,53))
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Anchor_IP = QLabel(self.widget)
        self.Anchor_IP.setMinimumSize(QSize(0, 31))
        self.Anchor_IP.setMaximumSize(QSize(80, 16777215))
        self.Anchor_IP.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.Anchor_IP.setObjectName("label_17")
        self.horizontalLayout_2.addWidget(self.Anchor_IP)
        self.textEdit_18 = QTextEdit(self.widget)
        self.textEdit_18.setMaximumSize(QSize(150, 31))
        self.textEdit_18.setPlaceholderText("")
        self.textEdit_18.setObjectName("textEdit_18")
        self.horizontalLayout_2.addWidget(self.textEdit_18)
        self.concect_dev = QPushButton(self.widget)
        self.concect_dev.setObjectName("concect_dev")
        self.horizontalLayout_2.addWidget(self.concect_dev)
        self.query_info = QPushButton(self.widget)
        self.query_info.setObjectName("query_info")
        self.horizontalLayout_2.addWidget(self.query_info)
        #串口连接选项
        self.widget_2 = QWidget()
        self.widget_2.setMinimumSize(QSize(677,53))
        self.widget_2.setMaximumSize(QSize(16777215,53))
        self.horizontalLayout_10 = QHBoxLayout(self.widget_2)
        self.cb_serial = QComboBox(self.widget_2)
        self.cb_serial.setEnabled(True)
        self.cb_serial.setMinimumSize(QSize(0, 28))
        self.cb_serial.setStyleSheet("")
        self.cb_serial.setObjectName("cb_serial")
        self.cb_serial.addItem("选择串口")
        self.cb_serial.addItem("comb1")
        self.horizontalLayout_10.addWidget(self.cb_serial)
        #去除波特率选择框
        '''self.cb_baudRate = QComboBox(self.widget_2)
        self.cb_baudRate.setMinimumSize(QSize(0, 28))
        self.cb_baudRate.setStyleSheet("")
        self.cb_baudRate.setObjectName("cb_baudRate")
        self.cb_baudRate.addItem("波特率")
        self.cb_baudRate.addItem("9600")
        self.cb_baudRate.addItem("115200")
        self.cb_baudRate.addItem("500000")
        self.cb_baudRate.addItem("921600")
        self.horizontalLayout_10.addWidget(self.cb_baudRate)'''
        self.refresh_port = QPushButton(self.widget_2)
        self.refresh_port.setText("刷新串口")
        self.refresh_port.setStyleSheet("QPushButton:hover{background-color:rgb(3, 54, 129)}QPushButton{background-color:rgb(7, 71, 166)}\n"
"QPushButton{font-family:\'宋体\';font-size:15px;color:white;}")
        self.refresh_port.setObjectName("refresh_port")
        self.horizontalLayout_10.addWidget(self.refresh_port)
        self.open_port = QPushButton(self.widget_2)
        self.open_port.setText("打开串口")
        self.open_port.setStyleSheet("QPushButton:hover{background-color:rgb(3, 54, 129)}QPushButton{background-color:rgb(7, 71, 166)}\n"
"QPushButton{font-family:\'宋体\';font-size:15px;color:white;}")
        self.open_port.setObjectName("open_port")
        self.horizontalLayout_10.addWidget(self.open_port)
        self.query_info2 = QPushButton(self.widget_2)
        self.query_info2.setText("信息查询")
        self.open_port.setStyleSheet("QPushButton:hover{background-color:rgb(3, 54, 129)}QPushButton{background-color:rgb(7, 71, 166)}\n"
"QPushButton{font-family:\'宋体\';font-size:15px;color:white;}")
        self.open_port.setObjectName("query_info2")
        self.horizontalLayout_10.addWidget(self.query_info2)

        self.horizontalLayout_9.addWidget(self.widget)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_18 = QLabel()
        self.label_18.setMinimumSize(QSize(117, 0))
        self.label_18.setMaximumSize(QSize(0, 16777215))
        self.label_18.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_18.setObjectName("label_18")
        self.horizontalLayout.addWidget(self.label_18)
        self.comboBox_2 = QComboBox()
        self.comboBox_2.setMaximumSize(QSize(150, 31))
        self.comboBox_2.setMinimumSize(QSize(150, 31))
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("测距模式")
        self.comboBox_2.addItem("定位模式")
        self.horizontalLayout.addWidget(self.comboBox_2)
        self.change_mode = QPushButton()
        self.change_mode.setObjectName("change_mode")
        self.horizontalLayout.addWidget(self.change_mode)
        self.horizontalLayout_8.addLayout(self.horizontalLayout)
        spacerItem1 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem1)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_19 = QLabel()
        self.label_19.setMinimumSize(QSize(117, 0))
        self.label_19.setMaximumSize(QSize(117, 16777215))
        self.label_19.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_19.setObjectName("label_19")
        self.horizontalLayout_3.addWidget(self.label_19)
        self.comboBox = QComboBox()
        self.comboBox.setMinimumSize(QSize(250, 31))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("主基站")
        self.comboBox.addItem("从基站")
        self.comboBox.addItem("主从基站")
        self.horizontalLayout_3.addWidget(self.comboBox)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_16 = QLabel()
        self.label_16.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_16.setObjectName("label_16")
        self.gridLayout.addWidget(self.label_16, 0, 0, 1, 1)
        self.Anchor_Macid_Edit = QTextEdit()
        self.Anchor_Macid_Edit.setMaximumSize(QSize(16777215, 31))
        self.Anchor_Macid_Edit.setObjectName("Anchor_Macid_Edit")
        self.Anchor_Macid_Edit.setReadOnly(True)
        self.gridLayout.addWidget(self.Anchor_Macid_Edit, 0, 1, 1, 1)
        self.label_27 = QLabel()
        self.label_27.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_27.setObjectName("label_27")
        self.gridLayout.addWidget(self.label_27, 0, 2, 1, 1)
        self.Eng_IP_Edit = QLineEdit()
        self.Eng_IP_Edit.setMaximumSize(QSize(16777215, 31))
        self.Eng_IP_Edit.setObjectName("Eng_IP_Edit")
        self.Eng_IP_Edit.setInputMask('000.000.000.000')
        self.gridLayout.addWidget(self.Eng_IP_Edit, 0, 3, 1, 1)
        self.label_20 = QLabel()
        self.label_20.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_20.setObjectName("label_20")
        self.gridLayout.addWidget(self.label_20, 1, 0, 1, 1)
        self.Seat_Edit = QTextEdit()
        self.Seat_Edit.setMaximumSize(QSize(16777215, 31))
        self.Seat_Edit.setObjectName("Seat_Edit")
        self.gridLayout.addWidget(self.Seat_Edit, 1, 1, 1, 1)
        self.label_24 = QLabel()
        self.label_24.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_24.setObjectName("label_24")
        self.gridLayout.addWidget(self.label_24, 1, 2, 1, 1)
        self.Clock_Num_Edit = QTextEdit()
        self.Clock_Num_Edit.setMaximumSize(QSize(16777215, 31))
        self.Clock_Num_Edit.setObjectName("Clock_Num_Edit")
        self.gridLayout.addWidget(self.Clock_Num_Edit, 1, 3, 1, 1)
        self.label_22 = QLabel()
        self.label_22.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_22.setObjectName("label_22")
        self.gridLayout.addWidget(self.label_22, 2, 0, 1, 1)
        self.MClock_ID_Edit = QTextEdit()
        self.MClock_ID_Edit.setMaximumSize(QSize(16777215, 31))
        self.MClock_ID_Edit.setObjectName("MClock_ID_Edit")
        self.gridLayout.addWidget(self.MClock_ID_Edit, 2, 1, 1, 1)
        self.label_23 = QLabel()
        self.label_23.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_23.setObjectName("label_23")
        self.gridLayout.addWidget(self.label_23, 2, 2, 1, 1)
        self.SMClock_ID_Edit = QTextEdit()
        self.SMClock_ID_Edit.setMaximumSize(QSize(16777215, 31))
        self.SMClock_ID_Edit.setObjectName("SMClock_ID_Edit")
        self.gridLayout.addWidget(self.SMClock_ID_Edit, 2, 3, 1, 1)
        self.label_26 = QLabel()
        self.label_26.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_26.setObjectName("label_26")
        self.gridLayout.addWidget(self.label_26, 3, 0, 1, 1)
        self.SClock_ID_Edit1 = QTextEdit()
        self.SClock_ID_Edit1.setMaximumSize(QSize(16777215, 31))
        self.SClock_ID_Edit1.setObjectName("SClock_ID_Edit1")
        self.gridLayout.addWidget(self.SClock_ID_Edit1, 3, 1, 1, 1)
        self.label_28 = QLabel()
        self.label_28.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_28.setObjectName("label_28")
        self.gridLayout.addWidget(self.label_28, 3, 2, 1, 1)
        self.SClock_ID_Edit2 = QTextEdit()
        self.SClock_ID_Edit2.setMaximumSize(QSize(16777215, 31))
        self.SClock_ID_Edit2.setObjectName("SClock_ID_Edit2")
        self.gridLayout.addWidget(self.SClock_ID_Edit2, 3, 3, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem2)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.log_ctl = QCheckBox()
        self.log_ctl.setObjectName("log_ctl")
        self.log_ctl.setEnabled(False)
        self.horizontalLayout_6.addWidget(self.log_ctl)
        self.submit = QPushButton()
        self.submit.setObjectName("submit")
        self.horizontalLayout_6.addWidget(self.submit)
        self.horizontalLayout_7.addLayout(self.horizontalLayout_6)
        spacerItem3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem4)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.reboot = QPushButton()
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reboot.sizePolicy().hasHeightForWidth())
        self.reboot.setSizePolicy(sizePolicy)
        self.reboot.setObjectName("reboot")
        self.horizontalLayout_4.addWidget(self.reboot)
        self.resip = QPushButton()
        self.resip.setObjectName("resip")
        self.horizontalLayout_4.addWidget(self.resip)
        self.reset = QPushButton()
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reset.sizePolicy().hasHeightForWidth())
        self.reset.setSizePolicy(sizePolicy)
        self.reset.setObjectName("reset")
        self.horizontalLayout_4.addWidget(self.reset)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_4)
        spacerItem5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem5)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.textBrowser = QTextBrowser()
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.Anchor_IP.setText("基站IP")
        self.textEdit_18.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'微软雅黑\',\'sans-serif\'; font-size:8pt;\">192.168.1.120</span></p></body></html>")
        self.concect_dev.setText("连接设备")
        self.query_info.setText("信息查询")
        self.label_18.setText("工作场景")
        self.change_mode.setText("场景切换")
        self.label_19.setText("基站DEV_MODE")
        self.label_16.setText("MAC ID")
        self.Anchor_Macid_Edit.setPlaceholderText("调试自动查询")
        self.label_27.setText("定位上报的IP地址")
        self.Eng_IP_Edit.setPlaceholderText("部署手动输入或调试自动查询")
        self.label_20.setText("坐标x,y,z")
        self.Seat_Edit.setPlaceholderText("部署手动输入或调试自动查询")
        self.label_24.setText("时钟区域ID个数")
        self.Clock_Num_Edit.setPlaceholderText("部署手动输入或调试自动查询")
        self.label_22.setText("主基站 clock ID")
        self.MClock_ID_Edit.setPlaceholderText("部署手动输入或调试自动查询")
        self.label_23.setText("主从基站SM clock ID")
        self.SMClock_ID_Edit.setPlaceholderText("部署手动输入或调试自动查询")
        self.label_26.setText("从基站1clock ID")
        self.SClock_ID_Edit1.setPlaceholderText("部署手动输入或调试自动查询")
        self.label_28.setText("从基站2clock ID")
        self.SClock_ID_Edit2.setPlaceholderText("部署手动输入或调试自动查询")
        self.log_ctl.setText("Log使能")
        self.submit.setText("提交保存")
        self.reboot.setText("基站重启")
        self.resip.setText("重设IP")
        self.reset.setText("恢复出厂设置")
        self.setLayout(self.verticalLayout)
        #self.refresh_p_fn()

        #连接信号与槽
        self.concect_dev.clicked.connect(self.UDP_connect)
        self.connect_mode.clicked.connect(self.connectmode_switch)
        self.query_info.clicked.connect(self.query_info_fn)
        self.refresh_port.clicked.connect(self.refresh_p_fn)
        self.open_port.clicked.connect(self.OpenSerial)
        self.query_info2.clicked.connect(self.query_info_fn)
        self.change_mode.clicked.connect(self.change_mode_fn)
        self.submit.clicked.connect(self.submit_fn)
        self.reboot.clicked.connect(self.dev_reboot)
        self.resip.clicked.connect(lambda:Resip_win.show())
        self.reset.clicked.connect(self.dev_reset)
        self.log_ctl.clicked.connect(self.log_ctl_fn)


    def connectmode_switch(self):#连接模式切换
        if (self.connect_mode.text() == '切换串口连接'):
            self.horizontalLayout_9.replaceWidget(self.widget,self.widget_2)
            self.widget.hide()
            self.widget_2.show()
            self.connect_mode.setText('切换网口连接')
            self.connect_code = 1
        elif (self.connect_mode.text() == '切换网口连接'):
            self.horizontalLayout_9.replaceWidget(self.widget_2,self.widget)
            self.widget_2.hide()
            self.widget.show()
            self.connect_mode.setText('切换串口连接')
            self.connect_code = 0


    def refresh_p_fn(self): #刷新串口号
        self.cb_serial.clear()
        plist = get_port_list()
        for i in range(0, len(plist)):
            plist_0 = list(plist[i])
            self.cb_serial.addItem(str(plist_0[0]))


    def clean_screen_fn(self):#log窗口清空
        self.textBrowser.clear()


    def log_string(self, s): #Log窗口日志输出
        self.textBrowser.append(s)
        cursor =  self.textBrowser.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.textBrowser.setTextCursor(cursor)


    def set_sp_state(self, state): # 设置串口打开关闭状态
        if(state == 0): #串口已打开
            self.open_port.setText("关闭串口")
            self.cb_serial.setEnabled(False)
            self.log_ctl.setEnabled(True)
        elif(state == 1): #串口已关闭
            self.open_port.setText("打开串口")
            self.cb_serial.setEnabled(True)
            self.log_ctl.setChecked(False)
            self.log_ctl.setEnabled(False)
            self.mThread = None


    def OpenSerial(self):#打开串口功能
        if(self.open_port.text() == '打开串口'):
            if self.cb_serial.currentText() != '':
                self.mThread = Debug_Thread(_port_name=self.cb_serial.currentText())#, baudRate=self.cb_baudRate.currentText()
                self.mThread.textSignal.connect(self.log_string)
                self.mThread.stateSignal.connect(self.set_sp_state)
                self.mThread.start()
            else:
                self.log_string('串口选择为空，请检查后重试！' + '\r\n')
        else:
            self.mThread.send(('AT+Log_OFF' + '\r\n').encode('utf-8'))
            self.mThread.my_stop()


    def set_udp_state(self, state): # 设置串口打开关闭状态
        if(state == 0): #串口已打开
            self.concect_dev.setText("断开连接")
            self.log_ctl.setEnabled(True)
        elif(state == 1): #串口已关闭
            self.concect_dev.setText("连接设备")
            self.log_ctl.setChecked(False)
            self.log_ctl.setEnabled(False)
            self.uThread = None


    def UDP_connect(self):#UDP连接
        if(self.concect_dev.text() == '连接设备'):
            if self.textEdit_18.toPlainText() != '':
                self.uThread = Debug_UDP_Thread(_ip_port = self.textEdit_18.toPlainText())
                self.uThread.udptextSignal.connect(self.log_string)
                self.uThread.udpstateSignal.connect(self.set_udp_state)
                self.uThread.start()
            else:
                self.log_string('请输入正确的IP')
        else:
            self.uThread.my_stop()


    def connect_dev_fn(self):#设备连接
        if self.mThread != None:
                self.mThread.send(('AT+Link' + '\r\n').encode('utf-8'))
        else:
            self.log_string("请先连接基站")


    def data_analysis(self,data):
        analyzed = ''
        for i in re.findall(r'.{2}',data):
            a = str(int(i,16))
            analyzed += a
        return analyzed


    def query_info_fn(self):#信息查询
        info = ''
        if self.connect_code == 0:
            if self.uThread != None:
                self.log_string('信息查询中……')
                self.uThread.send(('AT+GET?0F' + '\r\n').encode('utf-8'))
                timeout = 1.5
                time_start = time.time()
                while '0F-' not in self.uThread.data:
                    time_end = time.time()
                    if (time_end - time_start) > timeout:
                        break
                    else:
                        continue
                info = self.uThread.data
                if '0F-' not in info:
                    self.log_string('查询失败，未收到数据，请检查')
                    return
                time.sleep(0.1)
                info_list = re.findall(r'{(.*?)}',info)[0].split(',')
                Anchor_Macid = str(int(re.findall(r'-(.*)',info_list[0])[0],16))
                Eng_IP = re.findall(r'-(.*)',info_list[2])[0]
                Eng_IP_1 = ''
                for i in re.findall(r'.{2}',Eng_IP):
                    a = str(int(i,16))
                    Eng_IP_1 += (a + '.')
                Clock_Num = str(int(re.findall(r'-(.*)',info_list[4])[0],16))
                #MClock_ID = str(int(re.findall(r'-(.*)',info_list[5])[0],16))
                MClock_ID = self.data_analysis(re.findall(r'-(.*)',info_list[5])[0])
                SMClock_ID = self.data_analysis(re.findall(r'-(.*)',info_list[6])[0])
                SClock_ID1 = self.data_analysis(re.findall(r'-(.*)',info_list[7])[0])
                SClock_ID2 = self.data_analysis(re.findall(r'-(.*)',info_list[8])[0])
                self.Anchor_Macid_Edit.setPlainText(Anchor_Macid)
                self.Eng_IP_Edit.setText(Eng_IP_1)
                self.comboBox.setCurrentIndex(int(re.findall(r'-(.*)',info_list[3])[0]))
                self.Clock_Num_Edit.setPlainText(Clock_Num)
                self.MClock_ID_Edit.setPlainText(MClock_ID)
                self.SMClock_ID_Edit.setPlainText(SMClock_ID)
                self.SClock_ID_Edit1.setPlainText(SClock_ID1)
                self.SClock_ID_Edit2.setPlainText(SClock_ID2)
            else:
                self.log_string("请先连接设备！")
        else:
            if self.mThread != None:
                self.log_string('信息查询中……')
                self.mThread.send(('AT+GET?0F' + '\r\n').encode('utf-8'))
                while '0F' not in self.mThread.result:
                    continue
                info = self.mThread.result
                time.sleep(0.1)
                info_list = re.findall(r'{(.*?)}',info)[0].split(',')
                Anchor_Macid = str(int(re.findall(r'-(.*)',info_list[0])[0],16))
                Eng_IP = re.findall(r'-(.*)',info_list[2])[0]
                Eng_IP_1 = ''
                for i in re.findall(r'.{2}',Eng_IP):
                    a = str(int(i,16))
                    Eng_IP_1 += (a + '.')
                Clock_Num = str(int(re.findall(r'-(.*)',info_list[4])[0],16))
                MClock_ID = str(int(re.findall(r'-(.*)',info_list[5])[0],16))
                SMClock_ID = str(int(re.findall(r'-(.*)',info_list[6])[0],16))
                SClock_ID1 = str(int(re.findall(r'-(.*)',info_list[7])[0],16))
                SClock_ID2 = str(int(re.findall(r'-(.*)',info_list[8])[0],16))
                self.Anchor_Macid_Edit.setPlainText(Anchor_Macid)
                self.Eng_IP_Edit.setText(Eng_IP_1)
                self.comboBox.setCurrentIndex(int(re.findall(r'-(.*)',info_list[3])[0]))
                self.Clock_Num_Edit.setPlainText(Clock_Num)
                self.MClock_ID_Edit.setPlainText(MClock_ID)
                self.SMClock_ID_Edit.setPlainText(SMClock_ID)
                self.SClock_ID_Edit1.setPlainText(SClock_ID1)
                self.SClock_ID_Edit2.setPlainText(SClock_ID2)
            else:
                self.log_string("请先连接设备！")


    def change_mode_fn(self):#工作场景切换
        AT_ctl_dict = {'测距模式':'AT+WS_DM','定位模式':'AT+WS_LP'}
        if self.connect_code == 0:
            if self.uThread != None:
                self.uThread.send((AT_ctl_dict[self.comboBox_2.currentText()] + '\r\n').encode('utf-8'))
                timeout = 0.5
                time_start = time.time()
                while '-' not in self.uThread.data:
                    time_end = time.time()
                    if (time_end - time_start) > timeout:
                        break
                    else:
                        continue#设置超时
                if 'OK' in self.uThread.data:
                    self.log_string("已切换到"+self.comboBox_2.currentText() + '\r\n')
                else:
                    self.log_string('模式切换失败' + '\r\n')
            else:
                self.log_string("请先连接设备")
        else:
            if self.mThread != None:
                    self.mThread.send((AT_ctl_dict[self.comboBox_2.currentText()] + '\r\n').encode('utf-8'))
                    #timeout = 1
                    #time_start = time.time()
                    while '-' not in self.mThread.result:
                        '''time_end = time.time()
                        if (time_end - time_start) > timeout:
                            break
                        else:'''#设置超时
                        continue
                    self.log_string("已切换到"+self.comboBox_2.currentText() + '\r\n')
            else:
                self.log_string("请先连接设备")


    def submit_fn(self):
        dev_mode_dict = {'主基站':'0','从基站':'1','主从基站':'2'}
        try:
            Eng_IP = hex(int(self.Eng_IP_Edit.text()[:3]))[2:].upper() + hex(int(self.Eng_IP_Edit.text()[4:7]))[2:].upper() + hex(int(self.Eng_IP_Edit.text()[8:11]))[2:].upper() + hex(int(self.Eng_IP_Edit.text()[12:15]))[2:].upper()
            Clock_Num = hex(int(self.Clock_Num_Edit.toPlainText()))[2:].upper()
            MClock_ID = hex(int(self.MClock_ID_Edit.toPlainText()))[2:].upper()
            SMClock_ID = hex(int(self.SMClock_ID_Edit.toPlainText()))[2:].upper()
            SClock_ID1 = hex(int(self.SClock_ID_Edit1.toPlainText()))[2:].upper()
            SClock_ID2 = hex(int(self.SClock_ID_Edit2.toPlainText()))[2:].upper()
        except ValueError:
            self.log_string('输入有误，请检查')
            return
        query_AT = ('AT+SET=1F-{13-' + Eng_IP +',14-' + dev_mode_dict[self.comboBox.currentText()] + ',15-' + Clock_Num + ',16-' 
                    + MClock_ID + ',17-' + SMClock_ID + ',18-' + SClock_ID1 + ',19-' + SClock_ID2 +  '}\r\n')
        if self.connect_code == 0:
            if self.uThread != None:
                self.uThread.send(query_AT.encode('utf-8'))
                self.log_string("正在提交设置")
            else:
                self.log_string("请先连接基站")
        else:
            if self.mThread != None:
                self.mThread.send(query_AT.encode('utf-8'))
                self.log_string("正在提交设置")
            else:
                self.log_string("请先连接基站")

    def dev_reboot(self):#设备重启
        if self.connect_code == 0:
            if self.uThread != None:
                self.uThread.send(('AT+Reset' + '\r\n').encode('utf-8'))
                self.log_string("设备即将重启！")
            else:
                self.log_string("请先连接设备")
        else:
            if self.mThread != None:
                self.mThread.send(('AT+Reset' + '\r\n').encode('utf-8'))
                self.log_string("设备即将重启！")
            else:
                self.log_string("请先连接设备")


    def dev_reset(self):#设备恢复出厂
        if self.connect_code == 0:
            if self.uThread != None:
                self.uThread.send(('AT+Reboot' + '\r\n').encode('utf-8'))
                self.log_string("设备即将恢复出厂设置！")
            else:
                self.log_string("请先连接设备")

        else:
            if self.mThread != None:
                self.mThread.send(('AT+Reboot' + '\r\n').encode('utf-8'))
                self.log_string("设备即将恢复出厂设置！")
            else:
                self.log_string("请先连接设备")


    def log_ctl_fn(self):
        timeout = 0.5
        if self.connect_code == 0:
            if self.uThread != None:
                if self.log_ctl.isChecked():
                    self.uThread.send(('AT+Log_ON' + '\r\n').encode('utf-8'))
                    time_start = time.time()
                    while 'Log on ' not in self.uThread.data:
                        time_end = time.time()
                        if (time_end - time_start) > timeout:
                            break
                        else:
                            continue
                    result = self.uThread.data
                    time.sleep(0.2)
                    if 'Log on OK' in result:
                        self.log_string("Log开启")
                    else:
                        self.log_ctl.setChecked(False)
                        self.log_string('Log开启失败，请检查')
                else:
                    self.uThread.send(('AT+Log_OFF' + '\r\n').encode('utf-8'))
                    time_start = time.time()
                    while 'Log off ' not in self.uThread.data:
                        time_end = time.time()
                        if (time_end - time_start) > timeout:
                            break
                        else:
                            continue
                    if 'Log off OK' in self.uThread.data:
                        self.log_string("Log关闭")
                    else:
                        self.log_ctl.setChecked(True)
                        self.log_string('Log关闭失败，请检查')
            else:
                self.log_string("未连接设备，设置无效")
        else:
            if self.mThread != None:
                if self.log_ctl.isChecked():
                    self.mThread.send(('AT+Log_ON' + '\r\n').encode('utf-8'))
                    time_start = time.time()
                    while 'Log on ' not in self.mThread.result:
                        time_end = time.time()
                        if (time_end - time_start) > timeout:
                            break
                        else:
                            continue
                    result = self.mThread.result
                    time.sleep(0.2)
                    if 'Log on OK' in result:
                        self.log_string("Log开启")
                    else:
                        self.log_ctl.setChecked(False)
                        self.log_string('Log开启失败，请检查')
                else:
                    self.mThread.send(('AT+Log_OFF' + '\r\n').encode('utf-8'))
                    while 'Log off ' not in self.mThread.result:
                        continue
                    if 'Log off OK' in self.mThread.result:
                        self.log_string("Log关闭")
                    else:
                        self.log_ctl.setChecked(True)
                        self.log_string('Log关闭失败，请检查')
            else:
                self.log_string("未连接设备，设置无效")





if __name__=="__main__":
    app=QApplication(sys.argv)
    win=Debug_Tools()
    win.show()
    sys.exit(app.exec_())