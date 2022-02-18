import collections
import os
import re
import time
import random
from contextlib import suppress
from datetime import datetime

import disnake as discord
from disnake.ext import commands

from .utils import data


intents = discord.Intents(
    guilds=True,
    members=True,
    voice_states=True,
    guild_messages=True,
)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            intents=intents,
            activity=discord.Game("click me and invite me again for slash commands"),
            allowed_mentions=discord.AllowedMentions.none()
        )

        self.launched_at = None

        if not os.path.exists("./data"):
            os.mkdir("./data")

        self.configs = data.Dict("./data/configs.json")
        self.channels = data.List("./data/channels.json")
        self.blacklists = data.Dict("./data/blacklists.json")

        self.spam_control = {}
        self.spam_counter = collections.Counter()

        for filename in os.listdir("./bot/ext"):
            if filename.endswith(".py"):
                self.load_extension("bot.ext." + filename[:-3])
                print("loaded", filename)

    async def prepare(self):
        channels = self.channels.copy()
        self.channels.clear()
        for guild in self.guilds:
            for channel in guild.voice_channels:
                if channel.id in channels:
                    if len(channel.members) == 0:
                        await channel.delete()
                    else:
                        self.channels.append(channel.id)
                elif str(channel.id) in self.configs:
                    for member in channel.members:
                        await self.on_voice_join(member, channel)
        await self.channels.save()

        # migration from old to new framework
        for key in self.configs.keys():
            if "top" in self.configs[key]:
                self.configs[key]["position"] = "top" if self.configs[key]["top"] else "bottom"
                del self.configs[key]["top"]
        await self.configs.save()

    async def on_ready(self):
        if self.launched_at is None:
            self.launched_at = datetime.utcnow()
            await self.prepare()
            print("Logged in as", self.user)
            print("ID:", self.user.id)

    async def process_commands(self, message):
        return

    async def get_owner(self):
        if self.owner_id:
            owner = self.get_user(self.owner_id)
            if owner is not None:
                return owner
        app = await self.application_info()
        self.owner_id = app.owner.id
        return app.owner

    def get_settings(self, channel):
        settings = self.configs[str(channel.id)].copy()  # we don't want data stored that can be defaulted

        settings.setdefault("name", "@user's channel")
        settings.setdefault("limit", channel.user_limit)
        settings.setdefault("bitrate", channel.bitrate)
        settings.setdefault("position", "bottom")
        settings.setdefault("category", channel.category.id if channel.category else None)

        return settings

    def update_rate_limit(self, key):
        now = time.monotonic()
        if key in self.spam_control:
            time_passed = now - self.spam_control[key]
        else:
            time_passed = None
        self.spam_control[key] = now
        return time_passed

    async def on_voice_join(self, member, channel):
        if str(channel.id) not in self.configs:
            return
        # RATE LIMIT CHECK (3 time within 15 seconds)
        now = time.monotonic()
        mkey = str(member.id)
        if mkey in self.spam_control:
            time_passed = now - self.spam_control[mkey]
            if time_passed < 15.0:
                self.spam_counter[member.id] += 1
                if self.spam_counter[member.id] >= 3:
                    retry_after = 15.0 - time_passed
                    return await member.send(f"You are being rate limited. Try again in `{retry_after:.2f}` seconds.")
            else:
                del self.spam_counter[member.id]
        self.spam_control[mkey] = now

        settings = self.get_settings(channel)
        name = settings["name"]
        category = member.guild.get_channel(settings["category"])

        # figure out position
        if settings["position"] == "top":
            position = 0
        elif settings["position"] == "below":
            position = channel.position + 1
        elif settings["position"] == "above":
            position = channel.position
        else:
            position = discord.utils.MISSING

        # SUBSTITUTION
        if "@user" in name:
            name = name.replace("@user", member.display_name)

        if "@position" in name:
            channels = [c for c in category.voice_channels if c.id in self.channels]
            name = name.replace("@position", str(len(channels) + 1))

        name = re.sub(r"@\[([^\]]+)\]", lambda m: random.choice(m[1].split(",")), name)

        # -------------------------------------------------
        # NO LONGER SUPPORTED DUE TO MISSING INTENTS
        # UNCOMMENT IF YOU HAVE THE PRESENCE INTENT ENABLED
        # if '@game' in name:
        #     for activity in member.activities:
        #         if activity.type == discord.ActivityType.playing and activity.name is not None:
        #             name = name.replace('@game', activity.name)
        #             break
        #     else:
        #         name = name.replace('@game', 'no game')
        # -------------------------------------------------

        # BLACKLISTED WORDS
        blacklist = self.blacklists.get(str(member.guild.id), [])
        for word in blacklist:
            if word.casefold() in name.casefold():
                name = re.sub(word, '*' * len(word), name, flags=re.IGNORECASE)

        # OVERFLOW
        if len(name) > 100:
            name = name[:97] + '...'

        overwrites = channel.overwrites
        overwrites[member] = discord.PermissionOverwrite(
            manage_channels=True,
            view_channel=True,
            connect=True,
            speak=True
        )

        new_channel = await member.guild.create_voice_channel(
            name=name,
            category=category,
            position=position,
            bitrate=settings["bitrate"],
            user_limit=settings["limit"],
            rtc_region=channel.rtc_region,
            video_quality_mode=channel.video_quality_mode,
            overwrites=overwrites
        )

        await member.move_to(new_channel)
        self.channels.append(new_channel.id)
        await self.channels.save()

    async def on_voice_leave(self, channel):
        if channel.id in self.channels:
            if len(channel.members) == 0:
                await channel.delete()
                # no need to remove from self.channels because of on_guild_channel_delete

    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if before.channel is not None:
                # check for delted channel
                if member.guild.get_channel(before.channel.id) is None:
                    return
                await self.on_voice_leave(before.channel)
            if after.channel is not None:
                await self.on_voice_join(member, after.channel)

    async def on_guild_channel_delete(self, channel):
        if channel.id in self.channels:
            self.channels.remove(channel.id)
            await self.channels.save()

        key = str(channel.id)
        if key in self.configs:
            self.configs.pop(key)
            await self.configs.save()

    async def on_guild_remove(self, guild):
        with suppress(KeyError):
            self.blacklists.pop(str(guild.id))

        for channel in guild.voice_channels:
            if channel.id in self.channels:
                self.channels.remove(channel.id)
            if str(channel.id) in self.configs:
                self.configs.pop(str(channel.id))

        await self.channels.save()
        await self.configs.save()

    async def on_slash_command_error(self, ctx, error):
        await ctx.send(str(error), ephemeral=True)
