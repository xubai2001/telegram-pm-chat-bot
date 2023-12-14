from telegram.ext import (
        filters,
        MessageHandler,
        ApplicationBuilder,
        CommandHandler,
        )
from utils import *
from handlers import *


def main():
    app = (
        ApplicationBuilder()
        .token(CONFIG["Token"])
        .post_init(check_config)
        .post_stop(save_all_config)
        .build()
    )

    handlers = [
        CommandHandler('start', start),
        CommandHandler('ping', ping),
        CommandHandler("ban", ban),
        CommandHandler("unban", unban),
        CommandHandler("info", info),
        CommandHandler("setadmin", setadmin),
        CommandHandler("add", add),
        CommandHandler("delete", delete),
        MessageHandler(filters.COMMAND, unknown_command),
        MessageHandler(~filters.COMMAND, process_msg)
    ]

    for handler in handlers:
        app.add_handler(handler)

    app.run_polling()

if "__main__" == __name__:
    main()
