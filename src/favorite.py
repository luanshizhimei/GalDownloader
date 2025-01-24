import ast
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from chrome import Chrome
from conf import get_fav_uid, set_fav_uid, app
from db import Database
from logger import log


class Favorite:

    def __init__(self, driver: webdriver):
        self._driver = driver
        self._db = Database(app["db_path"])

    def close(self) -> None:
        self._db.close()

    def get_download_item(self) -> list[dict]:
        data = self._db.query_not_download_list()
        # 将字符串格式化的tag_list转化为可用list
        data = [{**item, 'tag_list': ast.literal_eval(item['tag_list'])} for item in data]
        return data

    def update_download(self, index: int) -> None:
        self._db.update_download(index)

    def refresh(self) -> None:
        self._open_webpage()

        dl_count = 0
        log.info("====== 执行更新收藏夹数据库 ======")
        for item in self._update_favorit_item():
            if self._db.query_index(item["index"]):
                continue

            # 将封面下载到本地
            img_url = item["img_url"]
            if app["download_cover"].lower() == "true":
                try:
                    img_path = self._driver.get_file(img_url, app["img_path"])
                except:
                    img_path = None
            img_path = img_path if img_path is not None else img_url

            fav_data_tuple = (
                item["index"], item["title"], item["link"],
                str(item["tag_list"]), img_path, 0
            )  # idx, title, link, tag_list, img_url, is_download
            self._db.insert(fav_data_tuple)
            dl_count += 1

        log.info(f"====== 更新收藏夹数据库完成，新增{dl_count}个游戏 ======")

    def _update_favorit_item(self) -> dict:
        item = {}
        soup = BeautifulSoup(self._driver.page_source, 'html.parser')
        father_element = soup.find(class_="inn-author-page__fans__body")
        for article in father_element.find_all('article'):
            item["title"] = article.find("h3").text.strip()
            item["link"] = article.find("a").get('href')
            link = item["link"]
            item["index"] = link[link.rfind(r"/") + 1:link.rfind(r".")]
            item["img_url"] = article.find("img").get('src')

            spans = article.find_all("span")
            sps_str = spans[0].text + "|" + spans[1].text
            sps_str = sps_str.replace(" ", "")
            sps_list = sps_str.split("|")
            item["tag_list"] = sps_list
            yield item

    def _open_webpage(self) -> None:
        # pass - 判断用户id是否可用
        uid = get_fav_uid()
        if uid == 0:
            uid = self._get_user_id()
            set_fav_uid(uid)
            return

        url = f"https://www.zfsya.com/author/{uid}/fav"
        self._driver.get(url)

    def _get_user_id(self):
        driver = self._driver
        if driver.is_visual_element(By.CSS_SELECTOR, ".poi-dialog__header__close"):
            log.info("发现入站提示，点击关闭")
            driver.click_element(By.CSS_SELECTOR, ".poi-dialog__header__close")

        log.info("打开用户界面导航")
        driver.click_element(By.CSS_SELECTOR, ".inn-user-menu__nav__avatar-btn__link", js_enable=True)
        if driver.is_visual_element(By.CSS_SELECTOR, ".inn-user-menu_mobile__item") is False:
            err_msg = "未成功打开用户界面导航"
            log.warning(err_msg)
            raise RuntimeError(err_msg)

        eles = driver.find_elements(By.CSS_SELECTOR, ".inn-user-menu_mobile__item a")
        for ele in eles:
            ele_text = ele.text
            ele_text = ele_text.strip()
            if ele_text == "收藏夹":
                log.info("点击收藏夹")
                ele.click()
                break

        url = driver.current_url
        pattern = r'https://www\.zfsya\.com/author/(\d+)/fav'
        match = re.match(pattern, url)
        if match:
            return match.group(1)
        else:
            err_msg = f"未正确获得用户编号，url: {url}"
            log.warning(err_msg)
            raise RuntimeError(err_msg)


def refresh_favortie():
    with Chrome() as _driver:
        favorite = Favorite(_driver)
        favorite.refresh()


if __name__ == "__main__":
    refresh_favortie()
