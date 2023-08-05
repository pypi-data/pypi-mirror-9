# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_about.ui'
#
# Created: Fri Jan 30 01:48:16 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(439, 498)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtGui.QWidget(Form)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.banner = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.banner.sizePolicy().hasHeightForWidth())
        self.banner.setSizePolicy(sizePolicy)
        self.banner.setMaximumSize(QtCore.QSize(130, 130))
        self.banner.setText("")
        self.banner.setPixmap(QtGui.QPixmap(":/hlp.png"))
        self.banner.setScaledContents(True)
        self.banner.setAlignment(QtCore.Qt.AlignCenter)
        self.banner.setObjectName("banner")
        self.horizontalLayout.addWidget(self.banner)
        self.verticalLayout.addWidget(self.widget)
        self.textBrowser = QtGui.QTextBrowser(Form)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.textBrowser.setHtml(QtGui.QApplication.translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">Idea and prototype by Hellzed.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">Rewrite in Python by ngld.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">For feedback and updates go to:<br /></span><a href=\"http://www.hard-light.net/forums/index.php?topic=86364\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt; text-decoration: underline; color:#0000ff;\">http://www.hard-light.net/forums/index.php?topic=86364</span></a></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">The code is available at:<br /></span><a href=\"https://github.com/ngld/Knossos\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt; text-decoration: underline; color:#0000ff;\">https://github.com/ngld/Knossos</span></a><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\"><br /></span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans Serif\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">Dependencies:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Sans Serif\'; font-size:9pt;\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://python.org\"><span style=\" text-decoration: underline; color:#0000ff;\">Python</span></a> (2 or 3)</li>\n"
"<li style=\" font-family:\'Sans Serif\'; font-size:9pt;\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://qt-project.org/wiki/Category:LanguageBindings::PySide\"><span style=\" text-decoration: underline; color:#0000ff;\">PySide</span></a> or <a href=\"http://riverbankcomputing.co.uk/software/pyqt/intro\"><span style=\" text-decoration: underline; color:#0000ff;\">PyQt4</span></a> (UI)</li>\n"
"<li style=\" font-family:\'Sans Serif\'; font-size:9pt;\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.7-zip.org/\"><span style=\" text-decoration: underline; color:#0000ff;\">7-Zip</span></a> (extracts the downloaded archives)</li>\n"
"<li style=\" font-family:\'Sans Serif\'; font-size:9pt;\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://github.com/workhorsy/py-cpuinfo\"><span style=\" text-decoration: underline; color:#0000ff;\">py-cpuinfo</span></a> (detects CPU flags)</li>\n"
"<li style=\" font-family:\'Sans Serif\'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://pypi.python.org/pypi/semantic_version\"><span style=\" text-decoration: underline; color:#0000ff;\">semantic_version</span></a> (compares version numbers)</li>\n"
"<li style=\" font-family:\'Sans Serif\'; font-size:9pt;\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://pypi.python.org/pypi/six\"><span style=\" text-decoration: underline; color:#0000ff;\">six</span></a> (helps supporting Python 2 and 3 with a single codebase)</li>\n"
"<li style=\" font-family:\'Sans Serif\'; font-size:9pt;\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://pypi.python.org/pypi/requests\"><span style=\" text-decoration: underline; color:#0000ff;\">requests</span></a> (simplifies HTTP request handling)</li>\n"
"<li style=\" font-family:\'Sans Serif\'; font-size:9pt;\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://libsdl.org\"><span style=\" text-decoration: underline; color:#0000ff;\">SDL</span></a> (detects your graphic cards and joysticks)</li>\n"
"<li style=\" font-family:\'Sans Serif\'; font-size:9pt;\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://kcat.strangesoft.net/openal.html\"><span style=\" text-decoration: underline; color:#0000ff;\">OpenAL Soft</span></a> (detects your sound cards)</li></ul>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\"><br /></span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">This tool also uses </span><a href=\"http://constexpr.org/innoextract/\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt; text-decoration: underline; color:#0000ff;\">InnoExtract</span></a><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\"> to unpack the GOG installer.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:9pt;\">If you used the Windows installer or the DMG file for Mac OS, this program contains 7-Zip which is licensed under the GNU LGPL license.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

