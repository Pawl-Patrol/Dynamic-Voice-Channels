from datetime import datetime
from typing import Optional

from discord import Embed, Color, Permissions
from discord.ext.commands import Cog, BucketType, command as _command, max_concurrency, bot_has_permissions, cooldown
from discord.ext.menus import ListPageSource, MenuPages
from discord.utils import oauth_url
from .utils.converters import CommandConverter, StrRange
from psutil import Process, virtual_memory, cpu_count


class HelpSource(ListPageSource):
    def format_page(self, menu, entries):
        embed = Embed(
            title=f'{menu.ctx.bot.user.name} ({len(menu.ctx.bot.commands)} commands)',
            description=f'Use `{menu.ctx.prefix}{menu.ctx.invoked_with} <command>` for more info on a command.',
            color=0x000000
        )
        embed.set_footer(text=f'Page {menu.current_page + 1} of {self.get_max_pages()}')
        for command in entries:
            usage = menu.ctx.prefix + command.name
            if command.signature:
                usage += ' ' + command.signature
            embed.add_field(name=usage, value=command.short_doc, inline=False)
        return embed


class Help(Cog):
    @_command(aliases=['h', 'commands', 'cmds'])
    @max_concurrency(1, BucketType.user)
    @cooldown(3, 10, BucketType.member)
    @bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True)
    async def help(self, ctx, *, command: CommandConverter = None):
        """Shows you all of the bot's commands  or help for a single command."""
        if command:
            usage = ctx.prefix + command.name
            if command.signature:
                usage += ' ' + command.signature
            await ctx.send(embed=Embed(
                title=' / '.join([command.name, *command.aliases]),
                description=f'{command.help}\n```md\n{usage}```',
                color=0x000000
            ))
        else:
            source = HelpSource(list(ctx.bot.commands), per_page=5)
            menu = MenuPages(source, clear_reactions_after=True)
            await menu.start(ctx)

    @_command(aliases=["suggest"])
    @cooldown(1, 120, BucketType.member)
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def support(self, ctx, *, message: StrRange(0, 2000)):
        """Sends a message to the bot's owner. Do not abuse."""
        owner = ctx.bot.get_user(ctx.bot.owner_id)
        embed = Embed(
            description=message
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await owner.send(embed=embed)
        await ctx.send(embed=Embed(
            description=":white_check_mark: Message has been sent. Thank you for your help!",
            color=Color.green()
        ))

    @_command(aliases=['join'])
    @cooldown(1, 30, BucketType.channel)
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def invite(self, ctx):
        """Gives you the bot's Invite Link. If you don't want the bot to create its own role or you want to set the
        permissions yourself, use the Invite without permissions. But don't forget that it won't work without these
        permissions.
        """
        no_perms = oauth_url(ctx.bot.client_id, Permissions.none())
        best_perms = oauth_url(ctx.bot.client_id, Permissions(
            send_messages=True,
            read_messages=True,
            embed_links=True,
            add_reactions=True,
            move_members=True,
            manage_channels=True
        ))
        await ctx.send(embed=Embed(
            title=':envelope: Invite links',
            description=f'[Invite (recommended)]({best_perms})\n[Invite (no permissions)]({no_perms})',
            color=0x000000
        ))

    @_command(aliases=['about', 'stats'])
    @cooldown(1, 30, BucketType.channel)
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def info(self, ctx):
        """Shows you information about the bot owner, bot uptime, latency, memory and cpu usage."""
        embed = Embed(color=0x000000)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        app = await ctx.bot.application_info()
        owner = app.owner
        embed.set_author(name=str(owner), icon_url=owner.avatar_url)
        proc = Process()
        with proc.oneshot():
            uptime = datetime.utcnow() - ctx.bot.launched_at
            mem_total = virtual_memory().total / (1024 ** 2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)
            cpu_usage = proc.cpu_percent() / cpu_count()
        embed.add_field(name='Uptime', value=str(uptime), inline=False)
        embed.add_field(name='Latency', value=f'{round(ctx.bot.latency * 1000, 2)} ms', inline=False)
        embed.add_field(name='Memory usage', value=f'{int(mem_usage)} / {int(mem_total)} MiB ({round(mem_of_total)}%)',
                        inline=False)
        embed.add_field(name='CPU usage', value=f'{round(cpu_usage)}%', inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
