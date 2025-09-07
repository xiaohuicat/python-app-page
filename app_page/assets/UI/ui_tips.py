# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tipscVzaRo.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QTextEdit, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(282, 82)
        font = QFont()
        font.setPointSize(15)
        Form.setFont(font)
        Form.setStyleSheet(u"#tips {\n"
"	color: #fff;\n"
"	background-color: #666;\n"
"	padding: 5px;\n"
"	border-radius: 8px;\n"
"}\n"
"\n"
"* {\n"
"  padding:0;\n"
"  margin:0;\n"
"  border:none;\n"
"  outline: none;\n"
"}\n"
"\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761 handle */\n"
"QScrollBar::handle::vertical{\n"
"  background: #fff;\n"
"  width: 4px;\n"
"  border-radius: 2px;\n"
"}\n"
"QScrollBar::handle::vertical:hover{\n"
"  background: #fff; \n"
"}\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761 \u533a\u57df */\n"
"QScrollBar::vertical{\n"
"  border-color: rgba(255, 255, 255, 10%);\n"
"  width: 4px;\n"
"  border-radius: 2px;\n"
"}\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761  handle\u4e0a\u3001\u4e0b\u533a\u57df\uff08\u672a\u88abhandle\u5360\u7528\u7684\u533a\u57df\uff09 */\n"
"QScrollBar::add-page::vertical, QScrollBar::sub-page::vertical,QScrollBar::add-line::vertical,QScrollBar::sub-line::vertical{\n"
"  border:none;\n"
"  outline:none;\n"
"}\n"
"\n"
"/* \u6c34\u5e73\u6eda\u52a8\u6761 handle */\n"
"QScrollBar::handle:horizontal{\n"
"  background: "
                        "#fff;\n"
"  height: 4px;\n"
"  border-radius: 2px;\n"
"}\n"
"/* \u6c34\u5e73\u6eda\u52a8\u6761 handle */\n"
"QScrollBar::handle:horizontal::hover{\n"
"  background: #fff; \n"
"}\n"
"/* \u6c34\u5e73\u6eda\u52a8\u6761 \u533a\u57df */\n"
"QScrollBar:horizontal{\n"
"  /* border-color: rgba(255, 255, 255, 10%); */\n"
"  height: 4px;\n"
"  border-radius: 2px;\n"
"  /* margin: 5px; */\n"
"}\n"
"/* \u6c34\u5e73\u6eda\u52a8\u6761  handle\u4e0a\u3001\u4e0b\u533a\u57df\uff08\u672a\u88abhandle\u5360\u7528\u7684\u533a\u57df\uff09 */\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal,QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal{\n"
"  border:none;\n"
"  outline:none;\n"
"}\n"
"\n"
"")
        self.tips = QTextEdit(Form)
        self.tips.setObjectName(u"tips")
        self.tips.setGeometry(QRect(0, 0, 280, 80))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tips.sizePolicy().hasHeightForWidth())
        self.tips.setSizePolicy(sizePolicy)
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(False)
        self.tips.setFont(font1)
        self.tips.setStyleSheet(u"border-radius: 8px;")
        self.tips.setReadOnly(True)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.tips.setHtml(QCoreApplication.translate("Form", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family: -apple-system, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei UI', sans-serif; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">\u4fe1\u606f\u63d0\u793a</span></p></body></html>", None))
    # retranslateUi

