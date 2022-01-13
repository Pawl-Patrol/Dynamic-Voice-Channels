import json
import uuid
import os
import asyncio


def handle(_type):
    class FileHandle(_type):
        def __init__(self, path, *, loop=None):
            self.path = path
            self.loop = loop or asyncio.get_event_loop()
            self.lock = asyncio.Lock()

            try:
                with open(self.path, "r") as file:
                    super().__init__(json.load(file))
            except FileNotFoundError:
                super().__init__()
                self._dump()

        def _dump(self):
            temp = f"{self.path}-{uuid.uuid4()}.tmp"
            with open(temp, "w", encoding="utf-8") as tmp:
                json.dump(self.copy(), tmp, ensure_ascii=True, separators=(",", ":"))
            os.replace(temp, self.path)

        async def save(self):
            async with self.lock:
                await self.loop.run_in_executor(None, self._dump)

    return FileHandle


List = handle(list)
Dict = handle(dict)
