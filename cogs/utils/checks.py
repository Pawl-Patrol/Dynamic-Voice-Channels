from discord.ext.commands import CheckFailure, BotMissingPermissions, check
from discord import Permissions


class NotInVoiceChannel(CheckFailure):
    pass


class ChannelNotEditable(CheckFailure):
    pass


class NotChannelOwner(CheckFailure):
    def __init__(self, owner_id):
        self.owner_id = owner_id


def bot_has_voice_permissions(**perms):
    invalid = set(perms) - set(Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError('Invalid permission(s): %s' % (', '.join(invalid)))

    def predicate(ctx):
        guild = ctx.guild
        me = guild.me if guild is not None else ctx.bot.user
        permissions = ctx.author.voice.channel.permissions_for(me)
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]
        if not missing:
            return True
        raise BotMissingPermissions(missing)

    return check(predicate)


def has_voice_state():
    async def predicate(ctx):
        if ctx.author.voice is None:
            raise NotInVoiceChannel()
        return True

    return check(predicate)


def is_voice_owner():
    async def predicate(ctx):
        owner_id = ctx.bot.channels.get(ctx.author.voice.channel.id)
        if owner_id is None:
            raise ChannelNotEditable()
        if ctx.author.id != owner_id:
            raise NotChannelOwner(owner_id)
        return True

    return check(predicate)
