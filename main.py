import re
import sys
import threading

import darkdetect

import qdarktheme

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QApplication, QDesktopWidget, QSystemTrayIcon, QAction, QMenu, qApp

from qframelesswindow import FramelessWindow
from system_hotkey import SystemHotkey

from MyDialog import MyGoogleDialog, MyBaiduDialog
from MyTranslate import GoogleTranslate, BaiduTranslate, YoudaoTranslate, DeepLTranslate

import images_rc

from win import Ui_Form



# 翻译线程
class MyThread(QThread):
    """该线程用于耗时的翻译操作"""
    _sig = pyqtSignal(object)  # 信号类型为 str

    def __init__(self, func, **args):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        result = self.func(**self.args)
        self._sig.emit(result)  # 获取结果完成后，发送结果


# 托盘图标
class Tray(QSystemTrayIcon):
    def __init__(self, UI):
        super(Tray, self).__init__()
        self.ui = UI  # 传入主程序
        self.setIcon(QIcon(':/icon.ico'))  # 自定义托盘图标
        self.setToolTip(self.ui.ui.window_title.text())  # 鼠标点在图标上的时候显示的气泡提示
        self.activated.connect(self.clickedIcon)  # 点击信号
        self.addContextMenu()
        self.show()

    # 点击托盘图标
    def clickedIcon(self, reason):
        # reason：鼠标点击托盘图标时传递的整数型信号，
        # 1表示单击右键，2表示双击左键，3表示单击左键，4表示点击中键。
        # 下面定义单击左键是弹出或隐藏界面，单击右键是弹出菜单。
        if reason == 3 or reason == 2:
            self.trayClickedEvent()
        elif reason == 1:
            self.contextMenu()

    # 托盘图标右键菜单
    def addContextMenu(self):
        show_action = QAction("显示窗口", self)
        hide_action = QAction("隐藏窗口", self)
        quit_action = QAction("退出", self)
        show_action.triggered.connect(self.ui.show)
        hide_action.triggered.connect(self.ui.hide)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.setContextMenu(tray_menu)

    # 单击托盘图标，程序在隐藏和显示之间来回切换
    def trayClickedEvent(self):
        if self.ui.isHidden():
            self.ui.setHidden(False)
            if self.ui.windowState() == QtCore.Qt.WindowMinimized:
                self.ui.showNormal()
            self.ui.raise_()
            self.ui.activateWindow()
        else:
            self.ui.setHidden(True)

    def triggered(self):
        self.deleteLater()  # 删除托盘图标，无此操作的话，程序退出后托盘图标不会自动清除
        qApp.quit()  # 后面会重写closeEvent，所以这里换一个退出程序的命令


# 系统热键切换窗口显隐
class HotKeyThread(QThread, SystemHotkey):
    """
    另开一个线程用于捕捉全局热键，以防止主线程堵塞导致假死
    具体逻辑如下:
    1、注册一个全局热键，callback为self.start()，即启动线程；
    2、线程启动后，通过run()函数发送一个信号；
    3、信号对应的槽函数为具体要执行的内容，在这里的目的是隐藏|弹出后台窗口。
    """
    trigger = pyqtSignal()

    def __init__(self, UI):
        self.ui = UI
        super(HotKeyThread, self).__init__()
        self.register(('control', 'alt', 'f'), callback=lambda x: self.start())
        self.trigger.connect(self.hotKeyEvent)

    def run(self):
        self.trigger.emit()

    def hotKeyEvent(self):
        if self.ui.isHidden():
            self.ui.setHidden(False)
            if self.ui.windowState() == QtCore.Qt.WindowMinimized:
                self.ui.showNormal()
            self.ui.raise_()
            self.ui.activateWindow()
        else:
            self.ui.setHidden(True)

    def quitThread(self):
        if self.isRunning():
            self.quit()


class Window(FramelessWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowIcon(QIcon(":/icon.ico"))

        # 窗口居中显示
        self.center()

        # 窗口设置
        self.ui = Ui_Form()
        # 设置窗口为自定义标题栏窗口
        self.ui.setupUi(self)

        # 由于通过QLabel来显示窗口标题文字，所以需要置于最底层，否则标题栏无法使用原始标题栏拖动窗口操作
        self.ui.window_title.lower()

        # 切换主题的下拉菜单
        self.ui.theme_comboBox.addItems(qdarktheme.get_themes())
        self.ui.theme_comboBox.setCurrentText('auto')
        self.ui.theme_comboBox.currentTextChanged.connect(self.change_theme)

        self.ui.input_comboBox.currentTextChanged.connect(self.change_language)
        self.ui.output_comboBox.currentTextChanged.connect(self.change_language)

        # 切换翻译引擎
        self.ui.google_radioButton.clicked.connect(self.change_request)
        self.ui.google_radioButton.setContextMenuPolicy(Qt.CustomContextMenu)  # 打开右键菜单策略
        self.ui.google_radioButton.customContextMenuRequested.connect(self.showGoogleDialog)  # 连接到菜单显示函数
        self.ui.deepl_radioButton.clicked.connect(self.change_request)
        self.ui.baidu_radioButton.clicked.connect(self.change_request)
        self.ui.baidu_radioButton.setContextMenuPolicy(Qt.CustomContextMenu)  # 打开右键菜单策略
        self.ui.baidu_radioButton.customContextMenuRequested.connect(self.showBaiduDialog)  # 连接到菜单显示函数
        self.ui.youdao_radioButton.clicked.connect(self.change_request)

        # 按钮响应
        self.ui.format_checkBox.clicked.connect(self.format_input)
        self.ui.instant_translate_checkBox.clicked.connect(self.instant_translate)
        self.ui.translate_pushButton.clicked.connect(self.get_translate_text)
        self.ui.copy_pushButton.clicked.connect(self.copy_result)
        self.ui.clear_pushButton.clicked.connect(self.clear_input_output)

        # 监听系统主题自动切换
        t = threading.Thread(target=darkdetect.listener, args=(self.change_theme,))
        t.daemon = True
        t.start()
        # 更新主题
        self.change_theme()

        # 剪贴板
        self.clipboard = QApplication.clipboard()
        # 热键响应
        self.hotKey = HotKeyThread(self)
        # 托盘图标
        self.tray = Tray(self)

        # 翻译引擎语言表
        self.Google = {'Chinese': 'zh-CN', 'English': 'en'}
        self.DeepL = {'Chinese': 'zh', 'English': 'en'}
        self.Baidu = {'Chinese': 'zh', 'English': 'en'}
        self.Youdao = {'Chinese': 'zh', 'English': 'en'}
        # 默认Google翻译引擎
        self.translator = GoogleTranslate()
        self.engine = 'Google'
        self.src = eval('self.' + self.engine)[self.ui.input_comboBox.currentText()]
        self.dest = eval('self.' + self.engine)[self.ui.output_comboBox.currentText()]
        self.translate_thread = None
        self.google_proxy = {'proxies': {'https': ''}}
        self.baidu_key = {'appid': '', 'appkey': ''}

        # 绘制窗口并显示
        # self.show()
        # 打开软件默认最小化到托盘图标
        self.close()

    def change_language(self):
        sender = self.sender()
        if sender == self.ui.input_comboBox:
            if self.ui.input_comboBox.currentText() == 'Chinese':
                self.ui.output_comboBox.setCurrentText('English')
            elif self.ui.input_comboBox.currentText() == 'English':
                self.ui.output_comboBox.setCurrentText('Chinese')
        elif sender == self.ui.output_comboBox:
            if self.ui.output_comboBox.currentText() == 'Chinese':
                self.ui.input_comboBox.setCurrentText('English')
            elif self.ui.output_comboBox.currentText() == 'English':
                self.ui.input_comboBox.setCurrentText('Chinese')

    def showGoogleDialog(self):
        MyGoogleDialog.show_dialog(self)

    def showBaiduDialog(self):
        MyBaiduDialog.show_dialog(self)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray.showMessage(
            self.ui.window_title.text(),
            "应用已经最小化到托盘图标,可以通过系统快捷键 Ctrl+Alt+F 切换窗口显示与隐藏！",
            QSystemTrayIcon.Information,
            2000
        )

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def change_request(self):
        sender = self.sender()
        self.engine = sender.text()

    def clear_input_output(self):
        self.ui.input_plainTextEdit.clear()
        self.ui.output_plainTextEdit.clear()

    def format_text(self):
        input_text = self.ui.input_plainTextEdit.toPlainText()
        if input_text and input_text.strip() != '':
            format_text = input_text.strip()
            format_text = re.sub('[\t\r ]+', ' ', format_text)
            format_text = re.sub(r'\n+\s*', '\n', format_text)
            if format_text != input_text:
                self.ui.input_plainTextEdit.setPlainText(format_text)

    def format_input(self):
        if self.ui.format_checkBox.isChecked():
            self.ui.input_plainTextEdit.textChanged.connect(self.format_text)
            self.format_text()
        else:
            self.ui.input_plainTextEdit.textChanged.disconnect(self.format_text)

    def copy_result(self):
        self.clipboard.setText(self.ui.output_plainTextEdit.toPlainText())

    def update_result(self, text):
        self.ui.output_plainTextEdit.setPlainText(text)

    def get_translate_text(self):
        input_text = self.ui.input_plainTextEdit.toPlainText()
        if input_text and input_text.strip() != '':

            # 创建翻译引擎对象
            if self.engine == 'Google':
                self.translator = GoogleTranslate(**self.google_proxy)
            elif self.engine == 'DeepL':
                self.translator = DeepLTranslate()
            elif self.engine == 'Baidu':
                self.translator = BaiduTranslate(**self.baidu_key)
            elif self.engine == 'Youdao':
                self.translator = YoudaoTranslate()

            # 新建线程处理翻译操作
            self.translate_thread = MyThread(
                func=self.translator.translate,
                **{'text': input_text,
                   'target': eval('self.' + self.engine)[self.ui.output_comboBox.currentText()],
                   'source': eval('self.' + self.engine)[self.ui.input_comboBox.currentText()]
                   }
            )
            # 新线程处理完后发过来的信号挂接到槽函数update_result进行UI显示处理
            self.translate_thread._sig.connect(self.update_result)
            # 启动新线程
            self.translate_thread.start()
            # 超时关闭线程
            QTimer.singleShot(5000, self.translate_thread.terminate)

    # 即时翻译
    def instant_translate(self):
        if self.ui.instant_translate_checkBox.isChecked():
            self.ui.input_plainTextEdit.textChanged.connect(self.get_translate_text)
            self.ui.google_radioButton.clicked.connect(self.get_translate_text)
            self.ui.deepl_radioButton.clicked.connect(self.get_translate_text)
            self.ui.baidu_radioButton.clicked.connect(self.get_translate_text)
            self.ui.youdao_radioButton.clicked.connect(self.get_translate_text)
            self.ui.input_comboBox.currentTextChanged.connect(self.get_translate_text)
            self.ui.output_comboBox.currentTextChanged.connect(self.get_translate_text)
            self.get_translate_text()
        else:
            self.ui.input_plainTextEdit.textChanged.disconnect(self.get_translate_text)
            self.ui.google_radioButton.clicked.disconnect(self.get_translate_text)
            self.ui.deepl_radioButton.clicked.disconnect(self.get_translate_text)
            self.ui.baidu_radioButton.clicked.disconnect(self.get_translate_text)
            self.ui.youdao_radioButton.clicked.disconnect(self.get_translate_text)
            self.ui.input_comboBox.currentTextChanged.disconnect(self.get_translate_text)
            self.ui.output_comboBox.currentTextChanged.disconnect(self.get_translate_text)

    # 切换主题
    def change_theme(self, mode=None):
        qdarktheme.setup_theme(theme=self.ui.theme_comboBox.currentText())

        minBtn_maxBtn_light_style = {
            "normal": {
                "color": (0, 0, 0, 255),
                'background': (0, 0, 0, 0),
            },
            "hover": {
                "color": (255, 255, 255),
                'background': (0, 100, 182)
            },
            "pressed": {
                "color": (255, 255, 255),
                'background': (0, 100, 182)
            },
        }
        closeBtn_light_style = {
            "normal": {
                'background': (0, 0, 0, 0),
                "icon": ":/framelesswindow/close_black.svg"
            },
            "hover": {
                'background': (232, 17, 35),
                "icon": ":/framelesswindow/close_white.svg"
            },
            "pressed": {
                'background': (241, 112, 122),
                "icon": ":/framelesswindow/close_white.svg"
            },
        }

        minBtn_maxBtn_dark_style = {
            "normal": {
                "color": (255, 255, 255, 255),
                'background': (0, 0, 0, 0),
            },
            "hover": {
                "color": (255, 255, 255),
                'background': (0, 100, 182)
            },
            "pressed": {
                "color": (255, 255, 255),
                'background': (0, 100, 182)
            },
        }
        closeBtn_dark_style = {
            "normal": {
                'background': (0, 0, 0, 0),
                "icon": ":/framelesswindow/close_white.svg"
            },
            "hover": {
                'background': (232, 17, 35),
                "icon": ":/framelesswindow/close_black.svg"
            },
            "pressed": {
                'background': (241, 112, 122),
                "icon": ":/framelesswindow/close_black.svg"
            },
        }

        if self.ui.theme_comboBox.currentText() == 'light' or (
                self.ui.theme_comboBox.currentText() == 'auto' and darkdetect.isLight()) or (
                self.ui.theme_comboBox.currentText() == 'auto' and mode == 'Light'):
            self.titleBar.minBtn.updateStyle(minBtn_maxBtn_light_style)
            self.titleBar.maxBtn.updateStyle(minBtn_maxBtn_light_style)
            self.titleBar.closeBtn.updateStyle(closeBtn_light_style)
        elif self.ui.theme_comboBox.currentText() == 'dark' or (
                self.ui.theme_comboBox.currentText() == 'auto' and darkdetect.isDark()) or (
                self.ui.theme_comboBox.currentText() == 'auto' and mode == 'Dark'):
            self.titleBar.minBtn.updateStyle(minBtn_maxBtn_dark_style)
            self.titleBar.maxBtn.updateStyle(minBtn_maxBtn_dark_style)
            self.titleBar.closeBtn.updateStyle(closeBtn_dark_style)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 自动切换主题
    qdarktheme.setup_theme(theme="auto")

    demo = Window()

    sys.exit(app.exec_())
