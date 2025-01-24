from configparser import ConfigParser

_user_path = r".\config\user.ini"
_appcfg_path = r".\config\app.ini"

user_conf = ConfigParser()
user_conf.read(_user_path, "utf-8")
app_conf = ConfigParser()
app_conf.read(_appcfg_path, "utf-8")

user = user_conf["user"]
app = app_conf["app"]

_fav_config = ConfigParser()
_fav_config.read(_user_path, "utf-8")


def get_fav_uid() -> int:
    uid = _fav_config["favorite"]["uid"]
    if len(uid) == 0:
        uid = 0
    return int(uid)


def set_fav_uid(uid: int) -> None:
    _fav_config.set('favorite', 'uid', uid)
    with open(_user_path, 'w', encoding='utf-8') as configfile:
        _fav_config.write(configfile)
