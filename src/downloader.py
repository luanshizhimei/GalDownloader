import os.path
import subprocess
import time
import xmlrpc.client

from aria2p import API, Client

from conf import app
from logger import log


class Downloader:
    def __init__(self, server_url: str):
        self._process = None
        if self._getVersion(server_url) is None:
            log.info("未检测外部aria2c，使用内部程序自启")
            self._process = subprocess.Popen(args=(
                app["aria2c_path"],
                "--enable-rpc",
                "--rpc-listen-all",
                "--max-connection-per-server=16",  # 与下载服务器的最大连接数（总共）
                "--split=16",  # 下载一个文件使用连接数
                "--min-split-size=1M"  # 文件分片大小
                # doc：https://aria2.github.io/manual/en/html/aria2c.html
            ), stdout=subprocess.DEVNULL)
        self._client = Client(host="http://localhost", port=6800, secret="")
        self._api = API(self._client)

    def _getVersion(self, server_url: str) -> str or None:
        try:
            s = xmlrpc.client.ServerProxy(server_url)
            result = s.aria2.getVersion()
        except Exception as e:
            return None
        else:
            return result

    def add(self, url: list[str], file_path: str):
        dir_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        return self._api.add_uris(url, options={"dir": dir_path, "out": file_name})

    def download_wait(self, url: list[str], file_path: str) -> None:
        task = self.add(url, file_path)
        log.info(f"正在下载文件：{task.name}")
        while not task.is_complete:
            task.update()
            if task.has_failed:
                err_msg = f"下载失败，错误报告: {task.error_message}"
                log.warning(err_msg)
                raise RuntimeError(err_msg)
            time.sleep(1)
        log.info(f"文件下载完成：{task.dir}")
        return task

    def close(self):
        if self._process is not None:
            log.info("关闭内建aria2c")
            self._process.kill()
