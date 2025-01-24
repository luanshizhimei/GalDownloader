import base64
import os
import time

import ddddocr
from selenium import webdriver
from selenium.webdriver.common.by import By

from conf import app, user
from driver import Driver
from logger import log


def verification_code(driver: webdriver) -> None:
    # 自动识别验证码, 需要训练图库，后面有时间再搞。
    img = driver.find_element(By.XPATH, '//img[@title="刷新验证码"]')
    bstr = img.get_attribute("src")
    bstr = bstr[bstr.rfind(",") + 1:]
    imgdata = base64.b64decode(bstr)

    ocr = ddddocr.DdddOcr(beta=True, show_ad=False)
    result = ocr.classification(imgdata, png_fix=True)
    log.info(f"验证码：{result}")

    img_path = "check.png"
    if os.path.exists(img_path):
        os.remove(img_path)
    with open(img_path, 'wb') as f:
        f.write(imgdata)


def _login_input(driver: webdriver, uid: str, pwd: str) -> None:
    sign_url = r"https://www.zfsya.com/sign"
    driver.get(sign_url)
    try:
        driver.find_element(By.NAME, "email").send_keys(uid)
        driver.find_element(By.NAME, "pwd").send_keys(pwd)
    except Exception as err_msg:
        log.warn(f"未搜索到元素，错误信息：{err_msg}")
    while driver.current_url == sign_url:
        time.sleep(1)


def login():
    chrome = Driver(visual=True)
    chrome.get(r"https://www.zfsya.com/")

    log.info("清除浏览器cookies")
    chrome.delete_all_cookies()
    chrome.refresh()

    log.info("删除cookies文件")
    cookies_path = app["cookies_path"]
    if os.path.exists(cookies_path):
        os.remove(cookies_path)

    log.info("执行登入操作，请输入验证码！")
    _login_input(chrome, user["uid"], user["pwd"])

    log.info("登入完成，保存cookies文件")
    chrome.save_cookies(cookies_path)


if __name__ == "__main__":
    login()
