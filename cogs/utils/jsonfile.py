from asyncio import Lock, get_event_loop
from json import load, dump
from os import replace
from uuid import uuid4


class JSONFile:
    def __init__(self, path, loop=None):
        self.path = path
        self.loop = loop or get_event_loop()
        self.lock = Lock()
        self.data = {}
        self.load()

    def load(self):
        try:
            with open(self.path, 'r') as file:
                self.data = load(file)
        except FileNotFoundError:
            pass

    def write(self):
        temp = f'{uuid4()}.tmp'
        with open(temp, 'w', encoding='utf-8') as tmp:
            dump(self.data.copy(), tmp, ensure_ascii=True, separators=(',', ':'))
        replace(temp, self.path)

    async def save(self):
        async with self.lock:
            await self.loop.run_in_executor(None, self.write)

    def get(self, key, *default):
        return self.data.get(str(key), *default)

    def __getitem__(self, key):
        return self.data[str(key)]

    def __setitem__(self, key, value):
        self.data[str(key)] = value

    def __delitem__(self, key):
        self.data.pop(str(key), None)

    def __contains__(self, key):
        return str(key) in self.data

    def __len__(self):
        return len(self.data)
