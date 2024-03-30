from enum import Enum
from discord import Client, Message
from discord.ext.commands import Context 
from settings import Settings
from typing import Set
import random
import re

class Status(Enum):
    STARTING = 1
    RECORDING = 2
    READY = 3

MATCH = re.compile(r'^".+" - .+')

class GoblinBot():
    status: Status
    settings: Settings
    quote_ids: Set[int] = set()

    def __init__(self, settings: Settings):
        # load settings
        self.status = Status.STARTING
        self.settings = settings

    async def initialise_quote_db(self, client: Client):
        self.status = Status.RECORDING
        target_channel = client.get_channel(self.settings.quote_channel_id)

        for message in [m async for m in target_channel.history(limit=None)]:
            if message.author.bot:
                continue

            re_match = re.fullmatch(MATCH, message.content)
            if re_match is None:
                continue

            self.quote_ids.add(message.id)
        
        self.status = Status.READY

    async def get_quote(self, client: Client) -> str:
        if self.status != Status.READY:
            return "bro im literally busy. (currently recording messages)"
        
        target_channel = client.get_channel(self.settings.quote_channel_id)
        
        message = None
        while message is None:
            if len(self.quote_ids) == 0:
                return "No quotes recorded :("
            
            id = random.choice(tuple(self.quote_ids))

            try:
                message = await target_channel.fetch_message(id)
            except Exception as e:
                self.quote_ids.remove(id)
                print(f"Purged erroring ID {id}: {str(e)}")
                message = None
        
        return message.content

    async def process_msg(self, message: Message):
        if message.channel.id != self.settings.quote_channel_id:
            return 
        
        re_match = re.fullmatch(MATCH, message.content)
        if re_match is None:
            return
        
        self.quote_ids.add(message.id)
        print(f"Added quote ID {message.id}")
