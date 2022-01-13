import disnake as discord
from disnake.ext import commands
import psutil
from datetime import datetime


permissions = discord.Permissions(
    manage_channels=True,  # for creating/deleting/moving channels
    move_members=True,  # for moving members into new channels
    connect=True,  # required for deleting channels, see Forbidden: Missing Access
    manage_roles=True  # required for setting channel permissions
)


@commands.slash_command(name="bot")
async def parent(_):
    pass


@parent.sub_command(name="invite")
async def child_invite(ctx):
    """Gives you the bot's invite link"""
    best_perms = discord.utils.oauth_url(ctx.bot.user.id, permissions=permissions, scopes=["bot", "applications.commands"])
    view = discord.ui.View(timeout=0)
    view.add_item(discord.ui.Button(label="invite", url=best_perms, emoji="✉️", style=discord.ButtonStyle.primary))
    await ctx.send("Invite me to another server by using the button below", view=view)


@parent.sub_command(name="info")
async def child_info(ctx):
    """Shows you information about the bot"""
    embed = discord.Embed(color=ctx.guild.me.color)
    embed.set_thumbnail(url=ctx.bot.user.avatar.url)
    owner = await ctx.bot.get_owner()
    embed.set_author(name=f'Owner: {owner}', icon_url=owner.avatar.url)
    proc = psutil.Process()
    with proc.oneshot():
        uptime = datetime.utcnow() - ctx.bot.launched_at
        mem_total = psutil.virtual_memory().total / (1024 ** 2)
        mem_of_total = proc.memory_percent()
        mem_usage = mem_total * (mem_of_total / 100)
        cpu_usage = proc.cpu_percent() / psutil.cpu_count()
    embed.add_field(name="Servers", value=str(len(ctx.bot.guilds)))
    embed.add_field(name="Channels", value=str(len(ctx.bot.channels)))
    embed.add_field(name="Latency", value=f"{round(ctx.bot.latency * 1000, 2)} ms")
    embed.add_field(name="Uptime", value=str(uptime))
    embed.add_field(name="CPU usage", value=f"{round(cpu_usage)}%")
    embed.add_field(name="Memory usage", value=f"{int(mem_usage)} / {int(mem_total)} MiB ({round(mem_of_total)}%)")
    await ctx.send(embed=embed)


@parent.sub_command(name="support")
async def child_support(ctx):
    """Gives you the github repo link"""
    await ctx.send("https://github.com/Pawl-Patrol/Dynamic-Voice-Channels/issues")


@parent.sub_command(name="permcheck")
@commands.has_guild_permissions(manage_guild=True)
async def child_permcheck(ctx):
    """Shows you if the bot is missing permissions"""
    perms = ctx.me.guild_permissions
    missing = discord.Permissions((perms.value ^ permissions.value) & permissions.value)
    if not perms.administrator and missing.value:
        await ctx.send("The bot is missing the following permissions:\n" + ", ".join(perm for perm, value in missing if value))
    else:
        await ctx.send("The bot is missing no permissions", ephemeral=True)


def setup(bot):
    bot.add_slash_command(parent)
