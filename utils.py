import glob
import json
import math
import os
import re
import shutil
import string
import tarfile
import time
import typing

import pyrogram

import db_management

config = None
with open(file="config.json", encoding="utf-8") as f:
    config = json.load(fp=f)


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


def PrintUser(user: typing.Union[pyrogram.Chat, pyrogram.User]) -> str:
    return (
        (user.first_name + (f" {user.last_name}" if user.last_name else ""))
        + " ("
        + (f"@{user.username} " if user.username else "")
        + f"#user{user.id})"
    )


def filter_callback_regex(pattern: str, flags=None):
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

    return pyrogram.Filters.create(f, regex=re.compile(pattern, flags), name="Regex")


def Backup() -> str:
    # empty downloads folder
    for filename in os.listdir("./downloads"):
        file_path = os.path.join("./downloads", filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as ex:
            print(f"Failed to delete {file_path}. Reason: {ex}")
    # remove previous backups
    for filename in glob.glob("./backupBotForReported*"):
        os.remove(filename)
    # compress db
    db_management.DB.execute_sql("VACUUM")
    db_management.DB.close()

    backup_name = f"backupBotForReported{int(time.time())}.tar.xz"
    with tarfile.open(backup_name, mode="w:xz") as f_tar_xz:
        for folderName, subfolders, filenames in os.walk("./"):
            if not folderName.startswith("./.git"):
                for filename in filenames:
                    if filename != backup_name and not (
                        filename.endswith(".session")
                        or filename.endswith(".session-journal")
                    ):
                        # exclude current backup and session files
                        filePath = os.path.join(folderName, filename)
                        f_tar_xz.add(filePath)

    db_management.DB.connect(reuse_if_open=True)
    return backup_name


def SendBackup(client: pyrogram.Client):
    tmp_msg = client.send_message(
        chat_id=config["master"],
        text="I am preparing the automatic backup.",
        disable_notification=True,
    )

    backup_name = Backup()

    client.send_document(
        chat_id=config["master"],
        document=backup_name,
        disable_notification=True,
        progress=DFromUToTelegramProgress,
        progress_args=(tmp_msg, "I am sending the automatic backup.", time.time()),
    )


def GetDrives():
    return [drive for drive in string.ascii_uppercase if os.path.exists(drive + ":\\")]


def SizeFormatter(b: int, human_readable: bool = False) -> str:
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
            return f"{B} B"
        elif KB <= B < MB:
            return f"{B/KB:.2f} KB"
        elif MB <= B < GB:
            return f"{B/MB:.2f} MB"
        elif GB <= B < TB:
            return f"{B/GB:.2f} GB"
        elif TB <= B:
            return f"{B/TB:.2f} TB"
    else:
        B, b = divmod(int(b), 8)
        KB, B = divmod(B, 1024)
        MB, KB = divmod(KB, 1024)
        GB, MB = divmod(MB, 1024)
        TB, GB = divmod(GB, 1024)
        tmp = (
            ((f"{TB}TB, ") if TB else "")
            + ((f"{GB}GB, ") if GB else "")
            + ((f"{MB}MB, ") if MB else "")
            + ((f"{KB}KB, ") if KB else "")
            + ((f"{B}B, ") if B else "")
            + ((f"{b}b, ") if b else "")
        )
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
    tmp = (
        ((f"{days}d, ") if days else "")
        + ((f"{hours}h, ") if hours else "")
        + ((f"{minutes}m, ") if minutes else "")
        + ((f"{seconds}s, ") if seconds else "")
        + ((f"{milliseconds}ms, ") if milliseconds else "")
    )
    return tmp[:-2]


def DFromUToTelegramProgress(
    current: int, total: int, msg: pyrogram.Message, text: str, start: float
) -> None:
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
        progress = "[{0}{1}] {2}%\n".format(
            "".join(["█" for i in range(math.floor(percentage / 5))]),
            "".join(["░" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
        )
        tmp = progress + "{0}/{1}\n{2}/s {3}/{4}\n".format(
            SizeFormatter(b=current * 8, human_readable=True),
            SizeFormatter(b=total * 8, human_readable=True),
            SizeFormatter(b=speed * 8, human_readable=True),
            elapsed_time if elapsed_time != "" else "0 s",
            estimated_total_time if estimated_total_time != "" else "0 s",
        )

        msg.edit(text=text + tmp)
