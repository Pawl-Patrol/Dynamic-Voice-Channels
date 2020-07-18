from datetime import datetime
from difflib import get_close_matches
from typing import Optional

from discord import Embed, Color, Permissions
from discord.ext.commands import Cog, BucketType, command as _command, max_concurrency
from discord.ext.menus import ListPageSource, MenuPages
from discord.utils import oauth_url
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
    async def help(self, ctx, *, command: Optional[str]):
        """Shows you all of the bot's commands or help for a single command."""
        if command:
            cmd_name = get_close_matches(command.lower(), ctx.bot.all_commands, n=1)
            if cmd_name:
                cmd = ctx.bot.all_commands[cmd_name[0]]
                usage = ctx.prefix + cmd.name
                if cmd.signature:
                    usage += ' ' + cmd.signature
                await ctx.send(embed=Embed(
                    title=' / '.join([cmd.name, *cmd.aliases]),
                    description=f'{cmd.help}\n```md\n{usage}```',
                    color=0x000000
                ))
            else:
                await ctx.send(embed=Embed(
                    description=f':x: No command named `{command}` found.',
                    color=Color.red()
                ))
        else:
            source = HelpSource(list(ctx.bot.commands), per_page=5)
            menu = MenuPages(source, clear_reactions_after=True)
            await menu.start(ctx)

    @_command(aliases=['join'])
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
