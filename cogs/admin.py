import discord
from discord.ext import commands, tasks
import aiohttp
import config
import typing
import io
import textwrap
from contextlib import redirect_stdout
import traceback


class Api(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    async def on_ready(self):
        if config.discordbotlist_key:
            self.update_stats.start()

    @tasks.loop(hours=1)
    async def update_stats(self):
        url = 'https://discordbotlist.com/api/v1/bots/' + str(self.bot.user.id) + '/stats'
        data = {'guilds': len(self.bot.guilds), 'users': len(self.bot.users)}
        headers = {'Authorization': 'Bot ' + config.discordbotlist_key}
        async with aiohttp.ClientSession(loop=self.bot.loop) as session:
            await session.post(url=url, json=data, headers=headers)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def activity(self, ctx, activity_type: typing.Optional[int] = 0, *, name):
        """Changes the bots status."""
        await ctx.bot.change_presence(activity=discord.Activity(type=activity_type, name=name))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def eval(self, ctx, *, body: str):
        """Evaluates a code. Source: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py#L216-L261"""
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        if body.startswith('```') and body.endswith('```'):
            return '\n'.join(body.split('\n')[1:-1])
        body = body.strip('` \n')
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass
            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot):
    bot.add_cog(Api(bot))
