import discord
from discord.ext import commands, tasks
import aiohttp
import config
import typing


class Api(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.update_stats.start()

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
        await ctx.bot.change_presence(activity=discord.Activity(type=activity_type, name=name))


def setup(bot):
    bot.add_cog(Api(bot))
