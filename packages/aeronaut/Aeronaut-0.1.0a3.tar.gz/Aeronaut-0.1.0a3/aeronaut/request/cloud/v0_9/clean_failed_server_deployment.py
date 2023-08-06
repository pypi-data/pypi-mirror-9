from aeronaut.request.cloud.v0_9.server_action import ServerActionRequest


class CleanFailedServerDeployment(ServerActionRequest):

    def url(self):
        return super(CleanFailedServerDeployment, self).url('clean')
