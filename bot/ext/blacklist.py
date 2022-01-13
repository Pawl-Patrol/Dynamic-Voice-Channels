import disnake as discord
from disnake.ext import commands


@commands.slash_command(name="blacklist")
@commands.has_guild_permissions(manage_guild=True)
async def parent(_):
    pass


@parent.sub_command(name="add")
async def child_add(ctx, word: str):
    """Puts a word on the blacklist"""
    blacklist = ctx.bot.blacklists.get(str(ctx.guild.id), [])
    if word in blacklist:
        raise commands.BadArgument("This word is already blacklisted")
    blacklist.append(word)
    ctx.bot.blacklists[str(ctx.guild.id)] = blacklist
    await ctx.bot.blacklists.save()
    await ctx.send("The word has been blacklisted")


@parent.sub_command(name="remove")
async def child_remove(ctx, word: str):
    """Removes a word from the blacklist"""
    blacklist = ctx.bot.blacklists.get(str(ctx.guild.id), [])
    if word not in blacklist:
        raise commands.BadArgument("This word has not been blacklisted yet")
    if len(blacklist) > 1:
        blacklist.remove(word)
        ctx.bot.blacklists[str(ctx.guild.id)] = blacklist
    else:
        ctx.bot.blacklists.pop(str(ctx.guild.id))
    await ctx.bot.blacklists.save()
    await ctx.send("Removed the word from the Blacklist")


@parent.sub_command(name="clear")
async def child_clear(ctx):
    """Clears the blacklist"""
    try:
        del ctx.bot.blacklists[str(ctx.guild.id)]
    except KeyError:
        raise commands.CommandError("You haven't added any words to the blacklist yet")
    await ctx.bot.blacklists.save()
    await ctx.send("Blacklist has been cleared.")


@parent.sub_command(name="show")
async def child_show(ctx):
    """Shows the blacklist"""
    try:
        blacklist = ctx.bot.blacklists[str(ctx.guild.id)]
    except KeyError:
        raise commands.CommandError("You haven't added any words to the blacklist yet")
    await ctx.send("||" + " ".join(w for w in blacklist) + "||")


def setup(bot):
    bot.add_slash_command(parent)
