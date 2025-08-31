import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from conf import app, user
from driver import Driver
from logger import log


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

    time.sleep(10)
    log.info("登入完成，保存cookies文件")
    chrome.save_cookies(cookies_path)


if __name__ == "__main__":
    login()
