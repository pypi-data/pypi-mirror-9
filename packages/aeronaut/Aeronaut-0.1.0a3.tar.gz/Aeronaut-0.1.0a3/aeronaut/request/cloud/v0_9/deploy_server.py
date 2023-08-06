from aeronaut.request.cloud.v0_9.request import Request


class DeployServer(Request):

    def params(self):
        return {
            'admin_password': {
                'required': False,
                'default': None
            },

            'description': {
                'required': False,
                'default': ''
            },

            'disks': {
                'required': False,
                'default': []
            },

            'image_id': {
                'required': True
            },

            'name': {
                'required': True
            },

            'network_id': {
                'required': False,
                'default': None
            },

            'org_id': {
                'required': True
            },

            'private_ip': {
                'required': False,
                'default': None
            },

            'start': {
                'required': False,
                'default': True
            }
        }

    def http_method(self):
        return 'post'

    def url(self):
        template = '{base_url}/{org_id}/deployServer'

        return template.format(base_url=self.base_url,
                               org_id=self.get_param('org_id'))

    def body(self):
        template = """
            <DeployServer xmlns="http://oec.api.opsource.net/schemas/server">
                <name>{name}</name>
                <description>{description}</description>
                <imageId>{image_id}</imageId>
                <start>false</start>"""

        if self.has_param('admin_password'):
            template += """
                <administratorPassword>{admin_password}</administratorPassword>"""  # NOQA

        if self.has_param('network_id'):
            template += """
                <networkId>{network_id}</networkId>"""

        if self.has_param('private_ip'):
            template += """
                <privateIp>{private_ip}</privateIp>"""

        for speed in self.get_param('disks'):
            template += """
                <disk scsiId="{scsi_id}" speed="{speed}"/>""" \
                .format(scsi_id=speed['scsi_id'],
                        speed=speed['speed'])

        template += """
            </DeployServer>"""

        return template.format(admin_password=self.get_param('admin_password'),
                               name=self.get_param('name'),
                               description=self.get_param('description'),
                               image_id=self.get_param('image_id'),
                               location=self.get_param('location'),
                               network_id=self.get_param('network_id'),
                               private_ip=self.get_param('private_ip'),
                               start=str(self.get_param('start')).lower())
