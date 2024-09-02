import discord
from properties import Properties
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
token : str = os.getenv("TOKEN")
cogs_folder_path : str = "./cogs"

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.guilds = True
command_prefix : str = "!"
bot = commands.Bot(command_prefix=command_prefix, intents=intents, help_command=None)

guild : discord.Guild = bot.get_guild(Properties.GUILD_ID)

async def load_cogs():
    for filename in os.listdir(cogs_folder_path):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    await load_cogs()
    sync = await bot.tree.sync(guild=guild)
    # ------------------------------------logs------------------------------------
    print(f"Gustave has succesfuly logged as {bot.user}!\n--- {Properties.DATE_AND_TIME_IN_FRANCE.strftime('%d/%m/%Y %H:%M:%S')} ---\nsynced {len(sync)} commands")
    # ----------------------------------------------------------------------------

bot.run(token)