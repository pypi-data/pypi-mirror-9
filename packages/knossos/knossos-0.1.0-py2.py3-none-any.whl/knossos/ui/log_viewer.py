# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/log_viewer.ui'
#
# Created: Fri Jan 30 01:48:16 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(648, 661)
        Dialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pathLabel = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.pathLabel.setFont(font)
        self.pathLabel.setObjectName("pathLabel")
        self.verticalLayout.addWidget(self.pathLabel)
        self.content = QtGui.QTextBrowser(Dialog)
        self.content.setObjectName("content")
        self.verticalLayout.addWidget(self.content)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "fs2_open.log", None, QtGui.QApplication.UnicodeUTF8))
        self.pathLabel.setText(QtGui.QApplication.translate("Dialog", "fs2_open.log", None, QtGui.QApplication.UnicodeUTF8))

