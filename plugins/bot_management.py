import os
import secrets
import sys
import time
import urllib

import pyrogram

import db_management
import utils


@pyrogram.Client.on_message(
    pyrogram.Filters.user(utils.config["master"])
    & pyrogram.Filters.command("reboot", prefixes=["/", "!", "#", "."])
)
def CmdReboot(client: pyrogram.Client, msg: pyrogram.Message):
    python = sys.executable
    db_management.DB.close()
    os.execl(python, python, *sys.argv)


@pyrogram.Client.on_message(
    pyrogram.Filters.user(utils.config["master"])
    & pyrogram.Filters.command("getip", prefixes=["/", "!", "#", "."],)
)
def CmdGetIP(client: pyrogram.Client, msg: pyrogram.Message):
    ip = urllib.request.urlopen("https://ipecho.net/plain").read().decode("utf8")
    msg.reply_text(text=ip)


@pyrogram.Client.on_message(
    pyrogram.Filters.user(utils.config["master"])
    & pyrogram.Filters.command("backup", prefixes=["/", "!", "#", "."])
)
def CmdBackup(client: pyrogram.Client, msg: pyrogram.Message):
    utils.SendBackup(client=client)


@pyrogram.Client.on_message(
    pyrogram.Filters.user(utils.config["master"])
    & pyrogram.Filters.command("exec", prefixes=["/", "!", "#", "."])
)
def CmdExec(client: pyrogram.Client, msg: pyrogram.Message):
    expression = msg.text[len(msg.command[0]) + 2 :]

    if expression:
        text = None
        try:
            text = str(exec(expression, {"client": client, "msg": msg}))
        except Exception as error:
            text = str(error)

        if text:
            if len(text) > 4096:
                file_name = f"./downloads/message_too_long_{secrets.token_hex(5)}_{time.time()}.txt"
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(text)
                msg.reply_document(document=file_name)
                os.remove(file_name)
            else:
                msg.reply_text(text=text)


@pyrogram.Client.on_message(
    pyrogram.Filters.user(utils.config["master"])
    & pyrogram.Filters.command("eval", prefixes=["/", "!", "#", "."])
)
def CmdEval(client: pyrogram.Client, msg: pyrogram.Message):
    expression = msg.text[len(msg.command[0]) + 2 :]

    if expression:
        text = None
        try:
            text = str(eval(expression, {"client": client, "msg": msg}))
        except Exception as error:
            text = str(error)
        if text:
            if len(text) > 4096:
                file_name = f"./downloads/message_too_long_{secrets.token_hex(5)}_{time.time()}.txt"
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(text)
                msg.reply_document(document=file_name)
                os.remove(file_name)
            else:
                msg.reply_text(text=text)


@pyrogram.Client.on_message(
    pyrogram.Filters.chat(utils.config["master"])
    & pyrogram.Filters.command("block", prefixes=["/", "!", "#", "."])
)
def CMDBlock(client: pyrogram.Client, msg: pyrogram.Message):
    users_to_block = list()
    if msg.reply_to_message:
        if msg.reply_to_message.forward_from:
            users_to_block.append(msg.reply_to_message.forward_from)
        elif msg.reply_to_message.text.find("(#user") != -1:
            users_to_block.append(
                client.get_chat(
                    chat_id=int(
                        msg.reply_to_message.text[
                            msg.reply_to_message.text.find("(#user")
                            + 6 : msg.reply_to_message.text.find(")")
                        ]
                    )
                )
            )
    else:
        msg.command.remove(msg.command[0])
        for usr in msg.command:
            obj = client.get_chat(chat_id=usr)
            if isinstance(obj=obj, class_or_tuple=pyrogram.Users):
                users_to_block.append(obj)

    txt = ""
    for usr in users_to_block:
        db_management.Users.replace(
            id=usr.id,
            first_name=usr.first_name,
            last_name=usr.first_name,
            username=usr.username,
            is_blocked=True,
        ).execute()
        txt += f"(#user{usr.id}) {usr.first_name}\n"
        client.send_message(chat_id=usr.id, text="You have been blocked.")

    msg.reply_text(text=f"Blocked users:\n{txt}", disable_notification=False)


@pyrogram.Client.on_message(
    pyrogram.Filters.chat(utils.config["master"])
    & pyrogram.Filters.command("unblock", prefixes=["/", "!", "#", "."])
)
def CMDUnblock(client: pyrogram.Client, msg: pyrogram.Message):
    users_to_unblock = list()
    if msg.reply_to_message:
        if msg.reply_to_message.forward_from:
            users_to_unblock.append(msg.reply_to_message.forward_from)
        elif msg.reply_to_message.text.find("(#user") != -1:
            users_to_unblock.append(
                client.get_chat(
                    chat_id=int(
                        msg.reply_to_message.text[
                            msg.reply_to_message.text.find("(#user")
                            + 6 : msg.reply_to_message.text.find(")")
                        ]
                    )
                )
            )
    else:
        msg.command.remove(msg.command[0])
        for usr in msg.command:
            obj = client.get_chat(chat_id=usr)
            if isinstance(obj=obj, class_or_tuple=pyrogram.Users):
                users_to_unblock.append(obj)

    txt = ""
    for usr in users_to_unblock:
        db_management.Users.replace(
            id=usr.id,
            first_name=usr.first_name,
            last_name=usr.first_name,
            username=usr.username,
            is_blocked=False,
        ).execute()
        txt += f"(#user{usr.id}) {usr.first_name}\n"
        client.send_message(chat_id=usr.id, text="You have been unblocked.")

    msg.reply_text(text=f"Unblocked users:\n{txt}", disable_notification=False)
