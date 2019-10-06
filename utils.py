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
