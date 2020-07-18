from contextlib import suppress
from datetime import datetime
from random import choice
from sys import stderr
from traceback import print_tb

from discord import Object, PermissionOverwrite, HTTPException, Forbidden, Embed, Color, Activity, ActivityType
from discord.ext.commands import Bot, CooldownMapping, BucketType, when_mentioned_or, errors
from discord.ext.tasks import loop

from cogs.utils.checks import NotChannelOwner, NotInVoiceChannel, ChannelNotEditable
from cogs.utils.jsonfile import JSONFile

TOKEN = ''
CLIENT_ID = 0
OWNER_ID = 0


def prefix_callable(bot, msg):
    try:
        prefix = bot.configs[msg.guild.id]['prefix']
    except KeyError:
        prefix = 'dvc!'
    return when_mentioned_or(prefix)(bot, msg)


class VoiceCreator(Bot):
    def __init__(self):
        super().__init__(
            command_prefix=prefix_callable,
            help_command=None,
            case_insensitive=True,
            activity=Activity(type=ActivityType.watching, name='dvc!help')
        )
        self.launched_at = None
        self.client_id = CLIENT_ID
        self.configs = JSONFile('data/configs.json')
        self.channels = JSONFile('data/channels.json')
        self.rate_limiter = CooldownMapping.from_cooldown(3, 5, BucketType.user)
        self.load_extension("cogs.settings")
        self.load_extension("cogs.voice")
        self.load_extension("cogs.other")

    async def on_ready(self):
        if self.launched_at is None:
            self.launched_at = datetime.utcnow()
            print('Logged in!')

    async def on_message(self, message):
        if message.guild is None:
            return
        await self.process_commands(message)

    async def on_message_edit(self, before, after):
        if before.content != after.content:
            await self.on_message(after)

    async def on_command_error(self, ctx, error):
        if isinstance(error, errors.CommandNotFound):
            return
        elif isinstance(error, errors.BadArgument):
            return
        elif isinstance(error, errors.ArgumentParsingError) or isinstance(error, errors.MissingRequiredArgument):
            await ctx.send(embed=Embed(
                description=f':x: {error}.',
                color=Color.red()
            ))
        elif isinstance(error, errors.MissingPermissions):
            await ctx.send(embed=Embed(
                description=':x: You do not have permission to use this command.',
                color=Color.red()
            ))
        elif isinstance(error, NotInVoiceChannel):
            await ctx.send(embed=Embed(
                description=':x: You have to be in a voice channel to use this command.',
                color=Color.red()
            ))
        elif isinstance(error, ChannelNotEditable):
            await ctx.send(embed=Embed(
                description=':x: You cannot use this command in this channel.',
                color=Color.red()
            ))
        elif isinstance(error, NotChannelOwner):
            await ctx.send(embed=Embed(
                description=f':x: You have to be the owner of the voice channel to use this command. (<@{error.owner}>)',
                color=Color.red()
            ))
        elif isinstance(error, errors.MaxConcurrencyReached):
            await ctx.send(embed=Embed(
                description=f':x: Another instance of this command is already running.',
                color=Color.red()
            ))
        else:
            if isinstance(error, errors.CommandInvokeError):
                error = error.original
                if isinstance(error, HTTPException):
                    if isinstance(error, Forbidden):
                        with suppress(HTTPException):
                            await ctx.send(embed=Embed(
                                description=':x: I do not have permission to execute this command',
                                color=Color.red()
                            ))
                        return
            print(f'In {ctx.command.qualified_name}:', file=stderr)
            print_tb(error.__traceback__)
            print(f'{error.__class__.__name__}: {error}', file=stderr)

    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if before.channel is not None:
                await self.on_voice_leave(member, before.channel)
            if after.channel is not None:
                await self.on_voice_join(member, after.channel)

    async def on_voice_join(self, member, channel):
        config = self.configs.get(member.guild.id, {})
        if channel.id == config.get('channel', 0):
            fake_message = Object(id=0)
            fake_message.author = member
            bucket = self.rate_limiter.get_bucket(fake_message)
            retry_after = bucket.update_rate_limit()
            if retry_after:
                with suppress(HTTPException):
                    member.send(f'You are being rate limited. Try again in `{retry_after:.2f}` seconds.')
            else:
                name = config.get('name', "@user's channel").replace('@user', member.display_name)
                limit = config.get('limit', 10)
                category = member.guild.get_channel(config.get('category', 0))
                if category is None:
                    category = channel.category
                overwrites = channel.overwrites.copy()
                overwrites[member] = PermissionOverwrite(manage_channels=True)
                try:
                    new_channel = await member.guild.create_voice_channel(
                        name=name,
                        overwrites=overwrites,
                        category=category,
                        user_limit=limit,
                    )
                except HTTPException:
                    return
                else:
                    self.channels[new_channel.id] = member.id
                    await self.channels.save()
                    if config.get('top', False):
                        self.loop.create_task(new_channel.edit(position=0))
                        self.loop.create_task(member.move_to(new_channel))
                    else:
                        with suppress(HTTPException):
                            await member.move_to(new_channel)

    async def on_voice_leave(self, member, channel):
        if channel.id in self.channels:
            if len(channel.members) == 0:
                with suppress(HTTPException):
                    await channel.delete()
                del self.channels[channel.id]
                await self.channels.save()
            elif member.id == self.channels[channel.id]:
                new_owner = choice(channel.members)
                self.channels[channel.id] = new_owner.id
                await self.channels.save()


if __name__ == "__main__":
    VoiceCreator().run(TOKEN)
