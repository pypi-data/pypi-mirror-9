from aeronaut.resource.cloud.resource import Resource, ResourceList


class AdditionalDisk(Resource):

    def _root_(self):
        return "additionalDisk"

    def _members_(self):
        return {
            "id": {
                "xpath": "./*[local-name()='id']"},

            "scsi_id": {
                "xpath": "./*[local-name()='scsiId']",
                "type": int},

            "size_gb": {
                "xpath": "./*[local-name()='diskSizeGb']",
                "type": int},

            "state": {
                "xpath": "./*[local-name()='state']"},
        }


class AdditionalDiskList(ResourceList):

    def _root_(self):
        return "ServerImageWithState"

    def _items_(self):
        return {
            "xpath": "./*[local-name()='additionalDisk']",
            "type": AdditionalDisk
        }


class Disk(Resource):

    def _root_(self):
        return "disk"

    def _members_(self):
        return {
            "id": {
                "xpath": "./@*[local-name()='id']"},

            "scsi_id": {
                "xpath": "./@*[local-name()='scsiId']",
                "type": int},

            "size_gb": {
                "xpath": "./@*[local-name()='sizeGb']",
                "type": int},

            "speed": {
                "xpath": "./@*[local-name()='speed']"},

            "state": {
                "xpath": "./@*[local-name()='state']"},
        }


class DiskList(ResourceList):

    def _root_(self):
        return [
            "image",
            "server",
            "ServerImageWithState",
        ]

    def _items_(self):
        return {
            "xpath": "./*[local-name()='disk']",
            "type": Disk
        }
