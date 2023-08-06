

# ==========
# EXCEPTIONS
# ==========

class UnknownContentTypeError(Exception):

    def __init__(self, content_type):
        message = 'Unknown content-type: {}' \
                  .format(content_type)
        super(UnknownContentTypeError, self).__init__(message)


# ==============
# RESPONSE CLASS
# ==============

class Response(object):

    def __init__(self, response, request):
        self._response = response
        self._request = request

    # =============
    # MAGIC METHODS
    # =============

    def __getattr__(self, name):
        return getattr(self._response, name)

    # =================
    # PUBLIC PROPERTIES
    # =================

    @property
    def content_type(self):
        return self._response.headers['content-type'].split(';')[0]

    @property
    def body(self):
        return self._response.content
