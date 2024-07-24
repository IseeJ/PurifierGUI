import csv
import sys, os
import time
import datetime as dt
import serial
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QModelIndex, QObject, QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
import pyqtgraph as pg
from pyqtgraph import PlotWidget, AxisItem, ViewBox
from serial import SerialException
from pathlib import Path


import random
from mainwindow import Ui_MainWindow
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo



#https://realpython.com/python-pyqt-qthread/
#https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
class DateAxisItem(AxisItem):
    def __init__(self, *args, **kwargs):
        AxisItem.__init__(self, *args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [dt.datetime.fromtimestamp(value).strftime("%H:%M:%S\n%Y-%m-%d\n\n") for value in values]
        


class Worker(QThread):
    result = pyqtSignal(str,float,float)
    
    def __init__(self, port, interval, baud):
        super().__init__()
        self.ser = None
        self.is_running = True
        self.port = port
        self.interval = interval
        self.baud = baud
        print("Starting Serial")
        

    def run(self):
        try:
            self.ser = ser = serial.Serial(port=self.port,baudrate = 19200,parity='N',stopbits=1,bytesize=8,timeout=1)
            #print(self.ser)
            while self.is_running:
                write_time1 = dt.datetime.now()
                interval_dt = dt.timedelta(seconds = self.interval) 
                write_time2 = write_time1 + interval_dt
                while dt.datetime.now() <= write_time2:
                    pass

                now_time = dt.datetime.now()
                current_time = str(now_time.strftime('%Y%m%dT%H%M%S.%f')[:-3])  
                
                CGpressure = getConvectronP(self.ser)
                #IGpressure = getIonP(self.ser)
                 
                #print(str(IG_stat(self.ser)))
               
                if IG_stat(self.ser):
                    IGpressure = getIonP(self.ser)
                else:
                    IGpressure = np.nan
            
                print(current_time, CGpressure, IGpressure)
                
                
                self.result.emit(current_time, CGpressure, IGpressure)

        except serial.SerialException as e:
            print(f"Serial error: {e}")
        finally:
            if self.ser:
                self.ser.close()

    
    def stop(self):
        self.is_running = False
        if self.ser:
            self.ser.close()
        self.quit()
        self.wait()

def openSerial(portname):
    ser = serial.Serial(
        port=portname,
        baudrate = 19200,
        parity='N',
        stopbits=1,
        bytesize=8,
        timeout=1
    )
    return ser

def IG_stat(ser):
    ser.write(bytearray(b'#01IGS\r'))
    value = ser.readline().decode('utf-8')
    
    #*01 1 IG ON
    stat = str(value)[9:11]
    print(stat)
    if stat == 'ON':
        return True
    else:
        return False
    
def getConvectronP(ser):
    ser.write(bytearray(b'#01RDCG1\r'))
    ser.flush()
    value = ser.readline().decode('utf-8')
    pressure = value[4:-1]
    return float(pressure)

    
def getIonP(ser):
    ser.write(bytearray(b'#01RD\r'))
    ser.flush()
    value = ser.readline().decode('utf-8')
    pressure = value[4:-1]
    return float(pressure)
    
    
    
class PModel(QObject):
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(PModel, self).__init__(parent)
        self.Press_time = []
        self.CGPress_data = []
        self.IGPress_data = []
        
    def lenData(self, parent=QModelIndex()):
        return len(self.Press_time)
        
    def appendData(self, time, CG, IG):
        self.Press_time.append(time)
        self.CGPress_data.append(CG)
        self.IGPress_data.append(IG)
        self.dataChanged.emit()

    def clearData(self):
        self.Press_time = []
        self.CGPress_data = []
        self.IGPress_data = []
        self.dataChanged.emit()

    def getData(self):
        return self.Press_time, self.CGPress_data, self.IGPress_data
        
    def reset(self):
        self.Press_time = []
        self.CGPress_data = []
        self.IGPress_data = []
        return None

    
    
    
    
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowIcon(QIcon('logo.png'))
        self.worker = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.startStopButton.pressed.connect(self.toggleRun)
        self.ui.clearButton.pressed.connect(self.clearPlot)
        self.ui.LogButton.pressed.connect(self.startLogging)
        self.ui.refreshButton.pressed.connect(self.refreshSerialPorts)
        self.ui.saveDirectoryButton.pressed.connect(self.chooseSaveDirectory)

        self.pressure_model = PModel()
        self.initGraph()
        self.filename = None
        self.serialPort = None
        self.saveDirectory = None
        self.interval = 1 #2 sec default
        self.baud = 19200
        
    def initFile(self):
        now = dt.datetime.now()
        self.filename = "hornetpressure_log_" + str(now.strftime('%Y%m%dT%H%M%S')) + ".csv"
        try:
            with open(f"{self.saveDirectory}/{self.filename}", 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Time', 'CG', 'IG'])
        except Exception as e:
            print(f"Error opening file: {e}")

    def initGraph(self):
        self.ui.graphWidget.setBackground("w")
        styles = {"color": "black", "font-size": "18px"}
        self.ui.graphWidget.setLabel("left", "Pressure (Torr)", **styles)
        self.ui.graphWidget.setLabel("bottom", "Time", **styles)
        self.ui.graphWidget.getAxis('bottom').setStyle(tickTextOffset=10)
        self.ui.graphWidget.setAxisItems({'bottom': DateAxisItem(orientation='bottom')})
        self.ui.graphWidget.showGrid(x=True, y=True, alpha=0.4)
        
        self.colors = [(209, 84, 65), (0, 184, 245)]
        
        self.CGPress_plot = self.ui.graphWidget.plot([],[], pen=pg.mkPen(color=self.colors[0], width=2))
        self.IGPress_plot = self.ui.graphWidget.plot([],[], pen=pg.mkPen(color=self.colors[1], width=2))


    def toggleRun(self):
        if self.worker is not None:
            self.stopRun()
        else:
            self.startRun()

    def startRun(self):
        self.serialPort = self.ui.ComboBox_1.currentText()
        self.baud = int(self.ui.ComboBox_2.currentText())
        
        if 'COM' not in self.serialPort:
            self.serialPort = "/dev/" + self.ui.ComboBox_1.currentText()
    
        print(f"Connected to: {self.serialPort}")
        print(f"Set baud rate to: {self.baud}")
        
        if self.serialPort is None:
            print(self, "No port selected")
            return
            
        try:
            self.interval = int(self.ui.intervalInput.text())
            print(f"Using input interval: {self.interval} seconds")
        except ValueError:
            print("Using default interval: 2 seconds")
            self.interval = 2

        try:
            self.worker = Worker(self.serialPort, self.interval, self.baud)
            self.worker.result.connect(self.updateData)
            self.worker.start()
            print("Starting Worker")
        except serial.SerialException as e:
            print(f"Could not open serial port: {e}")
            self.worker = None

    def stopRun(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
            print("Stopping Serial")

    def clearPlot(self):
        self.pressure_model.clearData()

    def startLogging(self):
        self.initFile()
        self.ui.fileLabel.setText(f"{self.saveDirectory}/{self.filename}")
 
    def refreshSerialPorts(self):
        self.ui.ComboBox_1.clear()
        ports = QSerialPortInfo.availablePorts()
        for port in ports:
            self.ui.ComboBox_1.addItem(port.portName())

    def chooseSaveDirectory(self):
        self.saveDirectory = QFileDialog.getExistingDirectory(self, "Save Directory")
        if self.saveDirectory:
            self.ui.fileLabel.setText(f"{self.saveDirectory}")

    @pyqtSlot(str, float, float)
    def updateData(self, current_time, CGpressure, IGpressure):
        if CGpressure != 'err':
            self.ui.labels[0].setText(f"CG: {CGpressure}")
        if IGpressure != 'err':
            self.ui.labels[1].setText(f"IG: {IGpressure}")
            
    
        formattime = dt.datetime.strptime(current_time, '%Y%m%dT%H%M%S.%f').timestamp()

        self.pressure_model.appendData(formattime, CGpressure, IGpressure)
        Press_time, CG, IG = self.pressure_model.getData()

        if self.ui.checkboxes[0].isChecked():
            self.CGPress_plot.setData(Press_time, CG)
        if self.ui.checkboxes[1].isChecked():
            self.IGPress_plot.setData(Press_time, IG)
               

        if self.filename:
            self.LogData(current_time, CGpressure, IGpressure)

    def LogData(self, timestamp, CGpressure, IGpressure):
        try:
            with open(f"{self.saveDirectory}/{self.filename}", 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp,CGpressure, IGpressure])
        except Exception as e:
            print(f"Error writing to file: {e}")

app = QApplication(sys.argv)
#path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'RTDicon.PNG')
#app.setWindowIcon(QIcon(path))
window = MainWindow()
window.show()
app.exec_()