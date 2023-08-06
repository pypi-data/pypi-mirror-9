from aeronaut.request.cloud.v0_9.server_action import ServerActionRequest


class AddStorageToServer(ServerActionRequest):

    def params(self):
        p = super(AddStorageToServer, self).params().copy()
        p.update({
            'server_id': {
                'required': True
            },

            'size_gb': {
                'required': True
            },

            'disk_speed_id': {
                'required': False
            }
        })

        return p

    def url(self):
        u = super(AddStorageToServer, self).url('addLocalStorage')

        u += '&amount={}'.format(self.get_param('size_gb'))

        if self.has_param('disk_speed_id'):
            u += '&speed={}'.format(self.get_param('disk_speed_id'))

        return u
