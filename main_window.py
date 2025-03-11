import sys
import threading
import time
import logging
import pyautogui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFrame,
    QListWidget, QListWidgetItem, QStackedWidget
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

import keyboard

from browser_manager import BrowserManager
from key_config_widget import KeyConfigWidget
from ui_widgets import ProxyItemWidget

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NICO METODO")
        self.setFixedSize(350, 400)
        
        self.global_config = {
            'next_order': 0,
            'key_registra_conta': None,
            'key_senha_saque': None,
            'key_conta_saque': None,
            'key_3combo': None,
            'key_codigo_resgate': None,
            'key_hack': None,
            'combo_usuario': (False, float('inf')),
            'combo_email': (False, float('inf')),
            'combo_cpf': (False, float('inf')),
            'toggle_usuario': (False, float('inf')),
            'toggle_numero': (False, float('inf')),
            'toggle_senha1': (False, 0),
            'toggle_senha2': (False, 0),
            'toggle_nome': (False, float('inf')),
            'toggle_cpf': (False, float('inf')),
            'hack_on': False,
            'senha_saque_ativa': False
        }
        
        # Inicializa o gerenciador de abas e proxies
        self.browser_manager = BrowserManager()

        # Página Home
        self.home_widget = QWidget()
        home_layout = QVBoxLayout(self.home_widget)
        home_layout.setContentsMargins(20, 10, 20, 10)
        home_layout.setSpacing(4)

        top_line = QFrame()
        top_line.setFixedHeight(2)
        top_line.setStyleSheet("background-color:#34495e;")
        home_layout.addWidget(top_line)

        title = QLabel("NICO METODO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:16pt; font-weight:bold; color:white;")
        home_layout.addWidget(title)

        lab_url = QLabel("Digite o link:")
        lab_url.setStyleSheet("color:white;")
        home_layout.addWidget(lab_url)
        self.url_entry = QLineEdit()
        home_layout.addWidget(self.url_entry)

        lab_q = QLabel("Escolha a quantidade de abas:")
        lab_q.setStyleSheet("color:white;")
        home_layout.addWidget(lab_q)
        self.quant_combo = QComboBox()
        self.quant_combo.addItems(["1", "2", "3", "4", "5", "6", "10", "12"])
        self.quant_combo.setCurrentText("5")
        self.quant_combo.setStyleSheet("""
            QComboBox {
                background-color: #3e3e42;
                color: white;
                padding: 4px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #3e3e42;
                color: white;
                selection-background-color: #2980b9;
            }
        """)
        home_layout.addWidget(self.quant_combo)

        line_btn = QHBoxLayout()
        self.btn_abrir = QPushButton("Abrir Abas")
        self.btn_abrir.clicked.connect(self.on_abrir_abas)
        line_btn.addWidget(self.btn_abrir)
        self.btn_fechar = QPushButton("Fechar Abas")
        self.btn_fechar.clicked.connect(self.on_fechar_abas)
        line_btn.addWidget(self.btn_fechar)
        home_layout.addLayout(line_btn)

        config_line = QHBoxLayout()
        self.btn_capturar = QPushButton("Captura de Cliques")
        self.btn_capturar.setStyleSheet("background-color:#2c3e50; color:white; padding:6px;")
        self.btn_capturar.clicked.connect(self.on_toggle_capture)
        config_line.addWidget(self.btn_capturar)
        self.btn_proxy = QPushButton("Proxy")
        self.btn_proxy.clicked.connect(self.on_toggle_proxy)
        self.btn_proxy.setStyleSheet("background-color:#2c3e50; color:white; padding:6px;")
        config_line.addWidget(self.btn_proxy)
        home_layout.addLayout(config_line)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        home_layout.addWidget(sep)

        proxy_title = QLabel("Adicionar Proxy Manualmente")
        proxy_title.setStyleSheet("font-weight:bold; color:white;")
        home_layout.addWidget(proxy_title)
        proxy_fmt = QLabel("(Formato: ip:porta:usuário:senha)")
        proxy_fmt.setStyleSheet("color:white;")
        home_layout.addWidget(proxy_fmt)
        self.proxy_entry = QLineEdit()
        home_layout.addWidget(self.proxy_entry)
        pr_line = QHBoxLayout()
        self.btn_add_proxy = QPushButton("Adicionar Proxy")
        self.btn_add_proxy.clicked.connect(self.on_add_proxy)
        pr_line.addWidget(self.btn_add_proxy)
        pr_line.addStretch()
        self.btn_reload = QPushButton("Reload")
        self.btn_reload.setFixedSize(60, 25)
        self.btn_reload.setStyleSheet("background-color:#2980b9; color:white; border-radius:8px;")
        self.btn_reload.clicked.connect(self.on_reload_tabs_pressed)
        pr_line.addWidget(self.btn_reload)
        home_layout.addLayout(pr_line)

        hl_list = QHBoxLayout()
        lab_pl = QLabel("Lista de Proxies:")
        lab_pl.setStyleSheet("font-weight:bold; color:white;")
        hl_list.addWidget(lab_pl)
        btn_refresh = QPushButton("↻")
        btn_refresh.setFixedSize(24, 24)
        btn_refresh.setStyleSheet("background-color:transparent; color:white; border:none;")
        btn_refresh.clicked.connect(self.update_proxy_list_widget)
        hl_list.addWidget(btn_refresh)
        hl_list.addStretch()
        home_layout.addLayout(hl_list)

        self.proxy_list_widget = QListWidget()
        self.proxy_list_widget.setStyleSheet("background-color:#3e3e42;")
        self.proxy_list_widget.setFixedHeight(36)
        home_layout.addWidget(self.proxy_list_widget)

        bot_line = QFrame()
        bot_line.setFixedHeight(1)
        bot_line.setStyleSheet("background-color:#34495e;")
        home_layout.addWidget(bot_line)

        self.status_label = QLabel("")
        bot_line.setFixedHeight(0)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color:yellow;")

        self.update_proxy_list_widget()

        # Página Macro
        self.macro_widget = QWidget()
        macro_layout = QVBoxLayout(self.macro_widget)
        self.key_config_widget = KeyConfigWidget(self)
        macro_layout.addWidget(self.key_config_widget)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.home_widget)
        self.stacked_widget.addWidget(self.macro_widget)

        bottom_layout = QHBoxLayout()
        self.btn_home_mode = QPushButton("Home")
        self.btn_home_mode.setStyleSheet("""
            QPushButton {
                background-color:#2980b9;
                color:white;
                padding:8px;
                border-radius:8px;
                font-weight:bold;
            }
            QPushButton:hover { background-color:#3498db; }
            QPushButton:pressed { background-color:#1f5f7f; }
        """)
        self.btn_home_mode.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        bottom_layout.addWidget(self.btn_home_mode)
        self.btn_macro_mode = QPushButton("Macro")
        self.btn_macro_mode.setStyleSheet("""
            QPushButton {
                background-color:#2980b9;
                color:white;
                padding:8px;
                border-radius:8px;
                font-weight:bold;
            }
            QPushButton:hover { background-color:#3498db; }
            QPushButton:pressed { background-color:#1f5f7f; }
        """)
        self.btn_macro_mode.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        bottom_layout.addWidget(self.btn_macro_mode)
        bottom_layout.addStretch()

        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(bottom_layout)
        self.setCentralWidget(central)

        self.setStyleSheet("""
            QWidget { background-color: #1e1e2e; }
            QLineEdit, QComboBox { background-color: #3e3e42; color: white; padding: 4px; }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 6px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #388E3C; }
            QLabel { color: white; }
        """)

        self.reload_timer = QTimer(self)
        self.reload_timer.setInterval(5000)
        self.reload_timer.timeout.connect(self.enable_reload_button)

    def on_toggle_proxy(self):
        self.browser_manager.use_proxy = not self.browser_manager.use_proxy
        if self.browser_manager.use_proxy:
            self.btn_proxy.setStyleSheet("background-color:#27ae60; color:white; padding:6px;")
            print("Proxy ligado")
        else:
            self.btn_proxy.setStyleSheet("background-color:#2c3e50; color:white; padding:6px;")
            print("Proxy desligado")

    def on_abrir_abas(self):
        link = self.url_entry.text().strip()
        try:
            quantidade = int(self.quant_combo.currentText())
        except ValueError:
            quantidade = 1
        if not link:
            print("Nenhum link informado.")
            return
        self.btn_abrir.setEnabled(False)
        def finish_callback():
            self.btn_abrir.setEnabled(True)
            print("Abas abertas com sucesso!")
        threading.Thread(target=self.browser_manager.open_tabs, args=(link, quantidade, finish_callback), daemon=True).start()

    def on_fechar_abas(self):
        threading.Thread(target=self.browser_manager.close_tabs, daemon=True).start()

    def on_toggle_capture(self):
        self.browser_manager.toggle_capture()
        if self.browser_manager.capture_tabs_active:
            self.btn_capturar.setStyleSheet("background-color:#27ae60; color:white; padding:6px;")
        else:
            self.btn_capturar.setStyleSheet("background-color:#2c3e50; color:white; padding:6px;")
        logger.info("Captura de Cliques: %s", "Ativada" if self.browser_manager.capture_tabs_active else "Desativada")

    def on_hotkey_registra_pressed(self):
        if self.global_config.get('hack_on'):
            logger.info("Hack ativo: preenchimento automático via hack")
            self.on_hotkey_hack_pressed()
            return
        toggles = []
        for key in ["toggle_usuario", "toggle_numero", "toggle_senha1", "toggle_senha2", "toggle_nome", "toggle_cpf"]:
            active, order = self.global_config.get(key, (False, float('inf')))
            if active:
                toggles.append((order, key))
        toggles.sort(key=lambda x: x[0])
        if not toggles:
            logger.info("Nenhuma toggle ativa para registrar conta; nenhum dado gerado.")
            return
        texts = []
        for _, key in toggles:
            if key == "toggle_usuario":
                from data_generators import gerar_usuario
                texts.append(gerar_usuario())
            elif key == "toggle_numero":
                from data_generators import gerar_numero
                texts.append(gerar_numero())
            elif key == "toggle_senha1":
                from data_generators import gerar_senha_original
                texts.append(gerar_senha_original())
            elif key == "toggle_senha2":
                from data_generators import gerar_senha_original
                texts.append(gerar_senha_original())
            elif key == "toggle_nome":
                from data_generators import gerar_nome
                texts.append(gerar_nome())
            elif key == "toggle_cpf":
                from data_generators import gerar_cpf
                texts.append(gerar_cpf())
        active_driver = None
        for drv in self.browser_manager.drivers:
            try:
                if drv.execute_script("return document.hasFocus() && document.activeElement.tagName.toLowerCase() !== 'body';"):
                    active_driver = drv
                    break
            except Exception as e:
                logger.error("Erro verificando foco: %s", e)
        if not active_driver and self.browser_manager.drivers:
            active_driver = self.browser_manager.drivers[0]
        if active_driver:
            try:
                active_driver.execute_script("{}".format(
                    __import__('js_scripts').js_preencher_campos()
                ), texts, False)
                logger.info("Dados inseridos (Registrar Conta): %s", texts)
            except Exception as e:
                logger.error("Erro inserindo dados: %s", e)
        else:
            logger.info("Nenhuma aba para inserir dados.")

    def on_hotkey_senha_pressed(self):
        if not self.global_config['senha_saque_ativa']:
            logger.info("Senha de saque desativada.")
            return
        from data_generators import gerar_senha
        senha = gerar_senha()
        texts = [senha, senha]
        if self.global_config.get('hack_on'):
            for drv in self.browser_manager.drivers:
                try:
                    drv.execute_script(__import__('js_scripts').js_preencher_campos(), texts, True)
                    logger.info("Hack: Senha de saque inserida: %s", texts)
                except Exception as e:
                    logger.error("Erro no hack da senha: %s", e)
        else:
            active_driver = None
            for drv in self.browser_manager.drivers:
                try:
                    if drv.execute_script("return document.hasFocus() && document.activeElement.tagName.toLowerCase() !== 'body';"):
                        active_driver = drv
                        break
                except Exception as e:
                    logger.error("Erro verificando foco: %s", e)
            if not active_driver and self.browser_manager.drivers:
                active_driver = self.browser_manager.drivers[0]
            if active_driver:
                try:
                    active_driver.execute_script(__import__('js_scripts').js_preencher_campos(), texts, True)
                    logger.info("Senha de saque inserida: %s", texts)
                except Exception as e:
                    logger.error("Erro inserindo senha: %s", e)
            else:
                logger.info("Nenhuma aba para inserir senha.")

    def on_hotkey_conta_saque_pressed(self):
        toggles = []
        for key in ["combo_usuario", "combo_email", "combo_cpf"]:
            active, order = self.global_config.get(key, (False, float('inf')))
            if active:
                toggles.append((order, key))
        toggles.sort(key=lambda x: x[0])
        if not toggles:
            logger.info("Nenhuma toggle ativa para conta de saque; nenhum dado gerado.")
            return
        if self.global_config.get('hack_on'):
            best_time = 0
            best_x = None
            best_y = None
            for drv in self.browser_manager.drivers:
                try:
                    tstr = drv.execute_script("return window.localStorage.getItem('hackLastClickTime');")
                    xstr = drv.execute_script("return window.localStorage.getItem('hackClickX');")
                    ystr = drv.execute_script("return window.localStorage.getItem('hackClickY');")
                    if tstr:
                        tval = int(tstr)
                        if tval > best_time:
                            best_time = tval
                            best_x = xstr
                            best_y = ystr
                except Exception as e:
                    logger.error("Erro no hack combo: %s", e)
            if best_x is None or best_y is None:
                best_x = 0
                best_y = 0
            pageX = int(best_x) if best_x else 0
            pageY = int(best_y) if best_y else 0
            script = """
            var texts = arguments[0];
            var px = arguments[1];
            var py = arguments[2];
            var cx = px - window.scrollX;
            var cy = py - window.scrollY;
            var el = document.elementFromPoint(cx, cy);
            if(!el){
                el = document.querySelector('input, textarea, select, a, button, [tabindex]:not([tabindex="-1"])');
            }
            if(el){
                el.focus();
                el.value = texts[0];
                el.dispatchEvent(new Event('input', {bubbles:true}));
                function getNextFocusable(element){
                    var focusable = Array.prototype.slice.call(document.querySelectorAll('input, textarea, select, a, button, [tabindex]:not([tabindex="-1"])'));
                    var index = focusable.indexOf(element);
                    if(index > -1 && index < focusable.length - 1){
                        return focusable[index+1];
                    }
                    return null;
                }
                for(var i=1; i<texts.length; i++){
                    var next = getNextFocusable(el);
                    if(next){
                        next.focus();
                        next.value = texts[i];
                        next.dispatchEvent(new Event('input', {bubbles:true}));
                        el = next;
                    }
                }
            }
            """
            for drv in self.browser_manager.drivers:
                local_texts = []
                for _, key in toggles:
                    if key == "combo_usuario":
                        from data_generators import gerar_usuario
                        local_texts.append(gerar_usuario())
                    elif key == "combo_email":
                        from data_generators import gerar_email_uorak
                        local_texts.append(gerar_email_uorak())
                    elif key == "combo_cpf":
                        from data_generators import gerar_cpf
                        local_texts.append(gerar_cpf())
                try:
                    drv.execute_script(script, local_texts, pageX, pageY)
                    logger.info("Hack: Dados de conta de saque inseridos: %s", local_texts)
                except Exception as e:
                    logger.error("Erro no hack combo: %s", e)
        else:
            texts = []
            for _, key in toggles:
                if key == "combo_usuario":
                    from data_generators import gerar_usuario
                    texts.append(gerar_usuario())
                elif key == "combo_email":
                    from data_generators import gerar_email_uorak
                    texts.append(gerar_email_uorak())
                elif key == "combo_cpf":
                    from data_generators import gerar_cpf
                    texts.append(gerar_cpf())
            active_driver = None
            for drv in self.browser_manager.drivers:
                try:
                    if drv.execute_script("return document.hasFocus() && document.activeElement.tagName.toLowerCase() !== 'body';"):
                        active_driver = drv
                        break
                except Exception as e:
                    logger.error("Erro verificando foco: %s", e)
            if not active_driver and self.browser_manager.drivers:
                active_driver = self.browser_manager.drivers[0]
            if active_driver:
                try:
                    active_driver.execute_script(__import__('js_scripts').js_preencher_campos(), texts, False)
                    logger.info("Dados de conta de saque inseridos: %s", texts)
                except Exception as e:
                    logger.error("Erro inserindo combo: %s", e)
            else:
                logger.info("Nenhuma aba para inserir combo.")

    def on_hotkey_codigo_resgate_pressed(self):
        codigo_resgate = self.key_config_widget.edit_resgate.text().strip()
        if not codigo_resgate:
            logger.info("Código de resgate vazio.")
            return
        if self.global_config.get('hack_on'):
            best_time = 0
            best_x = None
            best_y = None
            for drv in self.browser_manager.drivers:
                try:
                    tstr = drv.execute_script("return window.localStorage.getItem('hackLastClickTime');")
                    xstr = drv.execute_script("return window.localStorage.getItem('hackClickX');")
                    ystr = drv.execute_script("return window.localStorage.getItem('hackClickY');")
                    if tstr:
                        tval = int(tstr)
                        if tval > best_time:
                            best_time = tval
                            best_x = xstr
                            best_y = ystr
                except Exception as e:
                    logger.error("Erro no hack código: %s", e)
            if best_x is None or best_y is None:
                best_x = 0
                best_y = 0
            pageX = int(best_x) if best_x else 0
            pageY = int(best_y) if best_y else 0
            script = """
            var codigo = arguments[0];
            var px = arguments[1];
            var py = arguments[2];
            var cx = px - window.scrollX;
            var cy = py - window.scrollY;
            var el = document.elementFromPoint(cx, cy);
            if(!el){
                el = document.querySelector('input, textarea, select, a, button, [tabindex]:not([tabindex="-1"])');
            }
            if(el){
                el.focus();
                el.value = codigo;
                el.dispatchEvent(new Event('input', {bubbles:true}));
            }
            """
            for drv in self.browser_manager.drivers:
                try:
                    drv.execute_script(script, codigo_resgate, pageX, pageY)
                    logger.info("Hack: Código de resgate inserido: %s", codigo_resgate)
                except Exception as e:
                    logger.error("Erro no hack código: %s", e)
        else:
            active_driver = None
            for drv in self.browser_manager.drivers:
                try:
                    if drv.execute_script("return document.hasFocus() && document.activeElement.tagName.toLowerCase() !== 'body';"):
                        active_driver = drv
                        break
                except Exception as e:
                    logger.error("Erro verificando foco: %s", e)
            if not active_driver and self.browser_manager.drivers:
                active_driver = self.browser_manager.drivers[0]
            if active_driver:
                try:
                    active_driver.execute_script("""
                    var codigo = arguments[0];
                    var el = document.activeElement;
                    if(!el || el.tagName.toLowerCase() === "body"){
                        el = document.querySelector('input, textarea, select, a, button, [tabindex]:not([tabindex="-1"])');
                    }
                    if(el){
                        el.focus();
                        el.value = codigo;
                        el.dispatchEvent(new Event('input', {bubbles:true}));
                    }
                    """, codigo_resgate)
                    logger.info("Código de resgate inserido: %s", codigo_resgate)
                except Exception as e:
                    logger.error("Erro inserindo código de resgate: %s", e)
            else:
                logger.info("Nenhuma aba para inserir código de resgate.")

    def on_hotkey_hack_pressed(self):
        toggles = []
        for key in ["toggle_usuario", "toggle_numero", "toggle_senha1", "toggle_senha2", "toggle_nome", "toggle_cpf"]:
            active, order = self.global_config.get(key, (False, float('inf')))
            if active:
                toggles.append((order, key))
        toggles.sort(key=lambda x: x[0])
        if not toggles:
            logger.info("Nenhuma toggle ativa para Hack.")
            return
        best_time = 0
        best_x = None
        best_y = None
        for drv in self.browser_manager.drivers:
            try:
                tstr = drv.execute_script("return window.localStorage.getItem('hackLastClickTime');")
                xstr = drv.execute_script("return window.localStorage.getItem('hackClickX');")
                ystr = drv.execute_script("return window.localStorage.getItem('hackClickY');")
                if tstr:
                    tval = int(tstr)
                    if tval > best_time:
                        best_time = tval
                        best_x = xstr
                        best_y = ystr
            except Exception as e:
                logger.error("Erro no hack: %s", e)
        if best_x is None or best_y is None:
            best_x = 0
            best_y = 0
        pageX = int(best_x) if best_x else 0
        pageY = int(best_y) if best_y else 0
        script = """
        var texts = arguments[0];
        var px = arguments[1];
        var py = arguments[2];
        var cx = px - window.scrollX;
        var cy = py - window.scrollY;
        var el = document.elementFromPoint(cx, cy);
        if(!el){
            el = document.querySelector('input, textarea, select, a, button, [tabindex]:not([tabindex="-1"])');
        }
        if(el){
            el.focus();
            el.value = texts[0];
            el.dispatchEvent(new Event('input', {bubbles:true}));
            function getNextFocusable(element){
                var focusable = Array.prototype.slice.call(document.querySelectorAll('input, textarea, select, a, button, [tabindex]:not([tabindex="-1"])'));
                var index = focusable.indexOf(element);
                if(index > -1 && index < focusable.length - 1){
                    return focusable[index+1];
                }
                return null;
            }
            for(var i=1; i<texts.length; i++){
                var next = getNextFocusable(el);
                if(next){
                    next.focus();
                    next.value = texts[i];
                    next.dispatchEvent(new Event('input', {bubbles:true}));
                    el = next;
                }
            }
        }
        """
        for drv in self.browser_manager.drivers:
            local_texts = []
            for _, key in toggles:
                if key == "toggle_usuario":
                    from data_generators import gerar_usuario
                    local_texts.append(gerar_usuario())
                elif key == "toggle_numero":
                    from data_generators import gerar_numero
                    local_texts.append(gerar_numero())
                elif key == "toggle_senha1":
                    from data_generators import gerar_senha_original
                    local_texts.append(gerar_senha_original())
                elif key == "toggle_senha2":
                    from data_generators import gerar_senha_original
                    local_texts.append(gerar_senha_original())
                elif key == "toggle_nome":
                    from data_generators import gerar_nome
                    local_texts.append(gerar_nome())
                elif key == "toggle_cpf":
                    from data_generators import gerar_cpf
                    local_texts.append(gerar_cpf())
            try:
                drv.execute_script(script, local_texts, pageX, pageY)
                logger.info("Hack: Dados inseridos: %s", local_texts)
            except Exception as e:
                logger.error("Erro no hack: %s", e)

    def on_reload_tabs_pressed(self):
        def finish_reload():
            self.btn_reload.setEnabled(False)
            self.reload_timer.start()
        threading.Thread(target=lambda: self.browser_manager.reload_tabs(finish_reload), daemon=True).start()

    def enable_reload_button(self):
        self.btn_reload.setEnabled(True)
        self.reload_timer.stop()

    def on_add_proxy(self):
        newp = self.proxy_entry.text().strip()
        ret = self.browser_manager.add_proxy(newp)
        print("Proxy adicionado:", newp)
        self.status_label.setText(ret)
        self.proxy_entry.clear()
        self.update_proxy_list_widget()
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))

    def update_proxy_list_widget(self):
        self.proxy_list_widget.clear()
        for pxy in self.browser_manager.proxy_list:
            item = QListWidgetItem(self.proxy_list_widget)
            widget = ProxyItemWidget(pxy, self.remove_proxy)
            item.setSizeHint(widget.sizeHint())
            self.proxy_list_widget.addItem(item)
            self.proxy_list_widget.setItemWidget(item, widget)

    def remove_proxy(self, pxy):
        self.browser_manager.remove_proxy(pxy)
        self.update_proxy_list_widget()
        print("Proxy removido:", pxy)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
