import math
import os
import platform

import pyrogram
from pykeyboard import InlineKeyboard

import utils


def BuildPager(page: int, n_items: int, max_items_keyboard: int) -> list:
    """
    Use this method to create the pager on the bottom of the keyboards.

    page (``int``): Current page you are on.

    n_items (``int``): Number of items to put in the keyboard.

    max_items_keyboard (``int``): Maximum number of items to put in the keyboard per page.


    SUCCESS Returns ``list`` of buttons to append to a keyboard that needs it.
    """
    page = int(page)
    n_items = int(n_items)
    max_items_keyboard = int(max_items_keyboard)
    pager = list()
    if n_items > max_items_keyboard:
        if page - 2 >= 0:
            # goto first
            pager.append(
                pyrogram.types.InlineKeyboardButton(
                    pyrogram.emoji.LAST_TRACK_BUTTON, callback_data=f"FMpages{page}<<"
                )
            )
        if page - 1 >= 0:
            # previous page
            pager.append(
                pyrogram.types.InlineKeyboardButton(
                    pyrogram.emoji.REVERSE_BUTTON, callback_data=f"FMpages{page}-"
                )
            )
        # select page button
        pager.append(
            pyrogram.types.InlineKeyboardButton(
                f"{page + 1}/{math.ceil(n_items / max_items_keyboard)}",
                callback_data="FMpages",
            )
        )
        if page + 1 < math.ceil(n_items / max_items_keyboard):
            # next page
            pager.append(
                pyrogram.types.InlineKeyboardButton(
                    pyrogram.emoji.PLAY_BUTTON, callback_data=f"FMpages{page}+"
                )
            )
        if page + 2 < math.ceil(n_items / max_items_keyboard):
            # goto last
            pager.append(
                pyrogram.types.InlineKeyboardButton(
                    pyrogram.emoji.NEXT_TRACK_BUTTON, callback_data=f"FMpages{page}>>"
                )
            )
    return pager


# TODO PAGINATION
def BuildItemsKeyboard(
    path: str, page: int = 0, max_columns: int = 2, max_rows: int = 8
) -> InlineKeyboard:
    """
    Use this method to process items of the folder in order to create a keyboard.

    path (``str``): Pass the path you want to build the keyboard on.

    page (``int``): Pass the page you want to be on.

    max_columns (``int``, *optional*, default = 2): Pass the maximum number of columns(buttons) to insert per keyboard(row) (1 to 8).

    max_rows (``int``, *optional*, default = 8): Pass the maximum number of rows to insert per keyboard (6 to 100).


    SUCCESS Returns ``InlineKeyboard`` of items and other useful buttons.

    FAILURE Returns an error (``str``).
    """
    path = str(path) if path else "/"
    page = int(page)
    max_rows = int(max_rows)
    max_columns = int(max_columns)
    # adjust the maximum number of columns(buttons) per keyboard(row) if out of bounds
    if max_columns < 1 or max_columns > 8:
        max_columns = 2
    # adjust the maximum number of rows per keyboard if out of bounds
    if max_rows < 6 or max_rows > 100:
        max_rows = 8
    max_items_keyboard = max_rows * max_columns
    if platform.system() == "Windows" and path == "/":
        # Windows root(s)
        path = ""
        items = utils.GetDrives()
    else:
        # Linux or Mac or other folder
        try:
            items = os.listdir(path)
        except Exception:
            items = list()

    keyboard = InlineKeyboard()
    if path:
        if items:
            keyboard.row(
                pyrogram.types.InlineKeyboardButton(
                    text=f"{pyrogram.emoji.OPEN_FILE_FOLDER} .",
                    callback_data=("FMcd."),
                ),
                pyrogram.types.InlineKeyboardButton(
                    text=f"{pyrogram.emoji.OPEN_FILE_FOLDER} ..",
                    callback_data=("FMcd.."),
                ),
                pyrogram.types.InlineKeyboardButton(
                    text=f"{pyrogram.emoji.OPEN_FILE_FOLDER} {pyrogram.emoji.DOWN_ARROW}",
                    callback_data=("FMul."),
                ),
            )
        else:
            keyboard.row(
                pyrogram.types.InlineKeyboardButton(
                    text=f"{pyrogram.emoji.OPEN_FILE_FOLDER} .",
                    callback_data=("FMcd."),
                ),
                pyrogram.types.InlineKeyboardButton(
                    text=f"{pyrogram.emoji.OPEN_FILE_FOLDER} ..",
                    callback_data=("FMcd.."),
                ),
            )

    tmp = list()
    for i, item in enumerate(sorted(items)):
        if i >= page * max_items_keyboard:
            if len(keyboard[-1]) >= max_columns:
                # max_columns buttons per line, then add another row
                keyboard.row(*tmp)
                tmp = list()
            tmp_path = os.path.abspath(os.path.join(path, item))
            if os.path.isfile(tmp_path):
                tmp.append(
                    pyrogram.types.InlineKeyboardButton(
                        text=pyrogram.emoji.PAGE_FACING_UP + f" {item}",
                        callback_data=f"FMul{i}",
                    )
                )
            elif os.path.isdir(tmp_path):
                tmp.append(
                    pyrogram.types.InlineKeyboardButton(
                        text=pyrogram.emoji.OPEN_FILE_FOLDER + f" {item}",
                        callback_data=f"FMcd{i}",
                    )
                )
            else:
                tmp.append(
                    pyrogram.types.InlineKeyboardButton(
                        text=pyrogram.emoji.QUESTION_MARK + f" {item}",
                        callback_data=f"FM{i}" if path else f"FMcddrive{i}",
                    )
                )
            if sum(len(row) for row in keyboard.inline_keyboard) >= max_items_keyboard:
                break

    keyboard.row(BuildPager(page, len(items), max_items_keyboard))
    return keyboard
