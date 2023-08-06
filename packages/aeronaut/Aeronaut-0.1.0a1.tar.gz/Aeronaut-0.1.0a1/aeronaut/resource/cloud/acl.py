from aeronaut.resource.cloud.resource import Resource, ResourceList, Status


class AclRule(Resource):

    def _root_(self):
        return 'AclRule'

    def _members_(self):
        return {
            "action": {
                "xpath": "./*[local-name()='action']"},

            "dest_ip_range": {
                "xpath": "./*[local-name()='destinationIpRange']",
                "type": AclRuleDestinationIpRange},

            "id": {
                "xpath": "./*[local-name()='id']"},

            "name": {
                "xpath": "./*[local-name()='name']"},

            "port_range": {
                "xpath": "./*[local-name()='portRange']",
                "type": AclRulePortRange},

            "position": {
                "xpath": "./*[local-name()='position']",
                "type": int},

            "protocol": {
                "xpath": "./*[local-name()='protocol']"},

            "status": {
                "xpath": "./*[local-name()='status']"},

            "source_ip_range": {
                "xpath": "./*[local-name()='sourceIpRange']",
                "type": AclRuleSourceIpRange},

            "type": {
                "xpath": "./*[local-name()='type']"}
        }


class AclRuleIpRange(Resource):

    def _members_(self):
        return {
            "ip_address": {
                "xpath": "./*[local-name()='ipAddress']"},

            "netmask": {
                "xpath": "./*[local-name()='netmask']"}
        }


class AclRuleDestinationIpRange(AclRuleIpRange):

    def _root_(self):
        return "destinationIpRange"


class AclRuleList(ResourceList):

    def _root_(self):
        return 'AclRuleList'

    def _items_(self):
        return {
            "xpath": "./*[local-name()='AclRule']",
            "type": AclRule
        }


class AclRulePortRange(Resource):

    def _root_(self):
        return "portRange"

    def _members_(self):
        return {
            "type": {
                "xpath": "./*[local-name()='type']"},

            "port1": {
                "xpath": "./*[local-name()='port1']"},

            "port2": {
                "xpath": "./*[local-name()='port2']"}
        }


class AclRuleSourceIpRange(AclRuleIpRange):

    def _root_(self):
        return "sourceIpRange"


class CreateAclRuleStatus(Status):
    pass


class DeleteAclRuleStatus(Status):
    pass
