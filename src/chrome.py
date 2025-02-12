from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conf import app, app_conf
from driver import Driver
from logger import log
from sct import sct


class Chrome(Driver):

    def __init__(self):
        visual = app_conf.getboolean("app", "browser_visual")
        super(Chrome, self).__init__(visual=visual)
        self._load_cookie()
        if self._check_login_status() is False:
            send_text = "Cookies已失效，请重新登入！"
            log.error(send_text)
            sct.send(send_text)
            exit(9)
        super(Chrome, self).maximize_window()

    def _load_cookie(self) -> None:
        self.get(r"https://www.zfsya.com/")
        self.load_cookies(app["cookies_path"])
        self.refresh()

    def _check_login_status(self) -> bool:
        try:
            WebDriverWait(self, 3, 0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "inn-user-menu__nav__avatar-btn"))
            )
            is_result = True
        except TimeoutException:
            is_result = False
        return is_result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
