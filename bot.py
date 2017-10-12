import aiohttp
import asyncio
import datetime
import discord
import json
import logging
import os
import sys
import traceback
from pathlib import Path
from discord.ext import commands

try:
    import credentials
except:
    pass


quote_emote = u"\U0001F4AC"

github_url = 'https://github.com/bsquidwrd/Quote-Bot'

description = """
Hello! I am a bot written by bsquidwrd to provide easy quoting for your amusement.
Simply add the {} reaction to a message to quote it!
""".format(quote_emote)

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
log.addHandler(handler)

initial_extensions = (
    'cogs.quote',
    'cogs.admin',
    'cogs.meta',
)

def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    return base

class QuoteBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=_prefix_callable, description=description,
                         pm_help=None, help_attrs=dict(hidden=True))

        self.client_id = int(os.getenv('CLIENT_ID', None))
        self.client_token = os.getenv('CLIENT_TOKEN', None)
        self.owner_id = int(os.getenv('OWNER_ID', None))
        self.dbots_key = os.getenv('DBOTS_KEY', None)
        self.invite_url = os.getenv('INVITE_URL', None)
        self.quote_emote = quote_emote
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.github_url = github_url
        self.log_channel = int(os.getenv('LOG_CHANNEL', None))

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print(f'{error.original.__class__.__name__}: {error.original}', file=sys.stderr)

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        print(f'Ready: {self.user} (ID: {self.user.id})')

    async def on_resumed(self):
        print('resumed...')

    def log(self, message):
        log.info(message)

    async def process_commands(self, message):
        ctx = await self.get_context(message)

        if ctx.command is None:
            return

        destination = None
        if type(message.channel) in [discord.DMChannel, discord.GroupChannel]:
            destination = 'Private Message'
        else:
            destination = '#{0.channel.name} ({0.guild.name})'.format(message)
        log_message = '{0.created_at}: {0.author.name} in {1}: {2}'.format(message, destination, ' '.join(message.content.split(' ')[1::]))
        self.log(log_message)

        await self.invoke(ctx)

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        super().run(self.client_token, reconnect=True)


if __name__ == '__main__':
    bot = QuoteBot()
    bot.run()
    handlers = log.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        log.removeHandler(hdlr)
