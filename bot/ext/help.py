import disnake as discord
from disnake.ext import commands
import difflib


def get_command_info(cmd):
    if isinstance(cmd, commands.InvokableSlashCommand):
        return cmd.name, cmd.description
    elif isinstance(cmd, commands.SubCommand):
        return cmd.qualified_name, cmd.option.description


class HelpMenu(discord.ui.View):
    def __init__(self, cmds, *, per_page):
        super().__init__()
        self.cmds = list(cmds)
        self.per_page = per_page
        self.page = 0
        self.pages = (len(self.cmds) + per_page - 1) // per_page

        self.add_item(discord.ui.Button(label="Wiki", emoji="📚", url="https://github.com/Pawl-Patrol/Dynamic-Voice-Channels/wiki"))
        self.add_item(discord.ui.Button(label="Issues", url="https://github.com/Pawl-Patrol/Dynamic-Voice-Channels/issues"))
        self.add_item(discord.ui.Button(label="Source", url="https://github.com/Pawl-Patrol/Dynamic-Voice-Channels"))

    def format_page(self, page):
        embed = discord.Embed(
            title="Help",
            description="Use `/help <command>` for more info on a command."
        )
        idx = self.page * self.per_page
        for cmd in self.cmds[idx:(min(idx + self.per_page, len(self.cmds)))]:
            name, description = get_command_info(cmd)
            embed.add_field(
                name=f"/{name}",
                value=description or "No description",
                inline=False
            )
        embed.set_footer(text=f"Page {self.page + 1} of {self.pages}")
        return embed

    def update(self):
        self.previous.disabled = self.page == 0
        self.first.disabled = self.page < 2
        self.next.disabled = self.page == (self.pages - 1)
        self.last.disabled = self.page > (self.pages - 3)

        return self.format_page(self.page)

    async def send_initial(self, ctx):
        await ctx.response.send_message(embed=self.update(), view=self)

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def first(self, button, ctx):
        self.page = 0
        await ctx.response.edit_message(embed=self.update(), view=self)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous(self, button, ctx):
        self.page -= 1
        await ctx.response.edit_message(embed=self.update(), view=self)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.secondary)
    async def close(self, button, ctx):
        self.clear_items()
        await ctx.response.edit_message(embed=self.update(), view=self)
        self.stop()

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, button, ctx):
        self.page += 1
        await ctx.response.edit_message(embed=self.update(), view=self)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def last(self, button, ctx):
        self.page = self.pages - 1
        await ctx.response.edit_message(embed=self.update(), view=self)


async def get_commands(ctx):
    cmds = []
    for cmd in ctx.bot.slash_commands:
        if not cmd.children:
            cmds.append(cmd)
            continue
        for subcmd in cmd.children.values():
            cmds.append(subcmd)
    return cmds


async def auto_complete(ctx, arg):
    cmds = [get_command_info(cmd)[0] for cmd in await get_commands(ctx)]
    results = difflib.get_close_matches(arg, cmds)
    for cmd in cmds:
        if arg in cmd and cmd not in results:
            results.append(cmd)
    return results


@commands.slash_command(name="help")
async def help_command(ctx, command: str = commands.Param(default=None, autocomplete=auto_complete)):
    """Shows you this"""
    if command is None:
        menu = HelpMenu(await get_commands(ctx), per_page=4)
        await menu.send_initial(ctx)
    else:
        cmd = discord.utils.find(lambda c: get_command_info(c)[0] == command, await get_commands(ctx))
        if not cmd:
            await ctx.send("Command not found.", ephemeral=True)
        else:
            name, description = get_command_info(cmd)
            await ctx.send(embed=discord.Embed(
                title=f"/{name}",
                description=description
            ))


def setup(bot):
    bot.add_slash_command(help_command)
