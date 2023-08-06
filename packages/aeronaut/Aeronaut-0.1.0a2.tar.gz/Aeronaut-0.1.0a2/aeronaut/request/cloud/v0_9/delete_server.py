from aeronaut.request.cloud.v0_9.server_action import ServerActionRequest


class DeleteServer(ServerActionRequest):

    def url(self):
        return super(DeleteServer, self).url('delete')
