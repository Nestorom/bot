import json
import random
import discord
import asyncio
from dotenv import load_dotenv
import os
from discord.ext import commands, tasks

from json import JSONEncoder


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default

DEBUG = False
load_dotenv()
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True
BOT_PREFIX = "!"
ACTIVE_EXTENSIONS = ['Extensions.Misc', 'Extensions.ActivityStats'] # 'Extensions.Currency',
                     #'Extensions.Gambling', 'Extensions.HorseRace', 'Extensions.MinerGame', 
                     # 'Extensions.CardCollector']
DATA_PATH = "/app/data/"


class Context(commands.Context):
    async def tick(self, value):
        emoji = '\N{WHITE HEAVY CHECK MARK}' if value else '\N{CROSS MARK}'
        try:
            await self.message.add_reaction(emoji)
        except discord.HTTPException:
            pass

    @commands.command()
    async def help(self, ctx):
        """!help"""
        msg = "I'm feeling down"
        await ctx.send(f'{msg}')


class DumbClickerBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TICK_RATE = int(os.getenv('TICK_RATE', 60))  # number of ticks per minute
        self.SAVE_RATE = 60  # Save Every minute
        self.SHORT_DELETE_DELAY = 5
        self.MEDIUM_DELETE_DELAY = 30
        self.LONG_DELETE_DELAY = 60
        self.VERY_LONG_DELETE_DELAY = 240
        self.CURRENCY_NAME = 'shekel'
        self.CURRENCY_TOKEN = '$'
        self.ADMINISTRATOR = os.getenv('ADMINISTRATOR')
        self.LOG_CHANNEL = int(os.getenv('LOG_CHANNEL'))  # Log Channel is used for story Bot Usage History
        self.DEBUG_CHANNEL = int(os.getenv('DEBUG_CHANNEL'))  # Test Channel is used for debugging
        self.ACTIVITY_IGNORE_LIST = ['Spiralling Ever Downwards']
        self.time_elapsed = 0

    async def on_ready(self):
        print('Logged in as', self.user.name, self.user.id)
        for cog in self.cogs:  # Call timeout on all cogs.
            cog = self.get_cog(cog)
            if hasattr(cog, 'load_data'):
                await cog.load_data()
            if hasattr(cog, 'on_message'):
                bot.add_listener(cog.on_message, 'on_message')
                print(cog, "Added on_message")
        print('------------------------------------------------------------')
        self.timeout.start()
    @tasks.loop(seconds=int(os.getenv('TICK_RATE', 60)))
    async def timeout(self):
        await self.wait_until_ready()
        channel = self.get_channel(self.DEBUG_CHANNEL)
        if not self.is_closed():
            for cog in self.cogs:  # Call timeout on all cogs.
                cog = self.get_cog(cog)
                if hasattr(cog, 'timeout'):
                    await cog.timeout()
            self.time_elapsed += self.TICK_RATE
            if self.time_elapsed % self.SAVE_RATE < self.TICK_RATE:
                for cog in self.cogs:  # Call save on all cogs.
                    cog = self.get_cog(cog)
                    if hasattr(cog, 'save_data'):
                        if DEBUG:
                            print(f'{cog.qualified_name} {cog} Saving... ', end='')
                        await cog.save_data()
                        if DEBUG:
                            print(f'saved. ')
                    else:
                        print(cog.qualified_name, 'no data to be saved.')
                print()
            if DEBUG:
                await channel.send(f"Runner Uptime: {self.time_elapsed - self.TICK_RATE}")

    async def get_context(self, message, *, cls=Context):
        return await super().get_context(message, cls=cls)


bot = DumbClickerBot(command_prefix=BOT_PREFIX, intents=intents)

async def load_exts():
    for extension in ACTIVE_EXTENSIONS:
        await bot.load_extension(extension)


async def main():
    # do other async things
    await load_exts()

    # start the client
    async with bot:
        await bot.start(TOKEN)


asyncio.run(main())
