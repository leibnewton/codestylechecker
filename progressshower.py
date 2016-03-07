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
        self.txeMessage.mousePressEvent = self.mousePress

        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.addWidget(self.txeMessage)
        self.setLayout(self.horizontalLayout)

        self.setWindowTitle('cpplint Progress')
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def showEvent(self, event):
        self.__enableSchedule = True
        return super(ProgressShower, self).showEvent(event)

    def write(self, msg):
        for c in ('\n', '\r'):
            if msg and msg[-1] == c:
                msg = msg[0:-1]
        self.txeMessage.append(msg)
        self.txeMessage.ensureCursorVisible()

    def flush(self):
        pass

    def abouttoclose(self):
        QtCore.QTimer.singleShot(1500, self._scheduleClose)

    def _scheduleClose(self):
        if self.__enableSchedule:
            self.close()

    def mousePress(self, event):
        self.__enableSchedule = False
        return QtGui.QTextEdit.mousePressEvent(self.txeMessage, event)

    def closeEvent(self, event):
        #cursor = self.txeMessage.textCursor()
        #print cursor.position(): #unicode(cursor.selectedText())
        self.txeMessage.clear()
        self.accept()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    dlg = ProgressShower()
    dlg.show()
    text = 'hello world-'*10
    text = text[:-1] + '\n'
    dlg.write(text*30)
    dlg.write('normal line\r')
    dlg.write('')
    dlg.write('\n')
    dlg.write('<h2><font color="green">Passed. No error found!</font></h2>')
    dlg.write('<h2><font color="red">Failed. 3 errors found!</font></h2>')
    QtCore.QTimer.singleShot(0, dlg.abouttoclose)
    app.exec_()
