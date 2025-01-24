import logging
import sys
from logging.handlers import TimedRotatingFileHandler

from conf import app

LEVEL = logging.DEBUG
FORMAT = "%(asctime)s / %(levelname)s / %(message)s"

log = logging.getLogger(__name__)
log.setLevel(LEVEL)
_formatter = logging.Formatter(FORMAT, "%Y-%m-%d %H:%M:%S")

_file_path = app["log_path"] + "\\daily.log"
_file_handler = TimedRotatingFileHandler(filename=_file_path, encoding="utf-8", when="D", interval=1, backupCount=10)
_file_handler.setFormatter(_formatter)
_file_handler.setLevel(logging.DEBUG)
log.addHandler(_file_handler)

_stream_handler = logging.StreamHandler(sys.stdout)
_stream_handler.setFormatter(_formatter)
log.addHandler(_stream_handler)
