from aeronaut.request.cloud.v0_9.request import Request


class ListServers(Request):

    def with_paging(self):
        return True

    def fields(self):
        return {
            'created': {
                'filter': True,
                'sort': True
            },

            'deployed': {
                'filter': True,
                'sort': True
            },

            'location': {
                'filter': True,
                'sort': True
            },

            'machine_name': {
                'filter': True
            },

            'name': {
                'filter': True
            },

            'network_id': {
                'filter': True
            },

            'os_id': {
                'sort': True,
                'query_key': 'operatingSystemId'
            },

            'private_ip': {
                'filter': True
            },

            'server_id': {
                'filter': True,
                'sort': True,
                'query_key': 'id'
            },

            'source_image_id': {
                'filter': True,
                'sort': True
            },

            'started': {
                'sort': True
            },

            'state': {
                'sort': True
            }
        }

    def params(self):
        return {
            'org_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'get'

    def url(self):
        t = '{base_url}/{org_id}/serverWithBackup?'

        return t.format(base_url=self.base_url,
                        org_id=self.get_param('org_id'))
