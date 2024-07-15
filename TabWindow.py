from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 900)
        self.colors = [(183, 101, 224), (93, 131, 212), (49, 205, 222), (36, 214, 75), (214, 125, 36) ,(230, 78, 192), (209, 84, 65), (0, 184, 245)]
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Create the tab widget
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1200, 900))
        self.tabWidget.setObjectName("tabWidget")

        # Create tab1 and tab2
        self.tab1 = QtWidgets.QWidget()
        self.tab1.setObjectName("tab1")
        self.tab2 = QtWidgets.QWidget()
        self.tab2.setObjectName("tab2")

        # Add tabs to tabWidget
        self.tabWidget.addTab(self.tab1, "Tab 1")
        self.tabWidget.addTab(self.tab2, "Tab 2")

        # Set the central widget
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Vertical layout for tab1
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab1)
        self.verticalLayout.setObjectName("verticalLayout")

        self.mainsetup_1 = QtWidgets.QHBoxLayout()
        self.mainsetup_1.setObjectName("setupLayout")
        
        self.refreshButton = QtWidgets.QPushButton(self.tab1)
        self.refreshButton.setObjectName("refreshButton")
        self.refreshButton.setText("Refresh Port")
        self.mainsetup_1.addWidget(self.refreshButton)

        self.intervalInput = QtWidgets.QLineEdit(self.tab1)
        self.intervalInput.setObjectName("intervalInput")
        self.intervalInput.setPlaceholderText("Logging Interval (s)")
        self.intervalInput.setMaximumSize(QtCore.QSize(200, 16777215)) 
        self.mainsetup_1.addWidget(self.intervalInput)
        
        self.LogBothButton = QtWidgets.QPushButton(self.tab1)
        self.LogBothButton.setObjectName("LogBothButton")
        self.LogBothButton.setText("Log Both")
        self.LogBothButton.setMaximumSize(QtCore.QSize(200, 16777215)) 
        self.mainsetup_1.addWidget(self.LogBothButton)

        self.startStopButton = QtWidgets.QPushButton(self.tab1)
        self.startStopButton.setMaximumSize(QtCore.QSize(200, 16777215))
        self.startStopButton.setObjectName("startStopButton")
        self.mainsetup_1.addWidget(self.startStopButton)

        self.verticalLayout.addLayout(self.mainsetup_1)

        # HUMIDITY
        # Sub Hum 1
        self.HumHLayout_1 = QtWidgets.QHBoxLayout()
        self.HumHLayout_1.setObjectName("HumHLayout")
        
        self.HumPortBox = QtWidgets.QComboBox(self.tab1)
        self.HumPortBox.setObjectName("HumPortBox")
        self.HumHLayout_1.addWidget(self.HumPortBox)
        
        self.HumBaudBox = QtWidgets.QComboBox(self.tab1)
        self.HumBaudBox.setObjectName("HumBaudBox")
        self.HumBaudBox.addItems(["9600", "4800", "9600","19200", "38400", "57600", "115200"])
        self.HumHLayout_1.addWidget(self.HumBaudBox)

        self.HumsaveDirectoryButton = QtWidgets.QPushButton(self.tab1)
        self.HumsaveDirectoryButton.setObjectName("HumsaveDirectoryButton")
        self.HumsaveDirectoryButton.setText("File Directory")
        self.HumHLayout_1.addWidget(self.HumsaveDirectoryButton)

        self.HumLogButton = QtWidgets.QPushButton(self.tab1)
        self.HumLogButton.setObjectName("HumLogButton")
        self.HumLogButton.setText("Log Humidity")
        self.HumHLayout_1.addWidget(self.HumLogButton)
        
        self.HumfileLabel = QtWidgets.QLabel(self.tab1)
        self.HumfileLabel.setObjectName("HumfileLabel")
        self.HumHLayout_1.addWidget(self.HumfileLabel)
        
        self.verticalLayout.addLayout(self.HumHLayout_1)

        # Sub Hum 2
        self.HumHLayout_2 = QtWidgets.QHBoxLayout()
        self.HumHLayout_2.setObjectName("HumHLayout_2")

        self.HumVLayout_2_1 = QtWidgets.QVBoxLayout()
        self.HumVLayout_2_1.setObjectName("HumVLayout_2_1")
        self.HumHLayout_2.addLayout(self.HumVLayout_2_1)

        self.Humlabel1 = QtWidgets.QLabel(self.tab1)
        self.Humlabel1.setObjectName("Humlabel2")
        self.Humlabel1.setText(f"RH: --")
        self.Humlabel1.setStyleSheet(f"font-weight: bold; font-size: 14px; color: rgb(190, 17, 17); background-color: white; border: 1px solid black;")
        self.Humlabel1.setFixedSize(100, 40)
        self.HumVLayout_2_1.addWidget(self.Humlabel1)

        self.Humlabel2 = QtWidgets.QLabel(self.tab1)
        self.Humlabel2.setObjectName("Humlabel2")
        self.Humlabel2.setText(f"Tmp: --")
        self.Humlabel2.setStyleSheet(f"font-weight: bold; font-size: 14px; color: rgb(0, 184, 245) ; background-color: white; border: 1px solid black;")
        self.Humlabel2.setFixedSize(100, 40)
        self.HumVLayout_2_1.addWidget(self.Humlabel2)

        self.Humlabel3 = QtWidgets.QLabel(self.tab1)
        self.Humlabel3.setObjectName("Humlabel2")
        self.Humlabel3.setText(f"Dew: --")
        self.Humlabel3.setStyleSheet(f"font-weight: bold; font-size: 14px; color: black ; background-color: white; border: 1px solid black;")
        self.Humlabel3.setFixedSize(100, 40)
        self.HumVLayout_2_1.addWidget(self.Humlabel3)

        self.HumclearButton = QtWidgets.QPushButton(self.tab1)
        self.HumclearButton.setMaximumSize(QtCore.QSize(60, 16777215))
        self.HumclearButton.setObjectName("HumclearButton")
        self.HumclearButton.setText("Clear")
        self.HumVLayout_2_1.addWidget(self.HumclearButton)
        
        self.HumPlotWidget = PlotWidget(self.tab1)
        self.HumPlotWidget.setMinimumSize(QtCore.QSize(348,305))
        self.HumPlotWidget.setObjectName("HumPlotWidget")
        self.HumHLayout_2.addWidget(self.HumPlotWidget)
        
        self.HumPlotWidget2 = PlotWidget(self.tab1)
        self.HumPlotWidget2.setMinimumSize(QtCore.QSize(200,0))
        self.HumPlotWidget2.setObjectName("HumPlotWidget2")
        self.HumHLayout_2.addWidget(self.HumPlotWidget2)
        
        self.verticalLayout.addLayout(self.HumHLayout_2)
        
        # For temperature
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        
        self.TempPortBox = QtWidgets.QComboBox(self.tab1)
        self.TempPortBox.setObjectName("TempPortBox")
        self.horizontalLayout_2.addWidget(self.TempPortBox)
        
        self.TempBaudBox = QtWidgets.QComboBox(self.tab1)
        self.TempBaudBox.setObjectName("TempBaudBox")
        self.TempBaudBox.addItems(["38400", "4800", "9600","19200", "57600", "115200"])
        self.horizontalLayout_2.addWidget(self.TempBaudBox)
        
        self.saveDirectoryButton = QtWidgets.QPushButton(self.tab1)
        self.saveDirectoryButton.setObjectName("saveDirectoryButton")
        self.saveDirectoryButton.setText("File Directory")
        self.horizontalLayout_2.addWidget(self.saveDirectoryButton)

        self.TempLogButton = QtWidgets.QPushButton(self.tab1)
        self.TempLogButton.setObjectName("TempLogButton")
        self.TempLogButton.setText("Log Temperature")
        self.horizontalLayout_2.addWidget(self.TempLogButton)
        
        self.fileLabel = QtWidgets.QLabel(self.tab1)
        self.fileLabel.setObjectName("fileLabel")
        self.horizontalLayout_2.addWidget(self.fileLabel)

        self.verticalLayout.addLayout(self.horizontalLayout_2)
        
        # Sub Temp 2
        self.TempHLayout_2 = QtWidgets.QHBoxLayout()
        self.TempHLayout_2.setObjectName("TempHLayout_2")

        self.TempVLayout_2_1 = QtWidgets.QVBoxLayout()
        self.TempVLayout_2_1.setObjectName("TempVLayout_2_1")
        self.TempHLayout_2.addLayout(self.TempVLayout_2_1)

        self.Templabel1 = QtWidgets.QLabel(self.tab1)
        self.Templabel1.setObjectName("Templabel1")
        self.Templabel1.setText(f"T1: --")
        self.Templabel1.setStyleSheet(f"font-weight: bold; font-size: 14px; color: rgb(183, 101, 224); background-color: white; border: 1px solid black;")
        self.Templabel1.setFixedSize(100, 40)
        self.TempVLayout_2_1.addWidget(self.Templabel1)

        self.Templabel2 = QtWidgets.QLabel(self.tab1)
        self.Templabel2.setObjectName("Templabel2")
        self.Templabel2.setText(f"T2: --")
        self.Templabel2.setStyleSheet(f"font-weight: bold; font-size: 14px; color: rgb(93, 131, 212); background-color: white; border: 1px solid black;")
        self.Templabel2.setFixedSize(100, 40)
        self.TempVLayout_2_1.addWidget(self.Templabel2)

        self.Templabel3 = QtWidgets.QLabel(self.tab1)
        self.Templabel3.setObjectName("Templabel3")
        self.Templabel3.setText(f"T3: --")
        self.Templabel3.setStyleSheet(f"font-weight: bold; font-size: 14px; color: rgb(49, 205, 222); background-color: white; border: 1px solid black;")
        self.Templabel3.setFixedSize(100, 40)
        self.TempVLayout_2_1.addWidget(self.Templabel3)

        self.Templabel4 = QtWidgets.QLabel(self.tab1)
        self.Templabel4.setObjectName("Templabel4")
        self.Templabel4.setText(f"T4: --")
        self.Templabel4.setStyleSheet(f"font-weight: bold; font-size: 14px; color: rgb(36, 214, 75); background-color: white; border: 1px solid black;")
        self.Templabel4.setFixedSize(100, 40)
        self.TempVLayout_2_1.addWidget(self.Templabel4)

        self.TempclearButton = QtWidgets.QPushButton(self.tab1)
        self.TempclearButton.setMaximumSize(QtCore.QSize(60, 16777215))
        self.TempclearButton.setObjectName("TempclearButton")
        self.TempclearButton.setText("Clear")
        self.TempVLayout_2_1.addWidget(self.TempclearButton)

        self.TempPlotWidget = PlotWidget(self.tab1)
        self.TempPlotWidget.setMinimumSize(QtCore.QSize(348,305))
        self.TempPlotWidget.setObjectName("TempPlotWidget")
        self.TempHLayout_2.addWidget(self.TempPlotWidget)
        
        self.TempPlotWidget2 = PlotWidget(self.tab1)
        self.TempPlotWidget2.setMinimumSize(QtCore.QSize(200,0))
        self.TempPlotWidget2.setObjectName("TempPlotWidget2")
        self.TempHLayout_2.addWidget(self.TempPlotWidget2)

        self.verticalLayout.addLayout(self.TempHLayout_2)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.startStopButton.setText(_translate("MainWindow", "Start Logging"))
        self.startStopButton.setStyleSheet("background-color: red; color: white")
        self.fileLabel.setText(_translate("MainWindow", "No Directory Selected"))
        self.HumfileLabel.setText(_translate("MainWindow", "No Directory Selected"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
