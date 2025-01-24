# GalDownloader - 自动订阅下载游戏脚本

----

基于selenium + aria2实现定时下载脚本，实现功能如下：
1. 完成每日签到，已获取积分。
2. 自动下载收藏夹内游戏，若积分不足则退出，实现类似订阅的功能。

----

## 零、环境要求

| 工作环境 | 版本 |
|----|----|
| 系统 | \>= windows 10 |
| 浏览器 | Edge |
| Pythen | \>= 3.12.8 |

----

## 一、安装方法
- 第一步：修改配置文件`config\user.ini.default`内容并将配置文件名称改为`user.ini`
```ini
[user]
uid = <账号>
pwd = <密码>
sct_key = <Server酱key> # 没有可不填
# 记得改配置文件名为user.ini，程序才能识别
```
- 第二步： 创建python环境（以下操作均在脚本根目录下执行）
```bash
python -m venv .\venv\
```
- 第三步： 激活当前环境（终端：powershell）
```bash
.\venv\Scripts\Activate.ps1
```
- 第四步： 安装依赖
<details>
<summary>【可选】升级pip</summary>

```bash   
python -m ensurepip --upgrade   
python -m pip install --upgrade setuptools   
python -m pip install --upgrade pip  
```

</details>

```bash
pip install -r requirements.txt
```

- 第五步： 刷新cookies信息
 ```bash
_refresh_cookies.bat
```

- 第六步： 启动程序（不显示终端后台启动可以用`_run_hidden.vbs`）
```bash
_run.bat
```

-----  

## 二、脚本使用说明

1. 启动脚本程序
```
_run.bat
```
2. 隐藏启动脚本程序
```
_run_hidden.vbs
```
3. 刷新cookies信息（一般用于登入失效、cookies信息过时）

 ```bash
_refresh_cookies.bat
```

-----

## 三、配置文件说明
- `config\app.ini`：程序配置文件
```ini
[app]
browser_visual=false # 是否显示浏览器操作

cookies_path=.\config\cookies.json
db_path=.\config\favorite.db
log_path=.\log

open_download_category = true # 是否开启下载游戏文件夹分类
download_path=.\download # 下载文件地址

checkin_time=20:00 # 签到任务执行时间
update_time=20:30 # 更新下载任务执行时间

download_cover =true # 是否开启下载网页游戏封面
img_path=.\img

aria2c_path = .\bin\aria2\aria2c.exe # 内部aria2c程序，建议不要改动
```
- `config\user.ini`: 用户配置文件
```ini
[user]
uid = <账号>
pwd = <密码>
sct_key = <Server酱key> # 没有可不填
# 记得改配置文件名为user.ini，程序才能识别
```