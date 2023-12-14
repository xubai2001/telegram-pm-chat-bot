"""
utils.py is a module containing various utility functions for the telegram-pm-chat-bot project.
It provides functions for common tasks such as saving and loading configuration files, managing
user preferences, and handling messages.
"""

import threading
import os
import json
import logging
from telegram.ext import Application


def save_data():
    """
    Save the message list to a JSON file.
    """
    with MESSAGE_LOCK:
        with open(PATH + 'data.json', 'w', encoding="UTF-8") as fp:
            fp.write(json.dumps(message_list))

def save_preference():
    """
    Save the user preference list to a JSON file.
    """
    with PREFERENCE_LOCK:
        with open(PATH + 'preference.json', 'w', encoding="UTF-8") as fp:
            fp.write(json.dumps(preference_list))

def save_config():
    """
    Save the config to a JSON file.
    """
    with CONFIG_LOCK:
        with open(PATH + 'config.json', 'w', encoding="UTF-8") as fp:
            fp.write(json.dumps(CONFIG, indent=4))


def load_config(filename):
    """
    Load the config from a JSON file.
    """
    with open(f"{PATH}/{filename}", mode="r", encoding="UTF-8") as fp:
        config = json.load(fp)
    return config


async def check_config(application: Application) -> None:
    """
    Check the bot name and ID when the bot starts and save it to config.json
    """
    bot = await application.bot.get_me()
    # 初始化bot信息
    if "ID" not in CONFIG:
        CONFIG["ID"] = bot.id
    if "Username" not in CONFIG:
        CONFIG["Username"] = bot.username
    threading.Thread(target=save_config).start()


async def save_all_config(application: Application) -> None:
    """
    Save all the data when the bot stops.
    """
    logging.info("Saving data....")
    save_config()
    save_data()
    save_preference()
    logging.info("Saving data successful!")


def add_filter_words(word: str):
    """
    Admin add filter words

    Parameters:
        word (str): The word to add.
    """
    with FILTER_LOCK:
        with open(f'{PATH}/{FILTER_WORD_PATH}', 'r', encoding='utf-8') as fp:
            content = fp.read()

        new_content = word + '\n' + content

        with open(f'{PATH}/{FILTER_WORD_PATH}', 'w', encoding='utf-8') as fp:
            fp.write(new_content)

def delete_filter_words(word: str) -> bool:
    """
    Admin delete filter words.

    Parameters:
        word (str): The word to delete.

    Returns:
        bool: True if the word was deleted, False otherwise.
    """
    with FILTER_LOCK:
        is_delete = False
        with open(f'{PATH}/{FILTER_WORD_PATH}', 'r', encoding='utf-8') as fp:
            content = fp.readlines()

        for line in content:
            if line.strip() == word:
                content.remove(line)
                is_delete = True
                break

    with open(f'{PATH}/{FILTER_WORD_PATH}', 'w', encoding='utf-8') as fp:
        fp.writelines(content)
    return is_delete


def has_filter_words(message_text: str) -> bool:
    """
    Check if a message contains a filter word.

    Parameters:
        message_text (str): The message text to check.
    
    Returns:
        bool: True if the message contains a filter word, False otherwise.
    """
    with FILTER_LOCK:
        with open(f'{PATH}/{FILTER_WORD_PATH}', 'r', encoding="UTF-8") as fp:
            for line in fp:
                word = line.strip()
                if word in message_text:
                    return True
        return False


def init_user(user):
    """
    Initialize user preferences.

    Parameters:
        user (User): The user object containing the user's information.

    Returns:
        None
    """
    user_id = str(user.id)
    preference = preference_list.setdefault(user_id, {}) # 若没有这个用户，新建一个

    # 若包含该用户，但是缺少默认首选项，添加默认首选项
    if 'notification' not in preference:
        preference['notification'] = False

    if 'blocked' not in preference:
        preference['blocked'] = False

    # 若用户名不一致，更新用户名
    if preference.get('name') != user.full_name:
        preference['name'] = user.full_name
        threading.Thread(target=save_preference).start()

PATH = os.path.dirname(os.path.realpath(__file__))
MESSAGE_LOCK = threading.Lock()
PREFERENCE_LOCK = threading.Lock()
CONFIG_LOCK = threading.Lock()
FILTER_LOCK = threading.Lock()

FILTER_WORD_PATH = "data/filter_words.txt"
CONFIG = load_config("data/config.json")
LANG = load_config("lang/" + CONFIG["Lang"] + ".json")
message_list = load_config("data/data.json")
preference_list = load_config("data/preference.json")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
