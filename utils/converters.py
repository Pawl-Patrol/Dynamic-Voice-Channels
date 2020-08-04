from discord.ext import commands
from .exceptions import IntNotInRange, StrNotInRange


class IntRange(commands.Converter):
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    async def convert(self, ctx, argument):
        try:
            number = int(argument)
        except ValueError:
            raise commands.BadArgument('Converting to int failed.')
        if not self.minimum <= number <= self.maximum:
            raise IntNotInRange(self.minimum, self.maximum)
        return number


class StrRange(IntRange):
    async def convert(self, ctx, argument):
        if not self.minimum <= len(argument) <= self.maximum:
            raise StrNotInRange(self.minimum, self.maximum)
        return argument
