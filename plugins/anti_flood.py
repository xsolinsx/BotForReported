import datetime
import time

import pyrogram
import utils


@pyrogram.Client.on_message(pyrogram.filters.private, group=-1)
def MessagesAntiFlood(client: pyrogram.Client, msg: pyrogram.types.Message):
    if msg.from_user.id == utils.config["master"]:
        return

    flooder = False
    utils.InstantiateFloodDictionary(msg.from_user.id)
    # take the current time
    timestamp_ = time.time()

    if len(utils.flood[msg.from_user.id]["times"]) > 4:
        # check if 5+ messages(recorded times) in less than 5 seconds
        if timestamp_ - utils.flood[msg.from_user.id]["times"][0] <= 5:
            flooder = True
        # remove oldest message(recorded time)
        utils.flood[msg.from_user.id]["times"].pop(0)
    # append last message(recorded time)
    utils.flood[msg.from_user.id]["times"].append(timestamp_)

    # if now this chat is out of the flood_wait time continue
    if timestamp_ >= utils.flood[msg.from_user.id]["flood_wait_expiry_date"]:
        if flooder:
            print(f"FLOODER: {msg.from_user.id}")
            utils.flood[msg.from_user.id]["flood_wait_minutes"] = 1
            # is the chat flooding inside a two minutes window after the previous flood_wait_expiry_date?
            if (
                utils.flood[msg.from_user.id]["flood_wait_expiry_date"] != 0
                and timestamp_
                <= utils.flood[msg.from_user.id]["flood_wait_expiry_date"] + 120
            ):
                # add one minute to the previous flood_wait time
                utils.flood[msg.from_user.id]["flood_wait_minutes"] += 1
            # transform into seconds and add current time to have an expiry date
            utils.flood[msg.from_user.id]["flood_wait_expiry_date"] = (
                timestamp_ + utils.flood[msg.from_user.id]["flood_wait_minutes"] * 60
            )
            if not utils.flood[msg.from_user.id]["warned"]:
                utils.flood[msg.from_user.id]["warned"] = True
                # wait two seconds to give the warn message as the last one due to multiple workers
                time.sleep(2)
                msg.reply_text(
                    text="You are flooding, the bot will not forward your messages for {0} minute(s).".format(
                        utils.flood[msg.from_user.id]["flood_wait_minutes"]
                    ),
                    disable_notification=False,
                )
                client.send_message(
                    chat_id=utils.config["master"],
                    text="(#user{0}) {1} is limited for flood for {2} minute(s).".format(
                        msg.from_user.id,
                        msg.from_user.first_name,
                        utils.flood[msg.from_user.id]["flood_wait_minutes"],
                    ),
                    disable_notification=False,
                )
            # do not process messages for flooders
            msg.stop_propagation()
        else:
            # reset user data
            utils.flood[msg.from_user.id]["warned"] = False
            utils.flood[msg.from_user.id]["flood_wait_minutes"] = 0
            utils.flood[msg.from_user.id]["flood_wait_expiry_date"] = 0
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
