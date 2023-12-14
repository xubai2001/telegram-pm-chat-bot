# 修改自[Netrvin/telegram-pm-chat-bot](https://github.com/Netrvin/telegram-pm-chat-bot)

Telegram 私聊机器人

**本项目为自用学习项目，大量代码来源于原仓库。使用了更新的python-telegram-bot版本(v20.7), 代码有部分更改**


## 安装

### 安装准备
* 创建Telegram机器人，获取Token
* 一台外面的服务器，安装好Python(Python3.8+)和pip，并用pip安装`python-telegram-bot==20.7`

### 配置
重命名 `config-sample.json` 为 `config.json`,然后配置
```json
{
    "Admin": 0,
    "//1": "管理员用户ID（数字ID）（可以先不设）",
    "Token": "",
    "//2": "机器人Token",
    "Lang": "zh",
    "//3": "语言包名称"
}
```
如果在前一步未设置管理员用户ID，第一个对机器人发送`/setadmin`的用户将成为管理员，之后可通过修改`config.json`修改管理员

## 升级
替换除`data/`路径外的文件以及文件夹

## 运行
```
python main.py
```

## 使用

### 回复
直接回复机器人转发过来的消息即可回复，支持文字、贴纸、图片、文件、音频和视频


### 查询用户身份
部分转发来的消息不便于查看发送者身份，可以通过回复该消息`/info`查询


### 封禁与解禁
向一条消息回复`/ban`可禁止其发送者再次发送消息

向一条消息回复`/unban`或发送`/unban <数字ID>`可解除对此用户的封禁

### 添加与删除屏蔽词
**直接发送**`/add <屏蔽词>`与`/delete <屏蔽词>`可添加或删除屏蔽词，设置屏蔽词后，其他用户向Admin发送的消息中若带有屏蔽词则会发出警告，且不转发

### 删除用户消息
**回复一条消息**`/delete`或者`delete all`，前者只删除一条消息，后者删除该用户(非Admin)的所有消息，删除的消息为**48小时**内的用户发送到Bot消息和Bot转发给Admin的消息.

**注意** 此条`/delete`指令与删除屏蔽词的区别在于是否是回复一条消息


## 可用指令,/unban以下为新增指令 (Available commands,/unban The following are new commands)
| Command                   | 用途                   |
| :---                      | :---                   |
| /ping                     | 确认机器人是否正在运行   |
| /setadmin                 | 设置当前用户为管理员     |
| /togglenotification(⚠️未实现)       | 切换消息发送提示开启状态 |
| /info                     | 查询用户身份            |
| /ban                      | 封禁用户                |
| /unban <数字ID (可选)>     | 解封用户                |
| /add <屏蔽词>             | 添加屏蔽词                |
| /delete <屏蔽词>          |   删除屏蔽词              |
| /delete <all (可选)>(必须回复某条消息) | 删除一条所回复的消息或者所有该发送者的消息 |