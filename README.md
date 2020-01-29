Telegram bot used as a proxy to chat with people.

### Features

- **Anti-Flood**: Prevent users to flood your bot with an automated system.
- **Blocking System**: Manual blocking of undesired users.
- **File-Manager**: Use a file-manager like keyboard to explore your server/vps and download/upload files.

### Requirements

- [Pyrogram](https://github.com/pyrogram/pyrogram).
- [Peewee](https://github.com/coleifer/peewee).
- A [Telegram API key](https://docs.pyrogram.org/intro/setup#api-keys).
- A [Bot API key](https://core.telegram.org/bots#6-botfather).

### Installing

Clone this repository.

Cd into it.

``` bash
pip3 install -r requirements.txt
```

Rename proto_config.json into config.json and update it with your data.

``` bash
python3 bot.py
```

### Copyright & License

- Copyright (C) 2020 Eric Solinas <<https://github.com/xsolinsx>>
- Licensed under the terms of the [MIT License](LICENSE)
