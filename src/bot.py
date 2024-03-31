from asyncio import AbstractEventLoop, sleep, run_coroutine_threadsafe
from enum import Enum
from datetime import datetime, timedelta
from discord import Client, Message
from settings import Settings
from typing import Set, Optional
import random
import re
from threading import Thread

class Status(Enum):
    STARTING = 1
    RECORDING = 2
    READY = 3

MATCH = re.compile(r'^".+" - .+')

class GoblinBot():
    status: Status
    settings: Settings
    quote_ids: Set[int] = set()
    loop: Optional[AbstractEventLoop] = None
    daily_terminate_flag: bool = False
    daily_thread: Optional[Thread] = None

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

    async def daily_post(self, client: Client, channel_id: int, dt: datetime):
        next_time = dt
        while True:
            if self.daily_terminate_flag:
                return
            if datetime.now() >= next_time:
                ch = client.get_channel(channel_id)
                quote = await self.get_quote(client)
                await ch.send(f"Quote of the Day:\n{quote}")
                next_time += timedelta(days=1)
            else:
                await sleep(10)

    async def start_daily_post(self, client: Client, channel_id: int, dt: datetime):
        # kill any existing thread
        if self.daily_thread is not None:
            print("Killing daily thread")
            self.daily_terminate_flag = True
            self.daily_thread.join()
            self.daily_thread = None
            self.daily_terminate_flag = False
        
        self.daily_thread = Thread(target=run_coroutine_threadsafe, args=(self.daily_post(client, channel_id, dt),self.loop))
        self.daily_thread.start()
        print("Started daily thread")
