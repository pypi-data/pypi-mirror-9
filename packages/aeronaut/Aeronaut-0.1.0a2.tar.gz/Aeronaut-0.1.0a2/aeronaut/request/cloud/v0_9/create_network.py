from aeronaut.request.cloud.v0_9.request import Request


class CreateNetwork(Request):

    def params(self):
        return {
            'description': {
                'required': False,
                'default': ''
            },
            'location': {
                'required': True
            },
            'name': {
                'required': True
            },
            'org_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'post'

    def url(self):
        template = '{base_url}/{org_id}/networkWithLocation'

        return template.format(base_url=self.base_url,
                               org_id=self.get_param('org_id'))

    def body(self):
        template = """
        <NewNetworkWithLocation xmlns="http://oec.api.opsource.net/schemas/network">
            <name>{name}</name>
            <description>{description}</description>
            <location>{location}</location>
        </NewNetworkWithLocation>
        """  # NOQA

        return template.format(name=self.get_param('name'),
                               description=self.get_param('description'),
                               location=self.get_param('location'))
