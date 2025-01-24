import time
import urllib.parse

import pathlib
import requests
import urllib3
from requests.models import Response
from requests.sessions import Session as BaseSession
from logger import log

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Session(BaseSession):

    def __init__(self, selenium_cookies: dict, headers: dict):
        self.cookies = selenium_cookies
        self.headers = headers
        self.verify = False
        super(Session, self).__init__()

    def request(self, *args, **kwargs) -> Response:
        try_count = 0
        while try_count <= 3:
            try:
                response = super(Session, self).request(cookies=self.cookies, headers=self.headers, verify=False,
                                                        *args, **kwargs)
                response.raise_for_status()
            except requests.exceptions.HTTPError as err_msg:
                log.warning(f"请求失败！尝试重新下载次数：{try_count}，错误信息: {err_msg}")
                try_count += 1
                time.sleep(1)
            else:
                break
        return response


class Api:

    def __init__(self, session: requests.sessions, url):
        self.session = session
        self.url = url
        self.key = url[url.rfind(r"/") + 1:]
        self.host = r"https://ttk.zfshx.com/api/v3/share/"

    def api(self, method: str, url: str) -> dict:
        response = self.session.request(method=method, url=url)
        result = response.json()
        if result["code"] != 0:
            err_msg = f"月上云请求API失败，请求体：{url}，返回数据：{result}"
            log.error(err_msg)
            raise ValueError(err_msg)
        return result

    def get_download_url(self, file_path) -> str:
        filepath_url_str = urllib.parse.quote(file_path)
        url = f"{self.host}download/{self.key}?path={filepath_url_str}"
        result = self.api("PUT", url)
        return result["data"]

    def _process(self, dir_str, files_info) -> list:
        if len(dir_str) > 0:
            dir_str = urllib.parse.quote(dir_str)
        url = f"{self.host}list/{self.key}{dir_str}"
        result = self.api("GET", url)
        for info in result["data"]["objects"]:
            path = str(pathlib.Path(info["path"], info["name"]).as_posix())
            if info["type"] == "dir":
                files_info = self._process(path, files_info)

            if info["type"] == "file":
                dl_url = self.get_download_url(path)
                files_info.append({
                    "name": info["name"],
                    "path": info["path"],
                    "size": info["size"],
                    "download_url": dl_url
                })
        return files_info

    def parse(self, pwd: str) -> list:
        self.api("GET", f"{self.host}info/{self.key}?password={pwd}")
        return self._process("/", [])


def create_cloud_api(selenium_cookies: dict, user_agent: str, referer_url: str) -> Api:
    # 处理selenium cookies
    session_cookies = {}
    for cookie in selenium_cookies:
        session_cookies[cookie['name']] = cookie['value']

    # 处理headers请求头
    headers = {'Referer': referer_url, 'User-Agent': user_agent}

    return Api(Session(
        selenium_cookies=session_cookies,
        headers=headers
    ), referer_url)
