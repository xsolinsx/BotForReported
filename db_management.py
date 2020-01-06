import datetime
import json
import logging

import peewee
from playhouse.sqliteq import SqliteQueueDatabase

DB = None
local_config = None
with open(file="config.json", encoding="utf-8") as f:
    local_config = json.load(fp=f)

if not local_config:
    logging.log(logging.FATAL, "Missing config.json")
    exit()

DB = SqliteQueueDatabase(
    database=local_config["database"],
    pragmas=[
        ("foreign_keys", 1),
        ("journal_mode", "wal"),
        ("ignore_check_constraints", 0),
        ("synchronous", "normal"),
    ],
)


class Users(peewee.Model):
    id = peewee.IntegerField(
        primary_key=True, constraints=[peewee.Check(constraint="id > 0")]
    )

    first_name = peewee.CharField(max_length=255)
    last_name = peewee.CharField(max_length=255, default=None, null=True)
    username = peewee.CharField(max_length=32, default=None, null=True)
    timestamp = peewee.DateTimeField(default=datetime.datetime.utcnow, null=False)
    # prevent forwards to master
    is_blocked = peewee.BooleanField(
        default=False,
        null=False,
        constraints=[peewee.Check(constraint="is_blocked == 0 OR is_blocked == 1")],
    )

    class Meta:
        database = DB


DB.create_tables(models=[Users], safe=True)
DB.close()
DB.connect()
