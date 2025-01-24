import time

import requests

from conf import user


class SCT:

    def __init__(self, key_str):
        self._key_ = key_str

    def send(self, title, context="", short=None):
        if len(self._key_) == 0:
            return

        # 构建消息体
        url = f"https://sctapi.ftqq.com/{self._key_}.send"
        header = {"Content-type": "application/json"}
        if len(title) > 32:
            print("SCT警告，title超过32个字符。信息会自动裁剪！")
            title = title[:32]

        ljson = {
            "title": title,
            "desp": context,
        }
        if short is not None:
            ljson["short"] = short

        # 发送请求
        is_retry = True
        count = 0
        max_retries = 3
        sleep_seconds = 5
        while is_retry and count <= max_retries:
            try:
                r = requests.post(url=url, headers=header, json=ljson)
                result = r.json()
                if result["data"]["error"] != "SUCCESS":
                    raise (RuntimeError(f"发送错误，返回值：{result}"))
            except Exception as e:
                if count == max_retries:
                    print(f"SCT错误，错误原因：{str(e)}")
                    return False
                count += 1
                time.sleep(sleep_seconds)
            else:
                return True


sct = SCT(user["sct_key"])
