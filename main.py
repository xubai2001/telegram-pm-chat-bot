from telegram import (
    Update
    )
from telegram.constants import ParseMode
from telegram.ext import (
        filters,
        MessageHandler,
        Application,
        ApplicationBuilder,
        CommandHandler,
        ContextTypes,
        CallbackContext
        )
import json
import logging
import threading
import os
import time

PATH = os.path.dirname(os.path.realpath(__file__)) + '/'
MESSAGE_LOCK = threading.Lock()
PREFERENCE_LOCK = threading.Lock()
CONFIG_LOCK = threading.Lock()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def save_data():  # 保存消息数据
    global MESSAGE_LOCK
    with MESSAGE_LOCK:
        with open(PATH + 'data.json', 'w', encoding="UTF-8") as fp:
            fp.write(json.dumps(message_list))

def save_preference():  # 保存用户资料与设置
    global PREFERENCE_LOCK
    with MESSAGE_LOCK:
        with open(PATH + 'preference.json', 'w', encoding="UTF-8") as fp:
            fp.write(json.dumps(preference_list))

def save_config():  # 保存配置
    global CONFIG_LOCK
    with CONFIG_LOCK:
        with open(PATH + 'config.json', 'w', encoding="UTF-8") as fp:
            fp.write(json.dumps(CONFIG, indent=4))

def load_config(PATH):
    with open(PATH) as fp:
        config = json.load(fp)
    return config


def init_user(user):
    if not str(user.id) in preference_list:  # 如果用户是第一次使用Bot
        preference_list[str(user.id)] = {}
        preference_list[str(user.id)]['notification'] = False  # 默认关闭消息发送提示
        preference_list[str(user.id)]['blocked'] = False # 默认用户未被封禁
        preference_list[str(user.id)]['name'] = user.full_name  # 保存用户昵称
        threading.Thread(target=save_preference).start()
        return
    if not 'blocked' in preference_list[str(user.id)]:
        preference_list[str(user.id)]['blocked'] = False
    if preference_list[str(user.id)]['name'] != user.full_name:  # 如果用户的昵称变了
        preference_list[str(user.id)]['name'] = user.full_name


async def process_msg(update: Update, context: CallbackContext):
    admin_id = CONFIG["Admin"]
    init_user(update.message.from_user)

    # 来自Admin的消息
    if update.message.chat_id == admin_id:
        reply_to_message = update.message.reply_to_message
        if reply_to_message:    # 如果admin发送的消息会回复某个消息
            if str(reply_to_message.message_id) in message_list:
                msg = update.message    # Admin发送的消息
                sender_id = message_list[str(reply_to_message.id)]["sender_id"]
                try:
                    if msg.audio:
                        await context.bot.send_audio(chat_id=sender_id,
                                audio=msg.audio, caption=msg.caption)
                    elif msg.document:
                        await context.bot.send_document(chat_id=sender_id,
                                document=msg.document,
                                caption=msg.caption)
                    elif msg.voice:
                        await context.bot.send_voice(chat_id=sender_id,
                                voice=msg.voice, caption=msg.caption)
                    elif msg.video:
                        await context.bot.send_video(chat_id=sender_id,
                                video=msg.video, caption=msg.caption)
                    elif msg.sticker:
                        await context.bot.send_sticker(chat_id=sender_id,
                                sticker=msg.sticker)
                    elif msg.photo:
                        await context.bot.send_photo(chat_id=sender_id,
                                photo=msg.photo[0], caption=msg.caption)
                    elif msg.text_markdown:
                        await context.bot.send_message(chat_id=sender_id,
                                text=msg.text_markdown,
                                parse_mode=ParseMode.MARKDOWN_V2)
                    else:
                        await context.bot.send_message(chat_id=CONFIG['Admin'],
                                text=LANG['reply_type_not_supported'])
                        return
                except Exception as e:
                    if str(e) == 'Forbidden: bot was blocked by the user':
                        await context.bot.send_message(chat_id=CONFIG['Admin'],
                                text=LANG['blocked_alert'])  # Bot被停用
                    else:
                        await context.bot.send_message(chat_id=CONFIG['Admin'],
                                text=LANG['reply_message_failed'])
                    return
            else:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=LANG["reply_to_message_no_data"]
                )
        else:
            await context.bot.send_message(
                    chat_id=admin_id,
                    text=LANG["reply_to_no_message"]
                )
    else:
        # 非Admin的消息
        if preference_list[str(update.message.from_user.id)]['blocked']: # blocked用户只发送被block提示
            await context.bot.send_message(
                chat_id=update.message.from_user.id,
                text=LANG["be_blocked_alert"]
            )
            return
        fwd_msg = await context.bot.forward_message(  # 转发消息
                chat_id=admin_id,
                from_chat_id = update.message.chat_id,
                message_id = update.message.message_id
            )
        # 消息id以及对应的用户id 存放到message_list
        message_list[str(fwd_msg.message_id)] = {}
        message_list[str(fwd_msg.message_id)]['sender_id'] = update.message.from_user.id
        threading.Thread(target=save_data).start()  # 保存消息数据

async def process_command(update: Update, context: CallbackContext): 
    id = update.message.from_user.id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_user(update.message.from_user)
    await context.bot.send_message(chat_id=update.message.chat_id,
                         text=LANG['start'])

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=LANG["ping_status"]
    )

# 回复消息以封禁用户
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == CONFIG['Admin']:  # 仅Admin可以执行
        reply_to_message = update.message.reply_to_message
        if reply_to_message:    # 如果/ban是回复某个转发的消息
            if str(reply_to_message.message_id) in message_list:
                sender_id = message_list[str(reply_to_message.message_id)]["sender_id"]
                preference_list[str(sender_id)]["blocked"] = True  # 将用户的blocked置为True
                await context.bot.send_message(   # 发送反馈消息给 /ban的发送者
                    chat_id=update.message.chat_id,
                    text=LANG['ban_user']
                    % (preference_list[str(sender_id)]['name'],
                    str(sender_id)),
                    parse_mode=ParseMode.MARKDOWN_V2)
                await context.bot.send_message(     # 向被封禁者发送封禁信息
                    chat_id=sender_id,
                    text=LANG["be_blocked_alert"]
                )
            else:   # 回复的消息不在消息数据中
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=LANG["reply_to_message_no_data"]
                )
        else:   # /ban不是回复消息
            await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=LANG["reply_to_no_message"]
                )
        threading.Thread(target=save_preference).start()
    else:   # 若不是管理员发送该指令，不执行，并发送提示信息
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=LANG["not_an_admin"]
        )      
  

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == CONFIG['Admin']:  # 仅Admin可以执行
        reply_to_message = update.message.reply_to_message
        if reply_to_message:    # 如果/ban是回复某个转发的消息
            if str(reply_to_message.message_id) in message_list:
                sender_id = message_list[str(reply_to_message.message_id)]["sender_id"]
                preference_list[str(sender_id)]["blocked"] = False  # 将用户的blocked置为False
                await context.bot.send_message(   # 发送反馈消息给 /unban的发送者
                    chat_id=update.message.chat_id,
                    text=LANG['unban_user']
                    % (preference_list[str(sender_id)]['name'],
                    str(sender_id)),
                    parse_mode=ParseMode.MARKDOWN_V2)
                await context.bot.send_message(     # 向被解封禁者发送封禁信息
                    chat_id=sender_id,
                    text=LANG["be_unbanned"]
                )
            else:   # 回复的消息不在消息数据中
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=LANG["reply_to_message_no_data"]
                )
        elif context.args:  # /ban不是回复某条消息，而是携带了用户id
            unban_id = context.args[0]
            if unban_id in preference_list:

                preference_list[unban_id]["blocked"] = False
                await context.bot.send_message(   # 发送反馈消息给 /unban的发送者
                    chat_id=update.message.chat_id,
                    text=LANG['unban_user']
                    % (preference_list[unban_id]['name'],
                    unban_id),
                    parse_mode=ParseMode.MARKDOWN_V2)
                await context.bot.send_message(     # 向被解封禁者发送封禁信息
                    chat_id=int(unban_id),
                    text=LANG["be_unbanned"]
                )
            else:   # 回复的消息不在消息数据中
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=LANG["user_not_found"]
                )
        else:   # /ban不是回复消息，且未携带信息
            await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=LANG["reply_to_no_message"]
                )
        threading.Thread(target=save_preference).start()
    else:   # 若不是管理员发送该指令，不执行，并发送提示信息
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=LANG["not_an_admin"]
        )  


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == CONFIG['Admin']:  # 仅Admin可以执行
        reply_to_message = update.message.reply_to_message
        if reply_to_message:
            if str(reply_to_message.message_id) in message_list:
                sender_id = message_list[str(reply_to_message.message_id)]["sender_id"]
                send_text = f"[{preference_list[str(sender_id)]['name']}](tg://user?id={sender_id})"
                print(send_text)
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=send_text,
                    parse_mode=ParseMode.MARKDOWN_V2
                )

    else:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=LANG["not_an_admin"]
        )    


async def setadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if CONFIG['Admin'] == 0:
        CONFIG['Admin'] = int(update.message.from_user.id)
        threading.Thread(target=save_config).start()
        await context.bot.send_message(chat_id=update.message.chat_id,
                             text=LANG['set_admin_successful'])
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                             text=LANG['set_admin_failed'])
    return

async def check_config(application: Application) -> None:
    bot = await application.bot.get_me()
    # 初始化bot信息
    if "ID" not in CONFIG:
        CONFIG["ID"] = bot.id
    if "Username" not in CONFIG:
        CONFIG["Username"] = bot.username
    threading.Thread(target=save_config).start()

async def save_all_config(application: Application) -> None:
    logging.info("Saving data....")
    save_config()
    save_data()
    save_preference()
    logging.info("Saving data successful!")

def main():
    global CONFIG
    global message_list
    global preference_list
    global LANG
    CONFIG = load_config(PATH + "config.json")
    LANG = load_config(PATH + "lang/" + CONFIG["Lang"] + ".json")
    message_list = load_config(PATH + "data.json")
    preference_list = load_config(PATH + "preference.json")

    app = ApplicationBuilder().token(CONFIG["Token"]).post_init(check_config).post_stop(save_all_config).build()

    process_msg_handler = MessageHandler(filters.ALL, process_msg)
    start_handler = CommandHandler('start', start)
    ping_handler = CommandHandler('ping', ping)
    ban_handler = CommandHandler("ban", ban)
    unban_handler = CommandHandler("unban", unban)
    info_handler = CommandHandler("info", info)
    setadmin_handler = CommandHandler("setadmin", setadmin)

    app.add_handler(setadmin_handler)
    app.add_handler(start_handler)
    app.add_handler(ping_handler)
    app.add_handler(ban_handler)
    app.add_handler(unban_handler)
    app.add_handler(info_handler)
    app.add_handler(process_msg_handler)
    
    app.run_polling()

if "__main__" == __name__:
    main()
