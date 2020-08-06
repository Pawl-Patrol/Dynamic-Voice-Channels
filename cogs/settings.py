import discord
from discord.ext import commands, menus
import config
import asyncio
from functools import cached_property
import inspect


NAME = config.emojis['name']
LIMIT = config.emojis['limit']
POSITION = config.emojis['position']
CATEGORY = config.emojis['category']
HELP = config.emojis['help']
EXIT = config.emojis['exit']


class EditMenu(menus.Menu):
    def __init__(self, channel):
        super().__init__(timeout=60, delete_message_after=True, check_embeds=True)
        self.channel = channel
        self.help = False

    def get_settings(self):
        return self.bot.configs.get(str(self.channel.id), {})

    async def set_settings(self, name, value):
        settings = self.get_settings()
        settings[name] = value
        self.bot.configs[str(self.channel.id)] = settings
        await self.bot.configs.save()

    @cached_property
    def main_menu(self):
        embed = discord.Embed(
            description=f'Editing **{self.channel.name}**',
            color=self.ctx.guild.me.color
        )
        embed.set_author(name=self.ctx.author, icon_url=self.ctx.author.avatar_url)
        embed.set_footer(text='Please react with an emoji to continue.')
        entries = []
        for emoji, button in self.buttons.items():
            entries.append(f'{emoji} {inspect.getdoc(button.action)}')
        embed.add_field(name='Options:', value='\n'.join(entries))
        return embed

    async def send_initial_message(self, ctx, channel):
        return await ctx.send(embed=self.main_menu)

    async def wait_for_message(self):
        message = await self.bot.wait_for(
            'message',
            check=lambda m: m.author == self.ctx.author and m.channel == self.ctx.channel,
            timeout=60
        )
        if not self._running:
            raise asyncio.TimeoutError()
        return message

    async def clean_up(self, to_delete):
        if self.ctx.channel.permissions_for(self.ctx.guild.me).manage_messages:
            await self.ctx.channel.delete_messages(to_delete)

    @menus.button(NAME, position=menus.Position(1))
    async def on_name(self, _):
        """Changes the default name"""
        msg = 'Please type the name you want to set.'
        to_delete = []
        while True:
            to_delete.append(await self.ctx.send(msg))
            try:
                message = await self.wait_for_message()
            except asyncio.TimeoutError:
                return
            to_delete.append(message)
            if len(message.content) < 2:
                msg = 'The name cannot be less than 2 characters. Try again.'
            else:
                await self.set_settings('name', message.content)
                to_delete.append(await self.ctx.send('Name has been updated.'))
                await asyncio.sleep(3)
                break
        self.bot.loop.create_task(self.clean_up(to_delete))

    @menus.button(LIMIT, position=menus.Position(2))
    async def on_limit(self, _):
        """Sets the default limit"""
        msg = 'Please type the limit you want to set.'
        to_delete = []
        while True:
            to_delete.append(await self.ctx.send(msg))
            try:
                message = await self.wait_for_message()
            except asyncio.TimeoutError:
                return
            to_delete.append(message)
            try:
                number = int(message.content)
            except ValueError:
                msg = 'This is not a number. Try again.'
            else:
                if not 0 <= number <= 99:
                    msg = 'The limit must be between 0 and 99. Try again'
                else:
                    await self.set_settings('limit', number)
                    to_delete.append(await self.ctx.send('Limit has been updated.'))
                    await asyncio.sleep(3)
                    break
        self.bot.loop.create_task(self.clean_up(to_delete))

    @menus.button(POSITION, position=menus.Position(3))
    async def on_position(self, _):
        """Changes the position."""
        top = not self.get_settings().get('top', False)
        await self.set_settings('top', top)
        pos = 'top' if top else 'bottom'
        await self.ctx.send(f'New channels are now created at the {pos}.', delete_after=3)

    @menus.button(CATEGORY, position=menus.Position(4))
    async def on_category(self, _):
        """Sets the category"""
        msg = 'Please type the name or id of the category you want to set.'
        to_delete = []
        while True:
            to_delete.append(await self.ctx.send(msg))
            try:
                message = await self.wait_for_message()
            except asyncio.TimeoutError:
                return
            to_delete.append(message)
            try:
                category_id = int(message.content)
            except ValueError:
                for category in self.ctx.guild.categories:
                    if category.name.casefold() == message.content.casefold():
                        category_id = category.id
                        break
                else:
                    msg = f'Category "{message.content}" not found. Try again'
                    continue
            await self.set_settings('category', category_id)
            to_delete.append(await self.ctx.send('Category has been updated.'))
            await asyncio.sleep(3)
            break
        self.bot.loop.create_task(self.clean_up(to_delete))

    @menus.button(HELP, position=menus.Position(7))
    async def on_help(self, _):
        """Shows you information"""
        if self.help:
            await self.message.edit(embed=self.main_menu)
            self.help = False
        else:
            embed = discord.Embed(
                title=f'Information',
                description='In this menu you can change the auto-channel settings.\n'
                            'You can use the buttons below to do the following actions:',
                color=self.ctx.guild.me.color
            )
            embed.set_author(name=self.ctx.author, url=self.ctx.author.avatar_url)
            settings = self.get_settings()
            name = settings.get('name', '@user\'s channel')
            embed.add_field(
                name=f'{NAME} Change the default name ({name})',
                value='Lets you change the default name for created channels.\n'
                      'Use @user to reference the user who created the channel.\n'
                      'Use @game to reference the game the user is playing.\n'
                      'Use @position to reference the amount of created channels in this category.',
                inline=False
            )
            limit = settings.get('limit', 10)
            embed.add_field(
                name=f'{LIMIT} Set the default limit ({limit})',
                value='Sets the default limit for created channels.\n'
                      'Must be between `0` and `99`. Use `0` to remove the user limit.',
                inline=False
            )
            pos = 'top' if settings.get('top', False) else 'bottom'
            embed.add_field(
                name=f'{POSITION} Change the position ({pos})',
                value='Changes the position channels are created at.\n'
                      'This can either be above or below the auto-channel.',
                inline=False
            )
            try:
                category = self.ctx.guild.get_channel(settings['category'])
            except KeyError:
                category = self.channel.category
            if category is None:
                category = 'No category'
            else:
                category = category.name
            embed.add_field(
                name=f'{CATEGORY} Set the category ({category})',
                value='Lets you change the category new channels are created in.\n',
                inline=False
            )
            await self.message.edit(embed=embed)
            self.help = True

    @menus.button(EXIT, position=menus.Position(8))
    async def on_exit(self, _):
        """Exits the menu"""
        self.stop()


class Settings(commands.Cog):
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def setup(self, ctx):
        """Automatically creates a new category and a new channel."""
        category = await ctx.guild.create_category(ctx.bot.user.name)
        channel = await category.create_voice_channel('join me')
        ctx.bot.configs[str(channel.id)] = {}
        await ctx.bot.configs.save()
        await ctx.safe_send(
            msg=f'A new category and a new channel have been created. Join `{channel.name}` and try it out.',
            color=discord.Color.green()
        )

    @commands.command(aliases=['channel'])
    @commands.has_permissions(manage_guild=True)
    async def add(self, ctx, *, channel: discord.VoiceChannel):
        """Adds a voice channel to the auto-channels."""
        if str(channel.id) in ctx.bot.configs:
            raise commands.BadArgument(f'This channel has already been added.')
        else:
            channels = [c for c in ctx.guild.voice_channels if str(c.id) in ctx.bot.configs]
            if len(channels) >= 25:
                raise commands.CommandError('You cannot add more than 25 auto-channels.')
            else:
                ctx.bot.configs[str(channel.id)] = {}
                await ctx.bot.configs.save()
                await ctx.safe_send(
                    msg='Channel has been added.',
                    color=discord.Color.green()
                )

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx, *, channel: discord.VoiceChannel):
        """Removes a voice channel from the auto-channels."""
        try:
            del ctx.bot.configs[str(channel.id)]
        except KeyError:
            raise commands.BadArgument('This channel has not been added yet.')
        else:
            await ctx.safe_send(
                msg='Channel has been removed.',
                color=discord.Color.green()
            )

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def edit(self, ctx, *, channel: discord.VoiceChannel):
        """Edits the default settings of an auto-channel."""
        if str(channel.id) not in ctx.bot.configs:
            raise commands.BadArgument('This channel has not been added yet.')
        else:
            menu = EditMenu(channel)
            await menu.start(ctx, wait=True)

    @commands.command()
    async def list(self, ctx):
        """Lists all auto-channels with their settings."""
        configs = ctx.bot.configs.copy()
        channels = [c for c in ctx.guild.voice_channels if str(c.id) in configs]
        if len(channels) == 0:
            raise commands.CommandError('You haven\'t added any Channels yet.')
        else:
            perms = ctx.channel.permissions_for(ctx.guild.me)
            if not perms.embed_links:
                raise commands.BotMissingPermissions(['embed_links'])
            embed = discord.Embed(
                title='Auto-channels',
                description='Here is a list with all auto-channels in this server.',
                color=discord.Color.blue()
            )
            for channel in channels:
                settings = configs[str(channel.id)]
                name = settings.get('name', '@user\'s channel')
                limit = settings.get('limit', 10)
                position = 'top' if settings.get('top', False) else 'bottom'
                try:
                    category = ctx.guild.get_channel(settings['category'])
                except KeyError:
                    category = channel.category
                if category is None:
                    category = 'No category'
                else:
                    category = category.name
                embed.add_field(
                    name=channel.name,
                    value=f'Category: {category}\n'
                          f'Name: {name}\n'
                          f'Limit: `{limit}`\n'
                          f'Position: at the {position}',
                    inline=False
                )
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, prefix=None):
        """Changes the bot's prefix on the server."""
        if prefix is None:
            pfx = ctx.bot.prefixes.get(str(ctx.guild.id), 'dvc!')
            msg = f'The bot\'s prefix on this server is `{pfx}`.'
        else:
            if prefix == 'dvc!':
                try:
                    ctx.bot.prefixes.pop(str(ctx.guild.id))
                except KeyError:
                    pass
                else:
                    await ctx.bot.prefixes.save()
            else:
                ctx.bot.prefixes[str(ctx.guild.id)] = prefix
                await ctx.bot.prefixes.save()
            msg = f'Changed the bot\'s prefix to `{prefix}`.'
        await ctx.safe_send(msg=msg, color=ctx.guild.me.color)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def blacklist(self, ctx, *, word=None):
        """Puts a word on the blacklist.
        If a word in the blacklist is in the new name of a channel it gets censored.
        E.g. "fuck" would be replaced with "****"
        """
        words = ctx.bot.bad_words.get(str(ctx.guild.id), [])
        if word is None:
            if words:
                await ctx.safe_send(
                    msg=' '.join(f'||{w}||' for w in words),
                    color=ctx.guild.me.color
                )
            else:
                raise commands.CommandError('You haven\'t added any words yet.')
        else:
            if word in words:
                raise commands.BadArgument('This word is already blacklisted.')
            else:
                words.append(word)
                ctx.bot.bad_words[str(ctx.guild.id)] = words
                await ctx.bot.bad_words.save()
                await ctx.safe_send(
                    msg='The word has been Blacklisted.',
                    color=discord.Color.green()
                )

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def whitelist(self, ctx, *, word):
        """Removes a word from the blacklist."""
        words = ctx.bot.bad_words.get(str(ctx.guild.id), [])
        if word in words:
            if len(words) > 1:
                words.remove(word)
                ctx.bot.bad_words[str(ctx.guild.id)] = words
            else:
                ctx.bot.bad_words.pop(str(ctx.guild.id))
            await ctx.bot.bad_words.save()
            await ctx.safe_send(
                msg='Removed the word from the Blacklist.',
                color=discord.Color.green()
            )
        else:
            raise commands.BadArgument('This word is not blacklisted.')


def setup(bot):
    bot.add_cog(Settings())
