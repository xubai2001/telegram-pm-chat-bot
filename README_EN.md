# Modified from [Netrvin/telegram-pm-chat-bot](https://github.com/Netrvin/telegram-pm-chat-bot)

Telegram Private Message Chat Bot


**This project is a personal learning project where a significant portion of the code originates from the original repository. It utilizes an updated version of python-telegram-bot (v20.7), with some modifications made to the code.**

## Installation

### Preparation
* Create a bot and get its token
* Install Python(Python3.8+) and pip, then use pip to install `python-telegram-bot==20.7`

### Configuration
ename `config-sample.json` to `config.json` and configure
```json
{
    "Admin": 0,
    "//1": "Admin ID (A digital ID)",
    "Token": "",
    "//2": "Bot Token",
    "Lang": "en",
    "//3": "Language Pack Name (Be careful! It's 'en'!)"
}
```
If you didn't set admin's ID previously, the user who sends `/setadmin` to the bot first will become the admin. You can edit `config.json` to change admin later.

## Upgrade

Replace files and folders other than the `data/` path

## Run
```
python main.py
```

## Usage

### Reply

Reply directly to the message forwarded by the robot to reply. You can reply text, sticker, photo, file, audio, voice and video.

### Inquire sender identity

You can reply `/info` to the message which you want to get its sender's info more clearly.


### Ban and unban

Reply `/ban` to a message to block the sender of the message from sending messages to you

Reply `unban` to a message or send `/unban <User ID>` to unban a user

### Adding and Deleting Filter Words

**Sending** `add <filter word>` or `/delete <filter word>` directly will add or remove filter words. After setting filter words, if messages from other users to Admin contain these words, a warning will be issued, and the message won't be forwarded.

### Deleting User Messages

**Replying to a message** with `/delete` or `delete all` will delete either a single message or all messages from that user (non-Admin). Messages deleted will include those sent to the Bot by the user and messages forwarded to Admin by the Bot, within **48 hours**.

**Note: The `/delete` command for messages differs from deleting filter words in that it depends on whether you're replying to a specific message.**


## Available commands,/unban The following are new commands
| Command                | Usage                                      |
| :---                   | :---                                       |
| /ping                  | Check if the bot is running                |
| /setadmin              | Set the current user as admin              |
| /togglenotification(⚠️Not implemented)    | Toggle message sending notification status |
| /info                  | Inquire sender identity                    |
| /ban                   | Ban a user                                 |
| /unban <ID (optional)> | Unban a user                               |
| /add <filter_word>             | Add filter_word                |
| /delete <filter_word>          |   Delete filter_word             |
| /delete <all (optional)>(Must reply to a message) | Delete a reply message or all messages from the sender |
