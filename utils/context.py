import discord
from discord.ext import commands


class Context(commands.Context):
    async def safe_send(self, msg, color):
        permissions = self.channel.permissions_for(self.guild.me)
        if permissions.embed_links:
            await self.send(embed=discord.Embed(description=msg, color=color))
        else:
            await self.send(msg)

    async def set_voice_permissions(self, target, **perms):
        overwrite = self.author.voice.channel.overwrites.pop(target, discord.PermissionOverwrite())
        overwrite.update(**perms)
        if overwrite.is_empty():
            await self.author.voice.channel.set_permissions(target, overwrite=None)
        else:
            await self.author.voice.channel.set_permissions(target, overwrite=overwrite)
