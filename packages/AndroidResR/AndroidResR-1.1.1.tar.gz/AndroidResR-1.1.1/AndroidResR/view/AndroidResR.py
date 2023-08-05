# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AndroidResR/view/AndroidResR.ui'
#
# Created: Thu Nov  6 00:12:20 2014
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(794, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 281, 541))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.srcPath = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.srcPath.setObjectName(_fromUtf8("srcPath"))
        self.horizontalLayout.addWidget(self.srcPath)
        self.selectSrc = QtGui.QPushButton(self.verticalLayoutWidget)
        self.selectSrc.setObjectName(_fromUtf8("selectSrc"))
        self.horizontalLayout.addWidget(self.selectSrc)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.srcListWidget = QtGui.QListWidget(self.verticalLayoutWidget)
        self.srcListWidget.setObjectName(_fromUtf8("srcListWidget"))
        self.verticalLayout.addWidget(self.srcListWidget)
        self.verticalLayoutWidget_2 = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(500, 10, 281, 541))
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_2 = QtGui.QLabel(self.verticalLayoutWidget_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.destPath = QtGui.QLineEdit(self.verticalLayoutWidget_2)
        self.destPath.setObjectName(_fromUtf8("destPath"))
        self.horizontalLayout_2.addWidget(self.destPath)
        self.selectDest = QtGui.QPushButton(self.verticalLayoutWidget_2)
        self.selectDest.setObjectName(_fromUtf8("selectDest"))
        self.horizontalLayout_2.addWidget(self.selectDest)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.destListWidget = QtGui.QListWidget(self.verticalLayoutWidget_2)
        self.destListWidget.setObjectName(_fromUtf8("destListWidget"))
        self.verticalLayout_2.addWidget(self.destListWidget)
        self.transferIcons = QtGui.QPushButton(self.centralwidget)
        self.transferIcons.setGeometry(QtCore.QRect(380, 270, 31, 25))
        self.transferIcons.setObjectName(_fromUtf8("transferIcons"))
        self.killIcon = QtGui.QPushButton(self.centralwidget)
        self.killIcon.setGeometry(QtCore.QRect(380, 300, 31, 25))
        self.killIcon.setObjectName(_fromUtf8("killIcon"))
        self.webView = QtWebKit.QWebView(self.centralwidget)
        self.webView.setGeometry(QtCore.QRect(310, 60, 171, 200))
        self.webView.setAutoFillBackground(False)
        self.webView.setProperty("url", QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.colorBlack = QtGui.QRadioButton(self.centralwidget)
        self.colorBlack.setGeometry(QtCore.QRect(310, 30, 61, 20))
        self.colorBlack.setObjectName(_fromUtf8("colorBlack"))
        self.colorWhite = QtGui.QRadioButton(self.centralwidget)
        self.colorWhite.setGeometry(QtCore.QRect(370, 30, 61, 20))
        self.colorWhite.setChecked(True)
        self.colorWhite.setObjectName(_fromUtf8("colorWhite"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(310, 10, 121, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.resultView = QtWebKit.QWebView(self.centralwidget)
        self.resultView.setGeometry(QtCore.QRect(310, 340, 171, 200))
        self.resultView.setAutoFillBackground(False)
        self.resultView.setProperty("url", QtCore.QUrl(_fromUtf8("about:blank")))
        self.resultView.setObjectName(_fromUtf8("resultView"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 794, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setObjectName(_fromUtf8("menuView"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionRefresh = QtGui.QAction(MainWindow)
        self.actionRefresh.setObjectName(_fromUtf8("actionRefresh"))
        self.menuFile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionAbout)
        self.menuView.addAction(self.actionRefresh)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label.setText(_translate("MainWindow", "Source Iconset", None))
        self.srcPath.setPlaceholderText(_translate("MainWindow", "Path to iconset", None))
        self.selectSrc.setText(_translate("MainWindow", "Browse", None))
        self.label_2.setText(_translate("MainWindow", "App resources", None))
        self.destPath.setPlaceholderText(_translate("MainWindow", "Path to app res folder", None))
        self.selectDest.setText(_translate("MainWindow", "Browse", None))
        self.transferIcons.setToolTip(_translate("MainWindow", "Copy Icons to App", None))
        self.transferIcons.setText(_translate("MainWindow", "->", None))
        self.killIcon.setToolTip(_translate("MainWindow", "Remove Icons from App", None))
        self.killIcon.setText(_translate("MainWindow", "X-", None))
        self.colorBlack.setText(_translate("MainWindow", "Black", None))
        self.colorWhite.setText(_translate("MainWindow", "White", None))
        self.label_3.setText(_translate("MainWindow", "Background color", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.menuView.setTitle(_translate("MainWindow", "View", None))
        self.actionQuit.setText(_translate("MainWindow", "Quit", None))
        self.actionQuit.setShortcut(_translate("MainWindow", "Alt+F4", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionRefresh.setText(_translate("MainWindow", "Refresh", None))
        self.actionRefresh.setShortcut(_translate("MainWindow", "F5", None))

from PyQt4 import QtWebKit
