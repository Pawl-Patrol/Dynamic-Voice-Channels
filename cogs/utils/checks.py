from discord.ext.commands import CheckFailure, check


class NotInVoiceChannel(CheckFailure):
    pass


class ChannelNotEditable(CheckFailure):
    pass


class NotChannelOwner(CheckFailure):
    def __init__(self, owner):
        self.owner = owner


def has_voice_state():
    async def predicate(ctx):
        if ctx.author.voice is None:
            raise NotInVoiceChannel()
        return True

    return check(predicate)


def is_voice_owner():
    async def predicate(ctx):
        owner = ctx.bot.channels.get(ctx.author.voice.channel.id)
        if owner is None:
            raise ChannelNotEditable()
        if ctx.author.id != owner:
            raise NotChannelOwner(owner)
        return True

    return check(predicate)
