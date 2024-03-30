# goblin_channel
Pull messages from a target channel of the form `"[quote]" - [speaker]`. Only stores message IDs, not the messages themselves.

## Setup

Install python libraries
```bash
python3 -m pip install -U discord.py
```

Create a settings file using the `setting.json.example` file. 
- `guild_id` is the target server's ID
- `quote_channel_id` is the target server to source quotes from
- `bot_token` is the [Discord Bot's](https://discordpy.readthedocs.io/en/stable/discord.html) auth token.

# Running
Run with
```bash
python3 ./src/main.py [path to settings file]
```
