import json
import math
import os
import pathlib
import re
import shutil
import sys
import time

import keyboards
import pyrogram
import utils


@pyrogram.Client.on_callback_query(
    pyrogram.filters.user(utils.config["master"]) & pyrogram.filters.regex(r"^FMcd\.")
)
def CbQryUpdateFolder(client: pyrogram.Client, cb_qry: pyrogram.types.CallbackQuery):
    cb_qry.answer(text="Updating folder...")
    cb_qry.edit_message_text(
        text="Path: " + utils.config["file_manager"]["path"],
        reply_markup=keyboards.BuildItemsKeyboard(
            path=utils.config["file_manager"]["path"],
            page=utils.config["file_manager"]["page"],
            max_columns=utils.config["file_manager"]["max_columns"],
            max_rows=utils.config["file_manager"]["max_rows"],
        ),
    )


@pyrogram.Client.on_callback_query(
    pyrogram.filters.user(utils.config["master"]) & pyrogram.filters.regex(r"^FMcd\.\.")
)
def CbQryPreviousFolder(client: pyrogram.Client, cb_qry: pyrogram.types.CallbackQuery):
    if utils.config["file_manager"]["path"][1:].endswith(":\\"):
        utils.config["file_manager"]["path"] = "/"
    else:
        utils.config["file_manager"]["path"] = str(
            pathlib.Path(utils.config["file_manager"]["path"]).parent
        )
    utils.config["file_manager"]["page"] = 0

    cb_qry.answer(text="Moving to " + utils.config["file_manager"]["path"])
    cb_qry.edit_message_text(
        text="Path: " + utils.config["file_manager"]["path"],
        reply_markup=keyboards.BuildItemsKeyboard(
            path=utils.config["file_manager"]["path"],
            page=utils.config["file_manager"]["page"],
            max_columns=utils.config["file_manager"]["max_columns"],
            max_rows=utils.config["file_manager"]["max_rows"],
        ),
    )

    with open(file="utils.config.json", mode="w", encoding="utf-8") as f:
        json.dump(utils.config, f, indent=4)


@pyrogram.Client.on_callback_query(
    pyrogram.filters.user(utils.config["master"])
    & utils.filter_callback_regex(r"FMcddrive(.+)", flags=re.I)
)
def CbQryCdDrive(client: pyrogram.Client, cb_qry: pyrogram.types.CallbackQuery):
    utils.config["file_manager"]["path"] = (
        utils.GetDrives()[int(cb_qry.data.replace("FMcddrive", ""))] + ":\\"
    )
    utils.config["file_manager"]["page"] = 0

    cb_qry.answer(text="Moving to drive " + utils.config["file_manager"]["path"])
    cb_qry.edit_message_text(
        text="Path: " + utils.config["file_manager"]["path"],
        reply_markup=keyboards.BuildItemsKeyboard(
            path=utils.config["file_manager"]["path"],
            page=utils.config["file_manager"]["page"],
            max_columns=utils.config["file_manager"]["max_columns"],
            max_rows=utils.config["file_manager"]["max_rows"],
        ),
    )

    with open(file="utils.config.json", mode="w", encoding="utf-8") as f:
        json.dump(utils.config, f, indent=4)


@pyrogram.Client.on_callback_query(
    pyrogram.filters.user(utils.config["master"])
    & utils.filter_callback_regex(r"FMcd(\d+)", flags=re.I)
)
def CbQryCdFolder(client: pyrogram.Client, cb_qry: pyrogram.types.CallbackQuery):
    i = int(cb_qry.data.replace("FMcd", ""))
    folder = sorted(os.listdir(utils.config["file_manager"]["path"]))[i]
    utils.config["file_manager"]["path"] = os.path.abspath(
        os.path.join(utils.config["file_manager"]["path"], folder)
    )
    utils.config["file_manager"]["page"] = 0

    cb_qry.answer(text="Moving to " + utils.config["file_manager"]["path"])
    cb_qry.edit_message_text(
        text="Path: " + utils.config["file_manager"]["path"],
        reply_markup=keyboards.BuildItemsKeyboard(
            path=utils.config["file_manager"]["path"],
            page=utils.config["file_manager"]["page"],
            max_columns=utils.config["file_manager"]["max_columns"],
            max_rows=utils.config["file_manager"]["max_rows"],
        ),
    )

    with open(file="utils.config.json", mode="w", encoding="utf-8") as f:
        json.dump(utils.config, f, indent=4)


@pyrogram.Client.on_callback_query(
    pyrogram.filters.user(utils.config["master"])
    & utils.filter_callback_regex(r"FMpages(\d+)(<<|\-|\+|>>)", flags=re.I)
)
def CbQryPagesMove(client: pyrogram.Client, cb_qry: pyrogram.types.CallbackQuery):
    items = os.listdir(utils.config["file_manager"]["path"])
    if cb_qry.data.endswith("<<"):
        utils.config["file_manager"]["page"] = 0
    elif cb_qry.data.endswith("-"):
        utils.config["file_manager"]["page"] -= 1
    elif cb_qry.data.endswith("+"):
        utils.config["file_manager"]["page"] += 1
    elif cb_qry.data.endswith(">>"):
        utils.config["file_manager"]["page"] = (
            math.ceil(
                len(items)
                / (
                    utils.config["file_manager"]["max_columns"]
                    * utils.config["file_manager"]["max_rows"]
                )
            )
            - 1
        )

    cb_qry.answer(text="Turning page...")
    cb_qry.edit_message_reply_markup(
        reply_markup=keyboards.BuildItemsKeyboard(
            path=utils.config["file_manager"]["path"],
            page=utils.config["file_manager"]["page"],
            max_columns=utils.config["file_manager"]["max_columns"],
            max_rows=utils.config["file_manager"]["max_rows"],
        )
    )

    with open(file="utils.config.json", mode="w", encoding="utf-8") as f:
        json.dump(utils.config, f, indent=4)


@pyrogram.Client.on_callback_query(
    pyrogram.filters.user(utils.config["master"]) & pyrogram.filters.regex(r"^FMpages")
)
def CbQryPages(client: pyrogram.Client, cb_qry: pyrogram.types.CallbackQuery):
    cb_qry.answer(text="Useless button.")


@pyrogram.Client.on_callback_query(
    pyrogram.filters.user(utils.config["master"]) & pyrogram.filters.regex(r"^FMul\.")
)
def CbQryUlFolder(client: pyrogram.Client, cb_qry: pyrogram.types.CallbackQuery):
    zip_name = str(pathlib.Path(utils.config["file_manager"]["path"]).name)
    zip_name = f"./downloads/{zip_name}"
    cb_qry.answer(text=f"Zipping and uploading {zip_name}")
    try:
        shutil.make_archive(
            zip_name,
            "zip",
            root_dir=str(pathlib.Path(sys.argv[0]).parent),
            base_dir=utils.config["file_manager"]["path"],
        )

        tmpmsg: pyrogram.types.Message = cb_qry.message.reply_text(
            text="Uploading "
            + os.path.join(str(pathlib.Path(sys.argv[0]).parent), zip_name),
            quote=True,
        )
        cb_qry.message.reply_document(
            document=f"./{zip_name}.zip",
            progress=utils.DFromUToTelegramProgress,
            progress_args=(tmpmsg, tmpmsg.text, time.time()),
        )

        os.remove(zip_name + ".zip")
    except Exception as e:
        print(e)


@pyrogram.Client.on_callback_query(
    pyrogram.filters.user(utils.config["master"])
    & utils.filter_callback_regex(r"FMul(\d+)", flags=re.I)
)
def CbQryUlFile(client: pyrogram.Client, cb_qry: pyrogram.types.CallbackQuery):
    i = int(cb_qry.data.replace("FMul", ""))
    file_name = sorted(os.listdir(utils.config["file_manager"]["path"]))[i]

    cb_qry.answer(text=f"Uploading {file_name}")
    try:
        tmpmsg: pyrogram.types.Message = cb_qry.message.reply_text(
            text=f"Uploading {file_name}", quote=True
        )
        cb_qry.message.reply_document(
            document=os.path.abspath(
                os.path.join(utils.config["file_manager"]["path"], file_name)
            ),
            progress=utils.DFromUToTelegramProgress,
            progress_args=(tmpmsg, tmpmsg.text, time.time()),
        )
    except Exception as e:
        print(e)


@pyrogram.Client.on_message(
    pyrogram.filters.user(utils.config["master"])
    & pyrogram.filters.command("filemanager", prefixes=["/", "!", "#", "."])
)
def CmdFileManager(client: pyrogram.Client, msg: pyrogram.types.Message):
    msg.reply_text(
        text="Path: " + utils.config["file_manager"]["path"],
        reply_markup=keyboards.BuildItemsKeyboard(
            path=utils.config["file_manager"]["path"],
            page=utils.config["file_manager"]["page"],
            max_columns=utils.config["file_manager"]["max_columns"],
            max_rows=utils.config["file_manager"]["max_rows"],
        ),
    )
