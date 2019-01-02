import datetime
import json
import logging
import time

import peewee
import pyrogram

import utils

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.ERROR)

last_user = None
print_string = "######################\n[{0}] {1}, @{2} ({3}): {4}"

with open(file="config.json",
          encoding="utf-8") as f:
    config = json.load(fp=f)
if not config:
    exit()


app = pyrogram.Client(session_name=config["telegram"]["bot_api_key"],
                      api_id=config["telegram"]["api_id"],
                      api_hash=config["telegram"]["api_hash"],
                      workers=4)
app.start()
master = app.get_chat(chat_id=config["master"])

db = peewee.SqliteDatabase(database=config["database"],
                           pragmas={"foreign_keys": 1,
                                    "journal_mode": "wal",
                                    'ignore_check_constraints': 0, })


class User(peewee.Model):
    id_ = peewee.IntegerField(primary_key=True,
                              constraints=[peewee.Check(constraint='id_ > 0')])

    first_name = peewee.CharField(max_length=255)
    last_name = peewee.CharField(max_length=255,
                                 default=None,
                                 null=True)
    username = peewee.CharField(max_length=32,
                                default=None,
                                null=True)
    # prevent forwards to master
    is_blocked = peewee.BooleanField(default=False,
                                     null=False,
                                     constraints=[peewee.Check(constraint='is_blocked == 0 OR is_blocked == 1')])

    class Meta:
        database = db


db.create_tables(models=[User, ],
                 safe=True)


# region ANTIFLOOD

flood = dict()


def InstanceFloodId(chat_id: str):
    # if chat_id not registered into the flood table register it
    if not chat_id in flood:
        flood[chat_id] = {}
        flood[chat_id]["times"] = list()
        flood[chat_id]["flood_wait_expiry_date"] = 0
        # from 0 to X minutes of wait depending on how much of an idiot is the user
        flood[chat_id]["flood_wait_minutes"] = 0
        # to know if id has been warned
        flood[chat_id]["warned"] = False


@app.on_message(group=-2)
def MessagesAntiFlood(client: pyrogram.Client,
                      msg: pyrogram.Message):
    usr, created = User.get_or_create(id_=msg.from_user.id,
                                      defaults={"first_name": msg.from_user.first_name,
                                                "last_name": msg.from_user.last_name,
                                                "username": msg.from_user.username})
    if usr.first_name != msg.from_user.first_name or usr.last_name != msg.from_user.last_name or usr.username != msg.from_user.username:
        User.replace(id_=msg.from_user.id,
                     first_name=msg.from_user.first_name,
                     last_name=msg.from_user.last_name,
                     username=msg.from_user.username,
                     is_blocked=usr.is_blocked).execute()

    if msg.from_user.id == master.id:
        return

    if usr.is_blocked:
        # do not process messages for blocked users
        msg.stop_propagation()

    chat_id = str(msg.from_user.id)
    flooder = False
    InstanceFloodId(chat_id)
    # take the current time
    timestamp_ = time.time()

    if len(flood[chat_id]["times"]) > 4:
        # check if 5+ messages(recorded times) in less than 5 seconds
        if timestamp_ - flood[chat_id]["times"][0] <= 5:
            flooder = True
        # remove oldest message(recorded time)
        flood[chat_id]["times"].pop(0)
    # append last message(recorded time)
    flood[chat_id]["times"].append(timestamp_)

    # if now this chat is out of the flood_wait time continue
    if timestamp_ >= flood[chat_id]["flood_wait_expiry_date"]:
        if flooder:
            print("FLOODER: " + chat_id)
            # is the chat flooding inside a two minutes window after the previous flood_wait_expiry_date?
            if flood[chat_id]["flood_wait_expiry_date"] != 0 and timestamp_ <= flood[chat_id]["flood_wait_expiry_date"] + 120:
                # add one minute to the previous flood_wait time
                flood[chat_id]["flood_wait_minutes"] = flood[chat_id]["flood_wait_minutes"] if flood[chat_id]["flood_wait_minutes"] != 0 else 1
            else:
                # one minute of flood_wait
                flood[chat_id]["flood_wait_minutes"] = 1
            # transform into seconds and add current time to have an expiry date
            flood[chat_id]["flood_wait_expiry_date"] = timestamp_ + \
                flood[chat_id]["flood_wait_minutes"] * 60
            if not flood[chat_id]["warned"]:
                flood[chat_id]["warned"] = True
                # wait two seconds to give the warn message as the last one due to multiple workers
                time.sleep(2)
                msg.reply(text="You are flooding, the bot will not forward your messages for {0} minute(s).".format(flood[chat_id]["flood_wait_minutes"]),
                          disable_notification=False)
                app.send_message(chat_id=master.id,
                                 text="(#user{0}) {1} is limited for flood for {2} minute(s).".format(chat_id,
                                                                                                      msg.from_user.first_name,
                                                                                                      flood[chat_id]["flood_wait_minutes"]),
                                 disable_notification=False)
            # do not process messages for flooders
            msg.stop_propagation()
        else:
            # reset user data
            flood[chat_id]["warned"] = False
            flood[chat_id]["flood_wait_minutes"] = 0
            flood[chat_id]["flood_wait_expiry_date"] = 0
    else:
        # do not process messages for flooders
        msg.stop_propagation()
    print(print_string.format(datetime.datetime.now().time(),
                              msg.from_user.first_name,
                              msg.from_user.username,
                              msg.from_user.id,
                              msg.text if not msg.media else ("MEDIA " + utils.ExtractMedia(msg=msg,
                                                                                            bigger_photo=True).file_id)))
    global last_user
    last_user = msg.from_user

# endregion


@app.on_message(pyrogram.Filters.chat(master.id) & pyrogram.Filters.command(command=["getlastuser", "getlast", "lastuser"], prefix=["/", "!", "#", "."]))
def CMDGetLastUser(client: pyrogram.Client,
                   msg: pyrogram.Message):
    msg.reply(text=print_string.format(datetime.datetime.now().time(),
                                       msg.from_user.first_name,
                                       msg.from_user.username,
                                       msg.from_user.id,
                                       msg.text if not msg.media else ("MEDIA " + utils.ExtractMedia(msg=msg,
                                                                                                     bigger_photo=True).file_id)),
              disable_notification=False)


@app.on_message(pyrogram.Filters.chat(master.id) & pyrogram.Filters.command(command="block", prefix=["/", "!", "#", "."]))
def CMDBlock(client: pyrogram.Client,
             msg: pyrogram.Message):
    users_to_block = list()
    if msg.reply_to_message:
        if msg.reply_to_message.forward_from:
            users_to_block.append(msg.reply_to_message.forward_from)
        elif msg.reply_to_message.text.find("(#user") != -1:
            users_to_block.append(app.get_chat(chat_id=int(msg.reply_to_message.text[msg.reply_to_message.text.find(
                "(#user") + 6: msg.reply_to_message.text.find(")")])))
    else:
        msg.command.remove(msg.command[0])
        for usr in msg.command:
            obj = app.get_chat(chat_id=usr)
            if isinstance(obj=obj,
                          class_or_tuple=pyrogram.User):
                users_to_block.append(obj)

    txt = ""
    for usr in users_to_block:
        User.replace(id_=usr.id,
                     first_name=usr.first_name,
                     last_name=usr.first_name,
                     username=usr.username,
                     is_blocked=True).execute()
        txt += "(#user{0}) {1}\n".format(usr.id,
                                         usr.first_name)
        app.send_message(chat_id=usr.id,
                         text="You have been blocked.")

    msg.reply(text="Blocked users:\n" + txt,
              disable_notification=False)


@app.on_message(pyrogram.Filters.chat(master.id) & pyrogram.Filters.command(command="unblock", prefix=["/", "!", "#", "."]))
def CMDUnblock(client: pyrogram.Client,
               msg: pyrogram.Message):
    users_to_unblock = list()
    if msg.reply_to_message:
        if msg.reply_to_message.forward_from:
            users_to_unblock.append(msg.reply_to_message.forward_from)
        elif msg.reply_to_message.text.find("(#user") != -1:
            users_to_unblock.append(app.get_chat(chat_id=int(msg.reply_to_message.text[msg.reply_to_message.text.find(
                "(#user") + 6: msg.reply_to_message.text.find(")")])))
    else:
        msg.command.remove(msg.command[0])
        for usr in msg.command:
            obj = app.get_chat(chat_id=usr)
            if isinstance(obj=obj,
                          class_or_tuple=pyrogram.User):
                users_to_unblock.append(obj)

    txt = ""
    for usr in users_to_unblock:
        User.replace(id_=usr.id,
                     first_name=usr.first_name,
                     last_name=usr.first_name,
                     username=usr.username,
                     is_blocked=False).execute()
        txt += "(#user{0}) {1}\n".format(usr.id,
                                         usr.first_name)
        app.send_message(chat_id=usr.id,
                         text="You have been unblocked.")

    msg.reply(text="Unblocked users:\n" + txt,
              disable_notification=False)


@app.on_message(pyrogram.Filters.command(command="start", prefix=["/", "!", "#", "."]))
def CMDStart(client: pyrogram.Client,
             msg: pyrogram.Message):
    if msg.from_user.id == master.id:
        msg.reply(text="""<code>/start</code> Shows this message

<code>/getlast</code> Sends last user's details
<b>Alternatives</b>: <code>/getlastuser</code>, <code>/lastuser</code>

<code>/block \{reply\}|\{users\}</code> Blocks the specified user(s)

<code>/unblock \{reply\}|\{users\}</code> Unblocks the specified user(s)""",
                  disable_notification=False,
                  parse_mode=pyrogram.ParseMode.HTML)
    else:
        msg.reply(text="Hi, use this bot to talk to {0} {1}, @{2} ({3})".format(master.first_name,
                                                                                master.last_name,
                                                                                master.username,
                                                                                master.id),
                  disable_notification=False)


@app.on_message()
def BasicHandler(client: pyrogram.Client,
                 msg: pyrogram.Message):
    global last_user
    if msg.from_user.id == master.id:
        if msg.reply_to_message:
            if msg.reply_to_message.forward_from:
                last_user = msg.reply_to_message.forward_from
            elif msg.reply_to_message.text.find("(#user") != -1:
                last_user = app.get_chat(chat_id=int(msg.reply_to_message.text[msg.reply_to_message.text.find(
                    "(#user") + 6: msg.reply_to_message.text.find(")")]))
        if last_user:
            msg.forward(chat_id=last_user.id,
                        disable_notification=False)
        else:
            msg.reply(text="Need to have last_user OR to reply to a forwarded message OR to reply to a message with the #user hashtag!",
                      disable_notification=False)
    else:
        msg.forward(chat_id=master.id,
                    disable_notification=False)
        app.send_message(chat_id=master.id,
                         text="↑ (#user{0}) {1} ↑".format(msg.from_user.id,
                                                          msg.from_user.first_name),
                         disable_notification=True)
        if msg.text == "/start":
            msg.reply(text="Hi, use this bot to talk to {0} {1}, @{2} ({3})".format(master.first_name,
                                                                                    master.last_name,
                                                                                    master.username,
                                                                                    master.id),
                      disable_notification=False)


app.idle()
