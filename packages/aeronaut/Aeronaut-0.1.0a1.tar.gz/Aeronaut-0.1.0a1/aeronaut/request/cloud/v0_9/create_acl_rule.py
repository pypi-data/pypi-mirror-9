from aeronaut.request.cloud.v0_9.request import Request


class CreateAclRule(Request):

    def params(self):
        return {
            'type': {
                'required': True
            },
            'action': {
                'required': True
            },
            'dest_ip': {
                'required': True
            },
            'dest_netmask': {
                'required': True
            },
            'from_port': {
                'required': True
            },
            'name': {
                'required': True
            },
            'network_id': {
                'required': True
            },
            'org_id': {
                'required': True
            },
            'position': {
                'required': True
            },
            'protocol': {
                'required': True
            },
            'source_ip': {
                'required': True
            },
            'source_netmask': {
                'required': True
            },
            'to_port': {
                'required': True
            }
        }

    def http_method(self):
        return 'post'

    def url(self):
        template = '{base_url}/{org_id}/network/{network_id}/aclrule'

        return template.format(base_url=self.base_url,
                               network_id=self.get_param('network_id'),
                               org_id=self.get_param('org_id'))

    def body(self):
        template = """
            <AclRule xmlns="http://oec.api.opsource.net/schemas/network">
                <name>{name}</name>
                <position>{position}</position>
                <action>{action}</action>
                <protocol>{protocol}</protocol>
"""

        if self.has_param('source_ip'):
            template += """
                <sourceIpRange>
                    <ipAddress>{source_ip}</ipAddress>
                    <netmask>{source_netmask}</netmask>
                </sourceIpRange>
"""
        else:
            template += """
                <sourceIpRange/>
"""

        template += """
                <destinationIpRange>
                    <ipAddress>{dest_ip}</ipAddress>
                    <netmask>{dest_netmask}</netmask>
                </destinationIpRange>
"""

        if self.get_param('from_port') == self.get_param('to_port'):
            template += """
                <portRange>
                    <type>EQUAL_TO</type>
                    <port1>{from_port}</port1>
                </portRange>
"""
        else:
            template += """
                <portRange>
                    <type>RANGE</type>
                    <port1>{from_port}</port1>
                    <port2>{to_port}</port2>
                </portRange>
"""

        template += """
                <type>{acl_type}</type>
            </AclRule>"""

        body = template.format(acl_type=self.get_param('type'),
                               action=self.get_param('action'),
                               dest_ip=self.get_param('dest_ip'),
                               dest_netmask=self.get_param('dest_netmask'),
                               from_port=self.get_param('from_port'),
                               name=self.get_param('name'),
                               network_id=self.get_param('network_id'),
                               position=self.get_param('position'),
                               protocol=self.get_param('protocol'),
                               source_ip=self.get_param('source_ip'),
                               source_netmask=self.get_param('source_netmask'),
                               to_port=self.get_param('to_port'))

        return body
