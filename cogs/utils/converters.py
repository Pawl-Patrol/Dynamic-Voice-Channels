from discord.ext.commands import Converter, BadArgument


class IntRange(Converter):
    def __init__(self, _min, _max):
        self._min = _min
        self._max = _max

    async def convert(self, ctx, argument):
        try:
            number = int(argument)
        except ValueError:
            raise BadArgument("Converting to int failed.")
        if not self._min <= number <= self._max:
            raise BadArgument(f"The supplied number must be in range of {self._min} to {self._max}.")
        return number


class StrRange(Converter):
    def __init__(self, _min, _max):
        self._min = _min
        self._max = _max

    async def convert(self, ctx, argument):
        number = len(argument)
        if not self._min <= number <= self._max:
            raise BadArgument('The supplied argument must not be shorter than '
                              f'{self._min} characters and longer than {self._max} characters.')
        return argument
