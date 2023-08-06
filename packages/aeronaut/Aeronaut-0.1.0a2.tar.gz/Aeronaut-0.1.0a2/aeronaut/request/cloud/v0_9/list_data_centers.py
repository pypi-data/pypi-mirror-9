from aeronaut.request.cloud.v0_9.request import Request


class ListDataCenters(Request):

    def with_paging(self):
        return True

    def fields(self):
        return {
            'location': {
                'filter': True,
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
        return '{base_url}/{org_id}/datacenterWithMaintenanceStatus?' \
               .format(base_url=self.base_url,
                       org_id=self.get_param('org_id'))
