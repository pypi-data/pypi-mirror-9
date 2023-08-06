from aeronaut.request.cloud.v0_9.request import Request


class GetServerImage(Request):

    def params(self):
        return {
            'org_id': {
                'required': True
            },

            'image_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'get'

    def url(self):
        t = '{base_url}/{org_id}/image/{image_id}'

        return t.format(base_url=self.base_url,
                        org_id=self.get_param('org_id'),
                        image_id=self.get_param('image_id'))
