from aeronaut.request.cloud.v0_9.request import Request


class UpdateAdminAccount(Request):

    def params(self):
        return {
            "department": {
                "required": False},

            "email": {
                "required": False},

            "first_name": {
                "required": False},

            "full_name": {
                "required": False},

            "last_name": {
                "required": False},

            "org_id": {
                "required": True},

            "password": {
                "required": False},

            "username": {
                "required": True}
        }

    def http_method(self):
        return 'post'

    def url(self):
        return '{base_url}/{org_id}/account/{username}' \
               .format(base_url=self.base_url,
                       org_id=self.get_param('org_id'),
                       username=self.get_param('username'))

    def body(self):
        req_data = []
        names = list(set(self.params().keys()) - set(['org_id', 'username']))

        for name in names:
            value = self.get_param(name)
            if value is not None:
                req_data.append('{}={}'.format(name, value))

        return '&'.join(req_data)
