from aircraft.value_object import ValueObject


# ==========
# EXCEPTIONS
# ==========

class MissingRequiredParametersError(Exception):
    def __init__(self, missing):
        if len(missing) == 1:
            substr = ' is'
        else:
            substr = 's are'

        message = 'The following parameter{} required: {}'.format(
            substr, ', '.join(missing))
        super(MissingRequiredParametersError, self).__init__(message)


class MissingDefaultValueError(Exception):
    """
    If this error is raised, that means the request class has a bug. Double
    check that all of its optional parameters have defaults.
    """
    def __init__(self, missing):
        message = "Optional parameter '{}' does not declare a default value" \
                  .format(missing)
        super(MissingDefaultValueError, self).__init__(message)


class UnexpectedParameterNameError(Exception):
    def __init__(self, name):
        message = 'Unknown parameter {}'.format(name)
        super(UnexpectedParameterNameError, self).__init__(message)


# ============
# PARAMS CLASS
# ============

class Params(ValueObject):

    def __init__(self, declared, actual):
        self._attrs = {}

        required_keys = [k for k, v in declared.items() if v['required']]
        optional_keys = list(set(declared.keys()) - set(required_keys))
        missing_keys = list(set(required_keys) - set(actual.keys()))
        default_keys = list(set(optional_keys) - set(actual.keys()))

        if missing_keys:
            raise MissingRequiredParametersError(missing_keys)

        for key in actual.keys():
            if key not in declared.keys():
                raise UnexpectedParameterNameError(key)

            self._attrs[key] = actual[key]

        for key in default_keys:
            if 'default' not in declared[key]:
                raise MissingDefaultValueError(key)

            self._attrs[key] = declared[key]['default']

    def __getitem__(self, key):
        return self._attrs[key]
