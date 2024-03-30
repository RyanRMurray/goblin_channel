import discord
import json
from pathlib import Path

class Settings:
    guild: discord.Object
    quote_channel_id: int
    bot_token: str

    def __init__(self, j):
        self.guild = discord.Object(j["guild_id"])
        self.quote_channel_id = int(j["quote_channel_id"])
        self.bot_token = j["bot_token"]


def load_settings(path: Path) -> Settings:
    if not path.is_file():
        raise Exception(f"File not found: {path}")
    
    j = None
    with open(path, "r") as f:
        j = json.load(f)
    
    return Settings(j)
