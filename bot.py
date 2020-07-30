from contextlib import suppress
from datetime import datetime
from itertools import cycle
from logging import FileHandler, Formatter, INFO, getLogger
from random import choice

from aiohttp import ClientSession
from discord import Object, PermissionOverwrite, HTTPException, Embed, Color, Activity, ActivityType
from discord.ext.commands import Bot, CooldownMapping, BucketType, when_mentioned_or, errors
from discord.ext.tasks import loop

import config
from cogs.utils.checks import NotChannelOwner, NotInVoiceChannel, ChannelNotEditable
from cogs.utils.converters import CannotFindCommand, IntNotInRange, StrNotInRange
from cogs.utils.jsonfile import JSONFile


def prefix_callable(bot, msg):
    try:
        prefix = bot.configs[msg.guild.id]['prefix']
    except KeyError:
        prefix = bot.default_prefix
    return when_mentioned_or(prefix)(bot, msg)


class VoiceCreator(Bot):
    def __init__(self):
        super().__init__(
            command_prefix=prefix_callable,
            help_command=None,
            case_insensitive=True,
            owner_id=config.owner_id
        )
        self.default_prefix = config.default_prefix
        self.launched_at = None
        self.logger = getLogger()
        self.init_logger()
        self.client_id = config.client_id
        self.activities = cycle(["dvc!help", "dvc!invite", "{guilds} guilds", "{channels} channels", "{users} users"])
        self.session = ClientSession(loop=self.loop)
        self.configs = JSONFile('data/configs.json')
        self.channels = JSONFile('data/channels.json')
        self.rate_limiter = CooldownMapping.from_cooldown(3, 5, BucketType.user)
        self.load_extension("cogs.settings")
        self.load_extension("cogs.voice")
        self.load_extension("cogs.other")

    def init_logger(self):
        handler = FileHandler('logs.log')
        formatter = Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def on_ready(self):
        if self.launched_at is None:
            self.launched_at = datetime.utcnow()
            self.update_presence.start()
            self.update_stats.start()
            print('Logged in!')

    @loop(seconds=15)
    async def update_presence(self):
        activity = next(self.activities).format(
            guilds=len(self.guilds),
            channels=len(self.channels),
            users=len(self.users)
        )
        await self.change_presence(activity=Activity(type=ActivityType.watching, name=activity))

    @loop(minutes=30)
    async def update_stats(self):
        headers = {'Authorization': 'Bot ' + config.discord_bot_list_key}
        data = {
            'guilds': len(self.guilds),
            'users': len(self.users)
        }
        url = 'https://discordbotlist.com/api/v1/bots/' + str(self.user.id) + '/stats'
        await self.session.post(url=url, json=data, headers=headers)
        self.logger.info("Updated discordbotlist.com stats")

    async def on_guild_join(self, guild):
        self.logger.warning(f'Joined guild "{guild.name}" with {guild.member_count} users (ID: {guild.id})')

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
        elif isinstance(error, errors.UserInputError):
            if isinstance(error, CannotFindCommand):
                msg = f'No command called **{error.argument}** found.'
                if error.close is not None:
                    msg += f' Did you mean **{error.close.title()}**?'
            elif isinstance(error, IntNotInRange):
                msg = f'The given number must be in the range from {error.minimum} to {error.maximum}.'
            elif isinstance(error, StrNotInRange):
                msg = f'The given argument must be longer than {error.minimum} and less than {error.maximum} characters.'
            else:
                msg = str(error)
        elif isinstance(error, errors.CheckFailure):
            if isinstance(error, NotInVoiceChannel):
                msg = ':x: You have to be in a voice channel to use this command.'
            elif isinstance(error, ChannelNotEditable):
                msg = ':x: You cannot use this command in this channel.'
            elif isinstance(error, NotChannelOwner):
                msg = f'You have to be the owner of the voice channel to use this command. (<@{error.owner_id}>)'
            elif isinstance(error, errors.NoPrivateMessage):
                msg = 'You cannot use this command in private messages.'
            elif isinstance(error, errors.MissingPermissions):
                perms = ', '.join(f'`{perm}`' for perm in error.missing_perms)
                msg = f'You need the {perms} permission(s) to use this command.'
            elif isinstance(error, errors.BotMissingPermissions):
                perms = ', '.join(f'`{perm}`' for perm in error.missing_perms)
                msg = f'The bot needs the {perms} permission(s) to execute this command.'
            else:
                return
        elif isinstance(error, errors.DisabledCommand):
            msg = 'This command is currently disabled.'
        elif isinstance(error, errors.CommandOnCooldown):
            msg = f'You are being rate limited. Try again in `{error.retry_after:.2f}` seconds.'
        elif isinstance(error, errors.MaxConcurrencyReached):
            msg = 'Another instance of this command is already running.'
        else:
            msg = 'An uncaught error occurred! My programmer has been informed and will fix the error.'
            self.logger.error('Uncaught exception', exc_info=(error.__class__.__name__, error, error.__traceback__))
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if perms.send_messages:
            if perms.embed_links:
                await ctx.send(embed=Embed(
                    description=msg.capitalize(),
                    color=Color.red()
                ))
            else:
                await ctx.send(msg)

    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if before.channel is not None:
                await self.on_voice_leave(member, before.channel)
            if after.channel is not None:
                await self.on_voice_join(member, after.channel)

    async def on_voice_join(self, member, channel):
        cfg = self.configs.get(member.guild.id, {})
        if channel.id == cfg.get('channel', 0):
            fake_message = Object(id=0)
            fake_message.author = member
            bucket = self.rate_limiter.get_bucket(fake_message)
            retry_after = bucket.update_rate_limit()
            if retry_after:
                with suppress(HTTPException):
                    await member.send(f'You are being rate limited. Try again in `{retry_after:.2f}` seconds.')
            else:
                name = cfg.get('name', "@user's channel").replace('@user', member.display_name)
                limit = cfg.get('limit', 10)
                category = member.guild.get_channel(cfg.get('category', 0))
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
                    if cfg.get('top', False):
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
    VoiceCreator().run(config.token)
