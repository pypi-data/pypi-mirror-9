from aeronaut.request.cloud.v0_9.request import Request


class ListAclRules(Request):

    def params(self):
        return {
            'network_id': {
                'required': True
            },
            'org_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'get'

    def url(self):
        template = '{base_url}/{org_id}/network/{network_id}/aclrule'

        return template.format(base_url=self.base_url,
                               network_id=self.get_param('network_id'),
                               org_id=self.get_param('org_id'))
