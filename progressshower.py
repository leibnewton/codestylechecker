# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 15:38:26 2016

@author: navicloud
"""

from PyQt4 import QtCore, QtGui

class ProgressShower(QtGui.QDialog):
    def __init__(self, parent=None):
        super(ProgressShower, self).__init__(parent)

        self.txeMessage = QtGui.QTextEdit(self)
        self.txeMessage.setMinimumSize(QtCore.QSize(400, 240))
        self.txeMessage.setFrameShape(QtGui.QFrame.NoFrame)
        self.txeMessage.setReadOnly(True)

        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.addWidget(self.txeMessage)
        self.setLayout(self.horizontalLayout)

        self.setWindowTitle('cpplint Progress')
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.__msg = ''

    def write(self, msg):
        self.__msg += msg
        self.txeMessage.setText(self.__msg)

    def flush(self):
        pass

    def abouttoclose(self):
        QtCore.QTimer.singleShot(1000, self.close)

    def closeEvent(self, event):
        cursor = self.txeMessage.textCursor()
        if self.__msg and cursor.position(): #unicode(cursor.selectedText())
            self.__msg = '' # provide a flag
            event.ignore()
            return
        self.__msg = ''
        self.write('')
        self.accept()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    dlg = ProgressShower()
    dlg.show()
    text = 'hello world-'*10
    text = text[:-1] + '\n'
    dlg.write(text*30)
    QtCore.QTimer.singleShot(0, dlg.abouttoclose)
    app.exec_()
