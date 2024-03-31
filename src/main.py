from asyncio import get_running_loop
import discord
from datetime import datetime, timedelta
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
    BOT.loop = get_running_loop()
    await BOT.initialise_quote_db(CLIENT)
    print(f"Loaded {len(BOT.quote_ids)} quote IDs")

@CLIENT.event
async def on_message(message: Message):
    await BOT.process_msg(message)

@TREE.command(
        name="quote",
        description="pick a random quote and post it",
        guild=SETTINGS.guild
)
async def quote(ctx: Context):
    msg = await BOT.get_quote(CLIENT)
    await ctx.response.send_message(msg)

@TREE.command(
    name="daily",
    guild=SETTINGS.guild,
)
async def daily(ctx: Context, time: str):
    """Set a time for the quote of the day

    Parameters
    -----------
    time: str
        The time to post - format HH:MM    
    """
    try:
        dt = datetime.strptime(time, "%H:%M")
    except ValueError as ve:
        print(f"Error: {str(ve)}")
        await ctx.response.send_message("Invalid datetime >:(")
        return

    # get the time for the next event
    now = datetime.today()
    next_time = datetime.today().replace(hour=dt.hour,minute=dt.minute,second=0)

    if now > next_time:
        next_time += timedelta(days=1)
    
    await BOT.start_daily_post(CLIENT, ctx.channel.id, next_time)
    await ctx.response.send_message(f"Next quote of the day will be at {next_time}")


CLIENT.run(SETTINGS.bot_token)
