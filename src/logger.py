import datetime
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from conf import app

# 设置日志格式
LEVEL = logging.DEBUG
FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
log = logging.getLogger(__name__)
log.setLevel(LEVEL)
_formatter = logging.Formatter(FORMAT, "%H:%M:%S")

# 清理之前日志
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
log_filename = os.path.join(app["log_path"], f"daily-{current_date}.log")
if os.path.exists(log_filename):
    os.remove(log_filename)
errlog_filename = os.path.join(app["log_path"], "err.log")
if os.path.exists(errlog_filename):
    os.remove(errlog_filename)

# 设置定时分隔日志定时器
_file_handler = TimedRotatingFileHandler(filename=log_filename, encoding="utf-8", when="D", interval=1,
                                         backupCount=10)
_file_handler.suffix = "daily-%Y-%m-%d.log"
_file_handler.setFormatter(_formatter)
_file_handler.setLevel(logging.DEBUG)
log.addHandler(_file_handler)

# 加入输出流
_stream_handler = logging.StreamHandler(sys.stdout)
_stream_handler.setFormatter(_formatter)
log.addHandler(_stream_handler)
