from aeronaut.resource.cloud.resource import ResourceList


class SoftwareLabelList(ResourceList):

    def _root_(self):
        return [
            "image",
            "server",
            "ServerImageWithState"
        ]

    def _items_(self):
        return {
            "xpath": "./*[local-name()='softwareLabel']"
        }
