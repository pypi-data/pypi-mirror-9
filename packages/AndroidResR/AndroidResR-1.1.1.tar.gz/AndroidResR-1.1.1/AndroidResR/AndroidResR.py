#!/usr/bin/env python
# coding=utf-8
import os
from os import listdir, remove
from os.path import join, isfile
import sys
from shutil import copyfile
from PyQt4 import QtGui, QtCore
from view.AndroidResR import Ui_MainWindow
from util.ConfigLoader import ConfigLoader


__author__ = 'Victor Häggqvist'
__version__ = '1.1.1'

DRAWABLEDIRS = ["drawable-mdpi", "drawable-hdpi", "drawable-xhdpi", "drawable-xxhdpi", "drawable-xxxhdpi"]
DRAWABLESHORT = ["mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"]
DEBUG = True


def log(msg):
    if DEBUG:
        print(msg)


class Window(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.setup()

        self.config = ConfigLoader()
        self.currentIndex = None
        self.currentIndexDest = None
        self.searchpath = None

        self.srcIconset = self.config.get(self.config.SRCPATH)
        if self.srcIconset:
            self.srcPath.setText(self.srcIconset)
            self.populateSrcList()

        self.appResFolder = self.config.get(self.config.DESTPATH)
        if self.appResFolder:
            self.destPath.setText(self.appResFolder)
            self.scanResources()

    # bind signals and stuff
    # noinspection PyUnresolvedReferences
    def setup(self):
        QtCore.QTextCodec.setCodecForCStrings(QtCore.QTextCodec.codecForName("utf-8"))

        self.setWindowTitle("AndroidResR")
        self.setWindowIcon(QtGui.QIcon("ic_launcher.png"))
        self.setFixedSize(self.size())
        self.statusbar.setSizeGripEnabled(False)
        self.selectSrc.clicked.connect(self.openSrc)
        self.selectDest.clicked.connect(self.openDest)
        self.srcListWidget.itemSelectionChanged.connect(self.srcSelectionChange)
        self.colorWhite.clicked.connect(self.colorClick)
        self.colorBlack.clicked.connect(self.colorClick)
        self.webView.setHtml("Select icon to the left to preview")
        self.resultView.setStyleSheet("background:transparent")

        self.destListWidget.itemSelectionChanged.connect(self.destSelectionChange)

        self.transferIcons.clicked.connect(self.copyIcons)
        self.killIcon.clicked.connect(self.deleteIcon)

        self.actionRefresh.triggered.connect(self.refresh)
        self.actionQuit.triggered.connect(self.quit)
        self.actionAbout.triggered.connect(self.openAbout)

    def quit(self):
        sys.exit(0)

    # open select iconset dialog
    def openSrc(self):
        startdir = self.srcIconset if self.srcIconset else self.config.userHome
        opendir = QtGui.QFileDialog.getExistingDirectory(self, "Select Iconset Folder", startdir)
        if not opendir:
            return

        self.srcPath.setText(opendir)
        self.srcIconset = str(opendir)

        self.config.set(self.config.SRCPATH, opendir)
        self.populateSrcList()

    # Open select app resources dialog
    def openDest(self):
        opendir = QtGui.QFileDialog.getExistingDirectory(self, "Select App's res folder", self.config.userHome)
        if not opendir:
            return

        self.destPath.setText(opendir)
        self.appResFolder = str(opendir)
        self.config.set(self.config.DESTPATH, opendir)
        self.scanResources()

    # Load items in to source list
    def populateSrcList(self):
        self.searchpath = join(self.srcIconset, DRAWABLEDIRS[2])

        self.srcIconFiles = [ f for f in listdir(self.searchpath) if isfile(join(self.searchpath, f)) ]
        self.srcIconFiles.sort()

        self.srcListWidget.clear()
        for f in self.srcIconFiles:
            self.srcListWidget.addItem(f)
        self.srcListWidget.verticalScrollBar().setValue(0)

    # Load items in to app resources list
    def scanResources(self):
        self.appResources = []
        for res in DRAWABLEDIRS:
            resdir = join(self.appResFolder, res)
            resShort = res.split("-")[1]
            try:
                files = listdir(resdir)
            except OSError:
                continue
            for f in files:
                if isfile(join(resdir,f)):
                    index = self.getAppResourceIndex(f)
                    if index < 0:
                        self.appResources.append((f,[resShort]))
                    else:
                        self.appResources[index][1].append(resShort)

        self.destListWidget.clear()
        self.appResources = sorted(self.appResources)
        for d in self.appResources:
            self.destListWidget.addItem(d[0])

    # Get item index in app resources list by file name
    def getAppResourceIndex(self, file):
        i = 0
        for r in self.appResources:
            if r[0] == file:
                return i
            i += 1
        return -1

    # On selection change in src list
    def srcSelectionChange(self):
        if len(self.srcListWidget.selectedIndexes()) > 0:
            self.currentIndex = self.srcListWidget.selectedIndexes()[0].row()
            self.previewIcon()

    # On color checkbox clicked
    def colorClick(self):
        self.setPreview(self.currentPreviewIcon)

    # Update webview
    def setPreview(self, icon):
        self.currentPreviewIcon = icon
        file = icon.split('/')[-1]
        if 'white' in file:
            self.colorBlack.setChecked(True)
        elif 'black' in file:
            self.colorWhite.setChecked(True)

        self.webView.setHtml('<body style="background:'+self.getColor()+'"><img src="file://'+icon+'"></body>')

    # Preview currently selected icon
    def previewIcon(self):
        if self.currentIndex is None:
            return

        icon = join(self.searchpath, self.srcIconFiles[self.currentIndex])
        self.setPreview(icon)

    # Setup app icon to preview
    def previewDestIcon(self):
        if self.currentIndexDest is None:
            return

        thisResource = self.appResources[self.currentIndexDest]
        previewResolution = 'xhdpi'
        if 'xhdpi' not in thisResource[1]:
            previewResolution = thisResource[-1]

        icon = join(self.appResFolder, 'drawable-'+previewResolution, thisResource[0])
        self.setPreview(icon)

    # Get colors by radio buttons
    def getColor(self):
        if self.colorWhite.isChecked():
            return '#fff'
        elif self.colorBlack.isChecked():
            return '#000'

    def destSelectionChange(self):
        self.currentIndexDest = self.destListWidget.selectedIndexes()[0].row() if len(self.destListWidget.selectedIndexes()) else None
        self.displayResInfo()
        self.previewDestIcon()

    def displayResInfo(self):
        if self.currentIndexDest is None:
            return

        item = self.appResources[self.currentIndexDest]

        html = '<body style="font-size:12px; margin:0; padding;">'
        html += item[0]+"<br>"

        for dip in DRAWABLESHORT:
            if dip in item[1]:
                html += dip+': <span style="color:#0f0">yes</span><br>'
            else:
                html += dip+': <span style="color:#f00">no</span><br>'
        html += "</body>"
        self.resultView.setHtml(html)

    def copyIcons(self):
        item = self.srcIconFiles[self.currentIndex]

        for dip in DRAWABLEDIRS:
            fullsrc = join(self.srcIconset, dip, item)
            fulldest = join(self.appResFolder, dip, item)
            try:
                copyfile(fullsrc, fulldest)
            except IOError:
                os.mkdir(join(self.appResFolder, dip))
                copyfile(fullsrc, fulldest)
        self.scanResources()
        self.statusMsg("Icons copied", 10)

    def refresh(self):
        self.scanResources()
        self.populateSrcList()

    def deleteIcon(self):
        if self.currentIndexDest is None:
            return

        icon = self.appResources[self.currentIndexDest]
        dips = icon[1]

        for dip in dips:
            path = join(self.appResFolder, "drawable-"+dip, icon[0])
            remove(path)
        self.statusMsg("Removed %s" % icon[0], 10)
        self.scanResources()

    def statusMsg(self, msg, t):
        self.statusBar().showMessage(msg, t*1000)

    @staticmethod
    def openAbout():
        box = QtGui.QMessageBox()
        box.setWindowTitle("About")
        box.setText("""
AndroidResR %s
Copyright © 2014-2015 Victor Häggqvist
GPLv2
https://victorhaggqvist.com
https://github.com/victorhaggqvist/AndroidResR
        """%__version__)
        box.exec_()


def main():
    app = QtGui.QApplication(sys.argv)
    ui = Window()
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
