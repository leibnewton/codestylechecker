#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 14:46:54 2016

@author: navicloud
"""

import sys, os, tempfile
from PyQt4 import QtCore, QtGui, QtWebKit
import cpplint, cpplint_htmlreport
import RedirectStdStreams as redirect
import addfilesdlg, progressshower
import codestylecheckerdlg_ui
import resources_qrc

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
        self.__shower = progressshower.ProgressShower()
        self.__webView = None
        self.setWindowIcon(QtGui.QIcon(':/stylechecker.png'))

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
        self.pbCheckNow.setVisible(hasNodes)
        self.pbViewHtml.setVisible(False)
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
        ecnt = self.cpplint()
        self.__isDirty = False
        self.pbCheckNow.setVisible(False)
        self.pbViewHtml.setVisible(ecnt > 0)

    def cpplint(self):
        sys.argv = ['',
                '--threadnum=4',
                '--output=xml',
                self.__dstdir]
        self.__shower.show()
        xmlPath = os.path.join(self.__chkdir, 'result.xml')
        ecnt = 0
        with open(xmlPath, 'w') as xmlfile:
            with redirect.RedirectStdStreams(
            stdout=self.__shower,
            stderr=xmlfile,
            xit=redirect.lazyExit):
                cpplint.main()
                ecnt = cpplint._cpplint_state.error_count
                self.__shower.write('\n')
                if not ecnt:
                    self.__shower.write('<h2><font color="green">Passed. No error found!</font></h2>')
                else:
                    self.__shower.write('<h2><font color="red">Failed. Found %d errors!</font></h2>' % ecnt)

        if ecnt:
            with redirect.RedirectStdStreams(
            stdout=self.__shower,
            stderr=self.__shower,
            xit=redirect.lazyExit):
                self.htmlreport(xmlPath)
        self.__shower.abouttoclose()
        return ecnt

    def htmlreport(self, xmlPath):
        reportPath = os.path.join(self.__chkdir, 'report')
        removeDir(reportPath, False)
        # no need to enclose path with quotes
        sys.argv=['',
                  '--file=%s' % xmlPath,
                  '--report-dir=%s' % reportPath,
                  '--source-dir=%s' % self.__chkdir]
        cpplint_htmlreport.main()

    @QtCore.pyqtSignature('')
    def on_pbViewHtml_clicked(self):
        if self.treeFiles.topLevelItemCount() == 0:
            QtGui.QMessageBox.critical(self, 'Error', 'file list is empty')
            return
        if self.__isDirty:
            QtGui.QMessageBox.critical(self, 'Error', 'Please check first.')
            return
        if not self.__webView:
            self.__webView = QtWebKit.QWebView()
            self.__webView.setMinimumSize(1024, 768)
        htmlFile = os.path.join(self.__chkdir, 'report/index.html')
        self.__webView.load(QtCore.QUrl(htmlFile))
        self.__webView.show()

    def closeEvent(self, event):
        removeDir(self.__chkdir)
        removeDir(self.__dstdir)
        event.accept()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(':/stylechecker128.png'))
    dlg = CodeStyleCheckerDlg()
    dlg.show()
    app.exec_()
