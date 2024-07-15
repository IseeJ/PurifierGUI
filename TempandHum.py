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
#from mainwindow import Ui_MainWindow
from AllWindow import Ui_MainWindow
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo



#https://realpython.com/python-pyqt-qthread/
#https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
class DateAxisItem(AxisItem):
    def __init__(self, *args, **kwargs):
        AxisItem.__init__(self, *args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [dt.datetime.fromtimestamp(value).strftime("%H:%M:%S\n%Y-%m-%d\n\n") for value in values]

class TimeAxisItem(AxisItem):
    def __init__(self, *args, **kwargs):
        AxisItem.__init__(self, *args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [dt.datetime.fromtimestamp(value).strftime('%H:%M:%S') for value in values]



class Hum_Worker(QThread):
    #add abshum conversion now 4 floats emit
    result = pyqtSignal(str, float, float, float, float)
    def __init__(self, port, interval, baud):
        super().__init__()
        self.ser2 = None
        self.interval = interval
        self.port = port
        self.baud = baud
        self.is_running2 = True
        self.sensor_string = ""
        self.sensor_string_complete = False
        self.last_emit_time = dt.datetime.now()

    #debugging incomplete reading that occurs every 12 readings
    def run(self):
        try:
            self.ser2 = serial.Serial(self.port, self.baud, parity='N', stopbits=1, bytesize=8, timeout=10000)
            self.ser2.write(b'O,HUM,1\r\n')
            self.ser2.write(b'O,T,1\r\n')
            self.ser2.write(b'O,Dew,1\r\n')

            while self.is_running2:
                now_time = dt.datetime.now()
                timestamp = str(now_time.strftime('%Y%m%dT%H%M%S.%f')[:-3])  

                #continue readings (data comes in every 1 s)
                if self.ser2.in_waiting > 0:
                    inchar = self.ser2.read().decode('utf-8')
                    self.sensor_string += inchar
                    if inchar == '\r':
                        self.sensor_string_complete = True

                if self.sensor_string_complete:
                    #print(self.sensor_string)
                    parts = self.sensor_string.split(",")
                    if len(parts) == 4:
                        HUM = float(parts[0].strip())
                        TMP = float(parts[1].strip())
                        DEW = float(parts[3].strip())
                        #add abshum conversion
                        absHUM = (6.112*np.exp((17.67*TMP)/(TMP+243.5))*HUM*2.1674)/(273.15+TMP)
                        self.latest_reading = (HUM, TMP, DEW, absHUM)
                    if not self.sensor_string[0].isdigit():
                        print(timestamp, self.sensor_string)

                    self.sensor_string = ""
                    self.sensor_string_complete = False

                #only emit data to log file based on our interval input 
                if now_time - self.last_emit_time >= dt.timedelta(seconds=self.interval):
                    if self.latest_reading:
                        self.result.emit(timestamp, *self.latest_reading)
                    else:
                        self.result.emit(timestamp, np.nan, np.nan, np.nan, np.nan)
                    self.last_emit_time = now_time

        except serial.SerialException as e:
            print(f"Serial error: {e}")
        finally:
            if self.ser2:
                self.ser2.close()
                
    """
    def run(self):
        try:
            self.ser2 = serial.Serial(self.port, self.baud, parity='N',stopbits=1,bytesize=8,timeout=10000)
            #self.ser2 = serial.Serial('COM7', 9600, timeout = 10000)
            self.ser2.write(b'O,HUM,1\r\n')
            self.ser2.write(b'O,T,1\r\n')
            self.ser2.write(b'O,Dew,1\r\n')
            #time.sleep(0.1)
            while self.is_running2:
                now_time = dt.datetime.now()
                timestamp = str(now_time.strftime('%Y%m%dT%H%M%S.%f')[:-3])  
                write_time1 = dt.datetime.now()
                interval_dt = dt.timedelta(seconds = self.interval) 
                write_time2 = write_time1 + interval_dt
                while dt.datetime.now() <= write_time2:
                    pass
                line = self.ser2.read_until(b'\r').decode('utf-8')
                #line = self.ser2.read(20).decode('utf-8')
                print(line)
                try:
                    parts = line.split(',')
                    #fix parsing error when reading is incomplete (index out of range happens once in a while but will pause the process)
                    if len(parts) == 4:
                        HUM = float(parts[0].strip())
                        TMP = float(parts[1].strip())
                        DEW = float(parts[3].strip())
                        self.result.emit(timestamp, HUM, TMP, DEW)
                    #sometimes only hum is printed
                    #elif len(parts) == 1:
                    #    HUM = float(parts[0].strip())
                    #    self.result.emit(timestamp, HUM, np.nan, np.nan)
                    else:
                        self.result.emit(timestamp, np.nan, np.nan, np.nan)
                except ValueError:
                    self.result.emit(timestamp, np.nan, np.nan, np.nan)

        except serial.SerialException as e:
            print(f"Serial error: {e}")
        finally:
            if self.ser2:
                self.ser2.close()
    """
    def stop(self):
        self.is_running2 = False
        if self.ser2:
            self.ser2.close()
        self.quit()
        self.wait()


class Temp_Worker(QThread):
    result = pyqtSignal(str, tuple)
    
    def __init__(self, port, interval, baud):
        super().__init__()
        self.ser = None
        self.is_running = True
        self.port = port
        self.interval = interval
        self.baud = baud
        
        self.READ_BIT_INHEX = 74
        self.READ_BIT = 37
        self.MAX_TEMP = 18000 #1800C to determine negative val
        #self.ser = serial.Serial(self.port, self.baud, timeout=10000)
        #print("Starting Serial")

    
    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=10000)
            hex_data = [0x01, 0x16, 0x7B, 0x28, 0x48, 0x4C, 0x45, 0x48, 0x54, 0x43, 0x34, 0x30, 0x39, 0x35, 0x67, 0x71, 0x29, 0x7D, 0x7E, 0x04]
            byte_data = bytearray(hex_data)
            while self.is_running:
                write_time1 = dt.datetime.now()
                interval_dt = dt.timedelta(seconds = self.interval) 
                write_time2 = write_time1 + interval_dt
                while dt.datetime.now() <= write_time2:
                    pass
                self.ser.write(byte_data)
                time.sleep(0.1)
                if self.ser.in_waiting:
                    response = self.ser.read(self.READ_BIT)
                    if response:
                        temperatures = parse_temp(self,response)
                        now_time = dt.datetime.now()
                        current_time = str(now_time.strftime('%Y%m%dT%H%M%S.%f')[:-3])  
                        print(f"{current_time}, Temperatures: {temperatures}")
                        self.result.emit(current_time, temperatures)
                    else:
                        print("No response")

        except serial.SerialException as e:
            print(f"Serial error: {e}")
        finally:
            if self.ser:
                self.ser.close()
    """
    #for test w/o serial
    def run(self):
        while self.is_running:
            temperatures = test_temp()
            current_time = str(dt.datetime.now().strftime('%Y%m%dT%H%M%S.%f'))
            print(f"Time: {current_time}, Temperatures: {temperatures}")
            self.result.emit(current_time, temperatures)
            time.sleep(5)
    """
    
    def stop(self):
        self.is_running = False
        if self.ser:
            self.ser.close()
        self.quit()
        self.wait()

#temp conversion from hexadecimal 
def hex_dec(self, T_hex):
    try:
        T_val = int(T_hex, 16)
        T_max = self.MAX_TEMP
        hex_max = 0xFFFF
        if T_val > T_max:
            T = -(hex_max - T_val + 1) / 10
        else:
            T = T_val / 10
        return T
    except ValueError:
        return 'err'

#for test w/o serial
def test_temp():
    temperatures = []
    for i in range(8):
        temperatures.append(random.randint(500, 4000))
    return tuple(temperatures)
        
def parse_temp(self, response):
    response_hex = response.hex()
    if len(response_hex) < self.READ_BIT_INHEX:
        return tuple('err' for _ in range(8))
    temperatures = []
    for i in range(8):
        hex_str = response_hex[34 + i*4:36 + i*4] + response_hex[32 + i*4:34 + i*4]
        temperatures.append(hex_dec(self,hex_str))
    return tuple(temperatures)

#to store tempdata
class TemperatureModel(QObject):
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(TemperatureModel, self).__init__(parent)
        self.data = []

    def lenData(self, parent=QModelIndex()):
        return len(self.data)

    def appendData(self, time, *temps):
        self.data.append((time,) + temps)
        self.dataChanged.emit()

    def clearData(self):
        self.data = []
        self.dataChanged.emit()

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            return self.data[row]

    def reset(self):
        self.data = []
        return None


#to store humidity data
class HumidityModel(QObject):
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(HumidityModel, self).__init__(parent)
        self.data = []

    def lenData(self, parent=QModelIndex()):
        return len(self.data)
    #add abshum
    def appendData(self, time, hum, tmp, dew, abshum):
        self.data.append((time, hum, tmp, dew, abshum))
        self.dataChanged.emit()

    def clearData(self):
        self.data = []
        self.dataChanged.emit()

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            return self.data[row]

    def reset(self):
        self.data = []
        return None



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowIcon(QIcon('logo.png'))
        self.worker1 = None
        self.worker2 = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #connect buttons to actions
        #self.ui.startStopButton.pressed.connect(self.toggleRun)
        self.ui.startStopButton.setCheckable(True)
        self.ui.startStopButton.clicked.connect(self.toggleRun)

        
        self.ui.clearButton.pressed.connect(self.clearPlot)
        self.ui.HumclearButton.pressed.connect(self.HumclearPlot)
        
        self.ui.TempLogButton.pressed.connect(self.TempstartLogging)
        self.ui.HumLogButton.pressed.connect(self.HumstartLogging)
        self.ui.LogBothButton.setCheckable(True)
        self.ui.LogBothButton.clicked.connect(self.BothstartLogging)

        
        self.ui.refreshButton.pressed.connect(self.refreshSerialPorts)
        self.ui.saveDirectoryButton.pressed.connect(self.chooseSaveDirectory)
        self.ui.HumsaveDirectoryButton.pressed.connect(self.chooseHumSaveDirectory)


        self.temperature_model = TemperatureModel()
        self.humidity_model = HumidityModel() 
        self.initGraph()
        self.filename = None
        self.Humfilename = None
        self.serialPort = None
        self.serialPort2 = None
        self.saveDirectory = None
        self.HumsaveDirectory = None
        self.interval = 2 #2 sec default
        self.baud = 38400 #38400 default
        
        
    def initFile(self):
        now = dt.datetime.now()
        self.filename = "temp_log_" + str(now.strftime('%Y%m%dT%H%M%S')) + ".csv"
        try:
            with open(f"{self.saveDirectory}/{self.filename}", 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Time', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8'])
        except Exception as e:
            print(f"Error opening file: {e}")
    
    def HuminitFile(self):
        now = dt.datetime.now()
        self.Humfilename = "hum_log_" + str(now.strftime('%Y%m%dT%H%M%S')) + ".csv"
        try:
            with open(f"{self.HumsaveDirectory}/{self.Humfilename}", 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Time', 'HUM', 'TMP', 'DEW', 'absHUM'])
        except Exception as e:
            print(f"Error opening file: {e}")

    def initGraph(self):
        #PLOT1
        self.ui.graphWidget.setBackground("w")
        styles = {"color": "black", "font-size": "18px"}
        self.ui.graphWidget.setLabel("left", "Temperature (°C)", **styles)
        self.ui.graphWidget.setLabel("bottom", "Time", **styles)
        self.ui.graphWidget.getAxis('bottom').setStyle(tickTextOffset=10)
        self.ui.graphWidget.setAxisItems({'bottom': DateAxisItem(orientation='bottom')})
        self.ui.graphWidget.showGrid(x=True, y=True, alpha=0.4)
        self.time = []
        self.data = [[] for _ in range(8)]
        self.plotLines = []
        self.colors = [(183, 101, 224), (93, 131, 212), (49, 205, 222), (36, 214, 75), (214, 125, 36), (230, 78, 192), (209, 84, 65), (0, 184, 245)]
        for i in range(8):
            plot_line = self.ui.graphWidget.plot(self.time, self.data[i], pen=pg.mkPen(color=self.colors[i], width=2))
            self.plotLines.append(plot_line)


        #PLOT 2
        """
        self.ui.HumPlotWidget.setBackground("w")
        self.ui.HumPlotWidget.setLabel("left", "Value", **styles)
        self.ui.HumPlotWidget.setLabel("bottom", "Time", **styles)
        self.ui.HumPlotWidget.getAxis('bottom').setStyle(tickTextOffset=10)
        self.ui.HumPlotWidget.setAxisItems({'bottom': DateAxisItem(orientation='bottom')})
        self.ui.HumPlotWidget.showGrid(x=True, y=True, alpha=0.4)
        self.hum_time = []
        self.hum_data = {'HUM': [], 'TMP': [], 'DEW': [], 'absHUM': []}
        self.hum_plotLines = {}
        self.hum_plotLines['HUM'] = self.ui.HumPlotWidget.plot(self.hum_time, self.hum_data['HUM'], pen=pg.mkPen(color=(190, 17, 17), width=2), name='HUM')
        self.hum_plotLines['TMP'] = self.ui.HumPlotWidget.plot(self.hum_time, self.hum_data['TMP'], pen=pg.mkPen(color=(0, 184, 245), width=2), name='TMP')
        self.hum_plotLines['DEW'] = self.ui.HumPlotWidget.plot(self.hum_time, self.hum_data['DEW'], pen=pg.mkPen(color=(0,0,0), width=2), name='DEW')
        """

        self.ui.graphics_layout.setBackground("w")
        self.hum_plot = self.ui.graphics_layout.addPlot(row=0, col=0)
        self.tmp_plot = self.ui.graphics_layout.addPlot(row=1, col=0)
        self.dew_plot = self.ui.graphics_layout.addPlot(row=2, col=0)


        self.hum_plot.setLabel('left', text='<span style="color: #be1111;">RH(%)</span>')
        self.tmp_plot.setLabel('left', text='<span style="color: #00b8f5;">TMP(°C)</span>')
        self.dew_plot.setLabel('left',text='<span style="color: #000000;">DEW(°C)</span>')


        self.dew_plot.setLabel('bottom', 'Time', **styles)
        self.hum_plot.getAxis('bottom').setStyle(tickTextOffset=10)
        self.tmp_plot.getAxis('bottom').setStyle(tickTextOffset=10)
        self.dew_plot.getAxis('bottom').setStyle(tickTextOffset=10)

        self.hum_plot.setAxisItems({'bottom': TimeAxisItem(orientation='bottom')})
        self.tmp_plot.setAxisItems({'bottom': TimeAxisItem(orientation='bottom')})
        self.dew_plot.setAxisItems({'bottom': DateAxisItem(orientation='bottom')})

        self.hum_time = []
        self.hum_data = {'HUM': [], 'TMP': [], 'DEW': [], 'absHUM': []}
        self.hum_plotLines = {}
        self.hum_plotLines['HUM'] = self.hum_plot.plot(self.hum_time, self.hum_data['HUM'], pen=pg.mkPen(color=(190, 17, 17), width=2), name='HUM')
        self.hum_plotLines['TMP'] = self.tmp_plot.plot(self.hum_time, self.hum_data['TMP'], pen=pg.mkPen(color=(0, 184, 245), width=2), name='TMP')
        self.hum_plotLines['DEW'] = self.dew_plot.plot(self.hum_time, self.hum_data['DEW'], pen=pg.mkPen(color=(0,0,0), width=2), name='DEW')
    

        #PLOT 3
        self.ui.HumPlotWidget2.setBackground("w")
        self.temp_viewbox = pg.ViewBox()
        self.ui.HumPlotWidget2.plotItem.showAxis('right')
        self.ui.HumPlotWidget2.plotItem.scene().addItem(self.temp_viewbox)
        self.ui.HumPlotWidget2.plotItem.getViewBox().sigResized.connect(self.updateViews)
        
        self.ui.HumPlotWidget2.plotItem.getAxis('right').linkToView(self.temp_viewbox)
        self.temp_viewbox.setXLink(self.ui.HumPlotWidget2.plotItem)

        self.ui.HumPlotWidget2.setLabel('bottom', 'Time', **styles)
        self.ui.HumPlotWidget2.getAxis('bottom').setStyle(tickTextOffset=10)
        self.ui.HumPlotWidget2.setAxisItems({'bottom': DateAxisItem(orientation='bottom')})

        self.ui.HumPlotWidget2.setLabel("left", "Absolute Humidity (g/m3)", **{"color": "blue", "font-size": "18px"})
        self.hum_plot = self.ui.HumPlotWidget2.plot(self.hum_time, self.hum_data['absHUM'], pen=pg.mkPen(color='b', width=2), name="absHUM")
        self.ui.HumPlotWidget2.setLabel("right", "Output Temperature (°C)", **{"color": "red", "font-size": "18px"})
        self.temp_plot = pg.PlotDataItem(self.time, self.data[7], pen=pg.mkPen(color='r', width=2), name="T8")
        self.temp_viewbox.addItem(self.temp_plot)
    
    def updateViews(self):
        self.temp_viewbox.setGeometry(self.ui.HumPlotWidget2.getPlotItem().getViewBox().sceneBoundingRect())
        self.temp_viewbox.linkedViewChanged(self.ui.HumPlotWidget2.getPlotItem().getViewBox(), self.temp_viewbox.XAxis)
        
    
    def toggleRun(self):
        if self.ui.startStopButton.isChecked():
            self.ui.startStopButton.setText("Running")
            self.ui.startStopButton.setStyleSheet("QPushButton {background-color: lightgreen}")
        else:
            self.ui.startStopButton.setText("Stopped")
            self.ui.startStopButton.setStyleSheet("QPushButton {background-color: lightcoral}")
            self.ui.LogBothButton.setText("Logging Stopped")
            self.ui.LogBothButton.setStyleSheet("QPushButton {background-color: lightcoral}")
            
        if self.worker1 is not None:
            self.stopRun()
        else:
            self.startRun()

    def startRun(self):
        self.serialPort = self.ui.TempPortBox.currentText()
        self.baud = int(self.ui.TempBaudBox.currentText())

        self.serialPort2 = self.ui.HumPortBox.currentText()
        self.baud2 = int(self.ui.HumBaudBox.currentText())

        if 'COM' not in self.serialPort:
            self.serialPort = "/dev/" + self.ui.TempPortBox.currentText()
        if 'COM' not in self.serialPort2:
            self.serialPort2 = "/dev/" + self.ui.HumPortBox.currentText()
            
        print(f"Connected to Tmp: {self.serialPort}")
        #print(f"Set Tmp baud rate to: {self.baud}")
        print(f"Connected to Hum: {self.serialPort2}")
        #print(f"Set Hum baud rate to: {self.baud2}")
        
        
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
            self.worker1 = Temp_Worker(self.serialPort, self.interval, self.baud)
            self.worker1.result.connect(self.updateTemp)
            self.worker1.start()
            print("Starting Temp_Worker")

            self.worker2 = Hum_Worker(self.serialPort2, self.interval, self.baud2)
            self.worker2.result.connect(self.updateHum)
            self.worker2.start()
            print("Starting Hum_Worker")
            
        except serial.SerialException as e:
            print(f"Could not open serial port: {e}")
            self.worker1 = None

    def stopRun(self):
        if self.worker1:
            self.worker1.stop()
            self.worker1 = None
            print("Stopping Serial 1")
        if self.worker2:
            self.worker2.stop()
            self.worker2 = None
            print("Stopping Serial 2")

    def clearPlot(self):
        self.time = []
        self.data = [[] for _ in range(8)]
        for i in range(8):
            self.plotLines[i].setData(self.time, self.data[i])
        #self.temp_plot.setData(self.time, self.data[i])
        self.temp_plot.setData(self.time, self.data[7])
        
    def HumclearPlot(self):
        self.hum_time = []
        self.hum_data = {'HUM': [], 'TMP': [], 'DEW': [], 'absHUM': []}
        self.hum_plotLines['HUM'].setData(self.hum_time, self.hum_data['HUM'])
        self.hum_plotLines['TMP'].setData(self.hum_time, self.hum_data['TMP'])
        self.hum_plotLines['DEW'].setData(self.hum_time, self.hum_data['DEW'])
        self.hum_plot.setData(self.hum_time,self.hum_data['absHUM'])

    #Logging
    def TempstartLogging(self):
        self.initFile()
        self.ui.fileLabel.setText(f"{self.saveDirectory}/{self.filename}")
        
    def HumstartLogging(self):
        self.HuminitFile()
        self.ui.HumfileLabel.setText(f"{self.HumsaveDirectory}/{self.Humfilename}")

    def BothstartLogging(self):
        if self.ui.LogBothButton.isChecked():
            self.ui.LogBothButton.setText("Logging")
            self.ui.LogBothButton.setStyleSheet("QPushButton {background-color: lightgreen}")
            self.ui.HumLogButton.setStyleSheet("QPushButton {background-color: darkGray}")
            self.ui.TempLogButton.setStyleSheet("QPushButton {background-color: darkGray}")
        else:
            self.ui.LogBothButton.setText("Log Both")
            self.ui.LogBothButton.setStyleSheet("QPushButton {background-color: white}")
            self.ui.HumLogButton.setStyleSheet("QPushButton {background-color: white}")
            self.ui.TempLogButton.setStyleSheet("QPushButton {background-color: white}")
            
        self.initFile()
        self.ui.fileLabel.setText(f"{self.saveDirectory}/{self.filename}")
        self.HuminitFile()
        self.ui.HumfileLabel.setText(f"{self.HumsaveDirectory}/{self.Humfilename}")

    
 
    def refreshSerialPorts(self):
        self.ui.TempPortBox.clear()
        self.ui.HumPortBox.clear()
        ports = QSerialPortInfo.availablePorts()
        for port in ports:
            self.ui.TempPortBox.addItem(port.portName())
            self.ui.HumPortBox.addItem(port.portName())
        
            
            
    def chooseSaveDirectory(self):
        self.saveDirectory = QFileDialog.getExistingDirectory(self, "Save Directory")
        if self.saveDirectory:
            self.ui.fileLabel.setText(f"{self.saveDirectory}")

    def chooseHumSaveDirectory(self):
        self.HumsaveDirectory = QFileDialog.getExistingDirectory(self, "Save Directory")
        if self.HumsaveDirectory:
            self.ui.HumfileLabel.setText(f"{self.HumsaveDirectory}")

    @pyqtSlot(str, tuple)
    def updateTemp(self, current_time, temperatures):
        for i in range(8):
            if temperatures[i] != 'err':
                self.ui.labels[i].setText(f"T{i + 1}: {temperatures[i]:.1f}")
            else:
                self.ui.labels[i].setText(f"T{i + 1}: err")

        active_ch = tuple(temperatures[i] if self.ui.checkboxes[i].isChecked() else np.nan for i in range(8))
        self.temperature_model.appendData(current_time, *active_ch)

        formattime = dt.datetime.strptime(current_time, '%Y%m%dT%H%M%S.%f').timestamp()
        self.time.append(formattime)

        for i in range(8):
            self.data[i].append(temperatures[i])
            if self.ui.checkboxes[i].isChecked():
                self.plotLines[i].setData(self.time, self.data[i])
        self.temp_plot.setData(self.time, self.data[7])
        if self.filename:
            self.LogData(current_time, temperatures)


    def LogData(self, timestamp, temperatures):
        try:
            with open(f"{self.saveDirectory}/{self.filename}", 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp] + list(temperatures))
                file.flush()
        except Exception as e:
            print(f"Error writing to file: {e}")

    @pyqtSlot(str, float, float, float, float)
    def updateHum(self, timestamp, HUM, TMP, DEW, absHUM):
        print(f"{timestamp}, RH: {HUM}, TMP: {TMP}, DEW: {DEW}, AH: {absHUM:.2f}")
        self.ui.Humlabel1.setText(f"RH: {HUM:.2f}")
        self.ui.Humlabel2.setText(f"Tmp: {TMP:.2f}")
        self.ui.Humlabel3.setText(f"Dew: {DEW:.2f}")
        self.ui.Humlabel4.setText(f"AH: {absHUM:.2f}")
        formattime = dt.datetime.strptime(timestamp, '%Y%m%dT%H%M%S.%f').timestamp()

        self.humidity_model.appendData(timestamp, HUM, TMP, DEW, absHUM)
        self.hum_time.append(formattime)
        self.hum_data['HUM'].append(HUM)
        self.hum_data['TMP'].append(TMP)
        self.hum_data['DEW'].append(DEW)
        self.hum_data['absHUM'].append(absHUM)

        self.hum_plotLines['HUM'].setData(self.hum_time, self.hum_data['HUM'])
        self.hum_plotLines['TMP'].setData(self.hum_time, self.hum_data['TMP'])
        self.hum_plotLines['DEW'].setData(self.hum_time, self.hum_data['DEW'])
        self.hum_plot.setData(self.hum_time, self.hum_data['absHUM'])

        if self.Humfilename:
            self.HumLogData(timestamp, HUM, TMP, DEW, absHUM)
            
    def HumLogData(self, timestamp, HUM, TMP, DEW, absHUM):
        try:
            with open(f"{self.HumsaveDirectory}/{self.Humfilename}", 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, HUM,TMP,DEW, absHUM])
                file.flush()
        except Exception as e:
            print(f"Error writing to file: {e}")

app = QApplication(sys.argv)
path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'logo.png')
app.setWindowIcon(QIcon(path))
window = MainWindow()
window.show()
app.exec_()
