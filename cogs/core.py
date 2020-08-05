import discord
from discord.ext import commands
import psutil
import datetime


class Core(commands.Cog):
    @commands.command(aliases=['join'])
    async def invite(self, ctx):
        """Gives you the bot's Invite Link.
        If you don't want the bot to create its own role or you want to set the permissions yourself,
        use the Invite without permissions. But don't forget that it won't work without these permissions.
        """
        best_perms = discord.utils.oauth_url(ctx.bot.client_id, discord.Permissions(
            send_messages=True,
            read_messages=True,
            embed_links=True,
            add_reactions=True,
            move_members=True,
            manage_channels=True,
            manage_messages=True,
            manage_roles=True
        ))
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if perms.embed_links:
            no_perms = discord.utils.oauth_url(ctx.bot.client_id, discord.Permissions.none())
            await ctx.send(embed=discord.Embed(
                title=':envelope: Invite links',
                description=f'[Invite (recommended)]({best_perms})\n[Invite (no permissions)]({no_perms})',
                color=ctx.guild.me.color
            ))
        else:
            await ctx.send(best_perms)

    @commands.command(aliases=['about', 'stats'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    async def info(self, ctx):
        """Shows you information about the bot."""
        embed = discord.Embed(color=ctx.guild.me.color)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        app = await ctx.bot.application_info()
        owner = app.owner
        embed.set_author(name=f'Owner: {owner}', icon_url=owner.avatar_url)
        proc = psutil.Process()
        with proc.oneshot():
            uptime = datetime.datetime.utcnow() - ctx.bot.launched_at
            mem_total = psutil.virtual_memory().total / (1024 ** 2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)
            cpu_usage = proc.cpu_percent() / psutil.cpu_count()
        embed.add_field(name='Servers', value=str(len(ctx.bot.guilds)))
        embed.add_field(name='Channels', value=str(len(ctx.bot.channels)))
        embed.add_field(name='Latency', value=f'{round(ctx.bot.latency * 1000, 2)} ms')
        embed.add_field(name='Uptime', value=str(uptime))
        embed.add_field(name='CPU usage', value=f'{round(cpu_usage)}%')
        embed.add_field(name='Memory usage', value=f'{int(mem_usage)} / {int(mem_total)} MiB ({round(mem_of_total)}%)')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Core())
