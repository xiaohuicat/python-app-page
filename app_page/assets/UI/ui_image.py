# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'imageyZZVlV.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QVBoxLayout, QWidget)
import apprcc_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(960, 720)
        MainWindow.setMinimumSize(QSize(960, 720))
        MainWindow.setMaximumSize(QSize(16777215, 16777215))
        MainWindow.setStyleSheet(u"* {\n"
"  padding:0;\n"
"  margin:0;\n"
"  border:none;\n"
"  outline: none;\n"
"}\n"
"#header{\n"
"  background-color: #fff;\n"
"}\n"
"QLabel{\n"
"  background-color: #fff;\n"
"}\n"
"\n"
"/*\u6309\u94ae*/\n"
"QPushButton {\n"
"  font-size:14px;\n"
"  padding: 2px;\n"
"  \n"
"}\n"
"QPushButton:hover {\n"
"  background-color: rgba(0,0,0,0.05);\n"
"  color: #fff;\n"
"  border-color: #1E88E5;\n"
"  border-radius: 4px;\n"
"}\n"
"\n"
"#btn_close{\n"
"  image: url(:/image/assets/icon/image/btn_close.png);\n"
"}\n"
"\n"
"#btn_close:hover {\n"
"  background-color: #FF4040;\n"
"  image: url(:/image/assets/icon/image/btn_close_sleep.png);\n"
"}\n"
"\n"
"QTableWidget {\n"
"  border: none;\n"
"  outline: none;\n"
"  background: #fff;\n"
"}\n"
"\n"
"/* \u8868\u683c\u6837\u5f0f\u8bbe\u7f6e */\n"
"/* QTableWidget \u6807\u9898\u5934\u6574\u4e2a\u533a\u57df */\n"
"QHeaderView{\n"
"  /* \u6574\u4e2a\u6807\u9898\u5934\u533a\u57df\u80cc\u666f\u8272 */\n"
"  background-color:transparent;\n"
"}\n"
"/* \u6807\u9898\u5934 \u6bcf\u4e2a"
                        "\u5355\u72ec\u7684\u6807\u9898\u533a\u57df */\n"
"QHeaderView::section{\n"
"  font-size:14px;                \n"
"  font-family:\"Microsoft YaHei\"; \n"
"  color:#FFFFFF;\n"
"  background:#43A047;/*\u4e2d\u7eff*/\n"
"  background:#0D47A1;/*\u6df1\u84dd*/\n"
"  background:#1B5E20;/*\u6df1\u7eff*/\n"
"  /*background:#4527A0;\u84dd\u8272*/\n"
"  border:none;\n"
"  /* \u6bcf\u4e2a\u6807\u9898\u7684\u5bf9\u9f50\u65b9\u5f0f\uff08\u8c8c\u4f3c\u4e0d\u80fd\u7528\uff09\u3002\n"
"  \u5efa\u8bae\u4f7f\u7528tableWidget->horizontalHeader()->setDefaultAlignment(Qt::AlignLeft | Qt::AlignVCenter)*/\n"
"  text-align:center;               \n"
"  min-height:30px;               \n"
"  max-height:30px;              \n"
"  margin-left:0px;               \n"
"  padding-left:0px;     \n"
"}\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761 handle */\n"
"QScrollBar::handle::vertical{\n"
"  background: #ddd;\n"
"  width:8px;\n"
"  border-radius:3px;  \n"
"}\n"
"QScrollBar::handle::vertical:hover{\n"
"  background: #ccc; \n"
"}\n"
"/* \u5782\u76f4\u6eda"
                        "\u52a8\u6761 \u533a\u57df */\n"
"QScrollBar::vertical{\n"
"  border-color: rgba(255, 255, 255, 10%);\n"
"  width: 8px;\n"
"  border-radius:3px;\n"
"  /* margin: 5px; */\n"
"}\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761  handle\u4e0a\u3001\u4e0b\u533a\u57df\uff08\u672a\u88abhandle\u5360\u7528\u7684\u533a\u57df\uff09 */\n"
"QScrollBar::add-page::vertical, QScrollBar::sub-page::vertical,QScrollBar::add-line::vertical,QScrollBar::sub-line::vertical{\n"
"  border:none;\n"
"  outline:none;\n"
"}\n"
"\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761 handle */\n"
"QScrollBar::handle:horizontal{\n"
"  background: #ddd;\n"
"  height:8px;\n"
"  border-radius:3px;  \n"
"}\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761 handle */\n"
"QScrollBar::handle:horizontal::hover{\n"
"  background: #ccc; \n"
"}\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761 \u533a\u57df */\n"
"QScrollBar:horizontal{\n"
"  /* border-color: rgba(255, 255, 255, 10%); */\n"
"  height: 8px;\n"
"  border-radius:3px;\n"
"  /* margin: 5px; */\n"
"}\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761  handl"
                        "e\u4e0a\u3001\u4e0b\u533a\u57df\uff08\u672a\u88abhandle\u5360\u7528\u7684\u533a\u57df\uff09 */\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal,QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal{\n"
"  border:none;\n"
"  outline:none;\n"
"}\n"
"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_main = QFrame(self.centralwidget)
        self.frame_main.setObjectName(u"frame_main")
        self.verticalLayout_2 = QVBoxLayout(self.frame_main)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(8, 8, 8, 8)
        self.header = QFrame(self.frame_main)
        self.header.setObjectName(u"header")
        self.header.setMinimumSize(QSize(0, 38))
        self.header.setMaximumSize(QSize(16777215, 38))
        self.header.setFrameShape(QFrame.StyledPanel)
        self.header.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.header)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.bar_left = QFrame(self.header)
        self.bar_left.setObjectName(u"bar_left")
        self.bar_left.setFrameShape(QFrame.StyledPanel)
        self.bar_left.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.bar_left)
        self.horizontalLayout_2.setSpacing(3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(3, 3, 3, 3)
        self.btn_left = QPushButton(self.bar_left)
        self.btn_left.setObjectName(u"btn_left")
        self.btn_left.setMinimumSize(QSize(28, 28))
        self.btn_left.setMaximumSize(QSize(28, 28))
        self.btn_left.setStyleSheet(u"image: url(:/image/assets/icon/image/btn_left.png);")

        self.horizontalLayout_2.addWidget(self.btn_left)

        self.btn_right = QPushButton(self.bar_left)
        self.btn_right.setObjectName(u"btn_right")
        self.btn_right.setMinimumSize(QSize(28, 28))
        self.btn_right.setMaximumSize(QSize(28, 28))
        self.btn_right.setStyleSheet(u"image: url(:/image/assets/icon/image/btn_right.png);")

        self.horizontalLayout_2.addWidget(self.btn_right)

        self.btn_list = QPushButton(self.bar_left)
        self.btn_list.setObjectName(u"btn_list")
        self.btn_list.setMinimumSize(QSize(28, 28))
        self.btn_list.setMaximumSize(QSize(28, 28))
        self.btn_list.setStyleSheet(u"image: url(:/image/assets/icon/image/btn_list.png);\n"
"padding: 3px;")

        self.horizontalLayout_2.addWidget(self.btn_list)

        self.btn_big = QPushButton(self.bar_left)
        self.btn_big.setObjectName(u"btn_big")
        self.btn_big.setMinimumSize(QSize(28, 28))
        self.btn_big.setMaximumSize(QSize(28, 28))
        self.btn_big.setStyleSheet(u"image:url(:/image/assets/icon/image/btn_big.png)")

        self.horizontalLayout_2.addWidget(self.btn_big)

        self.btn_small = QPushButton(self.bar_left)
        self.btn_small.setObjectName(u"btn_small")
        self.btn_small.setMinimumSize(QSize(28, 28))
        self.btn_small.setMaximumSize(QSize(28, 28))
        self.btn_small.setStyleSheet(u"image: url(:/image/assets/icon/image/btn_small.png);")

        self.horizontalLayout_2.addWidget(self.btn_small)

        self.btn_fixScale = QPushButton(self.bar_left)
        self.btn_fixScale.setObjectName(u"btn_fixScale")
        self.btn_fixScale.setMinimumSize(QSize(26, 26))
        self.btn_fixScale.setMaximumSize(QSize(26, 26))

        self.horizontalLayout_2.addWidget(self.btn_fixScale)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.horizontalLayout.addWidget(self.bar_left)

        self.frame = QFrame(self.header)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.btn_mini = QPushButton(self.frame)
        self.btn_mini.setObjectName(u"btn_mini")
        self.btn_mini.setMinimumSize(QSize(28, 28))
        self.btn_mini.setMaximumSize(QSize(28, 28))
        self.btn_mini.setStyleSheet(u"image:url(:/image/assets/icon/image/minimizing.png)")

        self.horizontalLayout_3.addWidget(self.btn_mini)

        self.btn_change = QPushButton(self.frame)
        self.btn_change.setObjectName(u"btn_change")
        self.btn_change.setMinimumSize(QSize(28, 28))
        self.btn_change.setMaximumSize(QSize(28, 28))
        self.btn_change.setStyleSheet(u"image:url(:/image/assets/icon/image/btn_change.png);\n"
"padding: 6px;")

        self.horizontalLayout_3.addWidget(self.btn_change)

        self.btn_close = QPushButton(self.frame)
        self.btn_close.setObjectName(u"btn_close")
        self.btn_close.setMinimumSize(QSize(28, 28))
        self.btn_close.setMaximumSize(QSize(28, 28))

        self.horizontalLayout_3.addWidget(self.btn_close)


        self.horizontalLayout.addWidget(self.frame)


        self.verticalLayout_2.addWidget(self.header)

        self.label = QLabel(self.frame_main)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 0))
        self.label.setMaximumSize(QSize(16777215, 16777215))
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label)


        self.verticalLayout.addWidget(self.frame_main)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 960, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btn_left.setText("")
        self.btn_right.setText("")
        self.btn_list.setText("")
        self.btn_big.setText("")
        self.btn_small.setText("")
        self.btn_fixScale.setText("")
        self.btn_mini.setText("")
        self.btn_change.setText("")
        self.btn_close.setText("")
        self.label.setText("")
    # retranslateUi

    def __getitem__(self,__name):
      return super().__getattribute__(__name)