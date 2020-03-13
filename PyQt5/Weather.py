# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Weather.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 391, 241))
        self.groupBox.setObjectName("groupBox")
        self.textEdit = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit.setGeometry(QtCore.QRect(20, 50, 351, 181))
        self.textEdit.setObjectName("textEdit")
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(100, 20, 91, 20))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(30, 20, 61, 21))
        self.label.setObjectName("label")
        self.queryBtn = QtWidgets.QPushButton(Dialog)
        self.queryBtn.setGeometry(QtCore.QRect(40, 250, 75, 23))
        self.queryBtn.setMaximumSize(QtCore.QSize(75, 16777215))
        self.queryBtn.setObjectName("queryBtn")
        self.clearBtn = QtWidgets.QPushButton(Dialog)
        self.clearBtn.setGeometry(QtCore.QRect(250, 250, 75, 23))
        self.clearBtn.setMaximumSize(QtCore.QSize(75, 16777215))
        self.clearBtn.setObjectName("clearBtn")
        
        self.retranslateUi(Dialog)
        self.queryBtn.clicked.connect(Dialog.queryWeather)
        self.clearBtn.clicked.connect(Dialog.clearText)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
    
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "城市天气预报"))
        self.comboBox.setItemText(0, _translate("Dialog", "北京"))
        self.comboBox.setItemText(1, _translate("Dialog", "上海"))
        self.comboBox.setItemText(2, _translate("Dialog", "天津"))
        self.label.setText(_translate("Dialog", "城市"))
        self.queryBtn.setText(_translate("Dialog", "查询"))
        self.clearBtn.setText(_translate("Dialog", "清空"))
