from discord.ext import commands
import discord
import os
import asyncio
import inspect
import json


DISCORD_BOTS_API ='https://bots.discord.pw/api'


class Meta:
    """Commands for utilities related to Discord or the Bot itself."""

    def __init__(self, bot):
        self.bot = bot
        self._task = bot.loop.create_task(self.run_tasks())
        bot.loop.create_task(self.update())

    def __unload(self):
        self._task.cancel()

    async def __error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(error)

    @commands.command(name='invite', hidden=True)
    async def _help(self, ctx, *, command: str = None):
        """Shows the invite url for the bot"""
        await ctx.send("{}, click here to invite me! {}".format(ctx.author.mention, self.bot.invite_url))

    @commands.command(hidden=True)
    async def hello(self, ctx):
        """Displays my intro message."""
        app_info = await self.bot.application_info()
        await ctx.send('Hello! I\'m a robot! {0.name}#{0.discriminator} made me.'.format(app_info.owner))

    @commands.command(hidden=True)
    async def source(self, ctx, *, command: str = None):
        """Displays my full source code or for a specific command.
        To display the source code of a subcommand you can separate it by
        periods, e.g. tag.create for the create subcommand of the tag command
        or by spaces.
        """
        source_url = self.bot.github_url
        if command is None:
            return await ctx.send(source_url)

        obj = self.bot.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.send('Could not find command.')

        # since we found the command we're looking for, presumably anyway, let's
        # try to access the code itself
        src = obj.callback.__code__
        lines, firstlineno = inspect.getsourcelines(src)
        location = obj.callback.__module__.replace('.', '/') + '.py'

        final_url = f'<{source_url}/blob/master/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>'
        await ctx.send(final_url)

    async def run_tasks(self):
        try:
            while not self.bot.is_ready():
                await asyncio.sleep(1)
            while not self.bot.is_closed():
                await self.update_avatar()
                await asyncio.sleep(3600)
        except asyncio.CancelledError as e:
            pass

    async def update_avatar(self):
        """
        Update the bot Avatar
        """
        path = 'avatar.png'
        try:
            os.remove(path)
        except:
            pass
        try:
            app_info = await self.bot.application_info()
            if app_info.icon_url is None or app_info.icon_url == "":
                return
            resp = await self.bot.session.get(app_info.icon_url)
            if resp.status == 200:
                with open(path, 'wb') as fd:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        fd.write(chunk)
                with open(path, 'rb') as f:
                    await self.bot.user.edit(avatar=f.read())
            else:
                raise Exception("Response code was not ok. Got {0.status_code}".format(r))
        except Exception as e:
            self.bot.log(e)

    async def on_guild_join(self, guild):
        self.bot.log('QuoteBot was added to {} with {} members'.format(str(guild), str(len(guild.members))))
        await self.update()

    async def on_guild_remove(self, guild):
        self.bot.log('QuoteBot was removed from {}'.format(str(guild)))
        await self.update()

    async def update(self):
        if not self.bot.dbots_key or self.bot.dbots_key == '':
            return
        while not self.bot.is_ready():
            await asyncio.sleep(1)
        payload = json.dumps({
            'server_count': len(self.guilds),
        })

        headers = {
            'authorization': self.bot.dbots_key,
            'content-type': 'application/json'
        }

        url = '{0}/bots/{1.user.id}/stats'.format(DISCORD_BOTS_API, self)
        try:
            async with self.bot.session.post(url, data=payload, headers=headers) as resp:
                await self.bot.log_channel.send('DBots statistics returned {0.status} for {1}'.format(resp, payload))
        except Exception as e:
            self.bot.log.info(e)

def setup(bot):
    bot.add_cog(Meta(bot))
