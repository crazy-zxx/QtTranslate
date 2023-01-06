from PyQt5.QtWidgets import *

from dialog import Ui_Form


class MyDialog(QDialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)
        self.setWindowTitle('设置')

        # 窗口设置
        self.ui = Ui_Form()
        # 设置窗口为自定义标题栏窗口
        self.ui.setupUi(self)

        self.ui.confirm_pushButton.clicked.connect(self.update_parent_info)

    def update_parent_info(self):
        pass

    # 静态方法创建对话框
    @staticmethod
    def show_dialog(parent=None):
        dialog = MyDialog(parent)
        dialog.exec_()


class MyGoogleDialog(QDialog):
    def __init__(self, parent=None):
        super(MyGoogleDialog, self).__init__(parent)
        self.setWindowTitle('设置')

        # 窗口设置
        self.ui = Ui_Form()
        # 设置窗口为自定义标题栏窗口
        self.ui.setupUi(self)

        self.ui.lineEdit_1.setText(self.parent().google_proxy['proxies']['https'])
        self.ui.lineEdit_2.setReadOnly(True)

        self.ui.confirm_pushButton.clicked.connect(self.update_parent_info)

    def update_parent_info(self):
        self.parent().google_proxy = {'proxies': {'https': self.ui.lineEdit_1.text()}}
        self.close()

    # 静态方法创建对话框
    @staticmethod
    def show_dialog(parent=None):
        dialog = MyGoogleDialog(parent)
        dialog.exec_()


class MyBaiduDialog(QDialog):
    def __init__(self, parent=None):
        super(MyBaiduDialog, self).__init__(parent)
        self.setWindowTitle('设置')

        # 窗口设置
        self.ui = Ui_Form()
        # 设置窗口为自定义标题栏窗口
        self.ui.setupUi(self)

        self.ui.label_1.setText('appid')
        self.ui.label_2.setText('appkey')
        self.ui.lineEdit_1.setText(self.parent().baidu_key['appid'])
        self.ui.lineEdit_2.setText(self.parent().baidu_key['appkey'])

        self.ui.confirm_pushButton.clicked.connect(self.update_parent_info)

    def update_parent_info(self):
        self.parent().baidu_key = {'appid': self.ui.lineEdit_1.text(),
                                   'appkey': self.ui.lineEdit_2.text()}
        self.close()

    # 静态方法创建对话框
    @staticmethod
    def show_dialog(parent=None):
        dialog = MyBaiduDialog(parent)
        dialog.exec_()
