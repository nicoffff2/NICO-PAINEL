from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QKeySequence
import keyboard

from ui_widgets import ToggleButton, SingleClickLineEdit, make_toggle_handler

class KeyConfigWidget(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.global_config = main_window.global_config

        # Inicializa as configurações se ainda não existirem
        for key in ['key_registra_conta', 'key_senha_saque', 'key_conta_saque',
                    'key_3combo', 'key_codigo_resgate', 'key_hack']:
            if key not in self.global_config:
                self.global_config[key] = None
        if 'next_order' not in self.global_config:
            self.global_config['next_order'] = 0
        for key in ['combo_usuario', 'combo_email', 'combo_cpf']:
            if key not in self.global_config:
                self.global_config[key] = (False, float('inf'))
        for key in ['toggle_usuario', 'toggle_numero', 'toggle_senha1',
                    'toggle_senha2', 'toggle_nome', 'toggle_cpf']:
            if key not in self.global_config:
                self.global_config[key] = (False, float('inf'))
        if 'key_capture' not in self.global_config:
            self.global_config['key_capture'] = None

        self.is_capturing_key = False
        self.capture_mode = None
        self.captured_key = None
        self.OFF_COLOR = "#2980b9"
        self.CAPTURE_OFF = "#c0392b"
        self.CAPTURE_ON = "#27ae60"

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(8, 8, 8, 8)
        mainLayout.setSpacing(10)

        header = QLabel("Configuração de Teclas")
        header.setFont(QFont("Arial", 15, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(header)
        mainLayout.addWidget(self._hr())

        # Registra Conta
        regLayout = QHBoxLayout()
        regLayout.addWidget(QLabel("Registra Conta"))
        self.btn_registra_conta = QPushButton("Key")
        self.btn_registra_conta.setFixedSize(60, 25)
        self.btn_registra_conta.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
        self.btn_registra_conta.clicked.connect(self.on_btn_registra_conta_clicked)
        regLayout.addWidget(self.btn_registra_conta)
        regLayout.addStretch()
        mainLayout.addLayout(regLayout)
        mainLayout.addWidget(self._hr())

        # Toggles para geração de dados
        togglesLayout = QHBoxLayout()
        self.btn_usuario = ToggleButton("usuario")
        self.btn_numero = ToggleButton("numero")
        self.btn_senha1 = ToggleButton("senha1")
        self.btn_senha2 = ToggleButton("senha2")
        self.btn_nome = ToggleButton("nome")
        self.btn_cpf = ToggleButton("cpf")
        self.btn_usuario.toggled.connect(make_toggle_handler("toggle_usuario", self.btn_usuario, self.global_config))
        self.btn_numero.toggled.connect(make_toggle_handler("toggle_numero", self.btn_numero, self.global_config))
        self.btn_senha1.toggled.connect(self.on_senha1_toggled)
        self.btn_senha2.toggled.connect(self.on_senha2_toggled)
        self.btn_nome.toggled.connect(make_toggle_handler("toggle_nome", self.btn_nome, self.global_config))
        self.btn_cpf.toggled.connect(make_toggle_handler("toggle_cpf", self.btn_cpf, self.global_config))
        togglesLayout.addWidget(self.btn_usuario)
        togglesLayout.addWidget(self.btn_numero)
        togglesLayout.addWidget(self.btn_senha1)
        togglesLayout.addWidget(self.btn_senha2)
        togglesLayout.addWidget(self.btn_nome)
        togglesLayout.addWidget(self.btn_cpf)
        mainLayout.addLayout(togglesLayout)
        mainLayout.addWidget(self._hr())

        # Conta de Saque
        contLayout = QHBoxLayout()
        contLayout.addWidget(QLabel("Conta de saque"))
        self.btn_conta_saque = QPushButton("Key")
        self.btn_conta_saque.setFixedSize(60, 25)
        self.btn_conta_saque.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
        self.btn_conta_saque.clicked.connect(self.on_btn_conta_saque_clicked)
        contLayout.addWidget(self.btn_conta_saque)
        contLayout.addStretch()
        mainLayout.addLayout(contLayout)
        mainLayout.addWidget(self._hr())

        # Combo (usuário, email, cpf)
        comboLayout = QHBoxLayout()
        self.btn_combo_usuario = ToggleButton("usuario")
        self.btn_combo_usuario.setFixedSize(45, 18)
        self.btn_combo_email = ToggleButton("email")
        self.btn_combo_email.setFixedSize(45, 18)
        self.btn_combo_cpf = ToggleButton("cpf")
        self.btn_combo_cpf.setFixedSize(45, 18)
        self.btn_combo_usuario.toggled.connect(make_toggle_handler("combo_usuario", self.btn_combo_usuario, self.global_config))
        self.btn_combo_email.toggled.connect(make_toggle_handler("combo_email", self.btn_combo_email, self.global_config))
        self.btn_combo_cpf.toggled.connect(make_toggle_handler("combo_cpf", self.btn_combo_cpf, self.global_config))
        comboLayout.addWidget(self.btn_combo_usuario)
        comboLayout.addWidget(self.btn_combo_email)
        comboLayout.addWidget(self.btn_combo_cpf)
        comboLayout.addStretch()
        mainLayout.addLayout(comboLayout)
        mainLayout.addWidget(self._hr())

        # Senha de Saque
        senhaLayout = QHBoxLayout()
        senhaLayout.addWidget(QLabel("senha de saque"))
        self.btn_senha_saque = QPushButton("Key")
        self.btn_senha_saque.setFixedSize(60, 25)
        self.btn_senha_saque.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
        self.btn_senha_saque.clicked.connect(self.on_btn_senha_saque_clicked)
        senhaLayout.addWidget(self.btn_senha_saque)
        senhaLayout.addStretch()
        mainLayout.addLayout(senhaLayout)
        mainLayout.addWidget(self._hr())

        # Código de Resgate
        resgateLayout = QHBoxLayout()
        self.btn_resgate_key = QPushButton("Key")
        self.btn_resgate_key.setFixedSize(60, 25)
        self.btn_resgate_key.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
        self.btn_resgate_key.clicked.connect(self.on_btn_resgate_key_clicked)
        resgateLayout.addWidget(self.btn_resgate_key)
        resgateLayout.addWidget(QLabel("Código de Resgate"))
        self.edit_resgate = SingleClickLineEdit()
        self.edit_resgate.setFixedWidth(120)
        resgateLayout.addWidget(self.edit_resgate)
        resgateLayout.addStretch()
        mainLayout.addLayout(resgateLayout)
        mainLayout.addWidget(self._hr())

        # Captura de Cliques e Hack
        captureLayout = QHBoxLayout()
        self.btn_capture_toggle = QPushButton("Key")
        self.btn_capture_toggle.setFixedSize(60, 25)
        self.btn_capture_toggle.setStyleSheet(f"background-color:{self.CAPTURE_OFF}; color:white; border-radius:4px;")
        self.btn_capture_toggle.clicked.connect(self.on_btn_capture_toggle_clicked)
        captureLayout.addWidget(self.btn_capture_toggle)
        captureLayout.addWidget(QLabel("Atalho Captura de Cliques"))
        self.btn_hack_toggle = QPushButton("Hack")
        self.btn_hack_toggle.setCheckable(True)
        self.btn_hack_toggle.setFixedSize(60, 25)
        self.btn_hack_toggle.setStyleSheet("background-color:#c0392b; color:white; border-radius:4px;")
        self.btn_hack_toggle.clicked.connect(self.on_toggle_hack)
        captureLayout.addWidget(self.btn_hack_toggle)
        mainLayout.addLayout(captureLayout)
        mainLayout.addWidget(self._hr())

        mainLayout.addStretch()

    def _hr(self):
        hr = QFrame()
        hr.setFrameShape(QFrame.HLine)
        hr.setStyleSheet("background-color:#aaaaaa;")
        hr.setFixedHeight(2)
        return hr

    def cancel_if_press(self, btn, key_name):
        if btn.text().startswith("Press"):
            if self.global_config.get(key_name):
                key_str, hotkey_id = self.global_config[key_name]
                keyboard.remove_hotkey(hotkey_id)
                self.global_config[key_name] = None
            btn.setText("Key")
            if key_name == "key_capture":
                btn.setStyleSheet(f"background-color:{self.CAPTURE_OFF}; color:white; border-radius:4px;")
            else:
                btn.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
            return True
        return False

    def cancel_key_capture(self):
        if not self.is_capturing_key:
            return
        if self.capture_mode == "registra_conta":
            self.btn_registra_conta.setText("Key")
            self.btn_registra_conta.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
        elif self.capture_mode == "conta_saque":
            self.btn_conta_saque.setText("Key")
            self.btn_conta_saque.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
        elif self.capture_mode == "senha_saque":
            self.btn_senha_saque.setText("Key")
            self.btn_senha_saque.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
        elif self.capture_mode == "codigo_resgate":
            self.btn_resgate_key.setText("Key")
            self.btn_resgate_key.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
        self.is_capturing_key = False
        self.capture_mode = None
        self.releaseKeyboard()

    def on_btn_registra_conta_clicked(self):
        if self.cancel_if_press(self.btn_registra_conta, 'key_registra_conta'):
            return
        if self.global_config.get('key_registra_conta'):
            key_str, hotkey_id = self.global_config['key_registra_conta']
            keyboard.remove_hotkey(hotkey_id)
            self.global_config['key_registra_conta'] = None
            self.btn_registra_conta.setText("Key")
            self.btn_registra_conta.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
            return
        self.is_capturing_key = True
        self.capture_mode = "registra_conta"
        self.btn_registra_conta.setText("Press...")
        self.btn_registra_conta.setStyleSheet("background-color:#808080; color:white; border-radius:4px;")
        self.grabKeyboard()
        self.setFocus()

    def on_btn_conta_saque_clicked(self):
        if self.cancel_if_press(self.btn_conta_saque, 'key_conta_saque'):
            return
        if self.global_config.get('key_conta_saque'):
            key_str, hotkey_id = self.global_config['key_conta_saque']
            keyboard.remove_hotkey(hotkey_id)
            self.global_config['key_conta_saque'] = None
            self.btn_conta_saque.setText("Key")
            self.btn_conta_saque.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
            return
        self.is_capturing_key = True
        self.capture_mode = "conta_saque"
        self.btn_conta_saque.setText("Press...")
        self.btn_conta_saque.setStyleSheet("background-color:#808080; color:white; border-radius:4px;")
        self.grabKeyboard()
        self.setFocus()

    def on_btn_senha_saque_clicked(self):
        if self.cancel_if_press(self.btn_senha_saque, 'key_senha_saque'):
            self.global_config['senha_saque_ativa'] = False
            return
        if self.global_config.get('key_senha_saque'):
            key_str, hotkey_id = self.global_config['key_senha_saque']
            keyboard.remove_hotkey(hotkey_id)
            self.global_config['key_senha_saque'] = None
            self.global_config['senha_saque_ativa'] = False
            self.btn_senha_saque.setText("Key")
            self.btn_senha_saque.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
            return
        self.is_capturing_key = True
        self.capture_mode = "senha_saque"
        self.btn_senha_saque.setText("Press...")
        self.btn_senha_saque.setStyleSheet("background-color:#808080; color:white; border-radius:4px;")
        self.grabKeyboard()
        self.setFocus()

    def on_btn_resgate_key_clicked(self):
        if self.cancel_if_press(self.btn_resgate_key, 'key_codigo_resgate'):
            return
        if self.global_config.get('key_codigo_resgate'):
            key_str, hotkey_id = self.global_config['key_codigo_resgate']
            keyboard.remove_hotkey(hotkey_id)
            self.global_config['key_codigo_resgate'] = None
            self.btn_resgate_key.setText("Key")
            self.btn_resgate_key.setStyleSheet(f"background-color:{self.OFF_COLOR}; color:white; border-radius:4px;")
            return
        self.is_capturing_key = True
        self.capture_mode = "codigo_resgate"
        self.btn_resgate_key.setText("Press...")
        self.btn_resgate_key.setStyleSheet("background-color:#808080; color:white; border-radius:4px;")
        self.grabKeyboard()
        self.setFocus()

    def on_btn_capture_toggle_clicked(self):
        if self.cancel_if_press(self.btn_capture_toggle, 'key_capture'):
            return
        if self.global_config.get('key_capture'):
            key_str, hotkey_id = self.global_config['key_capture']
            keyboard.remove_hotkey(hotkey_id)
            self.global_config['key_capture'] = None
            self.btn_capture_toggle.setText("Key")
            self.btn_capture_toggle.setStyleSheet(f"background-color:{self.CAPTURE_OFF}; color:white; border-radius:4px;")
            return
        self.is_capturing_key = True
        self.capture_mode = "capture"
        self.btn_capture_toggle.setText("Press...")
        self.btn_capture_toggle.setStyleSheet("background-color:#808080; color:white; border-radius:4px;")
        self.grabKeyboard()
        self.setFocus()

    def keyPressEvent(self, event):
        if self.is_capturing_key:
            self.captured_key = event.text() or QKeySequence(event.key()).toString()
            if self.capture_mode == "registra_conta":
                self.btn_registra_conta.setText("Key: " + self.captured_key)
            elif self.capture_mode == "conta_saque":
                self.btn_conta_saque.setText("Key: " + self.captured_key)
            elif self.capture_mode == "senha_saque":
                self.btn_senha_saque.setText("Key: " + self.captured_key)
            elif self.capture_mode == "codigo_resgate":
                self.btn_resgate_key.setText("Key: " + self.captured_key)
            elif self.capture_mode == "capture":
                self.btn_capture_toggle.setText("Key: " + self.captured_key)
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self.is_capturing_key:
            self.is_capturing_key = False
            self.releaseKeyboard()
            captured_key = event.text() or QKeySequence(event.key()).toString()
            if self.capture_mode == "registra_conta":
                hotkey_id = keyboard.add_hotkey(captured_key, self.main_window.on_hotkey_registra_pressed, suppress=True)
                self.global_config['key_registra_conta'] = (captured_key, hotkey_id)
                self.btn_registra_conta.setText("Key: " + captured_key)
            elif self.capture_mode == "conta_saque":
                hotkey_id = keyboard.add_hotkey(captured_key, self.main_window.on_hotkey_conta_saque_pressed, suppress=True)
                self.global_config['key_conta_saque'] = (captured_key, hotkey_id)
                self.btn_conta_saque.setText("Key: " + captured_key)
            elif self.capture_mode == "senha_saque":
                hotkey_id = keyboard.add_hotkey(captured_key, self.main_window.on_hotkey_senha_pressed, suppress=True)
                self.global_config['key_senha_saque'] = (captured_key, hotkey_id)
                self.global_config['senha_saque_ativa'] = True
                self.btn_senha_saque.setText("Key: " + captured_key)
            elif self.capture_mode == "codigo_resgate":
                hotkey_id = keyboard.add_hotkey(captured_key, self.main_window.on_hotkey_codigo_resgate_pressed, suppress=True)
                self.global_config['key_codigo_resgate'] = (captured_key, hotkey_id)
                self.btn_resgate_key.setText("Key: " + captured_key)
            elif self.capture_mode == "capture":
                hotkey_id = keyboard.add_hotkey(captured_key, self.main_window.on_toggle_capture, suppress=True)
                self.global_config['key_capture'] = (captured_key, hotkey_id)
                self.btn_capture_toggle.setText("Key: " + captured_key)
                self.btn_capture_toggle.setStyleSheet(f"background-color:{self.CAPTURE_ON}; color:white; border-radius:4px;")
            self.capture_mode = None
            return
        super().keyReleaseEvent(event)

    def on_senha2_toggled(self, checked):
        if checked and not self.btn_senha1.isChecked():
            self.btn_senha1.setChecked(True)
        if checked:
            if self.btn_senha2.order is None:
                self.btn_senha2.order = self.global_config.get('next_order', 0)
                self.global_config['next_order'] = self.btn_senha2.order + 1
            self.global_config["toggle_senha2"] = (True, self.btn_senha2.order)
        else:
            self.btn_senha2.order = None
            self.global_config["toggle_senha2"] = (False, float('inf'))

    def on_senha1_toggled(self, checked):
        if not checked and self.btn_senha2.isChecked():
            self.btn_senha2.setChecked(False)
            self.global_config["toggle_senha1"] = (False, 0)
            self.global_config["toggle_senha2"] = (False, 0)
        else:
            if checked and self.btn_senha1.order is None:
                self.btn_senha1.order = self.global_config.get('next_order', 0)
                self.global_config['next_order'] = self.btn_senha1.order + 1
            self.global_config["toggle_senha1"] = (checked, self.btn_senha1.order if checked else float('inf'))

    def on_toggle_hack(self, checked):
        if checked:
            self.btn_hack_toggle.setStyleSheet("background-color:#27ae60; color:white; border-radius:4px;")
            self.global_config['hack_on'] = True
        else:
            self.btn_hack_toggle.setStyleSheet("background-color:#c0392b; color:white; border-radius:4px;")
            self.global_config['hack_on'] = False
