# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'message_selfNKCiFl.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QPushButton,
    QSizePolicy, QSpacerItem, QTextEdit, QWidget)
import app_page.assets.UI.apprcc_rc as apprcc_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(791, 91)
        Form.setMinimumSize(QSize(0, 32))
        self.horizontalLayout_3 = QHBoxLayout(Form)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QSize(0, 32))
        self.frame.setStyleSheet(u"#frame {\n"
"	background-color:  transparent;\n"
"}\n"
"#msg_text {\n"
"	width: auto;\n"
"	height: auto;\n"
"	font-size: 16px;\n"
"	background-color: #a9e97a;\n"
"	padding: 5px;\n"
"	border-radius: 6px;\n"
"}\n"
"#btn_avatar {\n"
"	padding: 0px;\n"
"	border-radius: 0px;\n"
"	border-radius: 6px;\n"
"}\n"
"\n"
"\n"
"\n"
"")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_3.setLineWidth(0)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.msg_text = QTextEdit(self.frame_3)
        self.msg_text.setObjectName(u"msg_text")
        self.msg_text.setUndoRedoEnabled(False)
        self.msg_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.msg_text.setReadOnly(True)
        self.msg_text.setOverwriteMode(True)

        self.horizontalLayout_2.addWidget(self.msg_text)


        self.horizontalLayout.addWidget(self.frame_3)

        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(36, 0))
        self.frame_2.setMaximumSize(QSize(32, 16777215))
        self.frame_2.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.frame_2.setStyleSheet(u"")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.btn_avatar = QPushButton(self.frame_2)
        self.btn_avatar.setObjectName(u"btn_avatar")
        self.btn_avatar.setGeometry(QRect(0, 0, 36, 36))
        self.btn_avatar.setMinimumSize(QSize(36, 36))
        self.btn_avatar.setMaximumSize(QSize(36, 36))
        self.btn_avatar.setStyleSheet(u"image: url(:/icon/assets/icon/user.png);")

        self.horizontalLayout.addWidget(self.frame_2)


        self.horizontalLayout_3.addWidget(self.frame)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.btn_avatar.setText("")
    # retranslateUi

