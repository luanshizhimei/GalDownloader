import os
import re
import sys
import traceback

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from api import create_cloud_api
from chrome import Chrome
from conf import app, app_conf
from downloader import Downloader
from favorite import Favorite
from logger import log
from sct import sct


def get_category(tag_list: list) -> str:
    re_set = set(tag_list) & set(["PC", "手机", "RPG"])
    return "Other" if len(re_set) == 0 else list(re_set)[0]


def remove_illegal_characters(file_name: str) -> str:
    illegal_chars = r'[\\/:*?"<>|]'
    return re.sub(illegal_chars, '', file_name)


def _process_dl_path(dl: dict, game_info: dict, extract_pwd: str):
    root_path = app["download_path"]
    if app_conf.getboolean("app", "open_download_category"):
        root_path = os.path.join(app["download_path"], get_category(game_info["tag_list"]))
    root_path = os.path.join(root_path, remove_illegal_characters(game_info["title"]))

    # 创建密码文件夹
    pwd_folder = os.path.join(root_path, f"解压密码：{extract_pwd}")
    if len(extract_pwd) > 0 and extract_pwd is not None:
        os.makedirs(pwd_folder, exist_ok=True)

    sub_path = dl["path"][1:]
    root_path = os.path.join(root_path, sub_path)
    dl_filepath = os.path.join(root_path, dl["name"])
    return dl_filepath


def err_log_append(text: str):
    err_log_path = os.path.join(app["log_path"], "err.log")
    with open(err_log_path, 'a', encoding='utf-8') as err_log:
        err_log.write(text + "\n")


def validate_url(url, pattern):
    if re.match(pattern, url):
        return True
    else:
        return False


def _click_button(chrome: Chrome, by: str, selector: str) -> None:
    chrome.click_element_js(WebDriverWait(chrome, 10, 2).until(EC.presence_of_element_located((by, selector))))


def _process_webpage(chrome: Chrome, dl_info: dict) -> dict or None:
    chrome.get(dl_info["link"])
    log.info(f"尝试解析网页：{dl_info['title']}")
    log.info(f"当前网页url：{chrome.current_url}")

    log.info("点击点赞按钮")
    _click_button(chrome, By.CSS_SELECTOR, ".inn-singular__post__toolbar__item__link:nth-child(1) > .poi-icon__text")

    log.info("点击下载按钮")
    _click_button(chrome, By.CSS_SELECTOR, ".inn-singular__post__toolbar__item__link:nth-child(2) > .poi-icon__text")

    # 判断是否有弹出额度用尽弹出
    if chrome.is_visual_element(By.CSS_SELECTOR, ".poi-alert__msg"):
        ele = chrome.find_element(By.CSS_SELECTOR, ".poi-alert__msg")
        alert_msg = ele.text.strip()
        log.warning(f"提示弹出信息：{alert_msg}")
        if alert_msg == "用户组无权限或积分不足5（事项分类有详细积分说明）":
            log.info("积分已耗尽，退出本次任务")
            return None
        if chrome.is_visual_element(By.CSS_SELECTOR, ".poi-dialog__footer__btn"):
            log.info("点击弹出关闭按钮")
            chrome.find_element(By.CSS_SELECTOR, ".poi-dialog__footer__btn").click()

    log.info(f"下载网页url：{chrome.current_url}")

    # 校验是否进入下载页面中
    cur_url = chrome.current_url
    if validate_url(cur_url, r"^https://www\.zfsya\.com/download#.+$") is False:
        raise RuntimeError(f"未打开下载页面，url：{cur_url}")

    # 提取解压密码和打开网页
    eles = WebDriverWait(chrome, 10, 2).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".inn-download-page__content fieldset"))
    )
    ele = None
    for e in eles:
        title = e.find_element(By.CSS_SELECTOR, "legend").text.strip()
        if title.find("月上云") != -1:
            ele = e
            break

    if ele is None:
        raise RuntimeError(f"该游戏无月上云下载链接：{dl_info['title']}")

    result = {}
    result["download_pwd"] = ele.find_element(By.CSS_SELECTOR,
                                              ".inn-download-page__content__item__download-pwd input").get_attribute(
        'value')

    result["extract_pwd"] = ""
    try:
        result["extract_pwd"] = ele.find_element(By.CSS_SELECTOR,
                                                 ".inn-download-page__content__item__extract-pwd input").get_attribute(
            'value')
    except NoSuchElementException:
        result["extract_pwd"] = ""

    log.info("点击月上云下载按钮")
    chrome.click_element_js(ele.find_element(By.CSS_SELECTOR, ".inn-download-page__content__btn a:first-child"))
    WebDriverWait(chrome, 10, 2).until(EC.number_of_windows_to_be(2))
    chrome.switch_to.window(chrome.window_handles[1])

    # 校验月上云网址是否正常
    cur_url = chrome.current_url
    log.info(f"月上云盘url：{cur_url}，提取密码：{result['download_pwd']}")
    if validate_url(cur_url, r'^https://ttk\.zfshx\.com/s/.+$') is False:
        raise RuntimeError(f"打开月上云盘失败，url：{cur_url}")
    result["url"] = cur_url

    # 关闭网页回收资源
    chrome.close()
    chrome.switch_to.window(chrome.window_handles[0])

    return result


def update():
    with Chrome() as chrome:
        favorite = Favorite(chrome)
        favorite.refresh()
        log.info("====== （第二步）执行更新下载操作 ======")
        server_url = r"http://localhost:6800/rpc"
        downloader = Downloader(server_url)
        success_count = 0
        fail_count = 0
        send_text = ""
        for game_info in favorite.get_download_item():
            try:
                # 提取网盘链接
                netdisk = _process_webpage(chrome, game_info)
                if netdisk is None:
                    break

                # 提取下载链接
                api = create_cloud_api(chrome.get_cookies(), chrome.user_agent, netdisk["url"])
                dl_info = api.parse(netdisk["download_pwd"])

                # 执行下载
                for dl in dl_info:
                    dl_url = dl["download_url"]
                    dl_filepath = _process_dl_path(dl, game_info, netdisk["extract_pwd"])
                    downloader.download_wait([dl_url], dl_filepath)
                success_count += 1
                send_text += f"{game_info['title']}    \n"
            except Exception as err_msg:
                err_text = f"游戏下载失败：{game_info['title']}，序号：{game_info['idx']}"
                exc_type, exc_value, exc_traceback = sys.exc_info()
                tb = traceback.extract_tb(exc_traceback)[-1]
                log.warning(f"错误发生在文件: {tb.filename}，行号：{tb.lineno}，函数名：{tb.name}")
                log.warning(f"错误代码行内容: {tb.line}")
                log.warning(f"错误类型: {exc_type.__name__}，错误信息: {exc_value}")
                err_log_append(err_text)
                fail_count += 1
                continue
            favorite.update_download(game_info["idx"])

        downloader.close()
        favorite.close()
        send_text = f"累计下载{success_count}个游戏，下载失败：{fail_count}    \n  \n" + send_text
        log.info(send_text)
        sct.send("宅方社更新", send_text)
        log.info("====== 结束更新下载操作 ======")


if __name__ == "__main__":
    update()
