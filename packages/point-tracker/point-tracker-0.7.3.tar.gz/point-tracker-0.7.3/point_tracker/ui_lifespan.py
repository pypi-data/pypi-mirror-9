# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lifespan.ui'
#
# Created: Wed May 14 15:26:22 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_ChangeLifespan(object):
    def setupUi(self, ChangeLifespan):
        ChangeLifespan.setObjectName(_fromUtf8("ChangeLifespan"))
        ChangeLifespan.resize(282, 220)
        self.gridLayout = QtGui.QGridLayout(ChangeLifespan)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ChangeLifespan)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.startImages = QtGui.QComboBox(ChangeLifespan)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startImages.sizePolicy().hasHeightForWidth())
        self.startImages.setSizePolicy(sizePolicy)
        self.startImages.setObjectName(_fromUtf8("startImages"))
        self.gridLayout.addWidget(self.startImages, 0, 1, 1, 1)
        self.created = QtGui.QCheckBox(ChangeLifespan)
        self.created.setEnabled(False)
        self.created.setObjectName(_fromUtf8("created"))
        self.gridLayout.addWidget(self.created, 1, 0, 1, 2)
        self.label_2 = QtGui.QLabel(ChangeLifespan)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.endImages = QtGui.QComboBox(ChangeLifespan)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.endImages.sizePolicy().hasHeightForWidth())
        self.endImages.setSizePolicy(sizePolicy)
        self.endImages.setObjectName(_fromUtf8("endImages"))
        self.gridLayout.addWidget(self.endImages, 2, 1, 1, 1)
        self.divides = QtGui.QCheckBox(ChangeLifespan)
        self.divides.setEnabled(False)
        self.divides.setObjectName(_fromUtf8("divides"))
        self.gridLayout.addWidget(self.divides, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ChangeLifespan)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)

        self.retranslateUi(ChangeLifespan)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ChangeLifespan.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ChangeLifespan.reject)
        QtCore.QObject.connect(self.created, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.startImages.setDisabled)
        QtCore.QObject.connect(self.divides, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.endImages.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(ChangeLifespan)

    def retranslateUi(self, ChangeLifespan):
        ChangeLifespan.setWindowTitle(_translate("ChangeLifespan", "Change lifespan of cell", None))
        self.label.setText(_translate("ChangeLifespan", "Start", None))
        self.created.setText(_translate("ChangeLifespan", "Created by division", None))
        self.label_2.setText(_translate("ChangeLifespan", "End", None))
        self.divides.setText(_translate("ChangeLifespan", "Divides", None))

