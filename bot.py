import datetime
import logging
import os
import time

import pyrogram
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import utils

start_string = "{bot_version}\n{bot_data}"

scheduler = BackgroundScheduler()
scheduler.start()


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
    session_name="EricSolinasBot",
    api_id=utils.config["telegram"]["api_id"],
    api_hash=utils.config["telegram"]["api_hash"],
    bot_token=utils.config["telegram"]["bot_api_key"],
    workers=4,
    plugins=plugins,
)

APP.start()
APP.set_parse_mode(parse_mode=None)
APP.ME = APP.get_me()
APP.MASTER = APP.get_chat(chat_id=utils.config["master"])
print(
    start_string.format(
        bot_version=f"Pyrogram {APP.ME.first_name}", bot_data=utils.PrintUser(APP.ME)
    )
)
loaded_plugins = []
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
    parse_mode="html",
)
# schedule backup at 04:00 with a random delay between ± 10 minutes
scheduler.add_job(
    utils.SendBackup, kwargs=dict(client=APP), trigger=CronTrigger(hour=4, jitter=600),
)
APP.idle()
APP.stop()
