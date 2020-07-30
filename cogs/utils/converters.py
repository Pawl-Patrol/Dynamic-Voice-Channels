from discord.ext.commands import Converter, BadArgument
from difflib import get_close_matches


class CannotFindCommand(BadArgument):
    def __init__(self, argument, close):
        self.argument = argument
        self.close = close


class CommandConverter(Converter):
    async def convert(self, ctx, argument):
        command = ctx.bot.get_command(argument.casefold())
        if command is None:
            close = get_close_matches(argument, ctx.bot.all_commands, n=1)
            raise CannotFindCommand(argument, next(iter(close), None))
        return command


class IntNotInRange(BadArgument):
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum


class IntRange(Converter):
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def is_in_range(self, number):
        if number < self.minimum:
            return False
        if number > self.maximum:
            return False
        return True

    async def convert(self, ctx, argument):
        try:
            number = int(argument)
        except ValueError:
            raise BadArgument('Please supply a valid number.')
        if not self.is_in_range(number):
            raise IntNotInRange(self.minimum, self.maximum)
        return number


class StrNotInRange(IntNotInRange):
    pass


class StrRange(IntRange):
    async def convert(self, ctx, argument):
        number = len(argument)
        if not self.is_in_range(number):
            raise StrNotInRange(self.minimum, self.maximum)
        return argument
