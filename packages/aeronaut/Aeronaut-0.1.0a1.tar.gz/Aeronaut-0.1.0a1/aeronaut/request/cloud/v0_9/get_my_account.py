from aeronaut.request.cloud.v0_9.request import Request


class GetMyAccount(Request):

    def http_method(self):
        return 'get'

    def url(self):
        return '{base_url}/myaccount'.format(base_url=self.base_url)
