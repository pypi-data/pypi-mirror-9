from aeronaut.resource.cloud.resource import Resource, ResourceList


class Account(Resource):

    def _root_(self):
        return 'Account'

    def _members_(self):
        return {
            "department": {
                "xpath": "./*[local-name()='department']"},

            "email": {
                "xpath": "./*[local-name()='emailAddress']"},

            "first_name": {
                "xpath": "./*[local-name()='firstName']"},

            "full_name": {
                "xpath": "./*[local-name()='fullName']"},

            "last_name": {
                "xpath": "./*[local-name()='lastName']"},

            "org_id": {
                "xpath": "./*[local-name()='orgId']"},

            "password": {
                "writeonly": True},

            "roles": {
                "xpath": "./*[local-name()='roles']",
                "type": RoleList},

            "username": {
                "xpath": "./*[local-name()='userName']"}
        }


class RoleList(ResourceList):

    def _root_(self):
        return 'roles'

    def _items_(self):
        return {
            "xpath": "./*[local-name()='role']",
            "type": Role
        }


class Role(Resource):

    def _root_(self):
        return 'role'

    def _members_(self):
        return {
            "name": {"xpath": "./*[local-name()='name']"}
        }
