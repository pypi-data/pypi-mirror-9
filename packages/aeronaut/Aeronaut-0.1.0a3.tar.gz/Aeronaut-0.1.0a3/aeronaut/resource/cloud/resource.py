from lxml import etree, objectify
import math


# =========
# EXCEPTION
# =========

class MissingResourceMembersDeclaration(Exception):

    def __init__(self, obj):
        message = 'class {} does not have a _members_ method' \
                  .format(obj.__class__.__name__)
        super(MissingResourceMembersDeclaration, self).__init__(message)


class MissingRootElementDeclarationError(Exception):

    def __init__(self, obj):
        message = 'class {} does not have a _root_ method' \
                  .format(obj.__class__.__name__)
        super(MissingRootElementDeclarationError, self).__init__(message)


class RootElementNotFoundError(Exception):

    def __init__(self, tags, xml):
        xmlstr = etree.tostring(xml)
        message = "Unable to find element '{}' in {}" \
                  .format(', '.join(tags), xmlstr)
        super(RootElementNotFoundError, self).__init__(message)


# ==============
# RESOURCE CLASS
# ==============

class Resource(object):

    def __init__(self, xml=None, **kwargs):
        xml_or_str = xml

        if not hasattr(self, '_members_') or self._members_() is None:
            raise MissingResourceMembersDeclaration(self)

        self.__ensure_members()

        # Initialize member values from the provided xml document
        if isinstance(xml_or_str, objectify.ObjectifiedElement) \
                or (isinstance(xml_or_str, str) and len(xml_or_str) > 0):

            if isinstance(xml_or_str, str):
                xml = objectify.fromstring(xml_or_str)
            else:
                xml = xml_or_str

            if not hasattr(self, '_root_'):
                raise MissingRootElementDeclarationError(self)

            root_tags = self._root_()

            if not isinstance(root_tags, list):
                root_tags = [root_tags]

            if xml.tag.split('}')[-1] not in root_tags:
                raise RootElementNotFoundError(root_tags, xml)

            root = xml

            attrs = self._members_()

            for key in attrs.keys():
                attr = attrs[key]

                if 'type' not in attr:
                    klass = str
                else:
                    klass = attr['type']

                if 'xpath' in attr:
                    result = root.xpath(attr['xpath'])
                    if result:
                        # Note that this returns a 'smart' string that knows
                        # about its orgiins and also has an xpath() method.
                        # See: http://lxml.de/tutorial.html
                        value = result[0]
                    else:
                        value = ''
                else:
                    value = ''

                if klass == bool:
                    # bool always evaluates strings as True (including the
                    # string 'false') so we have to treat boolean fields
                    # differently
                    value = value in ['True', True, 'true']
                elif klass == "auto":
                    value = self.__autocast(value)
                else:
                    try:
                        value = klass(value)
                    except ValueError:
                        value = None

                self.__init_property(key, value)

            # If the xml object has child elements named 'property', those will
            # be available via the [] accessor where the property name is the
            # key and the property value is the value.
            self.__items = {
                p.get('name'): self.__autocast(p.get('value'))
                for p in root.xpath("./*[local-name()='property']")
            }

        # Prevent random attributes from being added going forward
        self.__freeze()

    # ==============
    # PUBLIC METHODS
    # ==============

    def to_dict(self, only_dirty=False):
        """
        Returns the resource's members and their values as a dictionary.

        Args:
            only_dirty (bool): When True, returns only the members that changed
        """
        if only_dirty:
            properties = self.__dirty_properties
        else:
            properties = self.__all_properties

        items = {}

        for name in properties:
            items[name] = self.__get_property(name)

        return items

    # =============
    # MAGIC METHODS
    # =============

    def __getitem__(self, key):
        return self.__items[key]

    __isfrozen = False

    def __setattr__(self, key, value):
        if self.__isfrozen and not hasattr(self, key):
            raise AttributeError("Unknown attribute {}".format(key))
        object.__setattr__(self, key, value)

    # ===============
    # PRIVATE METHODS
    # ===============

    def __autocast(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            pass

        try:
            return float(value)
        except (ValueError, TypeError):
            pass

        return str(value)

    def __add_property(self, name):
        """
        Adapted from http://goo.gl/si4kmX

        This dynamically creates the Python properties from the attributes
        defined in _members_(). We do it this way so:

            1) the attributes are visible when inspecting the object via
               dir(object_instance) and

            2) more importantly, so we can freeze the instance after
               initialization, preventing accidental attribute creation due
               to misspellings.
        """
        getter = lambda self: self.__get_property(name)
        setter = lambda self, value: self.__set_property(name, value)
        setattr(self.__class__, name, property(getter, setter))

    def __ensure_members(self):
        attrs = self._members_()

        self.__all_properties = attrs.keys()
        self.__dirty_properties = []

        for key in attrs.keys():
            # This creates a getter and setter in the class if it doesn't exist
            if not hasattr(self.__class__, key):
                self.__add_property(key)

            # This creates an attribute in the instance
            self.__init_property(key, None)

    def __freeze(self):
        self.__isfrozen = True

    def __get_property(self, name):
        """
        Returns the value of the given property
        """
        return getattr(self, '__property_' + name)

    def __init_property(self, name, value):
        """
        Initialize the property. This is used by __init__ for setting the value
        of the given property without marking the property "dirty"
        """
        setattr(self, '__property_' + name, value)

    def __set_property(self, name, value):
        """
        Sets the value of the given property and marks it as "dirty"
        """
        if name not in self.__dirty_properties:
            self.__dirty_properties.append(name)
        setattr(self, '__property_' + name, value)


# ===================
# RESOURCE LIST CLASS
# ===================

class ResourceList(object):

    def __init__(self, xml=None, resources=None):
        if isinstance(xml, objectify.ObjectifiedElement) \
                or (isinstance(xml, str) and len(xml) > 0):

            if isinstance(xml, str):
                xml = objectify.fromstring(xml)

            if not hasattr(self, '_root_'):
                raise MissingRootElementDeclarationError(self)

            root_tags = self._root_()

            if not isinstance(root_tags, list):
                root_tags = [root_tags]

            if xml.tag.split('}')[-1] not in root_tags:
                raise RootElementNotFoundError(root_tags, xml)

            self.__root_node = xml

            xpath = self._items_()['xpath']

            if 'type' not in self._items_():
                klass = str
            else:
                klass = self._items_()['type']

            self.__items = [klass(item) for item in xml.xpath(xpath)]

    def __getitem__(self, index):
        return self.__items[index]

    def __len__(self):
        return len(self.__items)

    @property
    def page_number(self):
        return self._get_paging_value_or_none('pageNumber')

    @property
    def page_size(self):
        return self._get_paging_value_or_none('pageSize')

    @property
    def total_count(self):
        return self._get_paging_value_or_none('totalCount')

    @property
    def total_pages(self):
        total_count = self._get_paging_value_or_none('totalCount')
        page_size = self._get_paging_value_or_none('pageSize')

        if total_count:
            return int(math.ceil(float(total_count) / page_size))
        else:
            return None

    def _get_paging_value_or_none(self, name):
        v = self.__root_node.xpath("./@{}".format(name))

        if v:
            return int(v[0])
        else:
            return None


# ============
# STATUS CLASS
# ============

class StatusAdditionalInfo(Resource):

    def _root_(self):
        return "additionalInformation"

    def _members_(self):
        return {
            "name": {
                "xpath": "./@*[local-name()='name']"},

            "value": {
                "xpath": "./*[local-name()='value']"},
        }


class StatusAdditionalInfoList(ResourceList):

    def _root_(self):
        return 'Status'

    def _items_(self):
        return {
            "xpath": "./*[local-name()='additionalInformation']",
            "type": StatusAdditionalInfo
        }


class Status(Resource):

    def _root_(self):
        return "Status"

    def _members_(self):
        return {
            "additional_info": {
                "xpath": ".",
                "type": StatusAdditionalInfoList},

            "operation": {
                "xpath": "./*[local-name()='operation']"},

            "result": {
                "xpath": "./*[local-name()='result']"},

            "result_detail": {
                "xpath": "./*[local-name()='resultDetail']"},

            "result_code": {
                "xpath": "./*[local-name()='resultCode']"}
        }

    @property
    def is_success(self):
        return self.result_code == 'REASON_0'
