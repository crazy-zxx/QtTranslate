import sys
import threading

import darkdetect
import qdarktheme

from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QLabel

from qframelesswindow import FramelessWindow


# 自动切换主题的窗口
class AutoThemeWindow(FramelessWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # 增加窗口标题
        self.titleLabel = QLabel(self)
        self.titleLabel.setStyleSheet("QLabel{font: 13px 'Times Nwe Roman'; margin: 9px}")
        self.titleLabel.lower()
        self.set_window_title('窗口标题')

        # 窗口居中显示
        self.center()

        # 自动切换主题
        qdarktheme.setup_theme(theme="auto")
        # 监听系统主题自动切换标题栏主题
        t = threading.Thread(target=darkdetect.listener, args=(self.auto_change_theme,))
        t.daemon = True
        t.start()
        # 更新换标题栏主题
        self.auto_change_theme()

    def set_window_title(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    # 窗口居中显示
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 自动切换标题栏主题
    def auto_change_theme(self, mode=None):

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

        if darkdetect.isLight() or mode == 'Light':
            self.titleBar.minBtn.updateStyle(minBtn_maxBtn_light_style)
            self.titleBar.maxBtn.updateStyle(minBtn_maxBtn_light_style)
            self.titleBar.closeBtn.updateStyle(closeBtn_light_style)
        elif darkdetect.isDark() or mode == 'Dark':
            self.titleBar.minBtn.updateStyle(minBtn_maxBtn_dark_style)
            self.titleBar.maxBtn.updateStyle(minBtn_maxBtn_dark_style)
            self.titleBar.closeBtn.updateStyle(closeBtn_dark_style)


# 测试窗口
class Win(AutoThemeWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # 窗口设置
        self.set_window_title('哈哈哈')
        self.ui = QMainWindow()
        self.resize(800, 600)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 窗口
    demo = Win()

    sys.exit(app.exec_())
