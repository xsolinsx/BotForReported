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
    except Exception as e:
        print(e)
        return False


def ExtractMedia(msg: pyrogram.Message,
                 bigger_photo: bool = True) -> object:
    """Extract the media from a :obj:`Message <pyrogram.Message>`.

    msg (:obj:`Message <pyrogram.Message>`): Message from which you want to extract the media

    bigger_photo (``bool``, *optional*, default = True): True if you want to extract the bigger photo OR False if you want the list of photo of different sizes (useful only with photos).


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
                if bigger_photo:
                    media = msg.photo.thumbnails[-1]
            elif msg.sticker:
                media = msg.sticker
            elif msg.video:
                media = msg.video
            elif msg.video_note:
                media = msg.video_note
            elif msg.voice:
                media = msg.voice

    return media
