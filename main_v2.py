import sys
import threading

import darkdetect

import qdarktheme

from PyQt5 import QtCore, QtWidgets, QtNetwork
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView

from PyQt5.QtWidgets import QApplication, QDesktopWidget, QSystemTrayIcon, QAction, QMenu, qApp

from qframelesswindow import FramelessWindow
from system_hotkey import SystemHotkey

from win_v2 import Ui_Form

import images_rc


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

        # 翻译引擎地址
        google_url = 'https://translate.google.com/'
        deepl_url = 'https://www.deepl.com/translator'
        baidu_url = 'https://fanyi.baidu.com/'
        youdao_url = 'https://fanyi.youdao.com/index.html#/'

        self.add_web(google_url)
        self.add_web(deepl_url)
        self.add_web(baidu_url)
        self.add_web(youdao_url)

        # 监听系统主题自动切换
        t = threading.Thread(target=darkdetect.listener, args=(self.change_theme,))
        t.daemon = True
        t.start()
        # 更新主题
        self.change_theme()

        # 热键响应
        self.hotKey = HotKeyThread(self)
        # 托盘图标
        self.tray = Tray(self)

        # 绘制窗口并显示
        # self.show()
        # 打开软件默认最小化到托盘图标
        self.close()

    def add_web(self, url):

        tab = None
        browser = None
        if 'google' in url:
            tab = self.ui.google_tab
            # # 设置代理
            # proxy = QtNetwork.QNetworkProxy(QtNetwork.QNetworkProxy.HttpProxy, '127.0.0.1', 60801)
            # QtNetwork.QNetworkProxy.setApplicationProxy(proxy)
            # browser = self.google_browser = QWebEngineView(self)
        elif 'deepl' in url:
            tab = self.ui.deepl_tab
            browser = self.deepl_browser = QWebEngineView(self)
        elif 'baidu' in url:
            tab = self.ui.baidu_tab
            browser = self.baidu_browser = QWebEngineView(self)
        elif 'youdao' in url:
            tab = self.ui.youdao_tab
            browser = self.youdao_browser = QWebEngineView(self)

        if browser and tab:
            # 指定打开界面的 URL
            browser.setUrl(QUrl(url))

            # 添加浏览器到窗口中
            self.ui.gridLayout_1 = QtWidgets.QGridLayout(tab)
            self.ui.gridLayout_1.setContentsMargins(0, 0, 0, 0)
            self.ui.gridLayout_1.setSpacing(0)
            self.ui.gridLayout_1.setObjectName("gridLayout_1")
            self.ui.gridLayout_1.addWidget(browser)

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

    # 切换主题
    def change_theme(self, mode=None):
        qdarktheme.setup_theme(theme='auto')

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

        if mode == 'Light' or darkdetect.isLight():
            self.titleBar.minBtn.updateStyle(minBtn_maxBtn_light_style)
            self.titleBar.maxBtn.updateStyle(minBtn_maxBtn_light_style)
            self.titleBar.closeBtn.updateStyle(closeBtn_light_style)
        elif mode == 'Dark' or darkdetect.isDark():
            self.titleBar.minBtn.updateStyle(minBtn_maxBtn_dark_style)
            self.titleBar.maxBtn.updateStyle(minBtn_maxBtn_dark_style)
            self.titleBar.closeBtn.updateStyle(closeBtn_dark_style)



if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 自动切换主题
    qdarktheme.setup_theme(theme="auto")

    demo = Window()

    sys.exit(app.exec_())
