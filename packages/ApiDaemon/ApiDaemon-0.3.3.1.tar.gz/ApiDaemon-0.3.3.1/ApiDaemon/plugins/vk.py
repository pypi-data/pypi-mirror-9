import AsyncVk
import asyncio
class VkPlugin:
    def __init__(self, notify=None, **kwargs):
        self.api = AsyncVk.API(
            **kwargs
        )

    def __getattr__(self, item):
        return getattr(self.api, item)

    @asyncio.coroutine
    def get_token(self):
        return self.api.access_token
