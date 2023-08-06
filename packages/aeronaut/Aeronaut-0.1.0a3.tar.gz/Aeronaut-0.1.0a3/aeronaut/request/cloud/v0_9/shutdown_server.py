from aeronaut.request.cloud.v0_9.server_action import ServerActionRequest


class ShutdownServer(ServerActionRequest):

    def url(self):
        return super(ShutdownServer, self).url('shutdown')
