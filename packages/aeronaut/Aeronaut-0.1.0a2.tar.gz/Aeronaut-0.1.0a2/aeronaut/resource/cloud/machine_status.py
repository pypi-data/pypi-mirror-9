from aeronaut.resource.cloud.resource import Resource, ResourceList


class MachineStatus(Resource):

    def _root_(self):
        return "machineStatus"

    def _members_(self):
        return {
            "name": {
                "xpath": "./@*[local-name()='name']"},

            "value": {
                "xpath": "./*[local-name()='value']",
                "type": "auto"}
        }


class MachineStatusList(ResourceList):

    def _root_(self):
        return [
            "server",
            "ServerImageWithState"
        ]

    def _items_(self):
        return {
            "xpath": "./*[local-name()='machineStatus']",
            "type": MachineStatus
        }
