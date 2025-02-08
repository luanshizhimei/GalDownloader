import datetime
import os
import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from chrome import Chrome
from logger import log
from sct import sct

drawgame_match_list = [
    "免费抽奖（每日）",
    "每周礼物",
    "【限时】假期积分礼包"
]


def _screenshot(driver: Chrome, title: str) -> None:
    screenshot_dir = os.path.join(Path.cwd(), r'\screenshot')
    screenshot_name = f"{datetime.datetime.now().strftime('%y%m%d')}-{title}.png"
    screenshot_path = os.path.join(screenshot_dir, screenshot_name)
    log.info(f"执行截屏：{screenshot_path}")
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)
    driver.save_screenshot(screenshot_path)


def check_in():
    with Chrome() as chrome:
        for idx in range(1, 3):
            log.info(f"第{idx}次查询每日签收按钮是否存在")
            chrome.get("https://www.zfsya.com/")
            chrome.refresh()
            if chrome.is_visual_element(By.ID, "inn-nav__point-sign-daily"):
                log.info(" -> 检测成功，执行下一步")
                break
            log.warning(" -> 未找到")
            time.sleep(10)

        log.info("判断是否存在入站提示")
        if chrome.is_visual_element(By.CSS_SELECTOR, ".poi-dialog__footer__btn"):
            chrome.click_element(By.CSS_SELECTOR, ".poi-dialog__footer__btn")
            log.info("取消入站提示")

        if chrome.is_visual_element(By.ID, "inn-nav__point-sign-daily"):
            log.info("执行每日签到：第一步 点击每日签到")
            chrome.click_element(By.CSS_SELECTOR, ".inn-nav__point-sign-daily__btn")
            log.info("点击成功")

        log.info("执行每日签到：第二步 点击每日和每周抽奖")
        chrome.get("https://www.zfsya.com/account/lottery")
        eles = WebDriverWait(chrome, 3, 0.5).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".inn-account__lottery__item__title"))
        )
        for ele in eles:
            title = ele.text.strip()
            if title in drawgame_match_list:
                ele.click()
                chrome.click_element(By.CSS_SELECTOR, ".poi-btn", js_enable=True)
                chrome.click_element(By.CSS_SELECTOR, ".poi-dialog__footer__btn")
                log.info(f"点击成功：{title}")

        ele = chrome.find_element(By.CSS_SELECTOR, ".inn-account__products__preface__item")
        points_str = ele.text
        points_str = points_str.strip().replace(" ", "")
        points_str = points_str.replace("积分", "")
        send_text = f"完成本日签到，积分总数：{points_str}"
        log.info(send_text)
        sct.send("宅方社签到", send_text)


if __name__ == "__main__":
    check_in()
