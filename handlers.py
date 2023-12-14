from telegram import (
    Update
    )
from telegram.constants import ParseMode
from telegram.ext import (
        ContextTypes,
        CallbackContext
        )
from utils import *

async def process_msg(update: Update, context: CallbackContext):
    """
    Process all incoming messages except for commands.
    """
    admin_id = CONFIG["Admin"]
    init_user(update.message.from_user)

    if update.message.chat_id == admin_id:
        await process_admin_message(update, context, admin_id)
    else:
        await process_user_message(update, context, admin_id)


async def process_admin_message(update: Update, context: CallbackContext, admin_id: str):
    """
    Process all incoming messages from admin.
    """
    reply_to_message = update.message.reply_to_message
    if reply_to_message:
        reply_id = str(reply_to_message.message_id)
        if reply_id in message_list:
            await handle_admin_reply(update, context, reply_id)
        else:
            await context.bot.send_message(
                chat_id=admin_id, text=LANG["reply_to_message_no_data"]
            )
    else:
        await context.bot.send_message(
            chat_id=admin_id, text=LANG["reply_to_no_message"]
        )


async def handle_admin_reply(update: Update, context: CallbackContext, reply_id: str):
    """
    Process all the reply messages from admin.
    """
    msg = update.message
    sender_id = message_list[reply_id]["sender_id"]
    try:
        reply_types = {
            "audio": context.bot.send_audio,
            "document": context.bot.send_document,
            "voice": context.bot.send_voice,
            "video": context.bot.send_video,
            "sticker": context.bot.send_sticker,
            "photo": context.bot.send_photo,
            "text_markdown": context.bot.send_message,
        }
        for reply_type, handler in reply_types.items():
            if getattr(msg, reply_type):    # 循环检测对应消息类型的消息是否存在(按消息类型转发)
                kwargs = {"chat_id": sender_id, reply_type: getattr(msg, reply_type)} 

                message_content = getattr(msg, reply_type)
                if reply_type == "photo":
                    kwargs["caption"] = msg.caption
                    kwargs[reply_type] = message_content[0] # 要取第
                elif reply_type == "text_markdown":
                    kwargs["parse_mode"] = ParseMode.MARKDOWN_V2
                    kwargs["text"] = kwargs.pop(reply_type) # text_markdown类型的消息，发送要用text=xxxx
                else:
                    kwargs[reply_type] = message_content    # 不同消息类型，参数列表不一样
                await handler(**kwargs)     # 处理好参数列表后调用发送函数
                break
        else:
            await context.bot.send_message(
                chat_id=CONFIG["Admin"], text=LANG["reply_type_not_supported"]
            )
    except Exception as e:
        if str(e) == "Forbidden: bot was blocked by the user":
            await context.bot.send_message(
                chat_id=CONFIG["Admin"], text=LANG["blocked_alert"]
            )
        else:
            await context.bot.send_message(
                chat_id=CONFIG["Admin"], text=LANG["reply_message_failed"]
            )


async def process_user_message(
    update: Update, context: CallbackContext, admin_id: str
):
    """
    Process all incoming messages from user.
    """
    if update.message.text:
        if has_filter_words(update.message.text):
            await context.bot.send_message(
                chat_id=update.message.from_user.id,
                text=LANG["filter_word_alert"],
            )
            return

    user_id = str(update.message.from_user.id)
    if preference_list[user_id]["blocked"]:
        await context.bot.send_message(
            chat_id=update.message.from_user.id, text=LANG["be_blocked_alert"]
        )
        return

    fwd_msg = await context.bot.forward_message(
        chat_id=admin_id,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id,
    )
    message_list[str(fwd_msg.message_id)] = {
        "sender_id": update.message.from_user.id,
        "original_id": update.message.message_id,
    }

    threading.Thread(target=save_data).start()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send a message when the command /start is issued.
    """
    init_user(update.message.from_user)
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=LANG['start'])

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Check if the bot is online.
    """
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=LANG["ping_status"]
    )

# 回复消息以封禁用户
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command to ban a user.
    """
    if update.message.chat_id != CONFIG['Admin']:  # 仅Admin可以执行
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=LANG["not_an_admin"]
        )
        return

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

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command to unban a user(with user id is optional).
    """
    if update.message.chat_id != CONFIG['Admin']:  # 仅Admin可以执行
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=LANG["not_an_admin"]
        )
        return
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



async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command: Get User Info, and only accessible to users who have not set privacy
    """
    if update.message.chat_id == CONFIG['Admin']:  # 仅Admin可以执行
        reply_to_message = update.message.reply_to_message
        if reply_to_message:
            if str(reply_to_message.message_id) in message_list:
                sender_id = message_list[str(reply_to_message.message_id)]["sender_id"]
                send_text = f"[{preference_list[str(sender_id)]['name']}](tg://user?id={sender_id})"
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
    """
    When config.json does not have Admin, set Admin
    """
    if CONFIG['Admin'] == 0:
        CONFIG['Admin'] = int(update.message.from_user.id)
        threading.Thread(target=save_config).start()
        await context.bot.send_message(chat_id=update.message.chat_id,
                             text=LANG['set_admin_successful'])
    else:
        await context.bot.send_message(chat_id=update.message.chat_id,
                             text=LANG['set_admin_failed'])
    return


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin Command: Add filter words
    """
    if update.message.chat_id == CONFIG['Admin']:  # 仅Admin可以执行
        if context.args:
            if has_filter_words(context.args[0]): # 若已经有该屏蔽词
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text= LANG["has_same_filter_word"])
                return
            try:
                add_filter_words(context.args[0])
            except Exception as e:
                await context.bot.send_message( # 添加失败通知
                    chat_id=update.message.chat_id,
                    text= LANG["add_filter_word_alert"] % str(e))
            await context.bot.send_message( # 添加成功通知
                chat_id=update.message.chat_id,
                text=LANG["add_filter_word_successful"] % context.args[0])

        else:   # 未携带屏蔽词通知
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=LANG["command_format_error_alert"])

    else:   # 若不是管理员发送该指令，不执行，并发送提示信息
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=LANG["not_an_admin"])


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin Command: Delete message(reply a message) or delete filter words(with a filter word).
    """
    if update.message.chat_id != CONFIG['Admin']:  # 仅Admin可以执行
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=LANG["not_an_admin"]
        )
        return

    reply_to_message = update.message.reply_to_message
    if not reply_to_message:    # 若不是回复某条消息，则为删除屏蔽词
        is_delete = delete_filter_words(context.args[0])
        send_text = LANG["delete_successful" if is_delete else "delete_failed"] % context.args[0]
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=send_text
            )
        return
    # sender_id即要删除的消息的发送者的id
    sender_id = message_list[str(reply_to_message.message_id)]["sender_id"]
    if context.args:  # 指令携带信息，删除相同用户的所有信息
        arg = context.args[0]
        if arg == 'all':  # 例：/delete all 的情况，删除所有该用户的信息
            keys = list(message_list)
            for key in reversed(keys):  # key为message_id,此处从新往后删除，因为48小时外的消息不允许删除
                if message_list[key]["sender_id"] == sender_id: # 删除所有sender_id为指定用户的id
                    # 删除并使用is_delete判断是否删除，若未删除成功，本地以及本对话都不删除
                    is_delete = await context.bot.delete_message(
                        chat_id=sender_id,
                        message_id=message_list[key]["original_id"] # 这里使用原始消息id，先删除原始消息以判断是否能删除
                    )
                    if is_delete:   # 若能删除，则开始删除bot转发的消息，以及本地数据
                        await context.bot.delete_message(
                            chat_id=reply_to_message.chat_id,
                            message_id=int(key) # 这里使用原始消息id，先删除原始消息以判断是否能删除
                        )
                        del message_list[key]
                    else:   # 不能删除表示在这之前的消息均不能删除
                        break
            await update.message.delete()

        else:
            # 无法识别的情况
            await context.bot.send_message(
                chat_id=update.message.id,
                text=LANG["command_format_error_alert"]
            )

    else:   # 若未携带信息，仅 /delete,则只删除回复的消息
        original_message_id = message_list[str(reply_to_message.message_id)]["original_id"]
        is_delete =await context.bot.delete_message(
            chat_id=sender_id,
            message_id=original_message_id
        )
        await reply_to_message.delete()
        await update.message.delete()
        del message_list[str(reply_to_message.message_id)]
    threading.Thread(target=save_data).start()


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Process unknown command
    """
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=LANG["nonexistent_command"]
    )
