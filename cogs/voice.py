from discord import Embed, Color, Member
from discord.ext.commands import Cog, command

from .utils.checks import has_voice_state, is_voice_owner
from .utils.converters import StrRange, IntRange


class Voice(Cog):
    @command(aliases=["nick"])
    @is_voice_owner()
    @has_voice_state()
    async def name(self, ctx, *, name: StrRange(2, 100)):
        """Sets your voice channel's name.
        You have to be the owner of the channel you are in.
        The name must not be shorter than 2 characters and longer than 100 characters.
        """
        before = ctx.author.voice.channel.name
        await ctx.author.voice.channel.edit(name=name)
        await ctx.send(embed=Embed(
            description=f":white_check_mark: Changed your voice channel's name from `{before}` to `{name}`.",
            color=Color.green()
        ))

    @command(aliases=['userlimit'])
    @is_voice_owner()
    @has_voice_state()
    async def limit(self, ctx, number: IntRange(0, 99)):
        """Sets your voice channel's user limit.
        You have to be the owner of the channel you are in.
        Use 0 to set the user limit to unlimited.
        The limit must be between 0 and 99.
        """
        before = ctx.author.voice.channel.user_limit
        await ctx.author.voice.channel.edit(user_limit=number)
        await ctx.send(embed=Embed(
            description=f":white_check_mark: Changed your voice channel's limit from `{before}` to `{number}`.",
            color=Color.green()
        ))

    @command(aliases=['close'])
    @is_voice_owner()
    @has_voice_state()
    async def lock(self, ctx):
        """Locks your voice channel so no one can join.
        You have to be the owner of the channel you are in.
        """
        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, connect=False)
        await ctx.send(embed=Embed(
            description=':lock: Successfully locked your voice channel.',
            color=Color.green()
        ))

    @command(aliases=['open'])
    @is_voice_owner()
    @has_voice_state()
    async def unlock(self, ctx):
        """Unlocks your voice channel so members can join again.
        You have to be the owner of the channel you are in.
        """
        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, connect=None)
        await ctx.send(embed=Embed(
            description=':unlock: Successfully unlocked your voice channel.',
            color=Color.green()
        ))

    @command()
    @is_voice_owner()
    @has_voice_state()
    async def kick(self, ctx, *, member: Member):
        """Kicks a member from your voice channel.
        You have to be the owner of the channel you are in.
        """
        if member not in ctx.author.voice.channel.members:
            await ctx.send(embed=Embed(
                description=':x: This member is not in your voice channel.',
                color=Color.red()
            ))
        else:
            await member.move_to(None)
            await ctx.send(embed=Embed(
                description=f':boot: Kicked {member.mention} from your voice channel.',
                color=Color.green()
            ))

    @command(aliases=['ban', 'deny'])
    @is_voice_owner()
    @has_voice_state()
    async def reject(self, ctx, *, member: Member):
        """Bans a member from your voice channel.
        You have to be the owner of the channel you are in.
        """
        await ctx.author.voice.channel.set_permissions(member, connect=False)
        if member in ctx.author.voice.channel.members:
            await member.move_to(None)
        await ctx.send(embed=Embed(
            description=f':white_check_mark: {member.mention} no longer has access to the voice channel.',
            color=Color.green()
        ))

    @command(aliases=['unban', 'allow'])
    @is_voice_owner()
    @has_voice_state()
    async def permit(self, ctx, *, member: Member):
        """Unbans a member from your voice channel.
        You have to be the owner of the channel you are in.
        """
        await ctx.author.voice.channel.set_permissions(member, connect=True)
        await ctx.send(embed=Embed(
            description=f':white_check_mark: {member.mention} now has access to the voice channel again.',
            color=Color.green()
        ))

    @command(aliases=['invisible'])
    @is_voice_owner()
    @has_voice_state()
    async def hide(self, ctx):
        """Hides your voice channel from other members.
        You have to be the owner of the channel you are in.
        """
        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await ctx.send(embed=Embed(
            description=':dash: Your voice channel is now hidden.',
            color=Color.green()
        ))

    @command(aliases=['show', 'visible'])
    @is_voice_owner()
    @has_voice_state()
    async def unhide(self, ctx):
        """Makes your voice channel no longer hidden.
        You have to be the owner of the channel you are in.
        """
        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, view_channel=None)
        await ctx.send(embed=Embed(
            description=':eye: Your voice channel is no longer hidden.',
            color=Color.green()
        ))

    @command(aliases=['give', 'owner'])
    @is_voice_owner()
    @has_voice_state()
    async def transfer(self, ctx, *, member: Member):
        """Transfers your ownership to another user."""
        ctx.bot.channels[ctx.author.voice.channel.id] = member.id
        await ctx.bot.channels.save()
        await ctx.send(embed=Embed(
            description=f':white_check_mark: Successfully transferred the ownership to {member.mention}.',
            color=Color.green()
        ))

    @command()
    @has_voice_state()
    async def claim(self, ctx):
        """Transfers your ownership to another user."""
        owner_id = ctx.bot.channels[ctx.author.voice.channel.id]
        for member in ctx.author.voice.channel.members:
            if member.id == owner_id:
                await ctx.send("You cannot claim the ownership because the owner is still in your voice channel. "
                               f"[{member.mention}]")
                break
        else:
            ctx.bot.channels[ctx.author.voice.channel.id] = ctx.author.id
            await ctx.bot.channels.save()
            await ctx.send(embed=Embed(
                description=f':white_check_mark: You claimed the ownership of your voice channel.',
                color=Color.green()
            ))


def setup(bot):
    bot.add_cog(Voice())
