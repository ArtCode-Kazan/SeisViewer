# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\AppsBuilding\Packages\SeisRevisePackage\SeisRevise\Interface\QTForms\MainForm.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(746, 594)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 739, 581))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.pbCalculate = QtWidgets.QPushButton(self.tab)
        self.pbCalculate.setGeometry(QtCore.QRect(312, 200, 75, 23))
        self.pbCalculate.setObjectName("pbCalculate")
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.setGeometry(QtCore.QRect(4, 150, 439, 43))
        self.groupBox.setObjectName("groupBox")
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(10, 20, 137, 16))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setGeometry(QtCore.QRect(222, 20, 147, 16))
        self.label_7.setObjectName("label_7")
        self.sbMinFrequency = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.sbMinFrequency.setGeometry(QtCore.QRect(150, 16, 66, 22))
        self.sbMinFrequency.setProperty("value", 1.0)
        self.sbMinFrequency.setObjectName("sbMinFrequency")
        self.sbMaxFrequency = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.sbMaxFrequency.setGeometry(QtCore.QRect(366, 16, 66, 22))
        self.sbMaxFrequency.setProperty("value", 20.0)
        self.sbMaxFrequency.setObjectName("sbMaxFrequency")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(8, 78, 211, 16))
        self.label_3.setObjectName("label_3")
        self.pbSelectDirectory = QtWidgets.QPushButton(self.tab)
        self.pbSelectDirectory.setGeometry(QtCore.QRect(412, 4, 75, 23))
        self.pbSelectDirectory.setObjectName("pbSelectDirectory")
        self.dsbTimeInterval = QtWidgets.QDoubleSpinBox(self.tab)
        self.dsbTimeInterval.setGeometry(QtCore.QRect(222, 76, 51, 22))
        self.dsbTimeInterval.setMaximum(2.0)
        self.dsbTimeInterval.setProperty("value", 1.0)
        self.dsbTimeInterval.setObjectName("dsbTimeInterval")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_3.setGeometry(QtCore.QRect(4, 30, 703, 41))
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        self.label_2.setGeometry(QtCore.QRect(10, 15, 131, 16))
        self.label_2.setObjectName("label_2")
        self.sbSignalFrequency = QtWidgets.QSpinBox(self.groupBox_3)
        self.sbSignalFrequency.setEnabled(True)
        self.sbSignalFrequency.setGeometry(QtCore.QRect(140, 10, 66, 22))
        self.sbSignalFrequency.setMaximum(1000)
        self.sbSignalFrequency.setProperty("value", 250)
        self.sbSignalFrequency.setObjectName("sbSignalFrequency")
        self.label_9 = QtWidgets.QLabel(self.groupBox_3)
        self.label_9.setGeometry(QtCore.QRect(328, 14, 136, 16))
        self.label_9.setObjectName("label_9")
        self.sbResampleFrequency = QtWidgets.QSpinBox(self.groupBox_3)
        self.sbResampleFrequency.setGeometry(QtCore.QRect(464, 12, 71, 22))
        self.sbResampleFrequency.setMaximum(1000)
        self.sbResampleFrequency.setProperty("value", 250)
        self.sbResampleFrequency.setObjectName("sbResampleFrequency")
        self.label_8 = QtWidgets.QLabel(self.groupBox_3)
        self.label_8.setGeometry(QtCore.QRect(210, 12, 61, 20))
        self.label_8.setObjectName("label_8")
        self.cbNoResampleSignal = QtWidgets.QCheckBox(self.groupBox_3)
        self.cbNoResampleSignal.setGeometry(QtCore.QRect(540, 14, 161, 17))
        self.cbNoResampleSignal.setObjectName("cbNoResampleSignal")
        self.cbRecordType = QtWidgets.QComboBox(self.groupBox_3)
        self.cbRecordType.setGeometry(QtCore.QRect(274, 12, 49, 22))
        self.cbRecordType.setObjectName("cbRecordType")
        self.cbRecordType.addItem("")
        self.cbRecordType.addItem("")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(7, 5, 131, 16))
        self.label.setObjectName("label")
        self.leDirectoryPath = QtWidgets.QLineEdit(self.tab)
        self.leDirectoryPath.setGeometry(QtCore.QRect(137, 5, 269, 20))
        self.leDirectoryPath.setReadOnly(True)
        self.leDirectoryPath.setObjectName("leDirectoryPath")
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_2.setGeometry(QtCore.QRect(304, 102, 405, 43))
        self.groupBox_2.setObjectName("groupBox_2")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setGeometry(QtCore.QRect(10, 16, 121, 16))
        self.label_4.setObjectName("label_4")
        self.sbNoverlapSize = QtWidgets.QSpinBox(self.groupBox_2)
        self.sbNoverlapSize.setEnabled(False)
        self.sbNoverlapSize.setGeometry(QtCore.QRect(306, 14, 57, 22))
        self.sbNoverlapSize.setMaximum(100000)
        self.sbNoverlapSize.setProperty("value", 256)
        self.sbNoverlapSize.setObjectName("sbNoverlapSize")
        self.sbWindowSize = QtWidgets.QSpinBox(self.groupBox_2)
        self.sbWindowSize.setEnabled(False)
        self.sbWindowSize.setGeometry(QtCore.QRect(130, 16, 53, 22))
        self.sbWindowSize.setMaximum(100000)
        self.sbWindowSize.setProperty("value", 8192)
        self.sbWindowSize.setObjectName("sbWindowSize")
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setGeometry(QtCore.QRect(188, 18, 121, 16))
        self.label_5.setObjectName("label_5")
        self.label_24 = QtWidgets.QLabel(self.tab)
        self.label_24.setGeometry(QtCore.QRect(492, 8, 65, 16))
        self.label_24.setObjectName("label_24")
        self.cbFiletype = QtWidgets.QComboBox(self.tab)
        self.cbFiletype.setGeometry(QtCore.QRect(562, 4, 97, 22))
        self.cbFiletype.setObjectName("cbFiletype")
        self.cbFiletype.addItem("")
        self.cbFiletype.addItem("")
        self.teLog = QtWidgets.QTextEdit(self.tab)
        self.teLog.setGeometry(QtCore.QRect(10, 226, 703, 325))
        self.teLog.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.teLog.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.teLog.setReadOnly(True)
        self.teLog.setObjectName("teLog")
        self.groupBox_6 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_6.setGeometry(QtCore.QRect(4, 102, 291, 43))
        self.groupBox_6.setObjectName("groupBox_6")
        self.cbXComponent = QtWidgets.QCheckBox(self.groupBox_6)
        self.cbXComponent.setGeometry(QtCore.QRect(12, 20, 93, 17))
        self.cbXComponent.setChecked(True)
        self.cbXComponent.setObjectName("cbXComponent")
        self.cbYComponent = QtWidgets.QCheckBox(self.groupBox_6)
        self.cbYComponent.setGeometry(QtCore.QRect(108, 20, 95, 17))
        self.cbYComponent.setChecked(True)
        self.cbYComponent.setObjectName("cbYComponent")
        self.cbZComponent = QtWidgets.QCheckBox(self.groupBox_6)
        self.cbZComponent.setGeometry(QtCore.QRect(200, 20, 93, 17))
        self.cbZComponent.setChecked(True)
        self.cbZComponent.setObjectName("cbZComponent")
        self.groupBox_10 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_10.setGeometry(QtCore.QRect(450, 150, 261, 43))
        self.groupBox_10.setObjectName("groupBox_10")
        self.rbHourStructure = QtWidgets.QRadioButton(self.groupBox_10)
        self.rbHourStructure.setGeometry(QtCore.QRect(14, 20, 135, 17))
        self.rbHourStructure.setCheckable(True)
        self.rbHourStructure.setChecked(True)
        self.rbHourStructure.setObjectName("rbHourStructure")
        self.rbDeviceStructure = QtWidgets.QRadioButton(self.groupBox_10)
        self.rbDeviceStructure.setGeometry(QtCore.QRect(158, 20, 82, 17))
        self.rbDeviceStructure.setObjectName("rbDeviceStructure")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gbVisualizeParams = QtWidgets.QGroupBox(self.tab_2)
        self.gbVisualizeParams.setGeometry(QtCore.QRect(350, 186, 363, 69))
        self.gbVisualizeParams.setObjectName("gbVisualizeParams")
        self.label_12 = QtWidgets.QLabel(self.gbVisualizeParams)
        self.label_12.setGeometry(QtCore.QRect(10, 20, 141, 16))
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(self.gbVisualizeParams)
        self.label_13.setGeometry(QtCore.QRect(10, 44, 141, 16))
        self.label_13.setObjectName("label_13")
        self.dsbMinFrequencyVisualize = QtWidgets.QDoubleSpinBox(self.gbVisualizeParams)
        self.dsbMinFrequencyVisualize.setGeometry(QtCore.QRect(160, 20, 62, 22))
        self.dsbMinFrequencyVisualize.setProperty("value", 1.0)
        self.dsbMinFrequencyVisualize.setObjectName("dsbMinFrequencyVisualize")
        self.dsbMaxFrequencyVisualize = QtWidgets.QDoubleSpinBox(self.gbVisualizeParams)
        self.dsbMaxFrequencyVisualize.setGeometry(QtCore.QRect(160, 44, 62, 22))
        self.dsbMaxFrequencyVisualize.setProperty("value", 10.0)
        self.dsbMaxFrequencyVisualize.setObjectName("dsbMaxFrequencyVisualize")
        self.leReviseFolder = QtWidgets.QLineEdit(self.tab_2)
        self.leReviseFolder.setGeometry(QtCore.QRect(140, 6, 257, 20))
        self.leReviseFolder.setReadOnly(True)
        self.leReviseFolder.setObjectName("leReviseFolder")
        self.label_11 = QtWidgets.QLabel(self.tab_2)
        self.label_11.setGeometry(QtCore.QRect(6, 6, 129, 16))
        self.label_11.setObjectName("label_11")
        self.pbCalculation = QtWidgets.QPushButton(self.tab_2)
        self.pbCalculation.setGeometry(QtCore.QRect(316, 340, 75, 23))
        self.pbCalculation.setObjectName("pbCalculation")
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_4.setGeometry(QtCore.QRect(312, 76, 401, 43))
        self.groupBox_4.setObjectName("groupBox_4")
        self.label_14 = QtWidgets.QLabel(self.groupBox_4)
        self.label_14.setGeometry(QtCore.QRect(10, 20, 141, 16))
        self.label_14.setObjectName("label_14")
        self.label_15 = QtWidgets.QLabel(self.groupBox_4)
        self.label_15.setGeometry(QtCore.QRect(202, 20, 141, 16))
        self.label_15.setObjectName("label_15")
        self.sbTimeBegin = QtWidgets.QSpinBox(self.groupBox_4)
        self.sbTimeBegin.setGeometry(QtCore.QRect(152, 18, 47, 22))
        self.sbTimeBegin.setMaximum(10000000)
        self.sbTimeBegin.setProperty("value", 600)
        self.sbTimeBegin.setObjectName("sbTimeBegin")
        self.sbTimeEnd = QtWidgets.QSpinBox(self.groupBox_4)
        self.sbTimeEnd.setGeometry(QtCore.QRect(340, 16, 51, 22))
        self.sbTimeEnd.setMaximum(10000000)
        self.sbTimeEnd.setProperty("value", 1200)
        self.sbTimeEnd.setObjectName("sbTimeEnd")
        self.gbCorrelationParams = QtWidgets.QGroupBox(self.tab_2)
        self.gbCorrelationParams.setGeometry(QtCore.QRect(4, 184, 341, 71))
        self.gbCorrelationParams.setObjectName("gbCorrelationParams")
        self.label_17 = QtWidgets.QLabel(self.gbCorrelationParams)
        self.label_17.setGeometry(QtCore.QRect(10, 20, 141, 16))
        self.label_17.setObjectName("label_17")
        self.label_18 = QtWidgets.QLabel(self.gbCorrelationParams)
        self.label_18.setGeometry(QtCore.QRect(10, 46, 141, 16))
        self.label_18.setObjectName("label_18")
        self.dsbMinFrequencyCorrelation = QtWidgets.QDoubleSpinBox(self.gbCorrelationParams)
        self.dsbMinFrequencyCorrelation.setGeometry(QtCore.QRect(160, 20, 62, 22))
        self.dsbMinFrequencyCorrelation.setProperty("value", 1.0)
        self.dsbMinFrequencyCorrelation.setObjectName("dsbMinFrequencyCorrelation")
        self.dsbMaxFrequencyCorrelation = QtWidgets.QDoubleSpinBox(self.gbCorrelationParams)
        self.dsbMaxFrequencyCorrelation.setGeometry(QtCore.QRect(160, 46, 62, 22))
        self.dsbMaxFrequencyCorrelation.setProperty("value", 10.0)
        self.dsbMaxFrequencyCorrelation.setObjectName("dsbMaxFrequencyCorrelation")
        self.pbOpenFolder = QtWidgets.QPushButton(self.tab_2)
        self.pbOpenFolder.setGeometry(QtCore.QRect(402, 4, 75, 23))
        self.pbOpenFolder.setObjectName("pbOpenFolder")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_5.setGeometry(QtCore.QRect(4, 120, 707, 65))
        self.groupBox_5.setObjectName("groupBox_5")
        self.label_20 = QtWidgets.QLabel(self.groupBox_5)
        self.label_20.setGeometry(QtCore.QRect(10, 16, 121, 16))
        self.label_20.setObjectName("label_20")
        self.label_21 = QtWidgets.QLabel(self.groupBox_5)
        self.label_21.setGeometry(QtCore.QRect(12, 40, 115, 16))
        self.label_21.setObjectName("label_21")
        self.label_22 = QtWidgets.QLabel(self.groupBox_5)
        self.label_22.setGeometry(QtCore.QRect(312, 10, 171, 16))
        self.label_22.setObjectName("label_22")
        self.label_23 = QtWidgets.QLabel(self.groupBox_5)
        self.label_23.setGeometry(QtCore.QRect(330, 34, 151, 16))
        self.label_23.setObjectName("label_23")
        self.sbWindowSize_2 = QtWidgets.QSpinBox(self.groupBox_5)
        self.sbWindowSize_2.setGeometry(QtCore.QRect(132, 14, 61, 22))
        self.sbWindowSize_2.setMaximum(100000)
        self.sbWindowSize_2.setProperty("value", 8192)
        self.sbWindowSize_2.setObjectName("sbWindowSize_2")
        self.sbNoverlapSize_2 = QtWidgets.QSpinBox(self.groupBox_5)
        self.sbNoverlapSize_2.setGeometry(QtCore.QRect(130, 40, 71, 22))
        self.sbNoverlapSize_2.setMaximum(10000)
        self.sbNoverlapSize_2.setProperty("value", 4096)
        self.sbNoverlapSize_2.setObjectName("sbNoverlapSize_2")
        self.sbMedianFilterValue = QtWidgets.QSpinBox(self.groupBox_5)
        self.sbMedianFilterValue.setGeometry(QtCore.QRect(476, 8, 51, 22))
        self.sbMedianFilterValue.setMinimum(1)
        self.sbMedianFilterValue.setSingleStep(2)
        self.sbMedianFilterValue.setProperty("value", 7)
        self.sbMedianFilterValue.setObjectName("sbMedianFilterValue")
        self.sbMarmettFilterValue = QtWidgets.QSpinBox(self.groupBox_5)
        self.sbMarmettFilterValue.setGeometry(QtCore.QRect(476, 32, 51, 22))
        self.sbMarmettFilterValue.setProperty("value", 7)
        self.sbMarmettFilterValue.setObjectName("sbMarmettFilterValue")
        self.cbIsUsingMedianFilter = QtWidgets.QCheckBox(self.groupBox_5)
        self.cbIsUsingMedianFilter.setGeometry(QtCore.QRect(530, 10, 101, 17))
        self.cbIsUsingMedianFilter.setChecked(True)
        self.cbIsUsingMedianFilter.setObjectName("cbIsUsingMedianFilter")
        self.cbIUsingMarmettFilter = QtWidgets.QCheckBox(self.groupBox_5)
        self.cbIUsingMarmettFilter.setGeometry(QtCore.QRect(530, 34, 91, 17))
        self.cbIUsingMarmettFilter.setChecked(True)
        self.cbIUsingMarmettFilter.setObjectName("cbIUsingMarmettFilter")
        self.label_25 = QtWidgets.QLabel(self.tab_2)
        self.label_25.setGeometry(QtCore.QRect(484, 8, 65, 16))
        self.label_25.setObjectName("label_25")
        self.cbFiletype_2 = QtWidgets.QComboBox(self.tab_2)
        self.cbFiletype_2.setGeometry(QtCore.QRect(554, 4, 97, 22))
        self.cbFiletype_2.setObjectName("cbFiletype_2")
        self.cbFiletype_2.addItem("")
        self.cbFiletype_2.addItem("")
        self.groupBox_7 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_7.setGeometry(QtCore.QRect(6, 32, 703, 41))
        self.groupBox_7.setObjectName("groupBox_7")
        self.label_26 = QtWidgets.QLabel(self.groupBox_7)
        self.label_26.setGeometry(QtCore.QRect(10, 15, 131, 16))
        self.label_26.setObjectName("label_26")
        self.sbSignalFrequency_3 = QtWidgets.QSpinBox(self.groupBox_7)
        self.sbSignalFrequency_3.setEnabled(True)
        self.sbSignalFrequency_3.setGeometry(QtCore.QRect(140, 10, 66, 22))
        self.sbSignalFrequency_3.setReadOnly(False)
        self.sbSignalFrequency_3.setMaximum(1000)
        self.sbSignalFrequency_3.setProperty("value", 250)
        self.sbSignalFrequency_3.setObjectName("sbSignalFrequency_3")
        self.label_27 = QtWidgets.QLabel(self.groupBox_7)
        self.label_27.setGeometry(QtCore.QRect(328, 10, 136, 16))
        self.label_27.setObjectName("label_27")
        self.sbResampleFrequency_3 = QtWidgets.QSpinBox(self.groupBox_7)
        self.sbResampleFrequency_3.setGeometry(QtCore.QRect(464, 8, 71, 22))
        self.sbResampleFrequency_3.setMaximum(1000)
        self.sbResampleFrequency_3.setProperty("value", 250)
        self.sbResampleFrequency_3.setObjectName("sbResampleFrequency_3")
        self.label_28 = QtWidgets.QLabel(self.groupBox_7)
        self.label_28.setGeometry(QtCore.QRect(210, 10, 61, 20))
        self.label_28.setObjectName("label_28")
        self.cbNoResampleSignal_2 = QtWidgets.QCheckBox(self.groupBox_7)
        self.cbNoResampleSignal_2.setGeometry(QtCore.QRect(540, 10, 161, 17))
        self.cbNoResampleSignal_2.setObjectName("cbNoResampleSignal_2")
        self.cbRecordType_2 = QtWidgets.QComboBox(self.groupBox_7)
        self.cbRecordType_2.setGeometry(QtCore.QRect(272, 10, 49, 22))
        self.cbRecordType_2.setObjectName("cbRecordType_2")
        self.cbRecordType_2.addItem("")
        self.cbRecordType_2.addItem("")
        self.groupBox_8 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_8.setGeometry(QtCore.QRect(6, 76, 301, 43))
        self.groupBox_8.setObjectName("groupBox_8")
        self.cbXComponent_2 = QtWidgets.QCheckBox(self.groupBox_8)
        self.cbXComponent_2.setGeometry(QtCore.QRect(12, 20, 93, 17))
        self.cbXComponent_2.setChecked(True)
        self.cbXComponent_2.setObjectName("cbXComponent_2")
        self.cbYComponent_2 = QtWidgets.QCheckBox(self.groupBox_8)
        self.cbYComponent_2.setGeometry(QtCore.QRect(108, 20, 95, 17))
        self.cbYComponent_2.setChecked(True)
        self.cbYComponent_2.setObjectName("cbYComponent_2")
        self.cbZComponent_2 = QtWidgets.QCheckBox(self.groupBox_8)
        self.cbZComponent_2.setGeometry(QtCore.QRect(206, 20, 93, 17))
        self.cbZComponent_2.setChecked(True)
        self.cbZComponent_2.setObjectName("cbZComponent_2")
        self.teLog_2 = QtWidgets.QTextEdit(self.tab_2)
        self.teLog_2.setGeometry(QtCore.QRect(6, 366, 711, 179))
        self.teLog_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.teLog_2.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.teLog_2.setReadOnly(True)
        self.teLog_2.setObjectName("teLog_2")
        self.groupBox_9 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_9.setGeometry(QtCore.QRect(4, 256, 711, 83))
        self.groupBox_9.setObjectName("groupBox_9")
        self.cbGraphCorrelate = QtWidgets.QCheckBox(self.groupBox_9)
        self.cbGraphCorrelate.setGeometry(QtCore.QRect(350, 54, 221, 17))
        self.cbGraphCorrelate.setObjectName("cbGraphCorrelate")
        self.cbOneSpectrums = QtWidgets.QCheckBox(self.groupBox_9)
        self.cbOneSpectrums.setGeometry(QtCore.QRect(8, 58, 277, 17))
        self.cbOneSpectrums.setObjectName("cbOneSpectrums")
        self.cb_generalSpectrums = QtWidgets.QCheckBox(self.groupBox_9)
        self.cb_generalSpectrums.setGeometry(QtCore.QRect(350, 14, 345, 17))
        self.cb_generalSpectrums.setObjectName("cb_generalSpectrums")
        self.cbWriteSignalToFile = QtWidgets.QCheckBox(self.groupBox_9)
        self.cbWriteSignalToFile.setGeometry(QtCore.QRect(8, 18, 181, 17))
        self.cbWriteSignalToFile.setObjectName("cbWriteSignalToFile")
        self.cbSignalGraph = QtWidgets.QCheckBox(self.groupBox_9)
        self.cbSignalGraph.setGeometry(QtCore.QRect(8, 38, 201, 17))
        self.cbSignalGraph.setObjectName("cbSignalGraph")
        self.cbCorrelateToFile = QtWidgets.QCheckBox(self.groupBox_9)
        self.cbCorrelateToFile.setGeometry(QtCore.QRect(350, 34, 265, 17))
        self.cbCorrelateToFile.setObjectName("cbCorrelateToFile")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pbCalculate.setText(_translate("MainWindow", "Расчет"))
        self.groupBox.setTitle(_translate("MainWindow", "Визуализация"))
        self.label_6.setText(_translate("MainWindow", "Минимальная частота (Гц)"))
        self.label_7.setText(_translate("MainWindow", "Максимальная частота (Гц)"))
        self.label_3.setText(_translate("MainWindow", "Интервал создания спектрограмм (часы)"))
        self.pbSelectDirectory.setText(_translate("MainWindow", "Выбор папки"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Параметры сигнала"))
        self.label_2.setText(_translate("MainWindow", "Частота дискретизации"))
        self.label_9.setText(_translate("MainWindow", "Частота ресемплирования"))
        self.label_8.setText(_translate("MainWindow", "Тип записи"))
        self.cbNoResampleSignal.setText(_translate("MainWindow", "не ресемплировать сигнал"))
        self.cbRecordType.setItemText(0, _translate("MainWindow", "ZXY"))
        self.cbRecordType.setItemText(1, _translate("MainWindow", "XYZ"))
        self.label.setText(_translate("MainWindow", "Папка с данными сверки"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Параметры расчета"))
        self.label_4.setText(_translate("MainWindow", "Размер окна (отсчеты)"))
        self.label_5.setText(_translate("MainWindow", "Сдвиг окна (отсчеты)"))
        self.label_24.setText(_translate("MainWindow", "Тип файлов"))
        self.cbFiletype.setItemText(0, _translate("MainWindow", "Baikal7"))
        self.cbFiletype.setItemText(1, _translate("MainWindow", "Baikal8"))
        self.groupBox_6.setTitle(_translate("MainWindow", "Компоненты для обработки"))
        self.cbXComponent.setText(_translate("MainWindow", "X-компонента"))
        self.cbYComponent.setText(_translate("MainWindow", "Y-компонента"))
        self.cbZComponent.setText(_translate("MainWindow", "Z-компонента"))
        self.groupBox_10.setTitle(_translate("MainWindow", "Структура папок экспорта"))
        self.rbHourStructure.setText(_translate("MainWindow", "по часам (для сверки)"))
        self.rbDeviceStructure.setText(_translate("MainWindow", "по приборамэ"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Расчет 2D-спектрограмм"))
        self.gbVisualizeParams.setTitle(_translate("MainWindow", "Параметры визуализации спектров"))
        self.label_12.setText(_translate("MainWindow", "Минимальная частота (Гц)"))
        self.label_13.setText(_translate("MainWindow", "Максимальная частота (Гц)"))
        self.label_11.setText(_translate("MainWindow", "Папка c данными сверки"))
        self.pbCalculation.setText(_translate("MainWindow", "Расчет"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Интервал чистого участка сигнала"))
        self.label_14.setText(_translate("MainWindow", "Левая граница (секунды)"))
        self.label_15.setText(_translate("MainWindow", "Правая граница (секунды)"))
        self.gbCorrelationParams.setTitle(_translate("MainWindow", "Параметры расчета коэф-тов корреляции"))
        self.label_17.setText(_translate("MainWindow", "Минимальная частота (Гц)"))
        self.label_18.setText(_translate("MainWindow", "Максимальная частота (Гц)"))
        self.pbOpenFolder.setText(_translate("MainWindow", "Открыть"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Параметры расчета спектров"))
        self.label_20.setText(_translate("MainWindow", "Размер окна (отсчеты)"))
        self.label_21.setText(_translate("MainWindow", "Сдвиг окна (отсчеты)"))
        self.label_22.setText(_translate("MainWindow", "Параметр медианного фильтра"))
        self.label_23.setText(_translate("MainWindow", "Параметр marmett-фильтра"))
        self.cbIsUsingMedianFilter.setText(_translate("MainWindow", "использовать"))
        self.cbIUsingMarmettFilter.setText(_translate("MainWindow", "использовать"))
        self.label_25.setText(_translate("MainWindow", "Тип файлов"))
        self.cbFiletype_2.setItemText(0, _translate("MainWindow", "Baikal7"))
        self.cbFiletype_2.setItemText(1, _translate("MainWindow", "Baikal8"))
        self.groupBox_7.setTitle(_translate("MainWindow", "Параметры сигнала"))
        self.label_26.setText(_translate("MainWindow", "Частота дискретизации"))
        self.label_27.setText(_translate("MainWindow", "Частота ресемплирования"))
        self.label_28.setText(_translate("MainWindow", "Тип записи"))
        self.cbNoResampleSignal_2.setText(_translate("MainWindow", "не ресемплировать сигнал"))
        self.cbRecordType_2.setItemText(0, _translate("MainWindow", "ZXY"))
        self.cbRecordType_2.setItemText(1, _translate("MainWindow", "XYZ"))
        self.groupBox_8.setTitle(_translate("MainWindow", "Компоненты для обработки"))
        self.cbXComponent_2.setText(_translate("MainWindow", "X-компонента"))
        self.cbYComponent_2.setText(_translate("MainWindow", "Y-компонента"))
        self.cbZComponent_2.setText(_translate("MainWindow", "Z-компонента"))
        self.groupBox_9.setTitle(_translate("MainWindow", "Выходные данные"))
        self.cbGraphCorrelate.setText(_translate("MainWindow", "Создать график коэф-тов корреляции"))
        self.cbOneSpectrums.setText(_translate("MainWindow", "Создать графики спектров для каждого прибора"))
        self.cb_generalSpectrums.setText(_translate("MainWindow", "Создать обобщенный график сглаженных спектров"))
        self.cbWriteSignalToFile.setText(_translate("MainWindow", "Записать чистые куски в файл"))
        self.cbSignalGraph.setText(_translate("MainWindow", "Создать графики выборки сигнала"))
        self.cbCorrelateToFile.setText(_translate("MainWindow", "Записать матрицу коэф-тов корреляции в файл"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Расчет спектров и корреляций"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

