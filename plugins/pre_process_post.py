import datetime
import time

import pyrogram

import db_management


@pyrogram.Client.on_message(pyrogram.filters.private, group=-2)
def PreProcessMessage(client: pyrogram.Client, msg: pyrogram.types.Message):
    # as this is the first handler of this type, if the db is locked wait
    while db_management.DB.is_stopped():
        time.sleep(1)
    if db_management.Users.get_or_none(id=msg.from_user.id):
        db_management.Users.update(
            first_name=msg.from_user.first_name if msg.from_user.first_name else "",
            last_name=msg.from_user.last_name,
            username=msg.from_user.username,
            timestamp=datetime.datetime.utcnow(),
        ).where(db_management.Users.id == msg.from_user.id).execute()
    else:
        db_management.Users.create(
            id=msg.from_user.id,
            first_name=msg.from_user.first_name if msg.from_user.first_name else "",
            last_name=msg.from_user.last_name,
            username=msg.from_user.username,
        )

    if db_management.Users.get_or_none(id=msg.from_user.id).is_blocked:
        # do not process messages for blocked users
        msg.stop_propagation()
