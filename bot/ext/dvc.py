import disnake as discord
from disnake.ext import commands


not_added = commands.BadArgument("This channel has not been added yet")
no_added = commands.BadArgument("You haven't added any channels yet")


@commands.slash_command(name="dvc")
@commands.bot_has_guild_permissions(manage_channels=True)
async def parent(_):
    """Controls behaviour of a dynamic-voice-channel"""
    pass


@parent.sub_command(name="setup")
@commands.bot_has_guild_permissions(move_members=True, manage_roles=True, connect=True)
async def child_setup(ctx):
    """Automatically creates a new category and a new channel and adds it to the dynamic-voice-channels"""
    category = await ctx.guild.create_category("Dynamic Voice Channels")
    channel = await category.create_voice_channel("join me")
    ctx.bot.configs[str(channel.id)] = {}
    await ctx.bot.configs.save()
    await ctx.send(f"A new category and a new channel have been created. Join `{channel.name}` and try it out")


@parent.sub_command(name="add")
async def child_add(ctx, channel: discord.VoiceChannel):
    """Adds a voice channel to the dynamic-voice-channels"""
    if str(channel.id) in ctx.bot.configs:
        raise commands.BadArgument("This channel has already been added")
    else:
        limit = 25  # message embed limit -> non-paginated list command
        channels = [c for c in ctx.guild.voice_channels if str(c.id) in ctx.bot.configs]
        if len(channels) >= limit:
            raise commands.CommandError(f"You cannot add more than {limit} auto-channels")
        else:
            ctx.bot.configs[str(channel.id)] = {}
            await ctx.bot.configs.save()
            await ctx.send("Channel has been added")


@parent.sub_command(name="remove")
async def child_remove(ctx, channel: discord.VoiceChannel):
    """Removes a voice channel from the dynamic-voice-channels"""
    try:
        del ctx.bot.configs[str(channel.id)]
    except KeyError:
        raise not_added
    else:
        await ctx.bot.configs.save()
        await ctx.send("Channel has been removed")


@parent.sub_command(name="clear")
async def child_clear(ctx):
    """Automatically clears all dynamic-voice-channels"""
    n = 0
    for channel in ctx.guild.voice_channels:
        try:
            del ctx.bot.configs[str(channel.id)]
        except KeyError:
            continue
        else:
            n += 1
    if n == 0:
        raise no_added
    else:
        await ctx.bot.configs.save()
        await ctx.send(f"Successfully removed {n} channel(s)")


@parent.sub_command(name="list")
async def child_list(ctx):
    """Lists all dynamic-voice-channels including their settings"""
    channels = [c for c in ctx.guild.voice_channels if str(c.id) in ctx.bot.configs]
    if len(channels) == 0:
        raise no_added
    else:
        embed = discord.Embed(
            title="Dynamic-Voice-Channels",
            description="Here is a list with all dynamic-voice-channels in this server:",
            color=discord.Color.blue()
        )
        for channel in channels:
            settings = ctx.bot.get_settings(channel)
            category = ctx.guild.get_channel(settings["category"])
            embed.add_field(
                name=f"{channel.name} (ID: {channel.id})",
                value=f"Category: `{'no category' if category is None else category.name}`\n"
                      f"Name: `{settings['name']}`\n"
                      f"Limit: `{settings['limit']} users`\n" 
                      f"Bitrate: `{settings['bitrate']} kbps`\n"
                      f"Position: `{settings['position']}`",
                inline=False
            )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_slash_command(parent)
