from aircraft.request import Request as BaseRequest


class Request(BaseRequest):

    @property
    def base_url(self):
        if hasattr(self, '_base_url'):
            return '{}/oec/0.9'.format(self._base_url)
