import datetime
import logging
import os
import time

import pyrogram
from apscheduler.triggers.cron import CronTrigger
from pytz import utc

import db_management
import utils

start_string = "{bot_version}\n{bot_data}"


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)

if not utils.config:
    logging.log(logging.FATAL, "Missing config.json")
    exit()

plugins = dict(root="plugins")
# wait one second to have tables created
time.sleep(1)

APP = pyrogram.Client(
    name="EricSolinasBot",
    api_id=utils.config["telegram"]["api_id"],
    api_hash=utils.config["telegram"]["api_hash"],
    bot_token=utils.config["telegram"]["bot_api_key"],
    workers=4,
    plugins=plugins,
    parse_mode=pyrogram.enums.parse_mode.ParseMode.DISABLED,
)

APP.start()
APP.ME = APP.get_me()
db_management.DBUser(user=APP.ME)
APP.MASTER = APP.get_chat(chat_id=utils.config["master"])
db_management.DBUser(user=APP.MASTER)
print(
    start_string.format(
        bot_version=f"Pyrogram {APP.ME.first_name}", bot_data=utils.PrintUser(APP.ME)
    )
)
loaded_plugins = list()
for dirpath, dirnames, filenames in os.walk(APP.plugins["root"]):
    # filter out __pycache__ folders
    if "__pycache__" not in dirpath:
        loaded_plugins.extend(
            # filter out __init__.py
            filter(lambda x: x != "__init__.py", filenames)
        )

APP.send_message(
    chat_id=utils.config["master"],
    text=f"<b>Bot started!</b>\n<b>Pyrogram: {pyrogram.__version__}</b>\n<b>{datetime.datetime.utcnow()}</b>\n"
    + "\n".join(
        sorted(
            # put html and take only file_name
            map(lambda x: f"<code>{os.path.splitext(x)[0]}</code>", loaded_plugins)
        )
    )
    + f"\n\n<b>{len(loaded_plugins)} plugins loaded</b>",
    parse_mode=pyrogram.enums.parse_mode.ParseMode.HTML,
)
# schedule backup at UTC 02:30 with a random delay between ± 10 minutes
utils.scheduler.add_job(
    utils.SendBackup,
    trigger=CronTrigger(hour=2, minute=30, jitter=600, timezone=utc),
    kwargs=dict(client=APP),
)
pyrogram.idle()
APP.stop()

db_management.DB.close()
