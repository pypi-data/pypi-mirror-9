from aeronaut.request.cloud.v0_9.server_action import ServerActionRequest


class StartServer(ServerActionRequest):

    def url(self):
        return super(StartServer, self).url('start')
