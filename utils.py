import math
import os
import pathlib
import platform
import re
import string
import time

import pyrogram


def IsInt(v) -> bool:
    """
    Check if the parameter can be int.

    v: Variable to check.


    SUCCESS Returns ``True``.

    FAILURE Returns ``False``.
    """
    try:
        int(v)
        return True
    except Exception as ex:
        print(ex)
        return False


def ExtractMedia(msg: pyrogram.Message) -> object:
    """Extract the media from a :obj:`Message <pyrogram.Message>`.

    msg (:obj:`Message <pyrogram.Message>`): Message from which you want to extract the media


    SUCCESS Returns the media (``object``).

    FAILURE Returns ``None``.
    """
    media = None
    if msg:
        if msg.media:
            if msg.animation:
                media = msg.animation
            elif msg.audio:
                media = msg.audio
            elif msg.document:
                media = msg.document
            elif msg.photo:
                media = msg.photo
            elif msg.sticker:
                media = msg.sticker
            elif msg.video:
                media = msg.video
            elif msg.video_note:
                media = msg.video_note
            elif msg.voice:
                media = msg.voice

    return media

# region keyboards


def BuildKeyboard(main_buttons: list,
                  header_buttons: list = None,
                  footer_buttons: list = None) -> list:
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


def BuildPager(page: int,
               n_items: int,
               max_items_keyboard: int) -> list:
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
            page_shift_row.append(pyrogram.InlineKeyboardButton(pyrogram.Emoji.LAST_TRACK_BUTTON,
                                                                callback_data=f"FMpages{page}<<"))
        if page - 1 >= 0:
            # previous page
            page_shift_row.append(pyrogram.InlineKeyboardButton(pyrogram.Emoji.REVERSE_BUTTON,
                                                                callback_data=f"FMpages{page}-"))
        # select page button
        page_shift_row.append(pyrogram.InlineKeyboardButton(str(page + 1) + "/" + str(math.ceil(n_items / max_items_keyboard)),
                                                            callback_data=f"FMpages"))
        if page + 1 < math.ceil(n_items / max_items_keyboard):
            # next page
            page_shift_row.append(pyrogram.InlineKeyboardButton(pyrogram.Emoji.PLAY_BUTTON,
                                                                callback_data=f"FMpages{page}+"))
        if page + 2 < math.ceil(n_items / max_items_keyboard):
            # goto last
            page_shift_row.append(pyrogram.InlineKeyboardButton(pyrogram.Emoji.NEXT_TRACK_BUTTON,
                                                                callback_data=f"FMpages{page}>>"))
        pager.append(page_shift_row)
    return pager


def BuildItemsKeyboard(path: str,
                       page: int = 0,
                       max_columns: int = 2,
                       max_rows: int = 8):
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
        items = GetDrives()
    else:
        # Linux or Mac or other folder
        try:
            items = os.listdir(path)
        except Exception as ex:
            items = []

    header = list()
    if path:
        if items:
            header.append([pyrogram.InlineKeyboardButton(text=f"{pyrogram.Emoji.OPEN_FILE_FOLDER} .",
                                                         callback_data=("FMcd.")),
                           pyrogram.InlineKeyboardButton(text=f"{pyrogram.Emoji.OPEN_FILE_FOLDER} ..",
                                                         callback_data=("FMcd..")),
                           pyrogram.InlineKeyboardButton(text=f"{pyrogram.Emoji.OPEN_FILE_FOLDER} {pyrogram.Emoji.DOWN_ARROW}",
                                                         callback_data=("FMul."))])
        else:
            header.append([pyrogram.InlineKeyboardButton(text=f"{pyrogram.Emoji.OPEN_FILE_FOLDER} .",
                                                         callback_data=("FMcd.")),
                           pyrogram.InlineKeyboardButton(text=f"{pyrogram.Emoji.OPEN_FILE_FOLDER} ..",
                                                         callback_data=("FMcd.."))])

    keyboard = [[]]
    for i, item in enumerate(items):
        if i + 1 > page * max_items_keyboard:
            if len(keyboard[-1]) >= max_columns:
                # max_columns buttons per line, then add another row
                keyboard.append([])
            tmp_path = os.path.abspath(os.path.join(path, item))
            if os.path.isfile(os.path.abspath(os.path.join(path, item))):
                keyboard[-1].append(pyrogram.InlineKeyboardButton(text=pyrogram.Emoji.PAGE_FACING_UP + f" {item}",
                                                                  callback_data=f"FMul{i}"))
            elif os.path.isdir(os.path.abspath(os.path.join(path, item))):
                keyboard[-1].append(pyrogram.InlineKeyboardButton(text=pyrogram.Emoji.OPEN_FILE_FOLDER + f" {item}",
                                                                  callback_data=f"FMcd{i}"))
            else:
                keyboard[-1].append(pyrogram.InlineKeyboardButton(text=pyrogram.Emoji.QUESTION_MARK + f" {item}",
                                                                  callback_data=f"FM{i}" if path else f"FMcddrive{i}"))
            if sum([len(row) for row in keyboard]) >= max_items_keyboard:
                break

    footer = BuildPager(page,
                        len(items),
                        max_items_keyboard)
    list_of_buttons = BuildKeyboard(main_buttons=keyboard,
                                    header_buttons=header,
                                    footer_buttons=footer)
    return list_of_buttons

# endregion


def filter_callback_regex(pattern: str,
                          flags=None):
    """Filter messages that match a given RegEx pattern.

    Args:
        pattern (``str``):
            The RegEx pattern as string, it will be applied to the text of a message. When a pattern matches,
            all the `Match Objects <https://docs.python.org/3/library/re.html#match-objects>`_
            are stored in the *matches* field of the :class:`Message <pyrogram.Message>` itself.

        flags (``int``, *optional*):
            RegEx flags.
    """

    def f(filter_, callback_query):
        matches = [i for i in filter_.regex.finditer(callback_query.data)]
        return bool(matches)

    return pyrogram.Filters.create(f,
                                   regex=re.compile(pattern,
                                                    flags),
                                   name="Regex")

# region manage paths


def rreplace(s: str,
             old: str,
             new: str) -> str:
    li = s.rsplit(old, 1)
    # Split only once
    return new.join(li)


def GetLastPartOfPath(path: str) -> str:
    return os.path.basename(os.path.normpath(path))


def GetAbsolutePath(s: str,
                    currentAbsPath: str = "/") -> str:
    """
    Adjust the path that is passed as first parameter.

    s (``str``): "." (Indicates the same folder of the currentAbsPath) OR ".." (Indicates the previous folder of currentAbsPath) OR "this/is/a/relative/path" OR "/this/is/an/absolute/path".

    currentAbsPath (``str``, *optional*, default = "/"): If s is "." this parameter is the path returned OR If s is ".." this parameter is the path returned without the last folder OR If s is a relative path it is concatenated with this parameter OR If s is an absolute path this parameter is useless.


    SUCCESS Returns the absolute path (``str``).
    """
    path = None
    if s == ".":
        # same folder
        path = currentAbsPath
    elif s == "..":
        # previous folder
        s.replace("..", "")
        path = str(pathlib.Path(currentAbsPath).parent)
    elif s == "/":
        # root folder
        path = s
    elif os.path.isabs(s):
        # absolute path
        pieces = s.split("/")
        # split the path in order to find possible ".." or "."
        currentAbsPath = "/"
        for piece in pieces:
            if piece == ".":
                # ignore
                pass
            elif piece == "..":
                # previous folder
                currentAbsPath = str(pathlib.Path(currentAbsPath).parent)
            else:
                currentAbsPath += ("/" if not currentAbsPath.endswith("/")
                                   else "") + piece
        path = currentAbsPath
    else:
        # relative path
        pieces = s.split("/")
        # split the path in order to find possible ".." or "."
        for piece in pieces:
            if piece == ".":
                # ignore
                pass
            elif piece == "..":
                # previous folder
                currentAbsPath = str(pathlib.Path(currentAbsPath).parent)
            else:
                currentAbsPath += ("/" if not currentAbsPath.endswith("/")
                                   else "") + piece
        path = currentAbsPath
    return path


def GetDrives():
    return [drive for drive in string.ascii_uppercase if os.path.exists(drive + ":\\")]

# endregion

# region file upload/download


def SizeFormatter(b: int,
                  human_readable: bool = False) -> str:
    """
    Adjust the size from biys to the right measure.

    b (``int``): Number of bits.


    SUCCESS Returns the adjusted measure (``str``).
    """
    if human_readable:
        B = float(b / 8)
        KB = float(1024)
        MB = float(pow(KB, 2))
        GB = float(pow(KB, 3))
        TB = float(pow(KB, 4))

        if B < KB:
            return "{0} B".format(B)
        elif KB <= B < MB:
            return "{0:.2f} KB".format(B/KB)
        elif MB <= B < GB:
            return "{0:.2f} MB".format(B/MB)
        elif GB <= B < TB:
            return "{0:.2f} GB".format(B/GB)
        elif TB <= B:
            return "{0:.2f} TB".format(B/TB)
    else:
        B, b = divmod(int(b), 8)
        KB, B = divmod(B, 1024)
        MB, KB = divmod(KB, 1024)
        GB, MB = divmod(MB, 1024)
        TB, GB = divmod(GB, 1024)
        tmp = ((str(TB) + "TB, ") if TB > 0 else "") + \
            ((str(GB) + "GB, ") if GB > 0 else "") + \
            ((str(MB) + "MB, ") if MB > 0 else "") + \
            ((str(KB) + "KB, ") if KB > 0 else "") + \
            ((str(B) + "B, ") if B > 0 else "") + \
            ((str(b) + "b, ") if b > 0 else "")
        return tmp[:-2]


def TimeFormatter(milliseconds: int) -> str:
    """
    Adjust the time from milliseconds to the right measure.

    milliseconds (``int``): Number of milliseconds.


    SUCCESS Returns the adjusted measure (``str``).
    """
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days > 0 else "") + \
        ((str(hours) + "h, ") if hours > 0 else "") + \
        ((str(minutes) + "m, ") if minutes > 0 else "") + \
        ((str(seconds) + "s, ") if seconds > 0 else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds > 0 else "")
    return tmp[:-2]


def DFromUToTelegramProgress(current: int,
                             total: int,
                             msg: pyrogram.Message,
                             text: str,
                             start: float) -> None:
    """
    Use this method to update the progress of a download from/an upload to Telegram, this method is called every 512KB.
    Update message every ~4 seconds.

    client (:class:`Client <pyrogram.Client>`): The Client itself.

    current (``int``): Currently downloaded/uploaded bytes.

    total (``int``): File size in bytes.

    msg (:class:`Message <pyrogram.Message>`): The Message to update while downloading/uploading the file.

    text (``str``): Text to put into the update.

    start (``str``): Time when the operation started.


    Returns ``None``.
    """
    # 1048576 is 1 MB in bytes
    now = time.time()
    diff = now - start
    if round(diff % 4.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
        # 0% = [░░░░░░░░░░░░░░░░░░░░]
        # 100% = [████████████████████]
        progress = "[{0}{1}] {2}%\n".format(''.join(["█" for i in range(math.floor(percentage / 5))]),
                                            ''.join(
                                                ["░" for i in range(20 - math.floor(percentage / 5))]),
                                            round(percentage, 2))
        tmp = progress + "{0}/{1}\n{2}/s {3}/{4}\n".format(SizeFormatter(b=current * 8,
                                                                         human_readable=True),
                                                           SizeFormatter(b=total * 8,
                                                                         human_readable=True),
                                                           SizeFormatter(b=speed * 8,
                                                                         human_readable=True),
                                                           elapsed_time if elapsed_time != '' else "0 s",
                                                           estimated_total_time if estimated_total_time != '' else "0 s")

        msg.edit(text=text + tmp)

# endregion
