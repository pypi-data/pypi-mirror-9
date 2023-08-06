from aeronaut.request.cloud.v0_9.request import Request


class ServerActionRequest(Request):
    """Base request to be inherited by server action requests
    """

    def params(self):
        return {
            'server_id': {
                'required': True
            },

            'org_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'get'

    def url(self, action):
        template = "{base_url}/{org_id}/server/{server_id}?{action}"

        return template.format(base_url=self.base_url,
                               org_id=self.get_param('org_id'),
                               server_id=self.get_param('server_id'),
                               action=action)
