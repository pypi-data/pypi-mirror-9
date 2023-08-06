import document
from ..common import EqualityMixin

__all__ = ["BaseProperty", "IdProperty", "StringProperty", "IntProperty"]
__all__ += ["FloatProperty", "ListProperty", "EmbeddedDocumentProperty"]
__all__ += ["ReferenceProperty"]

class BaseProperty(EqualityMixin):
    """
    The base type for all property classes in :mod:`apibuilder.client`.
    Subclasses of this class must implement all of
    :func:`~apibuilder.client.properties.BaseProperty.get_val`,
    :func:`~apibuilder.client.properties.BaseProperty.set_val`, and
    :func:`~apibuilder.client.properties.BaseProperty.to_json`.
    """
    def get_val(self):
        """
        Retreives the value stored inside this property. All subclasses of
        :class:`~apibuilder.client.properties.BaseProperty` must implement this
        method.
        """
        raise NotImplementedError("Subclasses of BaseProperty must define get_val")
    def set_val(self, val):
        """
        Stores the value ``val`` in this property. All subclasses of
        :class:`~apibuilder.client.properties.BaseProperty` must implement this
        method.
        """
        raise NotImplementedError("Subclasses of BaseProperty must define set_val")
    def to_json(self):
        """
        Converts the value stored in this property to a JSON serializable object
        suitable to be sent to an :class:`~apibuilder.server.APIServer`
        instance. All subclasses of
        :class:`~apibuilder.client.properties.BaseProperty` must implement this
        method.
        """
        raise NotImplementedError("Subclasses of BaseProperty must define to_json")

class IdProperty(BaseProperty):
    """
    Holds the ID parameter of an object. It is **read-only**, so the value can
    only be assigned at initialization. All
    :class:`~apibuilder.client.document.Document` instances create an instance
    of this field by default upon initialization.

    :param val: The ID to store in this property. Must be a string. Defaults to
        None.
    """
    def __init__(self, val=None):
        if val and type(val) not in [str, unicode]:
            raise TypeError("IdProperty can only hold string values")
        self._val = val
    def get_val(self):
        """
        Retreives the ID stored in this property.
        """
        return self._val
    def set_val(self, val):
        """
        Throws a :exc:`RuntimeException`. This property is read-only.
        """
        raise RuntimeError("IdProperties are read-only")
    def to_json(self):
        """
        Returns a JSON serializable form of this property: simply the stored
        value itself.
        """
        return self.get_val()

class StringProperty(BaseProperty):
    """
    Holds a string value. It is used as follows::

        class Example(Document):
            name = StringProperty

    :param val: The string to store in this propery. Defaults to the empty
        string, "".
    """
    def __init__(self, val=""):
        self.set_val(val)
    def get_val(self):
        """
        Retreives the string stored in this property.
        """
        return self._val
    def set_val(self, val):
        """
        Store a new value in this property.

        :param val: The value to store. Must be a string.
        """
        if type(val) not in [str, unicode]:
            raise TypeError("Invalid value received - %r" % val)
        self._val = val
    def to_json(self):
        """
        Returns a JSON serializable form of this property: simply the stored
        value itself.
        """
        return self.get_val()

class IntProperty(BaseProperty):
    """
    Holds an integer value. It is used as follows::

        class Example(Document):
            value = IntProperty

    :param val: The integer to store in this property. Defaults to None.
    """
    def __init__(self, val=None):
        self._val = None
        if val:
            self.set_val(val)
    def get_val(self):
        """
        Retreives the value stored in this property.
        """
        return self._val
    def set_val(self, val):
        """
        Store a new value in this property.

        :param val: The value to store. Must be an integer.
        """
        if type(val) is not int:
            raise TypeError("Invalid value received - %r" % val)
        self._val = val
    def to_json(self):
        """
        Returns a JSON serializable form of this property: simply the stored
        value itself.
        """
        return self.get_val()

class FloatProperty(BaseProperty):
    """
    Holds a floating point value. It is used as follows::

        class Example(Document)
            value = FloatProperty

    :param val: The value to store in this property. Defaults to None.
    """
    def __init__(self, val=None):
        self._val = None
        if val:
            self.set_val(val)
    def get_val(self):
        """
        Retreives the value stored in this property.
        """
        return self._val
    def set_val(self, val):
        """
        Store a new value in this property.

        :param val: The value to store. Must be a float.
        """
        if type(val) is not float:
            raise TypeError("Invalid value received - %r" % val)
        self._val = val
    def to_json(self):
        """
        Returns a JSON serializable form of this property: simply the stored
        value itself.
        """
        return self.get_val()

def ListProperty(prop_type):
    """
    Returns a property type that will hold a list of properties of the given
    property type. It is used as follows::

        class Example(Document):
            strings = ListProperty(StringProperty)

    :param prop_type: The type of property to manage

    The constructor for the returned class takes a single optional paramater:

    :param val: A list of values to store. Defaults to [].

    The returned class also has the following methods:

    .. function:: get_val()
        :module: apibuilder.client.properties.ListProperty

        Calls :func:`~apibuilder.client.properties.BaseProperty.get_val` on each
        of the member properties in the list and returns an array of the
        results.

    .. function:: set_val(val=[])
        :module: apibuilder.client.properties.ListProperty

        :param val: An array of values, each of which is suitable to be
            stored in a :class:`prop_type` property.

        Takes in a list of values, generates a :class:`prop_type` instance
        of each one, and stores an array of these properties.

    .. function:: to_json()
        :module: apibuilder.client.properties.ListProperty

        Calls :func:`to_json` on each of the member properties in the list
        and returns an array of the results.
    """
    if not issubclass(prop_type, BaseProperty):
        raise TypeError("ListProperty can only hold BaseProperty subclasses")
    class Prop(BaseProperty):
        def __init__(self, val=[]):
            self.set_val(val)
        def get_val(self):
            return [subval.get_val() for subval in self._val]
        def set_val(self, val):
            if not isinstance(val, list):
                raise TypeError("Invalid value received - %r" % val)
            fields = []
            for subval in val:
                field = prop_type()
                field.set_val(subval)
                fields.append(field)
            self._val = fields
        def to_json(self):
            return [val.to_json() for val in self._val]
    return Prop

def EmbeddedDocumentProperty(doc_type):
    """
    Returns a property type that will hold an embedded document of the given
    document type. It is used as follows::

        class SubDoc(EmbeddedDocument):
            name = StringProperty
        class Example(Document):
            name = StringProperty
            sub = EmbeddedDocumentProperty(SubDoc)

    :param doc_type: The type of embedded document to hold. Must be an
        :class:`~apibuilder.client.document.EmbeddedDocument` subclass

    The constructor for the returned class takes a single optional parameter:

    :param val: A value to store. It can be either a :class:`doc_type` instance
        or a dictionary of values to pass to the constructor for
        :class:`doc_type` to create the :class:`doc_type` object to be stored.

    The returned class also has the following methods:

    .. function:: get_val()
        :module: apibuilder.client.properties.EmbeddedDocumentProperty

        Returns the :class:`doc_type` object stored in this property.

    .. function:: set_val(val)
        :module: apibuilder.client.properties.EmbeddedDocumentProperty

        :param val: Either a :class:`doc_type` instance or a dictionary of
            values to pass to the constructor for :class:`doc_type` to create
            the :class:`doc_type` object to be stored.

        Stores the given value in this property.

    .. function:: to_json()
        :module: apibuilder.client.properties.EmbeddedDocumentProperty

        Calls :func:`to_json` on the contained :class:`doc_type` instance and
        returns the result.
    """
    if not issubclass(doc_type, document.EmbeddedDocument):
        raise TypeError("EmbeddedDocumentProperty can only hold EmbeddedDocuemnt subclasses")
    class Prop(BaseProperty):
        def __init__(self, val=None):
            self.set_val(val or doc_type())
        def get_val(self):
            return self._val
        def set_val(self, val):
            if isinstance(val, doc_type):
                self._val = val
            elif isinstance(val, dict):
                self._val = doc_type(**val)
            else:
                raise TypeError("Invalid value received %r" % val)
        def to_json(self):
            return self.get_val().to_json() if self.get_val() else {}
    return Prop

def ReferenceProperty(doc_type):
    """
    Returns a property type that will hold a reference to a document of a
    given type. It is used as follows::

        class Doc1(Document):
            name = StringProperty
        class Doc2(Document):
            ref = ReferenceProperty(Doc1)

    :param doc_type: The type of document to hold a reference to. Must be a
        :class:`~apibuilder.client.document.Document` subclass

    The constructor for the returned class takes a single optional parameter:

    :param val: A value to store. It can be either a :class:`doc_type` instance
        or the object ID of a :class:`doc_type` instance.

    The returned class also has the following methods:

    .. function:: get_val()
        :module: apibuilder.client.properties.ReferenceProperty

        Returns the :class:`doc_type` object referenced by this property.

    .. function:: set_val(val)
        :module: apibuilder.client.properties.ReferenceProperty

        :param val: Either a :class:`doc_type` instance to be referenced or the
            object ID of a :class:`doc_type` instance to be referenced

        Stores a reference to the given :class:`doc_type` in this property

    .. function:: to_json()
        :module: apibuilder.client.properties.ReferenceProperty

        Returns the object ID of the object referenced by this property
    """
    if not issubclass(doc_type, document.Document):
        raise TypeError("ReferenceProperties can only hold references to Document subclasses")
    class Prop(BaseProperty):
        def __init__(self, val=None):
            self._id = None
            self._val = None
            if val:
                self.set_val(val)
        def get_val(self):
            if not self._val:
                if self._id:
                    self._val = doc_type.get_by_id(self._id)
            return self._val
        def set_val(self, val):
            if isinstance(val, doc_type):
                self._val = val
                self._id = val.id
            elif type(val) in [str, unicode]:
                self._id = val
            else:
                raise TypeError("Invalid value received - %r" % val)
        def to_json(self):
            return self._id
    return Prop
