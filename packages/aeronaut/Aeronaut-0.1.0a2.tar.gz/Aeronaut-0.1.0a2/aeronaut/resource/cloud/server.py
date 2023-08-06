from aeronaut.resource.cloud.action_status import ActionStatus
from aeronaut.resource.cloud.disk import DiskList
from aeronaut.resource.cloud.machine_status import MachineStatusList
from aeronaut.resource.cloud.os import OperatingSystem
from aeronaut.resource.cloud.resource import Resource, ResourceList, Status
from aeronaut.resource.cloud.software_label import SoftwareLabelList


class Backup(Resource):

    def _root_(self):
        return "backup"

    def _members_(self):
        return {
            "asset_id": {
                "xpath": "./@*[local-name()='assetId']"},

            "service_plan": {
                "xpath": "./@*[local-name()='servicePlan']"},

            "state": {
                "xpath": "./@*[local-name()='state']"}
        }


class CleanFailedServerDeploymentStatus(Status):
    pass


class DeleteServerStatus(Status):
    pass


class DeployServerStatus(Status):
    pass


class ModifyServerStatus(Status):
    pass


class PoweroffServerStatus(Status):
    pass


class RebootServerStatus(Status):
    pass


class ResetServerStatus(Status):
    pass


class Server(Resource):

    def _root_(self):
        return "server"

    def _members_(self):
        return {
            "backup": {
                "xpath": "./*[local-name()='backup']",
                "type": Backup},

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

            "is_deployed": {
                "xpath": "./*[local-name()='isDeployed']",
                "type": bool},

            "is_started": {
                "xpath": "./*[local-name()='isStarted']",
                "type": bool},

            "location": {
                "xpath": "./@*[local-name()='location']"},

            "machine_name": {
                "xpath": "./*[local-name()='machineName']"},

            "machine_status": {
                "xpath": ".",
                "type": MachineStatusList},

            "memory_mb": {
                "xpath": "./*[local-name()='memoryMb']",
                "type": int},

            "name": {
                "xpath": "./*[local-name()='name']"},

            "network_id": {
                "xpath": "./*[local-name()='networkId']"},

            "os": {
                "xpath": "./*[local-name()='operatingSystem']",
                "type": OperatingSystem},

            "public_ip": {
                "xpath": "./*[local-name()='publicIp']"},

            "private_ip": {
                "xpath": "./*[local-name()='privateIp']"},

            "software_labels": {
                "xpath": ".",
                "type": SoftwareLabelList},

            "source_image_id": {
                "xpath": "./*[local-name()='sourceImageId']"},

            "state": {
                "xpath": "./*[local-name()='state']"},

            "status": {
                "xpath": "./*[local-name()='status']",
                "type": ActionStatus}
        }


class ServerList(ResourceList):

    def _root_(self):
        return "ServersWithBackup"

    def _items_(self):
        return {
            "xpath": "./*[local-name()='server']",
            "type": Server
        }


class ShutdownServerStatus(Status):
    pass


class StartServerStatus(Status):
    pass
