import json
import os
import time
from datetime import datetime, timedelta

import requests
import urllib3
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException, WebDriverException
)
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
#from undetected_chromedriver import ChromeOptions  # 屏蔽selenium特征，不小心造重复轮子
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from logger import log

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['WDM_SSL_VERIFY'] = '0'  # 禁用 SSL 验证


class Driver(webdriver.Chrome):

    def __init__(self, visual=True, user_agent=None):
        self.options = ChromeOptions()
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--no-sandbox")
        # 不显示浏览器以加快脚本运行
        if not visual:
            self.options.add_argument("--headless")  # 添加无头模式参数
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.managed_default_content_settings.stylesheets": 2
            }
            self.options.add_experimental_option("prefs", prefs)
        self.visual = visual

        # 设置user-agent
        self.user_agent = user_agent or UserAgent().chrome
        self.options.add_argument(f"user-agent={self.user_agent}")

        try:
            self.service = ChromeService(executable_path=ChromeDriverManager().install())
        except WebDriverException as e:
            raise RuntimeError("ChromeDriver 初始化失败") from e

        super(Driver, self).__init__(service=self.service, options=self.options)

    def save_cookies(self, file_path: str) -> None:
        if os.path.exists(file_path):
            os.remove(file_path)

        cookies = super(Driver, self).get_cookies()
        # 设置cookie有效期为10年
        future_date = datetime.now() + timedelta(days=3650)
        future_timestamp = int(future_date.timestamp())
        i = 0
        for e in cookies:
            if "expiry" in e.keys():
                cookies[i]["expiry"] = future_timestamp
            i += 1

        json_cookies = json.dumps(cookies)
        with open(file_path, 'w') as f:
            f.write(json_cookies)

    def load_cookies(self, file_path: str) -> None:
        self.delete_all_cookies()
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'rb') as cookiesfile:
            with open(file_path, 'r') as f:
                cookies = json.load(f)
            for cookie in cookies:
                super(Driver, self).add_cookie(cookie)

    def click_element(self, by_type: str, find_value: str, js_enable: bool or None = None) -> None:
        try:
            element = WebDriverWait(super(Driver, self), 3, 0.5).until(
                EC.element_to_be_clickable((by_type, find_value))
            )
            if js_enable:
                self.click_element_js(element)
            else:
                element.click()
        except TimeoutException as err_msg:
            log.warning(f"未找该元素，错误信息：{err_msg}")

    def click_element_js(self, element: WebElement) -> None:
        super(Driver, self).execute_script("arguments[0].click();", element)

    def get_file(self, url: str, des_path: str) -> str:
        file_name = url[url.rfind(r"/") + 1:]
        mark = file_name.find(r"?")
        if mark != -1:
            file_name = file_name[:mark]
        file_path = os.path.join(des_path, file_name)
        if os.path.exists(file_path):  # 遇到之前下载的就返回
            return file_path

        selenium_cookies = super(Driver, self).get_cookies()
        session_cookies = {}
        for cookie in selenium_cookies:
            session_cookies[cookie['name']] = cookie['value']
        headers = {
            'Referer': super(Driver, self).current_url,
            'User-Agent': self.user_agent
        }

        try_count = 0
        while try_count <= 3:
            try:
                response = requests.get(url, cookies=session_cookies, headers=headers, verify=False)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                log.warning(f"文件下载失败，尝试重新下载次数：{try_count}，错误信息: {e}")
                try_count += 1
                time.sleep(3)
            else:
                break

        with open(file_path, "wb") as f:
            f.write(response.content)
        return file_path

    def is_visual_element(self, by_type: str, find_value: str) -> bool:
        try:
            WebDriverWait(super(Driver, self), 3, 0.5).until(
                EC.visibility_of_element_located((by_type, find_value))
            )
            return True
        except:
            return False

    def wait_for_window(self, old_handles, check_timeout=3):
        while True:
            time.sleep(check_timeout)
            wh_now = super(Driver, self).window_handles
            wh_then = old_handles
            if len(wh_now) > len(wh_then):
                return set(wh_now).difference(set(wh_then)).pop()
