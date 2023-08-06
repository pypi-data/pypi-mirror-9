from aeronaut.request.cloud.v0_9.request import Request


class ListNetworks(Request):

    def params(self):
        return {
            'location': {
                'required': False,
                'default': None
            },
            'org_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'get'

    def url(self):
        template = '{base_url}/{org_id}/networkWithLocation'

        if self.has_param('location'):
            template += '/{location}'

        return template.format(base_url=self.base_url,
                               location=self.get_param('location'),
                               org_id=self.get_param('org_id'))
