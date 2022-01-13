import disnake as discord
from disnake.ext import commands


class Default(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def configure(self, channel, key, value):
        try:
            self.bot.configs[str(channel.id)][key] = value
        except KeyError:
            raise commands.BadArgument("This channel has not been added yet")
        else:
            await self.bot.configs.save()

    @commands.slash_command(name="default")
    @commands.has_guild_permissions(manage_guild=True)
    async def parent(self, _):
        """Default settings for created channels"""
        pass

    @parent.sub_command(name="name")
    async def child_name(self, ctx, channel: discord.VoiceChannel, name: str):
        """Sets the default name of an dynamic-voice-channel. See help for more features."""
        await self.configure(channel, "name", name)
        await ctx.send(f"Default name has been set to `{name}`")

    @parent.sub_command(name="limit")
    async def child_limit(self, ctx, channel: discord.VoiceChannel, limit: int = commands.Param(min_value=0, max_value=99)):
        """Sets the default name of an dynamic-voice-channel."""
        await self.configure(channel, "limit", limit)
        await ctx.send(f"Default limit has been set to `{limit}`")

    @parent.sub_command(name="position")
    async def child_position(self, ctx, channel: discord.VoiceChannel, position: commands.option_enum(["bottom", "top", "below", "above"])):
        """Sets the default name of an dynamic-voice-channel."""
        await self.configure(channel, "position", position)
        await ctx.send(f"New channels are now created in the position: `{position}`")

    @parent.sub_command(name="bitrate")
    async def child_bitrate(self, ctx, channel: discord.VoiceChannel, bitrate: int = commands.Param(min_value=8000, max_value=384000)):
        """Sets the default name of an dynamic-voice-channel."""
        limit = int(channel.guild.bitrate_limit)
        if bitrate > limit:
            raise commands.BadArgument(f"Bitrate cannot be higher than {limit}")
        await self.configure(channel, "bitrate", bitrate)
        await ctx.send(f"Default bitrate has been set to `{bitrate}`")

    @parent.sub_command(name="category")
    async def child_category(self, ctx, channel: discord.VoiceChannel, category: discord.CategoryChannel):
        """Sets the default category of an dynamic-voice-channel"""
        await self.configure(channel, "category", category.id)
        await ctx.send(f"Default category has been set to `{category.name}`")


def setup(bot):
    bot.add_cog(Default(bot))
