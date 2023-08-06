# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plot_preview.ui'
#
# Created: Wed May 14 15:26:23 2014
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

class Ui_PlotPreview(object):
    def setupUi(self, PlotPreview):
        PlotPreview.setObjectName(_fromUtf8("PlotPreview"))
        PlotPreview.resize(437, 524)
        self.verticalLayout = QtGui.QVBoxLayout(PlotPreview)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.autoUpdate = QtGui.QCheckBox(PlotPreview)
        self.autoUpdate.setEnabled(False)
        self.autoUpdate.setObjectName(_fromUtf8("autoUpdate"))
        self.horizontalLayout.addWidget(self.autoUpdate)
        spacerItem = QtGui.QSpacerItem(28, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.zoomIn = QtGui.QPushButton(PlotPreview)
        self.zoomIn.setEnabled(False)
        self.zoomIn.setMinimumSize(QtCore.QSize(32, 32))
        self.zoomIn.setMaximumSize(QtCore.QSize(32, 32))
        self.zoomIn.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/gtk-zoom-in.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.zoomIn.setIcon(icon)
        self.zoomIn.setObjectName(_fromUtf8("zoomIn"))
        self.horizontalLayout.addWidget(self.zoomIn)
        self.zoomOut = QtGui.QPushButton(PlotPreview)
        self.zoomOut.setEnabled(False)
        self.zoomOut.setMinimumSize(QtCore.QSize(32, 32))
        self.zoomOut.setMaximumSize(QtCore.QSize(32, 32))
        self.zoomOut.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/gtk-zoom-out.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.zoomOut.setIcon(icon1)
        self.zoomOut.setObjectName(_fromUtf8("zoomOut"))
        self.horizontalLayout.addWidget(self.zoomOut)
        self.zoom1 = QtGui.QPushButton(PlotPreview)
        self.zoom1.setEnabled(False)
        self.zoom1.setMinimumSize(QtCore.QSize(32, 32))
        self.zoom1.setMaximumSize(QtCore.QSize(32, 32))
        self.zoom1.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/gtk-zoom-100.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.zoom1.setIcon(icon2)
        self.zoom1.setObjectName(_fromUtf8("zoom1"))
        self.horizontalLayout.addWidget(self.zoom1)
        self.zoomFit = QtGui.QPushButton(PlotPreview)
        self.zoomFit.setEnabled(False)
        self.zoomFit.setMinimumSize(QtCore.QSize(32, 32))
        self.zoomFit.setMaximumSize(QtCore.QSize(32, 32))
        self.zoomFit.setText(_fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/gtk-zoom-fit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.zoomFit.setIcon(icon3)
        self.zoomFit.setObjectName(_fromUtf8("zoomFit"))
        self.horizontalLayout.addWidget(self.zoomFit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.imageView = QtGui.QGraphicsView(PlotPreview)
        self.imageView.setEnabled(False)
        self.imageView.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.TextAntialiasing)
        self.imageView.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.imageView.setObjectName(_fromUtf8("imageView"))
        self.verticalLayout.addWidget(self.imageView)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.imageList = QtGui.QComboBox(PlotPreview)
        self.imageList.setEnabled(False)
        self.imageList.setObjectName(_fromUtf8("imageList"))
        self.horizontalLayout_2.addWidget(self.imageList)
        self.buttonBox = QtGui.QDialogButtonBox(PlotPreview)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(PlotPreview)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PlotPreview.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PlotPreview.reject)
        QtCore.QMetaObject.connectSlotsByName(PlotPreview)

    def retranslateUi(self, PlotPreview):
        PlotPreview.setWindowTitle(_translate("PlotPreview", "Dialog", None))
        self.autoUpdate.setText(_translate("PlotPreview", "Auto-update", None))

from . import icons_rc
