import functools
import threading
import time

import schedule

from check_in import check_in
from conf import app
from logger import log
from update import update


def catch_exceptions(job_func):
    @functools.wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            log.info(f"====== 开始执行任务：{job_func.__name__} ======")
            result = job_func(*args, **kwargs)
            log.info(f"====== 结束执行任务：{job_func.__name__} ======")
            return result
        except:
            import traceback
            log.warning(traceback.format_exc())
            return schedule.CancelJob

    return wrapper


def run_daemon_thread(target, *args, **kwargs):
    job_thread = threading.Thread(target=target, args=args, kwargs=kwargs)
    job_thread.daemon = True
    job_thread.start()


def job_checkin():
    job_func = catch_exceptions(check_in)
    job_time = app["checkin_time"]
    schedule.every().day.at(job_time).do(job_func)


def job_update():
    job_func = catch_exceptions(update)
    job_time = app["update_time"]
    schedule.every().day.at(job_time).do(job_func)


if __name__ == "__main__":
    run_daemon_thread(job_checkin)
    run_daemon_thread(job_update)
    schedule.run_all()  # 初次启动，全部执行

    while True:
        schedule.run_pending()
        time.sleep(1)
