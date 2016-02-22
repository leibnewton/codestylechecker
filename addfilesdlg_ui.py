# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addfilesdlg.ui'
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
        Dialog.resize(527, 519)
        Dialog.setSizeGripEnabled(False)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.leDirectory = QtGui.QLineEdit(Dialog)
        self.leDirectory.setEnabled(True)
        self.leDirectory.setObjectName(_fromUtf8("leDirectory"))
        self.horizontalLayout.addWidget(self.leDirectory)
        self.pbBrowser = QtGui.QPushButton(Dialog)
        self.pbBrowser.setObjectName(_fromUtf8("pbBrowser"))
        self.horizontalLayout.addWidget(self.pbBrowser)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)
        self.rbAllFiles = QtGui.QRadioButton(Dialog)
        self.rbAllFiles.setObjectName(_fromUtf8("rbAllFiles"))
        self.gridLayout.addWidget(self.rbAllFiles, 0, 1, 1, 1)
        self.leFilter = QtGui.QLineEdit(Dialog)
        self.leFilter.setEnabled(False)
        self.leFilter.setObjectName(_fromUtf8("leFilter"))
        self.gridLayout.addWidget(self.leFilter, 0, 2, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.chkRegExp = QtGui.QCheckBox(Dialog)
        self.chkRegExp.setEnabled(False)
        self.chkRegExp.setChecked(True)
        self.chkRegExp.setObjectName(_fromUtf8("chkRegExp"))
        self.horizontalLayout_2.addWidget(self.chkRegExp)
        self.chkRecursive = QtGui.QCheckBox(Dialog)
        self.chkRecursive.setEnabled(False)
        self.chkRecursive.setChecked(False)
        self.chkRecursive.setObjectName(_fromUtf8("chkRecursive"))
        self.horizontalLayout_2.addWidget(self.chkRecursive)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 0, 1, 1)
        self.rbGitStatus = QtGui.QRadioButton(Dialog)
        self.rbGitStatus.setChecked(True)
        self.rbGitStatus.setObjectName(_fromUtf8("rbGitStatus"))
        self.gridLayout.addWidget(self.rbGitStatus, 1, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(93, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 2, 0, 1, 1)
        self.rbGitCommit = QtGui.QRadioButton(Dialog)
        self.rbGitCommit.setCheckable(True)
        self.rbGitCommit.setChecked(False)
        self.rbGitCommit.setObjectName(_fromUtf8("rbGitCommit"))
        self.gridLayout.addWidget(self.rbGitCommit, 2, 1, 1, 1)
        self.leCommit = QtGui.QLineEdit(Dialog)
        self.leCommit.setEnabled(False)
        self.leCommit.setObjectName(_fromUtf8("leCommit"))
        self.gridLayout.addWidget(self.leCommit, 2, 2, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(108, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 2, 3, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout)
        self.stackedWidget = QtGui.QStackedWidget(Dialog)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.page = QtGui.QWidget()
        self.page.setObjectName(_fromUtf8("page"))
        self.verticalLayout = QtGui.QVBoxLayout(self.page)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(self.page)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.lstPreview = QtGui.QListWidget(self.page)
        self.lstPreview.setObjectName(_fromUtf8("lstPreview"))
        self.verticalLayout.addWidget(self.lstPreview)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName(_fromUtf8("page_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.page_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.lblErrorMsg = QtGui.QLabel(self.page_2)
        self.lblErrorMsg.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);"))
        self.lblErrorMsg.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblErrorMsg.setWordWrap(True)
        self.lblErrorMsg.setObjectName(_fromUtf8("lblErrorMsg"))
        self.verticalLayout_2.addWidget(self.lblErrorMsg)
        self.stackedWidget.addWidget(self.page_2)
        self.verticalLayout_3.addWidget(self.stackedWidget)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)
        self.label.setBuddy(self.leDirectory)
        self.label_2.setBuddy(self.lstPreview)

        self.retranslateUi(Dialog)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.rbGitCommit, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.leCommit.setEnabled)
        QtCore.QObject.connect(self.rbAllFiles, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.leFilter.setEnabled)
        QtCore.QObject.connect(self.rbAllFiles, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkRegExp.setEnabled)
        QtCore.QObject.connect(self.rbAllFiles, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkRecursive.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.leDirectory, self.pbBrowser)
        Dialog.setTabOrder(self.pbBrowser, self.rbAllFiles)
        Dialog.setTabOrder(self.rbAllFiles, self.rbGitStatus)
        Dialog.setTabOrder(self.rbGitStatus, self.lstPreview)
        Dialog.setTabOrder(self.lstPreview, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Add Files", None))
        self.label.setText(_translate("Dialog", "&Directory:", None))
        self.pbBrowser.setText(_translate("Dialog", "Browse...", None))
        self.rbAllFiles.setText(_translate("Dialog", "all files", None))
        self.chkRegExp.setText(_translate("Dialog", "正则", None))
        self.chkRecursive.setText(_translate("Dialog", "递归", None))
        self.rbGitStatus.setText(_translate("Dialog", "git status", None))
        self.rbGitCommit.setText(_translate("Dialog", "git commit", None))
        self.label_2.setText(_translate("Dialog", "Preview", None))
        self.lblErrorMsg.setText(_translate("Dialog", "error message", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

