from aeronaut.request.cloud.v0_9.server_action import ServerActionRequest


class PoweroffServer(ServerActionRequest):

    def url(self):
        return super(PoweroffServer, self).url('poweroff')
