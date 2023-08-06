from aeronaut.request.cloud.v0_9.server_action import ServerActionRequest


class RebootServer(ServerActionRequest):

    def url(self):
        return super(RebootServer, self).url('reboot')
