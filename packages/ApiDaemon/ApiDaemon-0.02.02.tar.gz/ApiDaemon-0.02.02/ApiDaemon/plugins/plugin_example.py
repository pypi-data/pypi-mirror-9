class ExamplePlugin:
    def __init__(self, **kwargs):
        self.login = kwargs.get('login')
        self.password = kwargs.get('password')
        self.token = kwargs.get('token')

    def __getattr__(self, item):
        return getattr(self.api, item)
