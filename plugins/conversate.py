import pyrogram
import utils


@pyrogram.Client.on_message(
    pyrogram.filters.chat(utils.config["master"])
    & pyrogram.filters.command("test", prefixes=["/", "!", "#", "."])
)
def CmdTestChat(client: pyrogram.Client, msg: pyrogram.types.Message):
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
        chats_to_test = filter(utils.IsInt, msg.command)

    txt = ""
    for cht in chats_to_test:
        try:
            client.send_chat_action(
                chat_id=int(cht), action=pyrogram.enums.chat_action.ChatAction.TYPING
            )
            txt += f"Can write to {cht}\n"
        except pyrogram.errors.UserIsBlocked:
            txt += f"{cht} blocked me\n"
        except pyrogram.errors.PeerIdInvalid:
            txt += f"Cannot write to {cht}, never encountered.\n"
        except Exception as ex:
            txt += f"Cannot write to {cht} {ex}\n"

    msg.reply_text(text=txt, disable_notification=False)


@pyrogram.Client.on_message(
    pyrogram.filters.user(utils.config["master"])
    & pyrogram.filters.command(["start", "help"], prefixes=["/", "!", "#", "."])
)
def CmdStart_HelpMaster(client: pyrogram.Client, msg: pyrogram.types.Message):
    msg.reply_text(
        text="""<code>/start</code> Shows this message
<code>/test {reply_from}|{chats}</code> Tests the specified chat(s)
<code>/exec</code> Executes Python3 code
<code>/eval</code> Evaluates Python3 expression
<code>/backup</code> Makes and sends backup
<code>/reboot</code> Reboots bot
<code>/getip</code> Sends server's IP
<code>/block {reply_from}|{users}</code> Blocks the specified user(s)
<code>/unblock {reply_from}|{users}</code> Unblocks the specified user(s)
<code>/filemanager</code> Sends a file manager keyboard for the server""",
        disable_notification=False,
        parse_mode=pyrogram.enums.parse_mode.ParseMode.HTML,
    )


@pyrogram.Client.on_message(
    pyrogram.filters.user(utils.config["master"]) & pyrogram.filters.private, group=1
)
def BasicHandlerMaster(client: pyrogram.Client, msg: pyrogram.types.Message):
    # ignore commands
    if msg.text[0] not in ["/", "!", "#", "."]:
        if msg.reply_to_message and msg.reply_to_message.text.find("(#user") != -1:
            user_id = int(
                msg.reply_to_message.text[
                    msg.reply_to_message.text.find("(#user")
                    + 6 : msg.reply_to_message.text.find(")")
                ]
            )
            try:
                msg.forward(chat_id=user_id, disable_notification=False)
                client.send_chat_action(
                    chat_id=utils.config["master"],
                    action=pyrogram.enums.chat_action.ChatAction.TYPING,
                )
            except pyrogram.errors.UserIsBlocked:
                msg.reply_text(
                    text=f"{user_id} blocked me.\n", disable_notification=False
                )
            except pyrogram.errors.PeerIdInvalid:
                msg.reply_text(
                    text=f"Cannot write to {user_id}, never encountered.\n",
                    disable_notification=False,
                )
            except Exception as ex:
                msg.reply_text(text=str(ex), disable_notification=False)


@pyrogram.Client.on_message(
    ~pyrogram.filters.user(utils.config["master"])
    & pyrogram.filters.command(["start", "help"], prefixes=["/", "!", "#", "."])
)
def CmdStart_HelpOthers(client: pyrogram.Client, msg: pyrogram.types.Message):
    msg.reply_text(
        text=f"Hi, use this bot to talk to {client.MASTER.first_name} {client.MASTER.last_name if client.MASTER.last_name else ''}, @{client.MASTER.username if client.MASTER.username else ''} ({client.MASTER.id})",
        disable_notification=False,
    )


@pyrogram.Client.on_message(
    ~pyrogram.filters.user(utils.config["master"])
    & ~pyrogram.filters.me
    & pyrogram.filters.private,
    group=1,
)
def BasicHandlerOthers(client: pyrogram.Client, msg: pyrogram.types.Message):
    msg.forward(chat_id=utils.config["master"], disable_notification=False)
    client.send_message(
        chat_id=utils.config["master"],
        text=f"↑ (#user{msg.from_user.id}) {msg.from_user.first_name} ↑",
        disable_notification=True,
    )
    client.send_chat_action(
        chat_id=msg.from_user.id, action=pyrogram.enums.chat_action.ChatAction.TYPING
    )
