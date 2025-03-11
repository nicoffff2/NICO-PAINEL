import sys
import threading
import time
import random
import pyautogui
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Se não precisar do seleniumwire, pode remover e usar apenas webdriver normal do Selenium
from seleniumwire import webdriver  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# from selenium_stealth import stealth  # Descomente se quiser camuflagem

from js_scripts import js_configurar_clique, js_replicate_click
# Caso não use, pode remover js_preencher_campos
from data_generators import (
    gerar_usuario, gerar_numero, gerar_senha,
    gerar_senha_original, gerar_nome, gerar_cpf, gerar_email_uorak
)

# Configuração do logger
logging.getLogger("seleniumwire").disabled = True
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class BrowserManager:
    def __init__(self):
        self.drivers = []
        self.proxy_list = []
        self.use_proxy = False
        self.capture_tabs_active = False
        self.poll_thread = None
        self.lock = threading.Lock()  # Protege acesso à lista de drivers e proxies

        # Obtém o caminho do driver apenas uma vez para agilizar a abertura de novas abas
        self.driver_path = ChromeDriverManager().install()

    def add_proxy(self, new_proxy):
        if not new_proxy:
            return "Insira um proxy."
        proxies = []
        for sep in ["\n", ","]:
            if sep in new_proxy:
                proxies = [p.strip() for p in new_proxy.split(sep) if p.strip()]
                break
        if not proxies:
            proxies = [new_proxy]
        added, invalid = 0, 0
        for p in proxies:
            parts = p.split(':')
            if len(parts) == 4:
                with self.lock:
                    self.proxy_list.append(p)
                added += 1
            else:
                invalid += 1
        if added > 0 and invalid == 0:
            return f"{added} proxy(s) adicionado(s)!"
        elif added > 0 and invalid > 0:
            return f"{added} proxy(s) adicionado(s), mas {invalid} inválido(s)!"
        else:
            return "Formato inválido!"

    def remove_proxy(self, proxy):
        with self.lock:
            if proxy in self.proxy_list:
                self.proxy_list.remove(proxy)

    def _create_chrome_options(self, link, pos, width, height):
        """Cria e retorna o objeto Options para abrir a aba de forma mais leve."""
        x, y = pos
        options = Options()
        # Se tiver um Chrome/Chromium em local diferente, ajuste o caminho abaixo:
        options.binary_location = r"C:\Users\NICO FF\AppData\Local\Chromium\Application\chrome.exe"

        # Configurações para minimizar uso de recursos e deixar o browser 'leve'
        options.add_argument(f"--app={link}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--new-window")
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument(f"--window-position={x},{y}")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-in-process-stack-traces")
        options.add_argument("--disable-logging")
        #user_agent = "Mozilla/5.0 (Linux; U; Android 14; pt-br; SM-G977F Build/UP1A.231005.007) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0.3163.128 Mobile Safari/537.36 XiaoMi/Mint Browser/3.9.3"
        #options.add_argument(f"user-agent={user_agent}")
        
        # Remove a mensagem "Chrome is being controlled by automated test software"
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        return options

    def open_tab(self, link, pos, width, height):
        """Abre uma aba do Chrome com configurações de proxy (se ativo) e de leveza."""
        options = self._create_chrome_options(link, pos, width, height)

        # Configuração de proxy (via seleniumwire) se necessário
        seleniumwire_options = {}
        if self.use_proxy and self.proxy_list:
            with self.lock:
                chosen_proxy = random.choice(self.proxy_list)
                self.proxy_list.remove(chosen_proxy)
            parts = chosen_proxy.split(':')
            if len(parts) == 4:
                host, prt, user, pwd = parts
                seleniumwire_options = {
                    'proxy': {
                        'http': f'http://{user}:{pwd}@{host}:{prt}',
                        'https': f'https://{user}:{pwd}@{host}:{prt}',
                        'no_proxy': 'localhost,127.0.0.1'
                    }
                }
                logger.info(f"Aba aberta com proxy: {chosen_proxy}")
        else:
            logger.info("Aba aberta sem proxy")

        try:
            service = Service(self.driver_path)
            driver = webdriver.Chrome(service=service, options=options, seleniumwire_options=seleniumwire_options)

            # Se quiser stealth, descomente:
            # stealth(driver,
            #         languages=["en-US", "en"],
            #         vendor="Google Inc.",
            #         platform="Win32",
            #         webgl_vendor="Intel Inc.",
            #         renderer="Intel Iris OpenGL Engine",
            #         fix_hairline=False)

            driver.get(link)

            # Se não fizer questão de remover navigator.webdriver, pode remover
            try:
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception as e:
                logger.warning("Não foi possível remover navigator.webdriver: %s", e)

            # Injetar script de captura de clique
            try:
                driver.execute_script(js_configurar_clique())
            except Exception as e:
                logger.error("Erro ao configurar captura de clique: %s", e)

            with self.lock:
                self.drivers.append(driver)

            logger.info(f"Abrindo aba na posição {pos} com tamanho {width}x{height} para o link: {link}")
        except Exception as e:
            logger.error("Erro ao abrir aba: %s", e)

    def open_tabs(self, link, quantidade, finished_callback=None):
        """Abre múltiplas abas em posições e tamanhos distribuídos na tela, de forma concorrente."""
        screen_w, screen_h = pyautogui.size()
        tab_height = 522
        if quantidade in [5, 6]:
            tab_height = 600

        # Definir posições
        positions = []
        if quantidade <= 5:
            tab_width = 385
            total_width = tab_width * quantidade
            start_x = (screen_w - total_width) // 2
            for i in range(quantidade):
                positions.append((start_x + i * tab_width, 0, tab_width, tab_height))
        elif quantidade in [6, 12]:
            max_por_linha = 6
            rows = (quantidade + max_por_linha - 1) // max_por_linha
            current_tab = 0
            for row in range(rows):
                tabs_na_linha = min(max_por_linha, quantidade - current_tab)
                w = screen_w // tabs_na_linha
                x_atual = 0
                for i in range(tabs_na_linha):
                    width = screen_w - x_atual if i == tabs_na_linha - 1 else w
                    positions.append((x_atual, row * tab_height, width, tab_height))
                    x_atual += width
                    current_tab += 1
        else:
            max_por_linha = 5
            rows = (quantidade + max_por_linha - 1) // max_por_linha
            current_tab = 0
            for row in range(rows):
                tabs_na_linha = min(max_por_linha, quantidade - current_tab)
                w = screen_w // tabs_na_linha
                x_atual = 0
                for i in range(tabs_na_linha):
                    width = screen_w - x_atual if i == tabs_na_linha - 1 else w
                    positions.append((x_atual, row * tab_height, width, tab_height))
                    x_atual += width
                    current_tab += 1

        # Abertura em paralelo
        def open_in_thread(pos_tuple):
            x, y, w, h = pos_tuple
            self.open_tab(link, (x, y), w, h)

        threads = []
        for pos_tuple in positions:
            t = threading.Thread(target=open_in_thread, args=(pos_tuple,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        if finished_callback:
            finished_callback()

    def close_tabs(self):
        """Fecha todas as abas em paralelo, garantindo múltiplas tentativas se necessário."""
        def attempt_quit(driver, attempts=3):
            for i in range(attempts):
                try:
                    driver.quit()
                    return True
                except Exception as e:
                    logger.error("Erro ao fechar aba (tentativa %d): %s", i+1, e)
                    time.sleep(1)
            return False

        with self.lock:
            drivers_copy = self.drivers.copy()
            self.drivers.clear()

        if not drivers_copy:
            logger.info("Nenhuma aba para fechar.")
            return

        logger.info("Fechando %d abas...", len(drivers_copy))
        with ThreadPoolExecutor(max_workers=len(drivers_copy)) as executor:
            results = list(executor.map(attempt_quit, drivers_copy))

        logger.info("Abas fechadas. Resultados: %s", results)

    def toggle_capture(self):
        """Ativa/Desativa a captura de cliques em todas as abas."""
        if self.capture_tabs_active:
            self.capture_tabs_active = False
            logger.info("Captura de Cliques desativada.")
        else:
            with self.lock:
                for drv in self.drivers:
                    try:
                        drv.execute_script("window.localStorage.removeItem('clickX'); window.localStorage.removeItem('clickY');")
                    except Exception:
                        pass
            self.capture_tabs_active = True
            self.poll_thread = threading.Thread(target=self.poll_clicks, daemon=True)
            self.poll_thread.start()
            logger.info("Captura de Cliques ativada.")

    def poll_clicks(self):
        """Fica em loop verificando se houve cliques em cada aba e replicando para todas."""
        while self.capture_tabs_active:
            with self.lock:
                current_drivers = self.drivers.copy()

            for drv in current_drivers:
                try:
                    x = drv.execute_script("""
                        var xx = window.localStorage.getItem('clickX');
                        window.localStorage.removeItem('clickX');
                        return xx;
                    """)
                    y = drv.execute_script("""
                        var yy = window.localStorage.getItem('clickY');
                        window.localStorage.removeItem('clickY');
                        return yy;
                    """)
                    if x and y:
                        self.replicate_click_in_all(int(x), int(y), drv)
                except Exception as e:
                    logger.error("Erro no polling de cliques em um driver fechado/inacessível: %s", e)
                    with self.lock:
                        if drv in self.drivers:
                            self.drivers.remove(drv)

            time.sleep(0.01)

    def replicate_click_in_all(self, x, y, driver_origin):
        """Replica o clique (x,y) em todas as abas, exceto na que originou o clique."""
        with self.lock:
            current_drivers = self.drivers.copy()

        for drv in current_drivers:
            if drv != driver_origin:
                try:
                    drv.execute_script(js_replicate_click(), x, y)
                except Exception as e:
                    logger.error("Erro ao replicar clique: %s", e)

    def reload_tabs(self, finished_callback=None):
        """Recarrega todas as abas em paralelo, reinjetando o script de captura."""
        def reload_driver(drv):
            try:
                drv.refresh()
                time.sleep(1)
                try:
                    drv.execute_script(js_configurar_clique())
                except Exception as e:
                    logger.error("Erro ao configurar clique após refresh: %s", e)
            except Exception as e:
                logger.error("Erro ao recarregar aba: %s", e)

        with ThreadPoolExecutor() as ex:
            ex.map(reload_driver, self.drivers)

        if finished_callback:
            finished_callback()
