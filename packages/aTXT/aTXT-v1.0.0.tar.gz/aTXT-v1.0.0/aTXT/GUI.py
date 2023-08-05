#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jonathan S. Prieto
# @Date:   2015-01-15 18:49:00
# @Last Modified by:   Jonathan Prieto 
# @Last Modified time: 2015-01-15 19:36:45
import sys
import os
from aTXT import aTXT
from version import __version__
import walking as wk
import logging as log
import shutil as sh
import datetime
from latin2ascii import enconding_path
from kitchen.text.converters import getwriter
from PySide import QtGui, QtCore
from aTXT import DEBUG

homeDirectory = os.path.expanduser('~')

UTF8Writer = getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)


if DEBUG:
    log_filename = "LOG.txt"
else:
    log_filename = (
        "aTXT" + datetime.datetime.now().strftime("-%Y_%m_%d_%H-%M") + ".log")

if DEBUG:
    log.basicConfig(
        filename=log_filename, filemode='w',
        level=log.DEBUG,
        format='%(asctime)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )


def debug(msg, *args):
    if DEBUG:
        try:
            if type(msg) is type(lambda x: x):
                log.debug(msg.func_name)
                for arg in args:
                    log.debug("\t{0}".format(args))
            else:
                log.debug(msg + ' ' + ' '.join(args))
        except:
            log.debug(msg)
            for arg in args:
                log.debug(arg)


class ProcessLib(QtCore.QThread):
    procDone = QtCore.Signal(bool)
    partDone = QtCore.Signal(int)
    message = QtCore.Signal(str)
    FLAG = True

    def __init__(self, window):
        QtCore.QThread.__init__(self)
        self.window = window

    def debug(self, msg):
        try:
            debug(msg)
            if self.window.checkDebug.isChecked():
                self.message.emit(msg)
                print msg
        except:
            pass

    def run(self):

        self.debug('created QThread for ProcessLib')

        self.window.buttonStart.setEnabled(False)
        self.window.buttonStop.setEnabled(True)

        self.partDone.emit(0)

        try:
            if not os.path.exists(self.window.directory):
                self.debug("Directory does not exist")
        except Exception, e:
            self.debug("Fail review directory of search")
            return

        # manager = self.window.aTXT
        manager = aTXT()
        conta = 0

        for root, dirs, files in wk.walk(
                self.window.directory,
                level=self.window.level,
                tfiles=self.window.tfiles):

            if not self.FLAG:
                self.debug("Process stopped.")
                self.partDone(0)
                self.procDone(True)
                return

            self.debug('Directory: ' + root)

            try:
                if os.path.isdir(self.window.savein):
                    savein = os.path.join(root, self.window.savein)
                else:
                    savein = self.window.savein
            except Exception, e:

                self.debug("Something wrong with savein path: ")
                self.debug(savein)
                self.debug(e)

            try:
                if self.window.clean and os.path.exists(savein):
                    self.debug("Cleaning directory of " + savein)
                    sh.rmtree(savein)
                    self.debug("Remove " + savein + " DONE")
            except Exception, e:
                self.debug("Fail remove " + savein)

            if self.window.clean:
                continue

            self.debug("Starting process over files in Directory:")

            for f in files:
                conta += 1
                try:
                    porc = conta * 100.0
                    porc /= self.window.totalfiles
                except:
                    porc = 0

                filepath = os.path.join(root, f.name)
                self.debug("File #" + str(conta))
                self.debug("Filepath: " + filepath)

                try:
                    self.debug('Converting File ... ')
                    if filepath.lower().endswith('.pdf'):
                        self.debug(
                            'It\'ll take few seconds or minutes (OCR Reconigtion)  ')
                        self.debug('Please Wait')

                    manager.convert(
                        filepath=filepath,
                        uppercase=self.window.uppercase,
                        overwrite=self.window.overwrite,
                        savein=self.window.savein
                    )

                except Exception, e:
                    self.debug('Fail conversion aTXT calling from GUI.py')
                    self.debug(e)
                    self.debug("*" * 50)
                self.partDone.emit(porc)
                self.debug("File finished")

        self.debug("Process finished")
        self.partDone.emit(100)

        self.message.emit("Total Files: " + str(conta))
        try:
            manager.close()
        except:
            pass
        self.procDone.emit(True)
        self.exit()
        return


class WalkSize(QtCore.QThread):
    procDone = QtCore.Signal(bool)
    partDone = QtCore.Signal(int)
    message = QtCore.Signal(str)
    fileCount = QtCore.Signal(int)
    sizeCount = QtCore.Signal(str)
    pathCount = QtCore.Signal(str)
    Ready = QtCore.Signal(bool)

    FLAG = True

    def __init__(self, window):
        QtCore.QThread.__init__(self)
        self.window = window

    def debug(self, msg):
        try:
            debug(msg)
            if self.window.checkDebug.isChecked():
                self.message.emit(msg)
                print msg
        except:
            pass

    def run(self):

        self.debug('created QThread for WalkSize')

        self.window.buttonStart.setEnabled(False)
        self.window.buttonStop.setEnabled(True)

        self.debug('Trasversing directory')

        self.partDone.emit(0)

        try:
            if not os.path.exists(self.window.directory):
                self.debug("Directory does not exist")
            else:
                self.debug('Directory is valid')
        except:
            self.debug("Fail review directory of search")
            return

        dir = enconding_path(self.window.directory)
        sdirs = []
        level = self.window.level
        tfiles = self.window.tfiles

        self.sizeCount.emit(0)
        self.fileCount.emit(0)

        conta = 0
        tsize = 0
        factor = 0.1 if level != 0 else 0.01 * level
        self.debug("wk.walk starting")
        for root, dirs, files in wk.walk(dir, sdirs=sdirs, level=level, tfiles=tfiles):
            if not self.FLAG:
                self.debug("Process stopped.")
                self.partDone(0)
                self.procDone(True)
                return

            for f in files:
                conta += 1
                self.partDone.emit(conta * factor)
                self.debug("File #" + str(conta))

                filepath = os.path.join(root, f.name)
                filepath = enconding_path(filepath)
                tsize += os.path.getsize(filepath)
                self.pathCount.emit(filepath)

                self.debug("path: " + filepath)

        self.debug("wk.walk Finish")

        self.partDone.emit(100)
        self.fileCount.emit(conta)
        self.sizeCount.emit(str(tsize))

        self.procDone.emit(True)
        self.Ready.emit(True)
        self.exit()
        return


class Window(QtGui.QWidget):
    checked = QtCore.Qt.Checked
    unchecked = QtCore.Qt.Unchecked
    debug = True
    totalfiles = 0
    totalsize = 0

    def __init__(self):
        debug('GUI aTXT ' + __version__ + " " + "=" * 30)
        super(Window, self).__init__()
        debug('set configuration')
        self.config()
        debug('drawing box Directory')
        self.putBoxDirectory()
        debug('drawing box Options')
        self.putBoxOptions()
        self.setLayout(self.layout)
        # self.aTXT = aTXT()

    def closeEvent(self, event):
        # do stuff
        # try:
        #     self.aTXT.close()
        # except:
        #     pass
        self.debug("Exit")
        event.accept()

        # if self.canExit():
        # event.accept() # let the window close
        # else:
        #     event.ignore()

    def debug(self, msg):
        try:
            debug(msg)
            if self.checkDebug.isChecked():
                self.setStatus(msg)
                print msg
        except:
            pass

    def config(self):
        self.setWindowTitle("aTXT " + __version__)

        debug('set size of window',)
        self.setFixedSize(650, 500)

        self.setContentsMargins(15, 15, 15, 15)
        self.layout = QtGui.QVBoxLayout()
        self.layout.addStretch(1)

    def putBoxDirectory(self):
        self.buttonDirectory = QtGui.QPushButton("Browser")
        self.buttonDirectory.clicked.connect(self.findDirectory)
        self.directoryLabel = QtGui.QLineEdit()
        self.directoryLabel.setText(homeDirectory)

        self.directoryLabel.setFixedSize(280, 20)
        self.directoryLabel.setAlignment(QtCore.Qt.AlignRight)

        self.boxDirectoryLayout = QtGui.QGridLayout()
        self.boxDirectoryLayout.addWidget(self.directoryLabel, 0, 1)
        self.boxDirectoryLayout.addWidget(self.buttonDirectory, 0, 0)

        label = QtGui.QLabel()
        label.setText("Level:")

        self.depth_search = QtGui.QSpinBox()
        self.depth_search.setMinimum(0)
        self.depth_search.setMaximum(100)
        # self.depth_search.setValue(1)
        self.depth_search.setFixedSize(50, 25)

        self.boxDirectoryLayout.addWidget(label, 0, 4)
        self.boxDirectoryLayout.addWidget(self.depth_search, 0, 5)

        self.boxDirectory = QtGui.QGroupBox("Directory")
        self.boxDirectory.setLayout(self.boxDirectoryLayout)
        self.layout.addWidget(self.boxDirectory)

    def findDirectory(self):
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                           "Select Root Directory",
                                                           self.directoryLabel.text(), options)
        if directory:
            self.directoryLabel.setText(directory)

    def setDirectorySaveIn(self):
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                           "Save In",
                                                           self.saveinLabel.text(), options)
        if directory:
            self.saveinLabel.setText(directory)

    def putBoxOptions(self):
        # TYPE FILES
        self.checkPDF = QtGui.QCheckBox(".pdf")
        self.checkPDF.setCheckState(self.checked)

        self.heroPDF = QtGui.QComboBox()
        self.heroPDF.addItems(['xpdf', 'pdfminer'])

        self.checkDOCX = QtGui.QCheckBox(".docx")
        self.checkDOCX.setCheckState(self.checked)

        self.checkDAT = QtGui.QCheckBox(".dat")
        self.checkDAT.setCheckState(self.checked)

        self.heroDOCX = QtGui.QComboBox()
        self.heroDOCX.addItems(['xml', 'python-docx'])
        self.checkDOC = QtGui.QCheckBox(".doc")
        self.checkDOC.setCheckState(self.checked)

        if not sys.platform in ["win32"]:
            self.checkDOC.setCheckState(self.unchecked)
            self.checkDOC.setEnabled(False)

        layout = QtGui.QGridLayout()

        layout.addWidget(QtGui.QLabel("Type"), 0, 0)
        layout.addWidget(QtGui.QLabel("Library"), 0, 1)
        layout.addWidget(self.checkPDF, 1, 0)
        layout.addWidget(self.heroPDF, 1, 1)
        layout.addWidget(self.checkDOCX, 2, 0)
        layout.addWidget(self.heroDOCX, 2, 1)
        layout.addWidget(self.checkDOC, 3, 0)
        layout.addWidget(self.checkDAT, 4, 0)

        self.boxTypeFiles = QtGui.QGroupBox("Types Files")
        self.boxTypeFiles.setLayout(layout)

        self.gridSettings = QtGui.QGridLayout()
        self.gridSettings.addWidget(self.boxTypeFiles, 0, 0)

        # SETTINGS
        self.checkUPPER_CASE = QtGui.QCheckBox("Content in Upper Case")

        self.saveinL = QtGui.QLabel("Save In:")
        self.saveinLabel = QtGui.QLineEdit("TXT")
        self.saveinLabel.setFixedSize(100, 20)
        self.saveinLabel.setToolTip("aTXT creates new folder\
            for each one that contains files of the search.")
        self.saveinBrowser = QtGui.QPushButton("...")
        self.saveinBrowser.clicked.connect(self.setDirectorySaveIn)

        self.checkOverwrite = QtGui.QCheckBox("Overwrite Files")
        self.checkOverwrite.setToolTip(
            "If there the .txt version of file, don't proccess file again with aTXT")
        self.checkOverwrite.setCheckState(self.checked)
        # debug
        self.checkClean = QtGui.QCheckBox("Clean Directory")
        self.checkClean.setToolTip("Remove Directories with name above enter")
        self.checkClean.setCheckState(self.unchecked)
        self.checkClean.setVisible(False)

        self.checkDebug = QtGui.QCheckBox("Debug")
        self.checkDebug.setCheckState(self.checked)

        layout = QtGui.QGridLayout()
        layout.addWidget(self.checkOverwrite, 0, 0)
        layout.addWidget(self.checkUPPER_CASE, 1, 0)
        layout.addWidget(self.saveinL, 3, 0)
        layout.addWidget(self.saveinLabel, 3, 1)
        layout.addWidget(self.saveinBrowser, 3, 2)
        layout.addWidget(self.checkDebug, 5, 0)
        layout.addWidget(self.checkClean, 5, 1)

        self.boxSettings = QtGui.QGroupBox("Settings")
        self.boxSettings.setLayout(layout)

        self.gridSettings.addWidget(self.boxSettings, 0, 1)
        self.layout.addLayout(self.gridSettings)

        # DETAILS

        self.progress_bar = QtGui.QProgressBar()
        frameStyle = QtGui.QFrame.Sunken | QtGui.QFrame.Panel
        self.current_process = QtGui.QTextEdit()
        self.current_process.setFrameStyle(frameStyle)

        self.boxDetails = QtGui.QGroupBox("Details")

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.current_process)
        self.boxDetails.setLayout(layout)
        self.layout.addWidget(self.boxDetails)

        # ACTIONS
        self.buttonReset = QtGui.QPushButton("Reset")
        self.buttonReset.clicked.connect(self.resetOptions)

        self.buttonScan = QtGui.QPushButton("Scan")
        self.buttonScan.clicked.connect(self.scanDir)

        self.buttonStop = QtGui.QPushButton("Stop")
        self.buttonStop.setEnabled(False)
        self.buttonStop.clicked.connect(self.stopProcess)

        self.buttonStart = QtGui.QPushButton("Execute")
        self.buttonStart.setEnabled(False)
        self.buttonStart.clicked.connect(self.startProcess)

        box = QtGui.QGroupBox("Actions")
        layout = QtGui.QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.addWidget(self.buttonReset, 0, 0)
        layout.addWidget(self.buttonScan, 0, 1)
        layout.addWidget(self.buttonStop, 0, 5)
        layout.addWidget(self.buttonStart, 0, 6)
        box.setLayout(layout)
        self.layout.addWidget(box)

    def resetOptions(self):
        self.setEnabled(True)
        # self.directoryLabel.setText(homeDirectory)
        self.depth_search.setValue(0)
        self.setProgress(0)
        self.checkPDF.setCheckState(self.checked)
        self.checkDOCX.setCheckState(self.checked)
        self.checkDAT.setCheckState(self.checked)

        self.checkDOC.setCheckState(self.checked)
        if not sys.platform in ["win32"]:
            self.checkDOC.setCheckState(self.unchecked)
            self.checkDOC.setEnabled(False)

        self.checkOverwrite.setCheckState(self.checked)
        # self.saveinLabel.setText("TXT")
        self.checkClean.setCheckState(self.unchecked)
        self.checkDebug.setCheckState(self.checked)
        self.checkUPPER_CASE.setCheckState(self.unchecked)
        self.buttonStart.setEnabled(False)
        self.buttonStop.setEnabled(False)
        self.buttonScan.setEnabled(True)
        self.current_process.setText("")
        return

    def fileCount(self, value):
        self.totalfiles = value

    def sizeCount(self, value):
        self.totalsize = value

    def pathCount(self, s):
        try:
            self.listfiles.append(s)
        except:
            self.listfiles = []
            self.listfiles.append(s)

    def scanDir(self):
        debug("")
        debug("from scanDir", "starting scanning")
        self.progress_bar.setValue(0)

        self.directory = self.directoryLabel.text()

        debug("directory:" + self.directory)

        self.level = self.depth_search.text()
        try:
            self.level = int(self.level)
        except:
            debug('Fail casting for number level')

        debug("level:" + str(self.level))

        self.tfiles = []
        if self.checkPDF.isChecked():
            self.tfiles.append('.pdf')
        if self.checkDOCX.isChecked():
            self.tfiles.append('.docx')
        if self.checkDOC.isChecked():
            self.tfiles.append('.doc')
        if self.checkDAT.isChecked():
            self.tfiles.append('.dat')

        debug("tfiles:", self.tfiles)

        self.setStatus('Calculating the total size of files ...')
        self.totalfiles, self.totalsize = [0] * 2
        self.listfiles = []

        if len(self.tfiles) > 0:
            debug('Starting Walking over Directory')

            self.thread = WalkSize(self)
            self.thread.partDone.connect(self.setProgress)
            self.thread.procDone.connect(self.fin)
            self.thread.Ready.connect(self.Ready)

            self.thread.message.connect(self.setStatus)
            self.thread.fileCount.connect(self.fileCount)
            self.thread.sizeCount.connect(self.sizeCount)
            self.thread.pathCount.connect(self.pathCount)

            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
            self.thread.start()

        debug("Options:")
        self.savein = self.saveinLabel.text()

        debug('savein:' + self.savein)

        self.heroes = [self.heroPDF.currentText(), self.heroDOCX.currentText()]
        debug('heroes: ' + str(self.heroes))

        debug('debug: ' + str(self.debug))

        self.clean = self.checkClean.isChecked()
        debug('clean: ' + str(self.clean))

        self.uppercase = self.checkUPPER_CASE.isChecked()
        debug("uppercase: " + str(self.uppercase))

        self.overwrite = self.checkOverwrite.isChecked()
        debug('overwrite: ' + str(self.overwrite))
        return

    def Ready(self):

        self.debug("Ready")
        self.debug("Total Files: " + str(self.totalfiles))
        self.debug("Total Size: " + wk.size_str(self.totalsize))
        self.debug("Type Files: " + str(self.tfiles))

        try:
            self.stopProcess()
        except:
            pass
        try:
            del self.thread
        except:
            pass

        if self.totalfiles > 0:
            self.buttonStop.setEnabled(False)
            self.buttonScan.setEnabled(False)
            self.buttonStart.setEnabled(True)
        else:
            self.buttonScan.setEnabled(True)
            self.buttonReset.setEnabled(True)
        return

    def stopProcess(self):
        try:
            self.thread.FLAG = False
            self.thread.terminate()
            if self.thread.isRunning():
                self.stopProcess()
                return
            self.buttonStop.setEnabled(False)
            self.buttonScan.setEnabled(True)
            self.buttonReset.setEnabled(True)
            self.boxDetails.setEnabled(True)
            self.progress_bar.reset()
            # self.progress_bar.setEnabled(False)
        except:
            pass
        self.setEnabled(True)
        return

    def startProcess(self):
        if len(self.listfiles) == 0:
            self.debug("There's not nothing to convert.")
            self.buttonStart.setEnabled(False)
            return
        try:
            del self.thread
        except:
            pass

        self.thread = ProcessLib(self)
        self.thread.partDone.connect(self.setProgress)
        self.thread.procDone.connect(self.fin)
        self.thread.message.connect(self.setStatus)
        self.buttonStop.setEnabled(True)
        self.buttonScan.setEnabled(False)
        self.buttonReset.setEnabled(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.thread.start()
        self.setEnabled(False)
        return

    def setEnabled(self, value):
        self.boxDirectory.setEnabled(value)
        self.boxSettings.setEnabled(value)
        self.boxTypeFiles.setEnabled(value)
        return

    def setStatus(self, menssage):
        if self.checkDebug.isChecked():
            self.current_process.append(menssage)
        else:
            self.current_process.setText(menssage)
        self.current_process.moveCursor(QtGui.QTextCursor.End)

    def setProgress(self, value):
        if value > 100:
            value = 100
        self.progress_bar.setValue(value)

    def fin(self):
        self.progress_bar.reset()
        self.stopProcess()


def main():
    app = QtGui.QApplication(sys.argv)
    wds = Window()
    wds.show()
    sys.exit(app.exec_())
    del wds

if __name__ == "__main__":
    main()
