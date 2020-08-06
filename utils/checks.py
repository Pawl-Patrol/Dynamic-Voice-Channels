import discord
from discord.ext import commands
from .exceptions import NotInVoiceChannel


def connected_to_voice():
    def predicate(ctx):
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            raise NotInVoiceChannel()
        return True

    return commands.check(predicate)


def has_voice_permissions(**perms):
    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError('Invalid permission(s): %s' % (', '.join(invalid)))

    def predicate(ctx):
        permissions = ctx.author.voice.channel.permissions_for(ctx.author)
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]
        if missing:
            raise commands.MissingPermissions(missing)
        return True

    return commands.check(predicate)


def bot_has_voice_permissions(**perms):
    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError('Invalid permission(s): %s' % (', '.join(invalid)))

    def predicate(ctx):
        permissions = ctx.author.voice.channel.permissions_for(ctx.guild.me)
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]
        if missing:
            raise commands.BotMissingPermissions(missing)
        return True

    return commands.check(predicate)
