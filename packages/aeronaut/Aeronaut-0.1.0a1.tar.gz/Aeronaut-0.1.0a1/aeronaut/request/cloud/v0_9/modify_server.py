import urllib

from aeronaut.request.cloud.v0_9.request import Request


class ModifyServer(Request):

    def params(self):
        return {
            'cpu_count': {
                'required': False,
                'default': None
            },

            'description': {
                'required': False,
                'default': None
            },

            'memory': {
                'required': False,
                'default': None
            },

            'name': {
                'required': False,
                'default': None
            },

            'server_id': {
                'required': True
            },

            'org_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'post'

    def url(self):
        template = "{base_url}/{org_id}/server/{server_id}"

        return template.format(base_url=self.base_url,
                               org_id=self.get_param('org_id'),
                               server_id=self.get_param('server_id'))

    def headers(self):
        headers = super(ModifyServer, self).headers()
        headers['Content-type'] = 'application/x-www-form-urlencoded'
        return headers

    def body(self):
        payload = {}

        for param in ['description', 'memory', 'name']:
            if self.has_param(param):
                payload[param] = self.get_param(param)

        if self.has_param('cpu_count'):
            payload['cpuCount'] = self.get_param('cpu_count')

        return urllib.urlencode(payload)
