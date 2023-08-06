from aeronaut.resource.cloud.resource import Resource, ResourceList


class ActionStatus(Resource):

    def _root_(self):
        return "status"

    def _members_(self):
        return {
            "action": {
                "xpath": "./*[local-name()='action']"},

            "failure_reason": {
                "xpath": "./*[local-name()='failureReason']"},

            "request_time": {
                "xpath": "./*[local-name()='requestTime']"},

            "steps": {
                "xpath": ".",
                "type": ActionStatusStepsList},

            "update_time": {
                "xpath": "./*[local-name()='updateTime']"},

            "username": {
                "xpath": "./*[local-name()='userName']"}
        }


class ActionStatusStep(Resource):

    def _root_(self):
        return "step"

    def _members_(self):
        return {
            "name": {
                "xpath": "./*[local-name()='name']"},

            "number": {
                "xpath": "./*[local-name()='number']",
                "type": int},

            "percent_complete": {
                "xpath": "./*[local-name()='percentComplete']",
                "type": int}
        }


class ActionStatusStepsList(ResourceList):

    def _root_(self):
        return "status"

    def _items_(self):
        return {
            "xpath": "./*[local-name()='step']",
            "type": ActionStatusStep
        }
