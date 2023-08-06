from aeronaut.request.cloud.v0_9.request import Request


class DoesImageNameExist(Request):

    def params(self):
        return {
            'image_name': {
                'required': True
            },

            'location': {
                'required': True
            },

            'org_id': {
                'required': True
            }
        }

    def http_method(self):
        return 'post'

    def url(self):
        t = '{base_url}/{org_id}/image/nameExists'

        return t.format(base_url=self.base_url,
                        org_id=self.get_param('org_id'))

    def body(self):
        template = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <ImageNameExists xmlns="http://oec.api.opsource.net/schemas/server">
                <location>{location}</location>
                <imageName>{image_name}</imageName>
            </ImageNameExists>
        """  # NOQA

        return template.format(image_name=self.get_param('image_name'),
                               location=self.get_param('location'))
