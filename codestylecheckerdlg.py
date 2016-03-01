# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 14:46:54 2016

@author: navicloud
"""

from PyQt4 import QtCore, QtGui
import codestylecheckerdlg_ui
import addfilesdlg

class CodeStyleCheckerDlg(QtGui.QDialog, codestylecheckerdlg_ui.Ui_Dialog):
    '''
    Code Style Checker Dialog
    '''

    def __init__(self, parent=None):
        super(QtGui.QDialog, self).__init__(parent)
        self.setupUi(self)
        self.updateButtonStatus()

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
        self.pbViewHtml.setEnabled(hasNodes and True)

    @QtCore.pyqtSignature('')
    def on_pbCheckNow_clicked(self):
        if self.treeFiles.topLevelItemCount() == 0:
            QtGui.QMessageBox.critical(self, 'Error', 'file list is empty')
            return

    @QtCore.pyqtSignature('')
    def on_pbViewHtml_clicked(self):
        print 'View HTML'


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    dlg = CodeStyleCheckerDlg()
    dlg.show()
    app.exec_()
