import datetime
import time

import pyrogram

import utils

flood = dict()


def InstantiateFloodDictionary(chat_id: int):
    # if chat_id not registered into the flood table register it
    if chat_id not in flood:
        flood[chat_id] = {}
        flood[chat_id]["times"] = list()
        flood[chat_id]["flood_wait_expiry_date"] = 0
        # from 0 to X minutes of wait depending on how much of an idiot is the user
        flood[chat_id]["flood_wait_minutes"] = 0
        # to know if id has been warned
        flood[chat_id]["warned"] = False


@pyrogram.Client.on_message(pyrogram.Filters.private, group=-1)
def MessagesAntiFlood(client: pyrogram.Client, msg: pyrogram.Message):
    if msg.from_user.id == utils.config["master"]:
        return

    flooder = False
    InstantiateFloodDictionary(msg.from_user.id)
    # take the current time
    timestamp_ = time.time()

    if len(flood[msg.from_user.id]["times"]) > 4:
        # check if 5+ messages(recorded times) in less than 5 seconds
        if timestamp_ - flood[msg.from_user.id]["times"][0] <= 5:
            flooder = True
        # remove oldest message(recorded time)
        flood[msg.from_user.id]["times"].pop(0)
    # append last message(recorded time)
    flood[msg.from_user.id]["times"].append(timestamp_)

    # if now this chat is out of the flood_wait time continue
    if timestamp_ >= flood[msg.from_user.id]["flood_wait_expiry_date"]:
        if flooder:
            print(f"FLOODER: {msg.from_user.id}")
            flood[msg.from_user.id]["flood_wait_minutes"] = 1
            # is the chat flooding inside a two minutes window after the previous flood_wait_expiry_date?
            if (
                flood[msg.from_user.id]["flood_wait_expiry_date"] != 0
                and timestamp_
                <= flood[msg.from_user.id]["flood_wait_expiry_date"] + 120
            ):
                # add one minute to the previous flood_wait time
                flood[msg.from_user.id]["flood_wait_minutes"] += 1
            # transform into seconds and add current time to have an expiry date
            flood[msg.from_user.id]["flood_wait_expiry_date"] = (
                timestamp_ + flood[msg.from_user.id]["flood_wait_minutes"] * 60
            )
            if not flood[msg.from_user.id]["warned"]:
                flood[msg.from_user.id]["warned"] = True
                # wait two seconds to give the warn message as the last one due to multiple workers
                time.sleep(2)
                msg.reply_text(
                    text="You are flooding, the bot will not forward your messages for {0} minute(s).".format(
                        flood[msg.from_user.id]["flood_wait_minutes"]
                    ),
                    disable_notification=False,
                )
                client.send_message(
                    chat_id=utils.config["master"],
                    text="(#user{0}) {1} is limited for flood for {2} minute(s).".format(
                        msg.from_user.id,
                        msg.from_user.first_name,
                        flood[msg.from_user.id]["flood_wait_minutes"],
                    ),
                    disable_notification=False,
                )
            # do not process messages for flooders
            msg.stop_propagation()
        else:
            # reset user data
            flood[msg.from_user.id]["warned"] = False
            flood[msg.from_user.id]["flood_wait_minutes"] = 0
            flood[msg.from_user.id]["flood_wait_expiry_date"] = 0
    else:
        # do not process messages for flooders
        msg.stop_propagation()
    print(
        "[UTC {0}] {1}, @{2} ({3}): {4}\n".format(
            datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"),
            msg.from_user.first_name,
            msg.from_user.username,
            msg.from_user.id,
            msg.text
            if not msg.media
            else f"MEDIA {utils.ExtractMedia(msg=msg).file_id}",
        )
    )
