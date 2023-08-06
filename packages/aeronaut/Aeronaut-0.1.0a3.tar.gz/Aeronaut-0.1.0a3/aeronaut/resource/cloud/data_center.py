from aeronaut.resource.cloud.resource import Resource, ResourceList


class Backup(Resource):

    def _root_(self):
        return "backup"

    def _members_(self):
        return {
            "type": {
                "xpath": "./@*[local-name()='type']"},

            "maintenance_status": {
                "xpath": "./@*[local-name()='maintenanceStatus']"}
        }


class DataCenter(Resource):

    def _root_(self):
        return "datacenter"

    def _members_(self):
        return {
            "backup": {
                "xpath": "./*[local-name()='backup']",
                "type": Backup},

            "city": {
                "xpath": "./*[local-name()='city']"},

            "country": {
                "xpath": "./*[local-name()='country']"},

            "display_name": {
                "xpath": "./*[local-name()='displayName']"},

            "hypervisor": {
                "xpath": "./*[local-name()='hypervisor']",
                "type": Hypervisor},

            "is_default": {
                "xpath": "./@*[local-name()='default']",
                "type": bool},

            "location": {
                "xpath": "./@*[local-name()='location']"},

            "networking": {
                "xpath": "./*[local-name()='networking']",
                "type": Networking},

            "state": {
                "xpath": "./*[local-name()='state']"},

            "vpn_url": {
                "xpath": "./*[local-name()='vpnUrl']"},
        }


class DataCenterList(ResourceList):

    def _root_(self):
        return "DatacentersWithMaintenanceStatus"

    def _items_(self):
        return {
            "xpath": "./*[local-name()='datacenter']",
            "type": DataCenter
        }


class DiskSpeed(Resource):

    def _root_(self):
        return "diskSpeed"

    def _members_(self):
        return {
            "abbreviation": {
                "xpath": "./*[local-name()='abbreviation']"},

            "description": {
                "xpath": "./*[local-name()='description']"},

            "display_name": {
                "xpath": "./*[local-name()='displayName']"},

            "id": {
                "xpath": "./@*[local-name()='id']"},

            "is_available": {
                "xpath": "./@*[local-name()='available']",
                "type": bool},

            "is_default": {
                "xpath": "./@*[local-name()='default']",
                "type": bool},
        }


class DiskSpeedList(ResourceList):

    def _root_(self):
        return "hypervisor"

    def _items_(self):
        return {
            "xpath": "./*[local-name()='diskSpeed']",
            "type": DiskSpeed
        }


class Hypervisor(Resource):

    def _root_(self):
        return "hypervisor"

    def _members_(self):
        return {
            "disk_speeds": {
                "xpath": ".",
                "type": DiskSpeedList},

            "maintenance_status": {
                "xpath": "./@*[local-name()='maintenanceStatus']"},

            "min_disk_size_gb": {
                "xpath": "./*[local-name()='property']"
                         "[@name='MIN_DISK_SIZE_GB']/@value",
                "type": int},

            "type": {
                "xpath": "./@*[local-name()='type']"}
        }


class Networking(Resource):

    def _root_(self):
        return "networking"

    def _members_(self):
        return {
            "maintenance_status": {
                "xpath": "./@*[local-name()='maintenanceStatus']"},

            "max_server_to_vip_connections": {
                "xpath": "./*[local-name()='property']"
                         "[@name='MAX_SERVER_TO_VIP_CONNECTIONS']/@value",
                "type": int},

            "type": {
                "xpath": "./@*[local-name()='type']",
                "type": int}
        }
