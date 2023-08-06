import AsyncVk

class VkPlugin:
    def __init__(self, **kwargs):
        self.api = AsyncVk.API(
            **kwargs
        )

    def __getattr__(self, item):
        return getattr(self.api, item)
