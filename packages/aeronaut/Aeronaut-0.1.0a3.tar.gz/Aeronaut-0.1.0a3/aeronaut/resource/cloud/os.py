from aeronaut.resource.cloud.resource import Resource


class OperatingSystem(Resource):

    def _root_(self):
        return "operatingSystem"

    def _members_(self):
        return {
            "id": {
                "xpath": "./@*[local-name()='id']"},

            "display_name": {
                "xpath": "./@*[local-name()='displayName']"},

            "type": {
                "xpath": "./@*[local-name()='type']"},
        }
