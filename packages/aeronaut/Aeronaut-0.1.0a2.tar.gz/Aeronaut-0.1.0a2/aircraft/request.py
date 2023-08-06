from aircraft.params import Params


# ==========
# EXCEPTIONS
# ==========

class UnknownFilterKeyError(Exception):

    def __init__(self, invalid_key, valid_keys):
        message = "'{invalid_key}' is invalid. Valid filters are " \
                  "{valid_keys}.".format(invalid_key=invalid_key,
                                         valid_keys=", ".join(valid_keys))
        super(UnknownFilterKeyError, self).__init__(message)


class UnknownSortKeyError(Exception):

    def __init__(self, invalid_key, valid_keys):
        message = "'{invalid_key}' is invalid. Valid sort keys are " \
                  "{valid_keys}.".format(invalid_key=invalid_key,
                                         valid_keys=", ".join(valid_keys))
        super(UnknownSortKeyError, self).__init__(message)


# ==================
# BASE REQUEST CLASS
# ==================

class Request(object):

    def __init__(self, auth_data=None, base_url=None, params={}):
        self._auth_data = auth_data
        self._base_url = base_url

        params_def = self._build_params_def()

        if params_def:
            self.__params__ = Params(params_def, params)

    # =================
    # PUBLIC PROPERTIES
    # =================

    @property
    def base_url(self):
        return self._base_url

    # ==============
    # PUBLIC METHODS
    # ==============

    def basic_auth(self):
        return None

    def body(self):
        return None

    def build_url(self):
        url = self.url()

        if self.with_paging():
            query = []
            page_number = self.get_param('page_number')
            page_size = self.get_param('page_size')

            if page_number:
                query.append("pageNumber={}".format(page_number))

            if page_size:
                query.append("pageSize={}".format(page_size))

            if '?' not in url and query:
                url += "?"

            if query:
                url += "&".join(query)

        # We expect filters here to be an array of 3-element arrays
        # with each element being a string:
        #       [[<field name>, <operator>, <value>], [<f>,<o>,<v>], ...]
        filters = self.get_param('filters')

        # However...

        # We can accommodate the scenario where filters is just
        # a 3-element array:
        #       [<field name>, <operator>, <value>]
        #
        # and this block will just convert that into an array of
        # 3-element arrays.
        if isinstance(filters, list) \
                and len(filters) == 3 \
                and all([isinstance(e, str) for e in filters]):
            filters = [filters]

        if filters:
            query = "&".join([
                "{key}{operator}{value}".format(
                    key=self._to_filter_query_key(f[0]),
                    operator=self._to_operator(f[1].upper()),
                    value=f[2])
                for f in filters
            ])

            if "?" not in url and query:
                url += "?"

            if query and url[-1] != "?":
                url += "&"

            url += query

        sorters = self.get_param("sort")

        if sorters:
            query = ",".join([
                "{key}.{direction}".format(
                    key=self._to_sort_query_key(s),
                    direction=self._to_sort_dir(s))
                for s in sorters
            ])

            if "?" not in url and query:
                url += "?"

            if query and url[-1] != "?":
                url += "&"

            url += "orderBy=" + query

        return url

    def get_param(self, name):
        if self.has_param(name):
            return getattr(self.__params__, name)
        else:
            return None

    def has_param(self, name):
        return hasattr(self, '__params__') and \
            hasattr(self.__params__, name) and \
            getattr(self.__params__, name) is not None

    def headers(self):
        return {}

    def http_method(self):
        return None

    def url(self):
        return None

    def with_paging(self):
        return False

    # ===============
    # PRIVATE METHODS
    # ===============

    def _build_params_def(self):
        if hasattr(self, 'params'):
            params_def = self.params()
        else:
            params_def = {}

        if self.with_paging():
            for param in ['page_number', 'page_size']:
                params_def[param] = {
                    'required': False,
                    'default': None
                }

        if hasattr(self, 'fields'):
            fields = self.fields()
            filterable = any([
                'filter' in v and v['filter']
                for k, v in fields.items()
            ])
            sortable = any([
                'sort' in v and v['sort']
                for k, v in fields.items()
            ])

            if filterable:
                params_def['filters'] = {
                    'required': False,
                    'default': []
                }
            if sortable:
                params_def['sort'] = {
                    'required': False,
                    'default': []
                }

        return params_def

    def _to_filter_query_key(self, string):
        fields = self.fields()
        valid_keys = [key for key, d
                      in fields.items()
                      if 'filter' in d and d['filter']]

        if string not in valid_keys:
            raise UnknownFilterKeyError(string, valid_keys)

        return self._to_query_key(string, fields)

    def _to_operator(self, string):
        if string.upper() in ["EQ", "EQUALS", "=", "=="]:
            return "="
        else:
            return ".{}=".format(string.upper())

    def _to_query_key(self, string, fields):
        if 'query_key' in fields[string]:
            return fields[string]['query_key']
        elif '_' in string and len(string.split('_')) > 1:
            parts = string.split('_')
            return ''.join(parts[0:1] + [s.capitalize() for s in parts[1:]])
        else:
            return string

    def _to_sort_dir(self, string):
        parts = string.split(" ")

        if len(parts) < 2:
            return "ASCENDING"
        elif parts[1].upper() in ["ASC", "ASCENDING"]:
            return "ASCENDING"
        else:
            return "DESCENDING"

    def _to_sort_query_key(self, string):
        string = string.split(" ")[0]
        fields = self.fields()
        valid_keys = [key for key, d
                      in fields.items()
                      if 'sort' in d and d['sort']]

        if string not in valid_keys:
            raise UnknownSortKeyError(string, valid_keys)

        return self._to_query_key(string, fields)
