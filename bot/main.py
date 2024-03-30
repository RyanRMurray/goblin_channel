import discord
from discord.ext.commands import Context 
from discord import Message
from discord import app_commands
from discord.abc import GuildChannel
from enum import Enum
import re
import os
import json
from typing import Set
import random

MATCH = re.compile(r'^".+" - .+')

class Status(Enum):
    STARTING = 1
    RECORDING = 2
    READY = 3

class Settings():
    guild: discord.Object
    target_channel_id: int
    bot_token: str

STATUS = Status.STARTING
QUOTE_IDS: Set[int] = set()

if not os.path.isfile("./settings.json"):
    print("Error: missing settings.json")
    exit(1)

settings = Settings()
with open("./settings.json") as f:
    j = json.load(f)
    settings.target_channel_id = int(j["target_channel_id"])
    settings.guild = discord.Object(id=int(j["guild_id"]))
    settings.bot_token = j["bot_token"]

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(
        name="record",
        description='Record all quotes in channel. Quotes defined as any message like "hilarious quip" - some guy',
        guild=settings.guild
)
async def record_channel(ctx: Context):
    if ctx.channel.id != settings.target_channel_id:
        await ctx.response.send_message("this isnt the target channel >:(")
        return

    if STATUS == Status.RECORDING:
        await ctx.response.send_message("bro im literally busy. (already recording messages)")
        return
    
    new_messages = 0
    message: Message
    messages = [m async for m in ctx.channel.history(limit=None)]
    for message in messages:
        if message.id in QUOTE_IDS:
            continue
        if message.author.bot:
            continue
        
        print(str(message) + ": " + message.content)
        re_match = re.fullmatch(MATCH, message.content)
        if re_match is None:
            continue

        QUOTE_IDS.add(message.id)
        new_messages += 1
    
    await ctx.response.send_message(f"Recorded {new_messages} quotes. Total is now {len(QUOTE_IDS)} :)")

@tree.command(
        name="quote",
        description="pick a random quote and post it",
        guild=settings.guild
)
async def quote(ctx: Context):
    channel = client.get_channel(settings.target_channel_id)
    
    message = None
    while message is None:
        if len(QUOTE_IDS) == 0:
            await ctx.response.send_message("No valid quotes recorded :(")
            return

        id = random.choice(tuple(QUOTE_IDS))
        try:
            message = await channel.fetch_message(id)
        except Exception as e:
            print(f"Error: {str(e)}")
            QUOTE_IDS.remove(id)
            message = None
    
    await ctx.response.send_message(message.content)
        

@client.event
async def on_ready():
    await tree.sync(guild=settings.guild)
    print(f"logged in as {client.user}")
    
client.run(settings.bot_token)