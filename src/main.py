import discord
from discord.ext.commands import Context 
from discord import Message, app_commands
from bot import GoblinBot
from sys import argv
from pathlib import Path

from settings import load_settings

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

SETTINGS = load_settings(Path(argv[1]))
CLIENT = discord.Client(intents=intents)
TREE = app_commands.CommandTree(CLIENT)
BOT = GoblinBot(SETTINGS)

@CLIENT.event
async def on_ready():
    print(f"logged in as {CLIENT.user}")
    await TREE.sync(guild=SETTINGS.guild)
    await BOT.initialise_quote_db(CLIENT)
    print(f"Loaded {len(BOT.quote_ids)} quote IDs")

@CLIENT.event
async def on_message(message: Message):
    print(message.content)
    await BOT.process_msg(message)

@TREE.command(
        name="quote",
        description="pick a random quote and post it",
        guild=SETTINGS.guild
)
async def quote(ctx: Context):
    msg = await BOT.get_quote(CLIENT)
    await ctx.response.send_message(msg)
        
CLIENT.run(SETTINGS.bot_token)
