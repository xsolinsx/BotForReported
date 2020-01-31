import math
import os
import platform

import pyrogram

import utils


def BuildKeyboard(
    main_buttons: list, header_buttons: list = None, footer_buttons: list = None
) -> list:
    """
    Build a list that can be used for an inline keyboard.

    main_buttons (``list``): Main list of buttons.

    header_buttons (``list``, *optional*, default = None): Buttons to place on the top of the keyboard.

    footer_buttons (``list``, *optional*, default = None): Buttons to place on the bottom of the keyboard.


    SUCCESS Returns ``list`` of buttons.
    """
    menu = []
    if header_buttons:
        menu.extend(header_buttons)
    menu.extend(main_buttons)
    if footer_buttons:
        menu.extend(footer_buttons)

    return menu


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
        page_shift_row = list()
        if page - 2 >= 0:
            # goto first
            page_shift_row.append(
                pyrogram.InlineKeyboardButton(
                    pyrogram.Emoji.LAST_TRACK_BUTTON, callback_data=f"FMpages{page}<<"
                )
            )
        if page - 1 >= 0:
            # previous page
            page_shift_row.append(
                pyrogram.InlineKeyboardButton(
                    pyrogram.Emoji.REVERSE_BUTTON, callback_data=f"FMpages{page}-"
                )
            )
        # select page button
        page_shift_row.append(
            pyrogram.InlineKeyboardButton(
                f"{page + 1}/{math.ceil(n_items / max_items_keyboard)}",
                callback_data=f"FMpages",
            )
        )
        if page + 1 < math.ceil(n_items / max_items_keyboard):
            # next page
            page_shift_row.append(
                pyrogram.InlineKeyboardButton(
                    pyrogram.Emoji.PLAY_BUTTON, callback_data=f"FMpages{page}+"
                )
            )
        if page + 2 < math.ceil(n_items / max_items_keyboard):
            # goto last
            page_shift_row.append(
                pyrogram.InlineKeyboardButton(
                    pyrogram.Emoji.NEXT_TRACK_BUTTON, callback_data=f"FMpages{page}>>"
                )
            )
        pager.append(page_shift_row)
    return pager


def BuildItemsKeyboard(
    path: str, page: int = 0, max_columns: int = 2, max_rows: int = 8
):
    """
    Use this method to process items of the folder in order to create a keyboard.

    path (``str``): Pass the path you want to build the keyboard on.

    page (``int``): Pass the page you want to be on.

    max_columns (``int``, *optional*, default = 2): Pass the maximum number of columns(buttons) to insert per keyboard(row) (1 to 8).

    max_rows (``int``, *optional*, default = 8): Pass the maximum number of rows to insert per keyboard (6 to 100).


    SUCCESS Returns ``list`` of items and other useful buttons.

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
            items = []

    header = list()
    if path:
        if items:
            header.append(
                [
                    pyrogram.InlineKeyboardButton(
                        text=f"{pyrogram.Emoji.OPEN_FILE_FOLDER} .",
                        callback_data=("FMcd."),
                    ),
                    pyrogram.InlineKeyboardButton(
                        text=f"{pyrogram.Emoji.OPEN_FILE_FOLDER} ..",
                        callback_data=("FMcd.."),
                    ),
                    pyrogram.InlineKeyboardButton(
                        text=f"{pyrogram.Emoji.OPEN_FILE_FOLDER} {pyrogram.Emoji.DOWN_ARROW}",
                        callback_data=("FMul."),
                    ),
                ]
            )
        else:
            header.append(
                [
                    pyrogram.InlineKeyboardButton(
                        text=f"{pyrogram.Emoji.OPEN_FILE_FOLDER} .",
                        callback_data=("FMcd."),
                    ),
                    pyrogram.InlineKeyboardButton(
                        text=f"{pyrogram.Emoji.OPEN_FILE_FOLDER} ..",
                        callback_data=("FMcd.."),
                    ),
                ]
            )

    keyboard = [[]]
    for i, item in enumerate(sorted(items)):
        if i >= page * max_items_keyboard:
            if len(keyboard[-1]) >= max_columns:
                # max_columns buttons per line, then add another row
                keyboard.append([])
            tmp_path = os.path.abspath(os.path.join(path, item))
            if os.path.isfile(tmp_path):
                keyboard[-1].append(
                    pyrogram.InlineKeyboardButton(
                        text=pyrogram.Emoji.PAGE_FACING_UP + f" {item}",
                        callback_data=f"FMul{i}",
                    )
                )
            elif os.path.isdir(tmp_path):
                keyboard[-1].append(
                    pyrogram.InlineKeyboardButton(
                        text=pyrogram.Emoji.OPEN_FILE_FOLDER + f" {item}",
                        callback_data=f"FMcd{i}",
                    )
                )
            else:
                keyboard[-1].append(
                    pyrogram.InlineKeyboardButton(
                        text=pyrogram.Emoji.QUESTION_MARK + f" {item}",
                        callback_data=f"FM{i}" if path else f"FMcddrive{i}",
                    )
                )
            if sum(len(row) for row in keyboard) >= max_items_keyboard:
                break

    footer = BuildPager(page, len(items), max_items_keyboard)
    list_of_buttons = BuildKeyboard(
        main_buttons=keyboard, header_buttons=header, footer_buttons=footer
    )
    return list_of_buttons
