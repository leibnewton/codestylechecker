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
    
    @QtCore.pyqtSignature('')
    def on_pbRemove_clicked(self):
        print 'Remove'
        
    @QtCore.pyqtSignature('')
    def on_pbCheckNow_clicked(self):
        print 'Check Now'
        
    @QtCore.pyqtSignature('')
    def on_pbViewHtml_clicked(self):
        print 'View HTML'
        

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    dlg = CodeStyleCheckerDlg()
    dlg.show()
    app.exec_()
    