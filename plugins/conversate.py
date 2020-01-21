import datetime

import pyrogram

import utils

last_user = None


@pyrogram.Client.on_message(
    pyrogram.Filters.chat(utils.config["master"])
    & pyrogram.Filters.command("getlast", prefixes=["/", "!", "#", "."])
)
def CmdGetLastUser(client: pyrogram.Client, msg: pyrogram.Message):
    global last_user
    msg.reply_text(
        text="[{0}] {1}, @{2} (#user{3})".format(
            datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"),
            last_user.first_name,
            last_user.username,
            last_user.id,
        ),
        disable_notification=False,
    )
    msg.stop_propagation()


@pyrogram.Client.on_message(
    pyrogram.Filters.chat(utils.config["master"])
    & pyrogram.Filters.command("test", prefixes=["/", "!", "#", "."])
)
def CmdTestChat(client: pyrogram.Client, msg: pyrogram.Message):
    chats_to_test = list()
    if msg.reply_to_message:
        if msg.reply_to_message.forward_from:
            chats_to_test.append(msg.reply_to_message.forward_from.id)
        elif msg.reply_to_message.text.find("(#user") != -1:
            chats_to_test.append(
                int(
                    msg.reply_to_message.text[
                        msg.reply_to_message.text.find("(#user")
                        + 6 : msg.reply_to_message.text.find(")")
                    ]
                )
            )
    else:
        msg.command.remove(msg.command[0])
        for cht in msg.command:
            chats_to_test.append(cht)

    txt = ""
    for cht in chats_to_test:
        try:
            client.send_chat_action(
                chat_id=cht if not utils.IsInt(cht) else int(cht), action="typing"
            )
            txt += f"Can write to {cht}\n"
        except pyrogram.errors.UserIsBlocked:
            txt += f"{cht} blocked me\n"
        except pyrogram.errors.PeerIdInvalid:
            txt += f"Cannot write to {cht}, never encountered.\n"
        except Exception as ex:
            txt += f"Cannot write to {cht} {ex}\n"

    msg.reply_text(text=txt, disable_notification=False)
    msg.stop_propagation()


@pyrogram.Client.on_message(
    pyrogram.Filters.user(utils.config["master"])
    & pyrogram.Filters.command(["start", "help"], prefixes=["/", "!", "#", "."])
)
def CmdStart_HelpMaster(client: pyrogram.Client, msg: pyrogram.Message):
    msg.reply_text(
        text="""<code>/start</code> Shows this message

<code>/test {reply_from}|{chats}</code> Tests the specified chat(s)

<code>/getlast</code> Sends last user's details

<code>/exec</code> Executes Python3 code

<code>/eval</code> Evaluates Python3 expression

<code>/backup</code> Makes and sends backup

<code>/reboot</code> Reboots bot

<code>/getip</code> Sends server's IP

<code>/block {reply_from}|{users}</code> Blocks the specified user(s)

<code>/unblock {reply_from}|{users}</code> Unblocks the specified user(s)""",
        disable_notification=False,
        parse_mode="html",
    )
    msg.stop_propagation()


@pyrogram.Client.on_message(
    pyrogram.Filters.user(utils.config["master"]) & pyrogram.Filters.private, group=1
)
def BasicHandlerMaster(client: pyrogram.Client, msg: pyrogram.Message):
    global last_user
    if msg.reply_to_message:
        if msg.reply_to_message.forward_from:
            last_user = msg.reply_to_message.forward_from
        elif msg.reply_to_message.text.find("(#user") != -1:
            last_user = client.get_chat(
                chat_id=int(
                    msg.reply_to_message.text[
                        msg.reply_to_message.text.find("(#user")
                        + 6 : msg.reply_to_message.text.find(")")
                    ]
                )
            )
    if last_user:
        try:
            msg.forward(chat_id=last_user.id, disable_notification=False)
            client.send_chat_action(chat_id=utils.config["master"], action="typing")
        except pyrogram.errors.UserIsBlocked:
            msg.reply_text(
                text=f"{last_user.id} blocked me.\n", disable_notification=False
            )
        except pyrogram.errors.PeerIdInvalid:
            msg.reply_text(
                text=f"Cannot write to {last_user.id}, never encountered.\n",
                disable_notification=False,
            )
        except Exception as ex:
            msg.reply_text(text=str(ex), disable_notification=False)
    else:
        msg.reply_text(
            text="Need to have last_user OR to reply to a forwarded message OR to reply to a message with the #user hashtag!",
            disable_notification=False,
        )


@pyrogram.Client.on_message(
    ~pyrogram.Filters.user(utils.config["master"])
    & pyrogram.Filters.command(["start", "help"], prefixes=["/", "!", "#", "."])
)
def CmdStart_HelpOthers(client: pyrogram.Client, msg: pyrogram.Message):
    msg.reply_text(
        text=f"Hi, use this bot to talk to {client.MASTER.first_name} {client.MASTER.last_name if client.MASTER.last_name else ''}, @{client.MASTER.username if client.MASTER.username else ''} ({client.MASTER.id})",
        disable_notification=False,
    )


@pyrogram.Client.on_message(
    ~pyrogram.Filters.user(utils.config["master"]) & pyrogram.Filters.private, group=1
)
def BasicHandlerOthers(client: pyrogram.Client, msg: pyrogram.Message):
    msg.forward(chat_id=utils.config["master"], disable_notification=False)
    client.send_message(
        chat_id=utils.config["master"],
        text=f"↑ (#user{msg.from_user.id}) {msg.from_user.first_name} ↑",
        disable_notification=True,
    )
    client.send_chat_action(chat_id=msg.from_user.id, action="typing")
