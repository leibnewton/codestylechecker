# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'codestylecheckerdlg.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(575, 541)
        self.horizontalLayout = QtGui.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.treeFiles = QtGui.QTreeWidget(Dialog)
        self.treeFiles.setHeaderHidden(True)
        self.treeFiles.setColumnCount(1)
        self.treeFiles.setObjectName(_fromUtf8("treeFiles"))
        self.treeFiles.headerItem().setText(0, _fromUtf8("1"))
        self.treeFiles.header().setVisible(False)
        self.horizontalLayout.addWidget(self.treeFiles)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pbAdd = QtGui.QPushButton(Dialog)
        self.pbAdd.setObjectName(_fromUtf8("pbAdd"))
        self.verticalLayout.addWidget(self.pbAdd)
        self.pbRemove = QtGui.QPushButton(Dialog)
        self.pbRemove.setObjectName(_fromUtf8("pbRemove"))
        self.verticalLayout.addWidget(self.pbRemove)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.pbCheckNow = QtGui.QPushButton(Dialog)
        self.pbCheckNow.setObjectName(_fromUtf8("pbCheckNow"))
        self.verticalLayout.addWidget(self.pbCheckNow)
        self.pbViewHtml = QtGui.QPushButton(Dialog)
        self.pbViewHtml.setObjectName(_fromUtf8("pbViewHtml"))
        self.verticalLayout.addWidget(self.pbViewHtml)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.pbQuit = QtGui.QPushButton(Dialog)
        self.pbQuit.setObjectName(_fromUtf8("pbQuit"))
        self.verticalLayout.addWidget(self.pbQuit)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.pbQuit, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Code Style Checker", None))
        self.pbAdd.setText(_translate("Dialog", "&Add...", None))
        self.pbRemove.setText(_translate("Dialog", "&Remove", None))
        self.pbCheckNow.setText(_translate("Dialog", "&Check now", None))
        self.pbViewHtml.setText(_translate("Dialog", "&View HTML", None))
        self.pbQuit.setText(_translate("Dialog", "&Quit", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

