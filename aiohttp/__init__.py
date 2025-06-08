import types
class _Response:
    def __init__(self, data=None):
        self._data = data or {}
    async def json(self):
        return self._data
class ClientSession:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def get(self, url, **kwargs):
        return _Response()
