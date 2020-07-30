from contextlib import suppress

from discord import Embed, Color, VoiceChannel, CategoryChannel, HTTPException
from discord.ext.commands import Cog, group, command, has_guild_permissions, bot_has_permissions, \
    bot_has_guild_permissions, cooldown, BucketType

from .utils.converters import StrRange, IntRange


async def update_config(ctx, key, value):
    config = ctx.bot.configs.get(ctx.guild.id, {})
    before = config[key]
    config[key] = value
    ctx.bot.configs[ctx.guild.id] = config
    await ctx.bot.configs.save()
    return before


class Settings(Cog):
    @group(aliases=['pfx', 'prefixes'], invoke_without_command=True)
    @cooldown(3, 10, BucketType.member)
    @has_guild_permissions(administrator=True)
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def prefix(self, ctx, prefix: StrRange(1, 16) = None):
        """Shows you the bot's prefix or lets you change it on this server."""
        if prefix is None:
            try:
                prefix = ctx.bot.configs[ctx.guild.id]['prefix']
            except KeyError:
                prefix = ctx.bot.default_prefix
            await ctx.send(embed=Embed(
                description=f"The bot's prefix on this server is `{prefix}`.",
                color=0x000000
            ))
        else:
            before = await update_config(ctx, 'prefix', prefix)
            await ctx.send(embed=Embed(
                description=f"Changed the bot's prefix from `{before}` to `{prefix}`.",
                color=Color.green()
            ))

    @command()
    @cooldown(1, 60, BucketType.guild)
    @bot_has_guild_permissions(manage_channels=True)
    @has_guild_permissions(administrator=True)
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def setup(self, ctx):
        """Automatically creates a new category and a new channel.
        This is a short version for the `channel` and `category` command.
        You can always change, delete or edit the channel.
        """
        category = await ctx.guild.create_category(name='dynamic voice chats')
        channel = await category.create_voice_channel(name='join me', user_limit=1, bitrate=8000)
        await update_config(ctx, 'category', category.id)
        await update_config(ctx, 'channel', channel.id)
        await ctx.send(embed=Embed(
            description='Done! A new category has been created. Feel free to edit the channels as you like.',
            color=Color.green()
        ))

    @command()
    @cooldown(3, 10, BucketType.member)
    @has_guild_permissions(administrator=True)
    @bot_has_guild_permissions(manage_channels=True)
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def channel(self, ctx, *, channel: VoiceChannel):
        """Sets the channel you have to join in order to create a new voice channel."""
        with suppress(HTTPException):
            await channel.edit(user_limit=1, bitrate=8000)
        await update_config(ctx, 'channel', channel.id)
        await update_config(ctx, 'category', channel.category.id)
        await ctx.send(embed=Embed(
            description=f'New voice channels are now created when connecting to **{channel.name}**.',
            color=Color.green()
        ))

    @command()
    @cooldown(3, 10, BucketType.member)
    @bot_has_guild_permissions(manage_channels=True)
    @has_guild_permissions(administrator=True)
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def category(self, ctx, *, category: CategoryChannel):
        """Sets the category new voice channels are created in.
        By default this is the category the auto voice channel is in.
        """
        await update_config(ctx, 'category', category.id)
        await ctx.send(embed=Embed(
            description=f'New voice channels are now created in **{category.name}**.',
            color=Color.green()
        ))

    @command()
    @cooldown(3, 10, BucketType.member)
    @has_guild_permissions(administrator=True)
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def defaultname(self, ctx, *, name: StrRange(2, 100)):
        """Sets the default name for created voice channels.
        You can use `@user` to reference the user who created the voice channel.
        The name must not be shorter than 2 characters and longer than 100 characters.
        """
        await update_config(ctx, 'name', name)
        await ctx.send(embed=Embed(
            title='Settings updated.',
            description=f'Changed the default name on this server to **{name}**.',
            color=Color.green()
        ))

    @command()
    @cooldown(3, 10, BucketType.member)
    @has_guild_permissions(administrator=True)
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def defaultlimit(self, ctx, number: IntRange(0, 99)):
        """Sets the default user limit for created voice channels.
        Use 0 to set the user limit to unlimited.
        The limit must be between 0 and 99.
        """
        await update_config(ctx, 'limit', number)
        await ctx.send(embed=Embed(
            title='Settings updated.',
            description=f'Changed the default limit on this server to `{number}`.',
            color=Color.green()
        ))

    @command()
    @cooldown(3, 10, BucketType.member)
    @has_guild_permissions(administrator=True)
    @bot_has_permissions(send_messages=True, embed_links=True)
    async def position(self, ctx):
        """Changes the position of created voice channels.
        Voice channels can either be created above or below the auto voice channel.
        """
        config = ctx.bot.configs.get(ctx.guild.id, {})
        before = config.get("top", False)
        config["top"] = not before
        ctx.bot.configs[ctx.guild.id] = config
        await ctx.bot.configs.save()
        pos = "top" if config["top"] else "bottom"
        await ctx.send(embed=Embed(
            description=f":white_check_mark: New voice channels are now created at the {pos}.",
            color=Color.green()
        ))


def setup(bot):
    bot.add_cog(Settings(bot))
