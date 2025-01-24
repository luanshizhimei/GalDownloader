import inspect
import json
import os
import time
from datetime import datetime, timedelta

import requests
import urllib3
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
#from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from undetected_edgedriver import EdgeOptions  # 屏蔽selenium特征

from logger import log

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['WDM_SSL_VERIFY'] = '0'  # 禁用 SSL 验证


class Driver(webdriver.Chrome):

    def __init__(self, visual=False, user_agent=None):
        self.options = EdgeOptions()
        self.options.use_chromium = True  # 确保使用 Chromium 内核的 Edge
        self.options.add_argument("--log-level=3")  # 设置日志级别以减少控制台输出
        # 不显示浏览器以加快脚本运行
        if visual is False:
            self.options.add_argument("--headless")  # 添加无头模式参数
            prefs = {}
            prefs["profile.managed_default_content_settings.images"] = 2  # 不加载图片
            prefs["permissions.default.stylesheet"] = 2  # 不加载css
            self.options.add_experimental_option("prefs", prefs)
        self.visual = visual

        # 设置user-agent
        if user_agent is None:
            user_agent = UserAgent().chrome
        self.user_agent = user_agent
        self.options.add_argument(f"user-agent={self.user_agent}")

        self.service = EdgeService(executable_path=EdgeChromiumDriverManager().install(), log_output='NUL')
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
            frame = inspect.currentframe()
            args, _, _, values = inspect.getargvalues(frame)
            log.warning(f"未找该元素，错误信息：{err_msg}，传入参数：{values}")

    def click_element_js(self, element: WebElement) -> None:
        super(Driver, self).execute_script("arguments[0].click();", element)

    def get_file(self, url: str, des_path: str) -> str or None:
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
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return file_path
            except requests.exceptions.HTTPError as e:
                log.warning(f"文件下载失败，尝试重新下载次数：{try_count}，错误信息: {e}")
                try_count += 1
                time.sleep(3)
                return None

    def is_visual_element(self, by_type: str, find_value: str) -> bool:
        try:
            WebDriverWait(super(Driver, self), 3, 0.5).until(
                EC.visibility_of_element_located((by_type, find_value))
            )
            return True
        except:
            return False
