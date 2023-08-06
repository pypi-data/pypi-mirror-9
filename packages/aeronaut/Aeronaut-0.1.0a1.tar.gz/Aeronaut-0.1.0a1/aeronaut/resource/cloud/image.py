from aeronaut.resource.cloud.disk import AdditionalDiskList, DiskList
from aeronaut.resource.cloud.machine_status import MachineStatusList
from aeronaut.resource.cloud.os import OperatingSystem
from aeronaut.resource.cloud.resource import Resource, ResourceList
from aeronaut.resource.cloud.software_label import SoftwareLabelList
from aeronaut.resource.cloud.action_status import ActionStatus


class Image(Resource):

    def _root_(self):
        return "image"

    def _members_(self):
        return {
            "cpu_count": {
                "xpath": "./*[local-name()='cpuCount']",
                "type": int},

            "created": {
                "xpath": "./*[local-name()='created']"},

            "description": {
                "xpath": "./*[local-name()='description']"},

            "disks": {
                "xpath": ".",
                "type": DiskList},

            "id": {
                "xpath": "./@*[local-name()='id']"},

            "location": {
                "xpath": "./@*[local-name()='location']"},

            "memory_mb": {
                "xpath": "./*[local-name()='memoryMb']",
                "type": int},

            "name": {
                "xpath": "./*[local-name()='name']"},

            "os": {
                "xpath": "./*[local-name()='operatingSystem']",
                "type": OperatingSystem},

            "software_labels": {
                "xpath": ".",
                "type": SoftwareLabelList},

            "source": {
                "xpath": "./*[local-name()='source']",
                "type": ImageSource},

            "state": {
                "xpath": "./*[local-name()='state']"}
        }


class ImageList(ResourceList):

    def _root_(self):
        return 'ImagesWithDiskSpeed'

    def _items_(self):
        return {
            "xpath": "./*[local-name()='image']",
            "type": Image
        }


class ImageNameExists(Resource):

    def _root_(self):
        return "Exists"

    def _members_(self):
        return {
            "is_true": {
                "xpath": ".",
                "type": bool}
        }


class ImageSource(Resource):

    def _root_(self):
        return "source"

    def _members_(self):
        return {
            "artifacts": {
                "xpath": ".",
                "type": ImageSourceArtifactList},

            "type": {
                "xpath": "./@*[local-name()='type']"}
        }


class ImageSourceArtifact(Resource):

    def _root_(self):
        return "artifact"

    def _members_(self):
        return {
            "date": {
                "xpath": "./@*[local-name()='date']"},

            "type": {
                "xpath": "./@*[local-name()='type']"},

            "value": {
                "xpath": "./@*[local-name()='value']"}
        }


class ImageSourceArtifactList(ResourceList):

    def _root_(self):
        return 'source'

    def _items_(self):
        return {
            "xpath": "./*[local-name()='artifact']",
            "type": ImageSourceArtifact
        }


class ServerImageOperatingSystem(Resource):

    def _root_(self):
        return "operatingSystem"

    def _members_(self):
        return {
            "id": {
                "xpath": "./*[local-name()='id']"},

            "display_name": {
                "xpath": "./*[local-name()='displayName']"},

            "type": {
                "xpath": "./*[local-name()='type']"},
        }


class ServerImage(Image):

    def _root_(self):
        return "ServerImageWithState"

    def _members_(self):
        base = super(ServerImage, self)._members_()

        override = {
            "deployed_time": {
                "xpath": "./*[local-name()='deployedTime']"},

            "disks": {
                "xpath": ".",
                "type": AdditionalDiskList},

            "id": {
                "xpath": "./*[local-name()='id']"},

            "location": {
                "xpath": "./*[local-name()='location']"},

            "os": {
                "xpath": "./*[local-name()='operatingSystem']",
                "type": ServerImageOperatingSystem},

            "os_storage_gb": {
                "xpath": "./*[local-name()='osStorageGb']",
                "type": int},

            "machine_status": {
                "xpath": ".",
                "type": MachineStatusList},

            "status": {
                "xpath": "./*[local-name()='status']",
                "type": ActionStatus}
        }

        # NOTE: The order of dictionaries below is important
        return dict(base.items() + override.items())
