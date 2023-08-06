from aeronaut.request.cloud.v0_9.server_action import ServerActionRequest


class ResetServer(ServerActionRequest):

    def url(self):
        return super(ResetServer, self).url('reset')
