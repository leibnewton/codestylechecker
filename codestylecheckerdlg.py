# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 14:46:54 2016

@author: navicloud
"""

from PyQt4 import QtCore, QtGui
import codestylecheckerdlg_ui
import addfilesdlg
import os, tempfile

def removeDir(dirPath, removeRoot = True):
    for root, dirs, files in os.walk(dirPath, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    if removeRoot:
        os.rmdir(dirPath)

def makeFreshDir(rootDir, desiredName):
    res = os.path.join(rootDir, desiredName)
    while os.path.exists(res):
        res += '_'
    os.mkdir(res)
    return res

class CodeStyleCheckerDlg(QtGui.QDialog, codestylecheckerdlg_ui.Ui_Dialog):
    '''
    Code Style Checker Dialog
    '''

    def __init__(self, parent=None):
        super(CodeStyleCheckerDlg, self).__init__(parent)
        self.setupUi(self)
        self.updateButtonStatus()
        self.__isDirty = False
        self.__dstdir = makeFreshDir(tempfile.gettempdir(), 'csc')
        self.__chkdir = makeFreshDir(tempfile.gettempdir(), 'chk')

    @QtCore.pyqtSignature('')
    def on_pbAdd_clicked(self):
        addDlg = addfilesdlg.AddFilesDlg(self)
        if addDlg.exec_():
            files = addDlg.getFiles()
            rootDir = addDlg.getRootDir()
            if len(files) == 0: return
            dirNode = QtGui.QTreeWidgetItem(self.treeFiles, [QtCore.QString(rootDir)])
            for f in files:
                QtGui.QTreeWidgetItem(dirNode, [QtCore.QString(f)])
            self.treeFiles.expand(self.treeFiles.indexFromItem(dirNode))
            self.updateButtonStatus()

    @QtCore.pyqtSignature('')
    def on_pbRemove_clicked(self):
        item = self.treeFiles.currentItem()
        if not item:
            QtGui.QMessageBox.critical(self, 'Error', 'no item selected')
            return
        decision = QtGui.QMessageBox.question(self, 'Please Confirm',
                                             'Sure to remove the item?',
                                             QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel)
        if decision == QtGui.QMessageBox.Cancel:
            return
        index = self.treeFiles.currentIndex()
        parent = item.parent()
        if parent:
            parentIndex = index.parent()
            parent.takeChild(index.row())
            if parent.childCount() == 0:
                self.treeFiles.takeTopLevelItem(parentIndex.row())
                del parent
        else:
            self.treeFiles.takeTopLevelItem(index.row())
        del item
        self.updateButtonStatus()

    '''
    @QtCore.pyqtSignature('QTreeWidgetItem*,QTreeWidgetItem*')
    def on_treeFiles_currentItemChanged(self, cur, prev):
        print cur.text(0), prev.text(0) if prev else '<None>'
    '''

    def updateButtonStatus(self):
        hasNodes = self.treeFiles.topLevelItemCount() > 0
        self.pbRemove.setEnabled(hasNodes)
        self.pbCheckNow.setEnabled(hasNodes)
        self.pbViewHtml.setEnabled(False)
        self.__isDirty = True

    @QtCore.pyqtSignature('')
    def on_pbCheckNow_clicked(self):
        if self.treeFiles.topLevelItemCount() == 0:
            QtGui.QMessageBox.critical(self, 'Error', 'file list is empty')
            return
        if not self.__isDirty:
            QtGui.QMessageBox.information(self, 'Info', 'Already checked.')
            return
        removeDir(self.__dstdir, False)
        for np in xrange(self.treeFiles.topLevelItemCount()):
            pathItem = self.treeFiles.topLevelItem(np)
            curpath = unicode(pathItem.text(0))
            for nf in xrange(pathItem.childCount()):
                fileItem = pathItem.child(nf)
                filepath = unicode(fileItem.text(0))
                srcpath = os.path.join(curpath, filepath)
                filename = os.path.basename(filepath)
                while True: # handle identical file name
                    dstpath = os.path.join(self.__dstdir, filename)
                    if not os.path.exists(dstpath):
                        break
                    # handle identicle path: if they are the same file
                    if os.path.realpath(dstpath) == os.path.realpath(srcpath):
                        dstpath = ''
                        #print 'Fount same file', filepath
                        break
                    if len(filepath) > len(filename):
                        filename = filepath.replace('/', '_')
                    else:
                        filename = '_' + filename
                if dstpath: os.symlink(srcpath, dstpath)
        # check
        # generate xml and html in self.__chkdir
        self.__isDirty = False
        self.pbCheckNow.setEnabled(False)
        self.pbViewHtml.setEnabled(True)

    @QtCore.pyqtSignature('')
    def on_pbViewHtml_clicked(self):
        print 'View HTML'

    def accept(self):
        removeDir(self.__chkdir)
        removeDir(self.__dstdir)
        return super(CodeStyleCheckerDlg, self).accept()

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    dlg = CodeStyleCheckerDlg()
    dlg.show()
    app.exec_()
