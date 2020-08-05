import discord
from discord.ext import commands, menus
from difflib import get_close_matches


class HelpSource(menus.GroupByPageSource):
    def format_page(self, menu: menus.MenuPages, entry):
        embed = discord.Embed(
            title=f'{entry.key.title()} commands',
            description=f'Use `{menu.ctx.prefix}{menu.ctx.invoked_with} <command>` for more info on a command.',
            color=menu.ctx.guild.me.color
        )
        embed.set_thumbnail(url=menu.ctx.bot.user.avatar_url)
        embed.set_footer(text=f'Page {menu.current_page + 1} of {self.get_max_pages()}')
        for command in entry.items:
            usage = menu.ctx.prefix + command.name
            if command.signature:
                usage += ' ' + command.signature
            embed.add_field(name=usage, value=command.short_doc.format(prefix=menu.ctx.prefix), inline=False)
        return embed


class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            'aliases': ['h', 'commands'],
            'max_concurrency': commands.MaxConcurrency(2, per=commands.BucketType.member, wait=False),
            'help': 'Starts an interactive session with a list of all available commands.'
        }, verify_checks=False)

    def command_not_found(self, string):
        msg = f'No command called **{string}** found.'
        close = get_close_matches(string, self.context.bot.all_commands, n=1)
        if close:
            msg += f' Did you mean **{close[0]}**?'
        return msg

    async def send_error_message(self, error):
        await self.context.safe_send(msg=error, color=discord.Color.red())

    async def send_bot_help(self, _):
        entries = []
        for cog in self.context.bot.cogs.values():
            entries += await self.filter_commands(cog.get_commands())
        source = HelpSource(entries, key=lambda c: c.cog.qualified_name, per_page=4, sort=True)
        menu = menus.MenuPages(source, timeout=60, check_embeds=True, delete_message_after=True)
        await menu.start(self.context, wait=True)

    async def send_command_help(self, command):
        perms = self.context.channel.permissions_for(self.context.guild.me)
        if perms.embed_links:
            usage = self.context.prefix + command.name
            if command.signature:
                usage += ' ' + command.signature
            await self.context.send(embed=discord.Embed(
                title=usage,
                description=command.help.format(prefix=self.context.prefix),
                color=self.context.guild.me.color
            ))
        else:
            raise commands.BotMissingPermissions(['embed_links'])
