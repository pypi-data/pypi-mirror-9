import threading
import api
import keep
import config
import copy

class ThreadSafeApiCache(object):
    """Threadsafe wrapper for API objects.

    This stores and returns a different api object per thread, because httplib2
    which underlies apiclient is not threadsafe.

    """

    def __init__(self, apiconfig=None, keep_params={}):
        if apiconfig is None:
            apiconfig = config.settings()
        self.apiconfig = copy.copy(apiconfig)
        self.local = threading.local()
        self.keep = keep.KeepClient(api_client=self, **keep_params)

    def localapi(self):
        if 'api' not in self.local.__dict__:
            self.local.api = api.api_from_config('v1', apiconfig=self.apiconfig)
        return self.local.api

    def __getattr__(self, name):
        # Proxy nonexistent attributes to the thread-local API client.
        if name == "api_token":
            return self.apiconfig['ARVADOS_API_TOKEN']
        return getattr(self.localapi(), name)
