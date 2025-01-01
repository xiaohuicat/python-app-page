# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main-neweVJXBO.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenuBar, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QStackedWidget,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1080, 753)
        font = QFont()
        font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1"])
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet(u"* {\n"
"  padding:0;\n"
"  margin:0;\n"
"  border:none;\n"
"  outline: none;\n"
"}\n"
"\n"
"#btn_change {\n"
"  padding: 4px;\n"
"}\n"
"\n"
"QFrame {\n"
"  margin: 0;\n"
"  border: 0;\n"
"}\n"
"\n"
"/*\u4e0b\u62c9\u9009\u62e9\u6846\u6837\u5f0f*/\n"
"QComboBox{\n"
"  font-size:14px;\n"
"  padding: 3px 5px;\n"
"  border:1px solid rgba(228,228,228,1);\n"
"  border-radius:5px;\n"
"}\n"
"QComboBox:hover {\n"
"  background-color: #E8F5E9;\n"
"}\n"
"\n"
"/*\u4e0b\u62c9\u5217\u8868*/\n"
"QComboBox::drop-down {\n"
"  subcontrol-origin: padding;\n"
"  subcontrol-position: top right;\n"
"  width: 20px;\n"
"  border:none;\n"
"}\n"
"\n"
"/*\u6dfb\u52a0\u7bad\u5934*/\n"
"QComboBox::down-arrow {\n"
"  image: url(./assets/icons/cil-arrow-bottom.png);\n"
"}\n"
"QComboBox QAbstractItemView{\n"
"	background:rgba(255,255,255,1);\n"
"  border:1px solid rgba(228,228,228,1);\n"
"  border-radius:0px 0px 5px 5px;\n"
"  font-size:14px;\n"
"  outline: 0px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item{\n"
"	height:28px;\n"
"	color:#6"
                        "66666;\n"
"	padding-left:9px;\n"
"	background-color:#FFFFFF;\n"
"}\n"
"QComboBox QAbstractItemView::item:hover{ \n"
"  background-color:#409CE1;\n"
"  color:#ffffff;\n"
"}\n"
"QComboBox QAbstractItemView::item:selected{\n"
"  background-color:#409CE1;\n"
"  color:#ffffff;\n"
"}\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"/*QTabWidget*/\n"
"QTabWidget::pane{\n"
"  border:none;\n"
"}\n"
"\n"
"/* \u8bbe\u7f6etabBar\u53f3\u79fb\u8ddd\u79bb */\n"
"QTabWidget::tab-bar {\n"
"  /* left: 5px; */\n"
"}\n"
"/* \u8bbe\u7f6etabBar\u6837\u5f0f */\n"
"QTabBar::tab {\n"
"  background: #fff;\n"
"  border: none;\n"
"  min-width: 60px;\n"
"  height: 24px;\n"
"  font-size: 16px;\n"
"  font-family: '\u5fae\u8f6f\u96c5\u9ed1';\n"
"  border-bottom: 3px solid #ddd;\n"
" }\n"
"\n"
"/*\u9009\u4e2dtabBar\u9009\u4e2d\u65f6\u5019\u80cc\u666f\u8272*/\n"
"QTabBar::tab:selected{\n"
"  background-color: #fff;\n"
"  color: #333;\n"
"  border-bottom: 3px solid skyblue;\n"
"}\n"
"/*\u9009\u4e2dtabBar\u9009\u4e2d\u65f6\u5019\u80cc\u666f\u8272*/\n"
"QTabBar::tab"
                        ":!selected{\n"
"  background-color: #ddd;\n"
"  color: #999;\n"
"}\n"
"\n"
"/*\u56db\u4e2a\u4e0b\u5c5e\u754c\u9762*/\n"
"#tab_baoyang,#tab_qiangxiu,#tab_xiaoxiu,#tab_specific{\n"
"  border: none;\n"
"  outline: none;\n"
"  background: #fff;\n"
"}\n"
"#listView_1,listView_2,listView_3,listView_4{\n"
"  border: none;\n"
"  outline: none;\n"
"  background: #fff;\n"
"}\n"
"\n"
"QTableWidget {\n"
"  border: none;\n"
"  outline: none;\n"
"  font-size:16px;\n"
"  background: #fff;\n"
"}\n"
"\n"
"/* \u8868\u683c\u6837\u5f0f\u8bbe\u7f6e */\n"
"/* QTableWidget \u6807\u9898\u5934\u6574\u4e2a\u533a\u57df */\n"
"QHeaderView{\n"
"  /* \u6574\u4e2a\u6807\u9898\u5934\u533a\u57df\u80cc\u666f\u8272 */\n"
"  background-color:transparent;\n"
"}\n"
"/* \u6807\u9898\u5934 \u6bcf\u4e2a\u5355\u72ec\u7684\u6807\u9898\u533a\u57df */\n"
"QHeaderView::section{\n"
"  font-size:16px; \n"
"  padding: 0 5px;               \n"
"  font-family:\"Microsoft YaHei\"; \n"
"  color:#FFFFFF;\n"
"  background:#43A047;/*\u4e2d\u7eff*/\n"
"  background:"
                        "#0D47A1;/*\u6df1\u84dd*/\n"
"  background:#1B5E20;/*\u6df1\u7eff*/\n"
"  background: #B0C4DE;\n"
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
"\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761 handle */\n"
"QScrollBar::handle::vertical{\n"
"  background: #ddd;\n"
"  width:8px;\n"
"  border-radius:3px;  \n"
"}\n"
"QScrollBar::handle::vertical:hover{\n"
"  background: #ccc; \n"
"}\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761 \u533a\u57df */\n"
"QScrollBar::vertical{\n"
"  border-color: rgba(255, 255, 255, 10%);\n"
"  width: 8px;\n"
"  border-radius:3px;\n"
"  /* margin: 5px; */\n"
"}\n"
"/* \u5782\u76f4"
                        "\u6eda\u52a8\u6761  handle\u4e0a\u3001\u4e0b\u533a\u57df\uff08\u672a\u88abhandle\u5360\u7528\u7684\u533a\u57df\uff09 */\n"
"QScrollBar::add-page::vertical, QScrollBar::sub-page::vertical,QScrollBar::add-line::vertical,QScrollBar::sub-line::vertical{\n"
"  border:none;\n"
"  outline:none;\n"
"}\n"
"\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761 handle */\n"
"QScrollBar::handle:horizontal{\n"
"  background: #eee;\n"
"  height:8px;\n"
"  border-radius:3px;  \n"
"}\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761 handle */\n"
"QScrollBar::handle:horizontal::hover{\n"
"  background: #ddd; \n"
"}\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761 \u533a\u57df */\n"
"QScrollBar:horizontal{\n"
"  /* border-color: rgba(255, 255, 255, 10%); */\n"
"  height: 8px;\n"
"  border-radius:3px;\n"
"  /* margin: 5px; */\n"
"}\n"
"/* \u5782\u76f4\u6eda\u52a8\u6761  handle\u4e0a\u3001\u4e0b\u533a\u57df\uff08\u672a\u88abhandle\u5360\u7528\u7684\u533a\u57df\uff09 */\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal,QScrollBar::add-line:horizonta"
                        "l,QScrollBar::sub-line:horizontal{\n"
"  border:none;\n"
"  outline:none;\n"
"}\n"
"\n"
"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(960, 720))
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.frame_header = QFrame(self.centralwidget)
        self.frame_header.setObjectName(u"frame_header")
        self.frame_header.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_header.sizePolicy().hasHeightForWidth())
        self.frame_header.setSizePolicy(sizePolicy)
        self.frame_header.setMinimumSize(QSize(0, 60))
        self.frame_header.setMaximumSize(QSize(16777215, 60))
        self.frame_header.setStyleSheet(u"#frame_header{\n"
"	padding: 0;\n"
"	margin: 0;\n"
"}\n"
"\n"
"QPushButton {\n"
"	border: none;\n"
"	color: rgb(255,255,255);\n"
"	border-radius: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: rgba(0,0,0,0.05);\n"
"}")
        self.frame_header.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_header.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_header)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_logo = QFrame(self.frame_header)
        self.frame_logo.setObjectName(u"frame_logo")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_logo.sizePolicy().hasHeightForWidth())
        self.frame_logo.setSizePolicy(sizePolicy1)
        self.frame_logo.setMinimumSize(QSize(0, 60))
        self.frame_logo.setMaximumSize(QSize(150, 60))
        self.frame_logo.setToolTipDuration(0)
        self.frame_logo.setStyleSheet(u"")
        self.frame_logo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_logo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_logo)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_logo = QLabel(self.frame_logo)
        self.label_logo.setObjectName(u"label_logo")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_logo.sizePolicy().hasHeightForWidth())
        self.label_logo.setSizePolicy(sizePolicy2)
        font1 = QFont()
        font1.setFamilies([u"Microsoft YaHei UI"])
        font1.setPointSize(18)
        font1.setBold(True)
        self.label_logo.setFont(font1)
        self.label_logo.setStyleSheet(u"color: #fff;\n"
"font-weight: bold;")
        self.label_logo.setTextFormat(Qt.TextFormat.AutoText)
        self.label_logo.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)

        self.horizontalLayout.addWidget(self.label_logo)


        self.horizontalLayout_2.addWidget(self.frame_logo)

        self.frame_search = QFrame(self.frame_header)
        self.frame_search.setObjectName(u"frame_search")
        sizePolicy.setHeightForWidth(self.frame_search.sizePolicy().hasHeightForWidth())
        self.frame_search.setSizePolicy(sizePolicy)
        self.frame_search.setMinimumSize(QSize(300, 60))
        self.frame_search.setMaximumSize(QSize(300, 60))
        self.frame_search.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_search.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_search)
        self.horizontalLayout_3.setSpacing(8)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.btn_leftRecord = QPushButton(self.frame_search)
        self.btn_leftRecord.setObjectName(u"btn_leftRecord")
        self.btn_leftRecord.setMinimumSize(QSize(28, 28))
        self.btn_leftRecord.setMaximumSize(QSize(28, 28))
        self.btn_leftRecord.setStyleSheet(u"border-radius: 14px;\n"
"background-color: rgba(0,0,0,0.1);")
        icon = QIcon()
        icon.addFile(u":/icon/assets/icon/left.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_leftRecord.setIcon(icon)

        self.horizontalLayout_3.addWidget(self.btn_leftRecord)

        self.btn_rightRecord = QPushButton(self.frame_search)
        self.btn_rightRecord.setObjectName(u"btn_rightRecord")
        self.btn_rightRecord.setMinimumSize(QSize(28, 28))
        self.btn_rightRecord.setMaximumSize(QSize(28, 28))
        self.btn_rightRecord.setStyleSheet(u"border-radius: 14px;\n"
"background-color: rgba(0,0,0,0.1);")
        icon1 = QIcon()
        icon1.addFile(u":/icon/assets/icon/right.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_rightRecord.setIcon(icon1)

        self.horizontalLayout_3.addWidget(self.btn_rightRecord)

        self.text_search = QLineEdit(self.frame_search)
        self.text_search.setObjectName(u"text_search")
        self.text_search.setMinimumSize(QSize(0, 32))
        self.text_search.setMaximumSize(QSize(16777215, 32))
        self.text_search.setStyleSheet(u"color: #fff;\n"
"font-size:14px;\n"
"padding: 3px 8px;\n"
"border-radius: 16px;\n"
"background-color: rgba(0,0,0,0.08);")

        self.horizontalLayout_3.addWidget(self.text_search)

        self.btn_voice = QPushButton(self.frame_search)
        self.btn_voice.setObjectName(u"btn_voice")
        self.btn_voice.setMinimumSize(QSize(32, 32))
        self.btn_voice.setMaximumSize(QSize(32, 32))
        self.btn_voice.setStyleSheet(u"border-radius: 16px;\n"
"background-color: rgba(0,0,0,0.1);")
        icon2 = QIcon()
        icon2.addFile(u":/icon/assets/icon/voice3.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_voice.setIcon(icon2)

        self.horizontalLayout_3.addWidget(self.btn_voice)


        self.horizontalLayout_2.addWidget(self.frame_search)

        self.frame_useSelect = QFrame(self.frame_header)
        self.frame_useSelect.setObjectName(u"frame_useSelect")
        self.frame_useSelect.setMinimumSize(QSize(400, 0))
        self.frame_useSelect.setMaximumSize(QSize(400, 16777215))
        self.frame_useSelect.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_useSelect.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_useInfo = QFrame(self.frame_useSelect)
        self.frame_useInfo.setObjectName(u"frame_useInfo")
        self.frame_useInfo.setGeometry(QRect(45, 0, 100, 60))
        sizePolicy1.setHeightForWidth(self.frame_useInfo.sizePolicy().hasHeightForWidth())
        self.frame_useInfo.setSizePolicy(sizePolicy1)
        self.frame_useInfo.setMinimumSize(QSize(100, 60))
        self.frame_useInfo.setMaximumSize(QSize(100, 60))
        self.frame_useInfo.setToolTipDuration(0)
        self.frame_useInfo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_useInfo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_useInfo)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.btn_login_icon = QPushButton(self.frame_useInfo)
        self.btn_login_icon.setObjectName(u"btn_login_icon")
        self.btn_login_icon.setMinimumSize(QSize(32, 32))
        self.btn_login_icon.setMaximumSize(QSize(32, 32))
        self.btn_login_icon.setStyleSheet(u"image: url(:/icon/assets/icon/user.png)")

        self.horizontalLayout_7.addWidget(self.btn_login_icon)

        self.btn_login_text = QPushButton(self.frame_useInfo)
        self.btn_login_text.setObjectName(u"btn_login_text")
        self.btn_login_text.setMinimumSize(QSize(0, 32))
        self.btn_login_text.setMaximumSize(QSize(16777215, 32))
        font2 = QFont()
        font2.setPointSize(11)
        self.btn_login_text.setFont(font2)
        self.btn_login_text.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self.horizontalLayout_7.addWidget(self.btn_login_text)

        self.frame_app = QFrame(self.frame_useSelect)
        self.frame_app.setObjectName(u"frame_app")
        self.frame_app.setGeometry(QRect(145, 0, 131, 60))
        self.frame_app.setMinimumSize(QSize(0, 60))
        self.frame_app.setMaximumSize(QSize(200, 60))
        self.frame_app.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_app.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_app)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.btn_skin = QPushButton(self.frame_app)
        self.btn_skin.setObjectName(u"btn_skin")
        self.btn_skin.setMinimumSize(QSize(32, 32))
        self.btn_skin.setMaximumSize(QSize(32, 32))
        icon3 = QIcon()
        icon3.addFile(u":/icon/assets/icon/skin.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_skin.setIcon(icon3)
        self.btn_skin.setIconSize(QSize(28, 28))

        self.horizontalLayout_8.addWidget(self.btn_skin)

        self.btn_setting = QPushButton(self.frame_app)
        self.btn_setting.setObjectName(u"btn_setting")
        self.btn_setting.setMinimumSize(QSize(32, 32))
        self.btn_setting.setMaximumSize(QSize(32, 32))
        icon4 = QIcon()
        icon4.addFile(u":/icon/assets/icon/setting.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_setting.setIcon(icon4)
        self.btn_setting.setIconSize(QSize(28, 28))

        self.horizontalLayout_8.addWidget(self.btn_setting)

        self.btn_message = QPushButton(self.frame_app)
        self.btn_message.setObjectName(u"btn_message")
        self.btn_message.setMinimumSize(QSize(32, 32))
        self.btn_message.setMaximumSize(QSize(32, 32))
        icon5 = QIcon()
        icon5.addFile(u":/icon/assets/icon/message.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_message.setIcon(icon5)
        self.btn_message.setIconSize(QSize(28, 28))

        self.horizontalLayout_8.addWidget(self.btn_message)

        self.frame_window = QFrame(self.frame_useSelect)
        self.frame_window.setObjectName(u"frame_window")
        self.frame_window.setGeometry(QRect(275, 0, 116, 60))
        self.frame_window.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.frame_window.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_window.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.frame_window)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.btn_mini = QPushButton(self.frame_window)
        self.btn_mini.setObjectName(u"btn_mini")
        self.btn_mini.setMinimumSize(QSize(32, 32))
        self.btn_mini.setMaximumSize(QSize(32, 32))
        font3 = QFont()
        font3.setFamilies([u"Microsoft YaHei UI"])
        self.btn_mini.setFont(font3)
        icon6 = QIcon()
        icon6.addFile(u":/icon/assets/icon/minimizing.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_mini.setIcon(icon6)
        self.btn_mini.setIconSize(QSize(28, 28))

        self.horizontalLayout_9.addWidget(self.btn_mini)

        self.btn_change = QPushButton(self.frame_window)
        self.btn_change.setObjectName(u"btn_change")
        self.btn_change.setMinimumSize(QSize(32, 32))
        self.btn_change.setMaximumSize(QSize(32, 32))
        self.btn_change.setStyleSheet(u"padding: 4px;\n"
"margin: 4px;")
        icon7 = QIcon()
        icon7.addFile(u":/icon/assets/icon/outline-maximize-3.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_change.setIcon(icon7)
        self.btn_change.setIconSize(QSize(28, 28))

        self.horizontalLayout_9.addWidget(self.btn_change)

        self.btn_close = QPushButton(self.frame_window)
        self.btn_close.setObjectName(u"btn_close")
        self.btn_close.setMinimumSize(QSize(32, 32))
        self.btn_close.setMaximumSize(QSize(32, 32))
        icon8 = QIcon()
        icon8.addFile(u":/icon/assets/icon/close.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_close.setIcon(icon8)
        self.btn_close.setIconSize(QSize(28, 28))

        self.horizontalLayout_9.addWidget(self.btn_close)


        self.horizontalLayout_2.addWidget(self.frame_useSelect, 0, Qt.AlignmentFlag.AlignRight)


        self.verticalLayout.addWidget(self.frame_header)

        self.frame_main = QFrame(self.centralwidget)
        self.frame_main.setObjectName(u"frame_main")
        self.frame_main.setStyleSheet(u"#frame_main{\n"
"	bacground-color: #fff;\n"
"}")
        self.frame_main.setLineWidth(0)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_main)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.frame_left = QFrame(self.frame_main)
        self.frame_left.setObjectName(u"frame_left")
        self.frame_left.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame_left.sizePolicy().hasHeightForWidth())
        self.frame_left.setSizePolicy(sizePolicy3)
        self.frame_left.setMinimumSize(QSize(219, 0))
        self.frame_left.setMaximumSize(QSize(219, 16777215))
        self.frame_left.setStyleSheet(u"QLabel {\n"
"	color: rgb(150,150,150);\n"
"	font-size: 13px;\n"
"}\n"
"QPushButton {\n"
"	margin: 1px 10px;\n"
"	font-size: 16px;\n"
"	text-align: left;\n"
"	padding: 0 10px;\n"
"	color: #444;\n"
"	border-radius: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgba(0,0,0,0.03);\n"
"}\n"
"QPushButton:actived {\n"
"	background-color: rgba(0,0,0,0.03);\n"
"}")
        self.frame_left.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_left.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_left.setLineWidth(0)
        self.verticalLayout_2 = QVBoxLayout(self.frame_left)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_13 = QFrame(self.frame_left)
        self.frame_13.setObjectName(u"frame_13")
        self.frame_13.setMinimumSize(QSize(0, 245))
        self.frame_13.setMaximumSize(QSize(16777215, 255))
        self.frame_13.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_13.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.frame_13)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 10, 0, 0)
        self.scrollArea_3 = QScrollArea(self.frame_13)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setStyleSheet(u"#scrollArea_3{\n"
"	background-color: transparent;\n"
"}")
        self.scrollArea_3.setWidgetResizable(True)
        self.leftbar_container = QWidget()
        self.leftbar_container.setObjectName(u"leftbar_container")
        self.leftbar_container.setGeometry(QRect(0, 0, 219, 245))
        self.scrollArea_3.setWidget(self.leftbar_container)

        self.horizontalLayout_11.addWidget(self.scrollArea_3)


        self.verticalLayout_2.addWidget(self.frame_13)

        self.frame_14 = QFrame(self.frame_left)
        self.frame_14.setObjectName(u"frame_14")
        self.frame_14.setMinimumSize(QSize(0, 30))
        self.frame_14.setMaximumSize(QSize(16777215, 30))
        self.frame_14.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_14.setFrameShadow(QFrame.Shadow.Raised)
        self.label_13 = QLabel(self.frame_14)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(20, 0, 71, 22))
        sizePolicy2.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy2)
        font4 = QFont()
        font4.setFamilies([u"Microsoft YaHei"])
        self.label_13.setFont(font4)
        self.label_13.setTextFormat(Qt.TextFormat.AutoText)
        self.label_13.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)

        self.verticalLayout_2.addWidget(self.frame_14)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout_10.addWidget(self.frame_left)

        self.frame_right = QFrame(self.frame_main)
        self.frame_right.setObjectName(u"frame_right")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(3)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.frame_right.sizePolicy().hasHeightForWidth())
        self.frame_right.setSizePolicy(sizePolicy4)
        self.frame_right.setStyleSheet(u"QPushButton {\n"
"	font-size: 14px;\n"
"	background-color: #fff;\n"
"	border-radius: 5px;\n"
"}\n"
"\n"
"QLineEdit {\n"
"	border-radius: 5px;\n"
"	padding: 0 5px;\n"
"}\n"
"\n"
"#frame_right{\n"
"	background-color: transparent;\n"
"}")
        self.horizontalLayout_4 = QHBoxLayout(self.frame_right)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.frame_right)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_1 = QWidget()
        self.page_1.setObjectName(u"page_1")
        self.stackedWidget.addWidget(self.page_1)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.stackedWidget.addWidget(self.page_2)

        self.horizontalLayout_4.addWidget(self.stackedWidget)


        self.horizontalLayout_10.addWidget(self.frame_right)


        self.verticalLayout.addWidget(self.frame_main)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1080, 33))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_logo.setText(QCoreApplication.translate("MainWindow", u"\u5c0f\u7070\u5999\u8bb0", None))
        self.btn_leftRecord.setText("")
        self.btn_rightRecord.setText("")
        self.text_search.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u641c\u7d22", None))
        self.btn_voice.setText("")
        self.btn_login_icon.setText("")
        self.btn_login_text.setText(QCoreApplication.translate("MainWindow", u"\u767b\u5f55", None))
        self.btn_skin.setText("")
        self.btn_setting.setText("")
        self.btn_message.setText("")
        self.btn_mini.setText("")
        self.btn_change.setText("")
        self.btn_close.setText("")
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"\u6700\u8fd1\u4f7f\u7528", None))
    # retranslateUi

