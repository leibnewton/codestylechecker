# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 15:08:04 2016

@author: navicloud
"""

from PyQt4 import QtCore, QtGui
import addfilesdlg_ui
import os, re, fnmatch
import subprocess

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
    
    def accept(self):
        #print 'accept'
        return super(AddFilesDlg, self).accept()
        
    @QtCore.pyqtSignature('')
    def on_pbBrowser_clicked(self):
        #print 'browser button clicked'
        pass
    
    def updatePreviewFromGit(self):
        rootDir = unicode(self.leDirectory.text())
        if not os.path.isdir(rootDir): return
        
        os.chdir(rootDir)
        try:
            res = subprocess.check_output('git status -s', shell=True)
            self.__filteredfiles__ = []
            for line in res.split(os.linesep):
                if not line: continue
                parts = line.split()
                if parts.startswith('M'):
                    self.__filteredfiles__.append(parts[1])
            self.lstPreview.clear()
            self.lstPreview.addItems(self.__filteredfiles__)
        except subprocess.CalledProcessError, e:
            QtGui.QMessageBox.critical(self, 'Error', 
            'Not a git repository (or any of the parent directories): .git')
    
    def updatePreview(self):
        rootDir = unicode(self.leDirectory.text())
        if not os.path.isdir(rootDir): return
        
        if not self.rbAllFiles.isChecked():
            return self.updatePreviewFromGit()
        
        recursive = self.chkRecursive.isChecked()
        if self.__allfiles__['path'] != rootDir or self.__allfiles__['recursive'] != recursive:
            self.__allfiles__['path']      = rootDir
            self.__allfiles__['recursive'] = recursive
            self.__allfiles__['files']     = [] #populate files
            for dirName, subdirList, fileList in os.walk(rootDir):
                dirName = os.path.relpath(dirName, rootDir) #get relative path
                self.__allfiles__['files'] += [os.path.join(dirName, f) for f in fileList]
                if not recursive: break
                
        ftext = self.leFilter.text()
        if not self.chkRegExp.isChecked(): #Unix shell-style wildcards
            ftext = fnmatch.translate(ftext)
            
        try:
            reobj = re.compile(ftext)
            self.__filteredfiles__ = [f for f in self.__allfiles__['files'] if reobj.match(f)]
        except re.error, e: #sre_constants.error
            self.__filteredfiles__ = []
            
        self.lstPreview.clear()
        self.lstPreview.addItems(self.__filteredfiles__)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    dlg = AddFilesDlg()
    dlg.show()
    app.exec_()
