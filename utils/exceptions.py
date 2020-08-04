from discord.ext import commands


class NotInVoiceChannel(commands.CheckFailure):
    def __init__(self):
        super().__init__('You are not in a voice channel.')


class IntNotInRange(commands.BadArgument):
    def __init__(self, minimum, maximum):
        super().__init__(f'The supplied number must be in range of {minimum} to {maximum}.')


class StrNotInRange(commands.BadArgument):
    def __init__(self, minimum, maximum):
        super().__init__(f'The supplied argument must be between {minimum} and {maximum} characters long.')
