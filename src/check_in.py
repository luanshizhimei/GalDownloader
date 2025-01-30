from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from chrome import Chrome
from logger import log
from sct import sct
import time

drawgame_match_list = [
    "免费抽奖（每日）",
    "每周礼物",
    "【限时】假期积分礼包"
]

def check_in():
    with Chrome() as chrome:
        chrome.get("https://www.zfsya.com/")
        log.info("执行每日签到：第一步 点击每日签到")
        time.sleep(5)
        if chrome.is_visual_element(By.CSS_SELECTOR, ".inn-nav__point-sign-daily"):
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
                log.info("点击成功")

        ele = chrome.find_element(By.CSS_SELECTOR, ".inn-account__products__preface__item")
        points_str = ele.text
        points_str = points_str.strip().replace(" ", "")
        points_str = points_str.replace("积分", "")
        send_text = f"完成本日签到，积分总数：{points_str}"
        log.info(send_text)
        sct.send("宅方社签到", send_text)


if __name__ == "__main__":
    check_in()
