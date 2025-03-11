from PyQt5.QtWidgets import QPushButton, QLineEdit, QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont

class ToggleButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setCheckable(True)
        self.setFixedSize(49, 18)
        self.setFont(QFont("Arial", 6))
        self.setStyleSheet("background-color:#c0392b; color:white; border-radius:2px;")
        self.setChecked(False)
        self.order = None
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked):
        if checked:
            self.setStyleSheet("background-color:#27ae60; color:white; border-radius:2px;")
        else:
            self.setStyleSheet("background-color:#c0392b; color:white; border-radius:2px;")
            self.order = None

class SingleClickLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def mousePressEvent(self, event):
        self.setReadOnly(False)
        super().mousePressEvent(event)

    def focusOutEvent(self, event):
        self.setReadOnly(True)
        super().focusOutEvent(event)

class ProxyItemWidget(QWidget):
    def __init__(self, proxy, remove_callback):
        super().__init__()
        self.proxy = proxy
        self.remove_callback = remove_callback
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        self.label = QLabel(proxy)
        self.label.setStyleSheet("color:white;")
        layout.addWidget(self.label)
        self.btn_remove = QPushButton("-")
        self.btn_remove.setFixedSize(16, 16)
        self.btn_remove.setStyleSheet("background-color:transparent; color:white; border:none; font-size:10pt;")
        layout.addWidget(self.btn_remove)
        self.btn_remove.clicked.connect(lambda: self.remove_callback(self.proxy))

def make_toggle_handler(key, btn, config):
    def handler(checked):
        if checked:
            if btn.order is None:
                btn.order = config.get('next_order', 0)
                config['next_order'] = btn.order + 1
        else:
            btn.order = None
        config[key] = (checked, btn.order if checked else float('inf'))
    return handler
