# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 15:08:04 2016

@author: navicloud
"""

from PyQt4 import QtCore, QtGui
import addfilesdlg_ui
import os, re, fnmatch
import subprocess

class CalledProcessError(Exception): pass
    
def check_output_with_emsg(cmd, shell = False):
    command_process = subprocess.Popen(cmd, 
                                       shell = shell, 
                                       stdout = subprocess.PIPE,
                                       stderr = subprocess.PIPE)
    status = command_process.wait()
    output,emsg = command_process.communicate()
    if status == 0:
        return output
    else:
        raise CalledProcessError(emsg)

class AddFilesDlg(QtGui.QDialog, addfilesdlg_ui.Ui_Dialog):
    '''
    Add Files Dialog
    '''
    
    def __init__(self, parent=None):
        super(AddFilesDlg, self).__init__(parent)
        
        self.__allfiles__ = {'path':'', 'recursive':True, 'files':[]}
        self.__filteredfiles__ = []
        
        self.setupUi(self)
        self.leDirectory.textChanged.connect(self.updatePreview) # editingFinished
        self.rbAllFiles.clicked.connect(self.updatePreview)
        self.leFilter.textChanged.connect(self.updatePreview)
        self.chkRegExp.clicked.connect(self.updatePreview)
        self.chkRecursive.clicked.connect(self.updatePreview)
        
        self.rbGitStatus.clicked.connect(self.updatePreviewFromGit)
        self.rbGitCommit.clicked.connect(self.updatePreviewFromGit)
        self.leCommit.textChanged.connect(self.updatePreviewFromGit)
    
    def getFiles(self):
        return self.__filteredfiles__[:]
    
    def getRootDir(self):
        rootDir = unicode(self.leDirectory.text())
        rootDir = os.path.expanduser(rootDir)
        return rootDir
    
    def accept(self):
        #print 'accept'
        return super(AddFilesDlg, self).accept()
        
    @QtCore.pyqtSignature('')
    def on_pbBrowser_clicked(self):
        #print 'browser button clicked'
        folderBrowser = QtGui.QFileDialog(self)
        folderBrowser.setFileMode(QtGui.QFileDialog.Directory)
        folderBrowser.setOption(QtGui.QFileDialog.ShowDirsOnly)
        if folderBrowser.exec_():
            self.leDirectory.setText(folderBrowser.selectedFiles()[0])
    
    def updatePreviewFromGit(self):
        self.__filteredfiles__ = []
        rootDir = self.getRootDir()
        if not os.path.isdir(rootDir):
            self.ShowErrorMessage('invalid directory.')            
            return
        
        os.chdir(rootDir)
        try:
            if self.rbGitStatus.isChecked():
                res = check_output_with_emsg('git status -s', shell=True)
                for line in res.split(os.linesep):
                    if not line: continue
                    parts = line.split()
                    if parts[0].startswith('M') or parts[0].startswith('A'):
                        self.__filteredfiles__.append(parts[1])
            elif self.rbGitCommit.isChecked():
                commitid = unicode(self.leCommit.text()).strip()
                if len(commitid) == 0: return
                command = 'git diff-tree --name-only -r --no-commit-id %s' % commitid
                res = check_output_with_emsg(command, shell=True)
                for line in res.split(os.linesep):
                    if not line: continue
                    self.__filteredfiles__.append(line)
            else:
                self.ShowErrorMessage('Unexpected status. Please contact developer.')
                return
            self.RefreshList()
        except CalledProcessError, e:
            self.ShowErrorMessage(e.message)

    def ShowErrorMessage(self, msg):
        self.lblErrorMsg.setText(msg)
        self.stackedWidget.setCurrentIndex(1)
    
    def ClearErrorMessage(self):
        self.stackedWidget.setCurrentIndex(0)
        
    def RefreshList(self):
        self.ClearErrorMessage()
        self.lstPreview.clear()
        self.lstPreview.addItems(self.__filteredfiles__)
    
    def updatePreview(self):
        self.__filteredfiles__ = []
        rootDir = self.getRootDir()
        if not os.path.isdir(rootDir):
            self.ShowErrorMessage('invalid directory.')
            return
        
        if not self.rbAllFiles.isChecked():
            return self.updatePreviewFromGit()
        
        recursive = self.chkRecursive.isChecked()
        if self.__allfiles__['path'] != rootDir or self.__allfiles__['recursive'] != recursive:
            self.__allfiles__['path']      = rootDir
            self.__allfiles__['recursive'] = recursive
            self.__allfiles__['files']     = [] #populate files
            for dirName, subdirList, fileList in os.walk(rootDir):
                dirName = os.path.relpath(dirName, rootDir) #get relative path
                if dirName == os.path.curdir:
                    self.__allfiles__['files'] += fileList
                else:
                    self.__allfiles__['files'] += [os.path.join(dirName, f) for f in fileList]
                if not recursive: break
                
        ftext = unicode(self.leFilter.text())
        if not self.chkRegExp.isChecked(): #Unix shell-style wildcards
            ftext = fnmatch.translate(ftext)
            
        try:
            reobj = re.compile(ftext)
            self.__filteredfiles__ = [f for f in self.__allfiles__['files'] if reobj.match(f)]
        except re.error, e: #sre_constants.error
            self.ShowErrorMessage(e.message)
            return
        self.RefreshList()

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    dlg = AddFilesDlg()
    dlg.show()
    app.exec_()
