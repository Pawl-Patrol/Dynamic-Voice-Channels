import discord
from discord.ext import commands
from utils.checks import connected_to_voice, has_voice_permissions, bot_has_voice_permissions
from utils.converters import StrRange, IntRange
import typing


class BucketType(commands.BucketType):
    def get_key(self, msg):
        return msg.author.voice.channel.id


class Voice(commands.Cog):
    @commands.command()
    @commands.cooldown(2, 600, BucketType.channel)
    @bot_has_voice_permissions(manage_channels=True)
    @has_voice_permissions(manage_channels=True)
    @connected_to_voice()
    async def name(self, ctx, *, name: StrRange(2, 100)):
        """Sets your voice channel's name.
        The name needs to be between 2 and 100 characters in length.
        """
        before = discord.utils.escape_markdown(ctx.author.voice.channel.name)
        words = ctx.bot.bad_words.get(str(ctx.guild.id), [])
        for word in words:
            if word in name:
                name = name.replace(word, '*'*len(word))
        await ctx.author.voice.channel.edit(name=name)
        await ctx.safe_send(
            msg=f'Changed your voice channel\'s name from **{before}** to **{discord.utils.escape_markdown(name)}**.',
            color=discord.Color.green()
        )

    @commands.command(aliases=['userlimit'])
    @bot_has_voice_permissions(manage_channels=True)
    @has_voice_permissions(manage_channels=True)
    @connected_to_voice()
    async def limit(self, ctx, number: IntRange(0, 99)):
        """Sets your voice channel's user limit.
        The limit has to be in range of 0 to 99.
        Use 0 to remove the user limit.
        """
        before = ctx.author.voice.channel.user_limit
        await ctx.author.voice.channel.edit(user_limit=number)
        await ctx.safe_send(
            msg=f'Changed your voice channel\'s limit from `{before}` to `{number}`.',
            color=discord.Color.green()
        )

    @commands.command()
    @bot_has_voice_permissions(manage_channels=True)
    @has_voice_permissions(manage_channels=True)
    @connected_to_voice()
    async def bitrate(self, ctx, number: IntRange(8000, 384000)):
        """Sets your voice channel's bitrate.
        The bitrate has to be in range of 8000 to your server's bitrate limit.
        """
        if number > ctx.guild.bitrate_limit:
            await ctx.safe_send(
                msg=f'The bitrate cannot be greater than `{int(ctx.guild.bitrate_limit)}`.',
                color=discord.Color.red()
            )
        else:
            before = ctx.author.voice.channel.bitrate
            await ctx.author.voice.channel.edit(bitrate=number)
            await ctx.safe_send(
                msg=f'Changed your voice channel\'s bitrate from `{before}` to `{number}`.',
                color=discord.Color.green()
            )

    @commands.command(usage='[member|role]')
    @bot_has_voice_permissions(manage_roles=True)
    @has_voice_permissions(manage_roles=True)
    @connected_to_voice()
    async def close(self, ctx, *, target: typing.Union[discord.Member, discord.Role] = None):
        """
        Denies a target to `connect` to your channel.
        The target can either be a member or role.
        If you don't specify a target it applies for everyone.

        **__Examples__**:
        > `{prefix}close` -> Closes the channel for @everyone
        > `{prefix}close @user` -> Closes the channel for @user
        > `{prefix}close @role` -> Closes the channel for @role
        """
        if target is None:
            target = ctx.guild.default_role
            mention = 'everyone'
        else:
            if isinstance(target, discord.Member) and target != ctx.author:
                perms = ctx.author.voice.channel.permissions_for(ctx.guild.me)
                if perms.move_members:
                    ctx.bot.loop.create_task(target.move_to(None))
            mention = target.mention
        await ctx.set_voice_permissions(target, connect=False)
        await ctx.safe_send(
            msg=f'Closed your channel for {mention}.',
            color=discord.Color.green()
        )

    @commands.command(usage='[member|role]')
    @bot_has_voice_permissions(manage_roles=True)
    @has_voice_permissions(manage_roles=True)
    @connected_to_voice()
    async def open(self, ctx, *, target: typing.Union[discord.Member, discord.Role] = None):
        """
        Removes the `connect` overwrite for a target in your channel.
        The target can either be a member or role.
        If you don't specify a target it applies for everyone.

        **__Examples__**:
        > `{prefix}open` -> Opens the channel for @everyone
        > `{prefix}open @user` -> Opens the channel for @user
        > `{prefix}open @role` -> Opens the channel for @role
        """
        if target is None:
            target = ctx.guild.default_role
            mention = 'everyone'
        else:
            mention = target.mention
        await ctx.set_voice_permissions(target, connect=None)
        await ctx.safe_send(
            msg=f'Opened your channel for {mention}.',
            color=discord.Color.green()
        )

    @commands.command(usage='[member|role]')
    @bot_has_voice_permissions(manage_roles=True)
    @has_voice_permissions(manage_roles=True)
    @connected_to_voice()
    async def grant(self, ctx, *, target: typing.Union[discord.Member, discord.Role] = None):
        """
        Allows a target to `connect` to your channel.
        Should be used after using the `close` command so only certain people can join.
        The target can either be a member or role.
        If you don't specify a target it applies for everyone.

        **__Examples__**:
        > `{prefix}grant` -> Grants @everyone to join your channel (Better use `open` instead)
        > `{prefix}grant @user` -> Grants @user to join your channel
        > `{prefix}grant @role` -> Grants @role to join your channel
        """
        if target is None:
            target = ctx.guild.default_role
            mention = 'everyone'
        else:
            mention = target.mention
        await ctx.set_voice_permissions(target, connect=True)
        await ctx.safe_send(
            msg=f'Granted {mention} to join your channel.',
            color=discord.Color.green()
        )

    @commands.command(usage='[member|role]')
    @bot_has_voice_permissions(manage_roles=True)
    @has_voice_permissions(manage_roles=True)
    @connected_to_voice()
    async def hide(self, ctx, *, target: typing.Union[discord.Member, discord.Role] = None):
        """
        Makes your channel hidden for a certain target.
        The target can either be a member or role.
        If you don't specify a target it applies for everyone.

        **__Examples__**:
        > `{prefix}hide` -> Hides your channel for @everyone
        > `{prefix}hide @user` -> Hides your channel for @user
        > `{prefix}hide @role` -> Hides your channel for @role
        """
        if target is None:
            target = ctx.guild.default_role
            mention = 'everyone'
        else:
            mention = target.mention
        await ctx.set_voice_permissions(target, view_channel=False)
        await ctx.safe_send(
            msg=f'Your channel is now hidden for {mention}.',
            color=discord.Color.green()
        )

    @commands.command(usage='[member|role]')
    @bot_has_voice_permissions(manage_roles=True)
    @has_voice_permissions(manage_roles=True)
    @connected_to_voice()
    async def unhide(self, ctx, *, target: typing.Union[discord.Member, discord.Role] = None):
        """
        Makes your channel no longer hidden for a certain target.
        The target can either be a member or role.
        If you don't specify a target it applies for everyone.

        **__Examples__**:
        > `{prefix}unhide` -> Unhides your channel for @everyone
        > `{prefix}unhide @user` -> Unhides your channel for @user (Better use `show` instead)
        > `{prefix}unhide @role` -> Unhides your channel for @role (Better use `show` instead)
        """
        if target is None:
            target = ctx.guild.default_role
            mention = 'everyone'
        else:
            mention = target.mention
        await ctx.set_voice_permissions(target, view_channel=None)
        await ctx.safe_send(
            msg=f'Your channel is no longer hidden for {mention}.',
            color=discord.Color.green()
        )

    @commands.command(usage='[member|role]')
    @bot_has_voice_permissions(manage_roles=True)
    @has_voice_permissions(manage_roles=True)
    @connected_to_voice()
    async def show(self, ctx, *, target: typing.Union[discord.Member, discord.Role] = None):
        """
        Makes your channel visible for a certain target.
        The target can either be a member or role.
        If you don't specify a target it applies for everyone.

        **__Examples__**:
        > `{prefix}show` -> Makes your channel visible for @everyone (Better use `unhide` instead)
        > `{prefix}show @user` -> Makes your channel visible for @user
        > `{prefix}show @role` -> Makes your channel visible for @role
        """
        if target is None:
            target = ctx.guild.default_role
            mention = 'everyone'
        else:
            mention = target.mention
        await ctx.set_voice_permissions(target, view_channel=True)
        await ctx.safe_send(
            msg=f'Your channel now visible for {mention}.',
            color=discord.Color.green()
        )

    @commands.command()
    @bot_has_voice_permissions(move_members=True)
    @has_voice_permissions(move_members=True)
    @connected_to_voice()
    async def kick(self, ctx, *, member: discord.Member):
        """Kicks a member from your voice channel."""
        if member == ctx.author:
            raise commands.BadArgument('You cannot kick yourself.')
        elif member not in ctx.author.voice.channel.members:
            raise commands.BadArgument('This member is not in your channel.')
        else:
            await member.move_to(None)
            await ctx.safe_send(
                msg=f'Kicked {member.mention} from your channel.',
                color=discord.Color.green()
            )

    @commands.command()
    @bot_has_voice_permissions(manage_roles=True)
    @has_voice_permissions(manage_roles=True)
    @connected_to_voice()
    async def permit(self, ctx, *, member: discord.Member):
        """Gives a certain member the `manage channel` permission.
        The member is then the co-owner of your channel.
        This cannot be undone since the original owner is not saved.
        """
        await ctx.set_voice_permissions(member, manage_channels=True, move_members=True, manage_roles=True)
        await ctx.safe_send(
            msg=f'Gave {member.mention} permissions.',
            color=discord.Color.green()
        )

    @commands.command()
    @bot_has_voice_permissions(manage_roles=True)
    @has_voice_permissions(manage_roles=True)
    @connected_to_voice()
    async def transfer(self, ctx, *, member: discord.Member):
        """Transfers your ownership to another member.
        This means you lose your `manage channel` permission.
        Use `permit` instead if you want to keep your permissions.
        """
        overwrites = ctx.author.voice.channel.overwrites.copy()
        overwrite = overwrites.pop(ctx.author, discord.PermissionOverwrite())
        overwrite.update(manage_channels=None, move_members=None, manage_roles=None)
        if not overwrite.is_empty():
            overwrites[ctx.author] = overwrite
        overwrite = overwrites.pop(member, discord.PermissionOverwrite())
        overwrite.update(manage_channels=True, move_members=True, manage_roles=True)
        overwrites[member] = overwrite
        await ctx.author.voice.channel.edit(overwrites=overwrites)
        await ctx.safe_send(
            msg=f'Transferred permissions to {member.mention}.',
            color=discord.Color.green()
        )

    @commands.command()
    @bot_has_voice_permissions(manage_roles=True)
    @connected_to_voice()
    async def claim(self, ctx):
        """Claim ownership of your channel.
        You can only claim the channel if nobody else in your channel has the `manage channels` permission.
        """
        for target, overwrite in ctx.author.voice.channel.overwrites.items():
            if isinstance(target, discord.Member) and overwrite.manage_channels:
                await ctx.safe_send(
                    msg=f'You cannot claim the permissions of your channel.',
                    color=discord.Color.red()
                )
                break
        else:
            await ctx.set_voice_permissions(ctx.author, manage_channels=True)
            await ctx.safe_send(
                msg='You claimed the permissions of your voice channel.',
                color=discord.Color.green()
            )


def setup(bot):
    bot.add_cog(Voice())
