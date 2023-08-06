from aeronaut.request.cloud.v0_9.request import Request


class DeleteAclRule(Request):

    def params(self):
        return {
            'network_id': {
                'required': True
            },
            'org_id': {
                'required': True
            },
            'rule_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'get'

    def url(self):
        template = "{base_url}/{org_id}/network/{network_id}/" \
                   "aclrule/{rule_id}?delete"

        return template.format(base_url=self.base_url,
                               network_id=self.get_param('network_id'),
                               org_id=self.get_param('org_id'),
                               rule_id=self.get_param('rule_id'))
