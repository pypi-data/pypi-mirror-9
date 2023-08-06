from aeronaut.resource.cloud.resource import Resource, ResourceList, Status


class CreateNetworkStatus(Status):
    pass


class Network(Resource):

    def _root_(self):
        return 'network'

    def _members_(self):
        return {
            "description": {
                "xpath": "./*[local-name()='description']"},

            "id": {
                "xpath": "./*[local-name()='id']"},

            "is_multicast": {
                "xpath": "./*[local-name()='multicast']",
                "type": bool},

            "location": {
                "xpath": "./*[local-name()='location']"},

            "name": {
                "xpath": "./*[local-name()='name']"},

            "private_net": {
                "xpath": "./*[local-name()='privateNet']"}
        }


class NetworkList(ResourceList):

    def _root_(self):
        return 'NetworkWithLocations'

    def _items_(self):
        return {
            "xpath": "./*[local-name()='network']",
            "type": Network
        }
