import re
import properties
from ..common import EqualityMixin
from connection import get_client
from connection import DEFAULT_HANDLE

__all__ = ["DocumentMeta", "BaseDocument", "Document", "EmbeddedDocument"]

class DocumentMeta(type):
    """
    A metaclass for document types. Handles the :attr:`_options` attribute in
    :class:`~apibuilder.client.document.Document` classes and generates names
    for classes by converting the class names to snake case.
    """
    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        cls._field_types = None
        options = attrs.get("_options", {})
        if "_options" in attrs:
            del attrs["_options"]
        cls._conn_handle = options.get("conn_handle", DEFAULT_HANDLE)
        default_name = re.sub('(?!^)([A-Z]+)', r'_\1', name).lower()
        cls._name = options.get("name", default_name)
    def __call__(cls, *args, **kwargs):
        if cls._field_types is None:
            field_types = {}
            for name in dir(cls):
                if not name.startswith('_'):
                    field_type = getattr(cls, name)
                    if isinstance(field_type, type) and issubclass(field_type,
                            properties.BaseProperty):
                        field_types[name] = field_type
            cls._field_types = field_types
        return type.__call__(cls, *args, **kwargs)

class BaseDocument(EqualityMixin):
    """
    Base class for any document types in this class. The constructor takes a
    dictionary of property types, constructs the relevant property objects and
    stores them in the :attr:`_properties` attribute of the object.

    :class:`BaseDocument` also overrides :func:`__getitem__`,
    :func:`__setitem__`, :func:`__getattribute__`, and :func:`__setattribute__`
    to access property. Thus, a property :attr:`attr1` can be accessed in either
    of two ways. With attribute-style access::

        doc.attr1 = "val1"

    Or with dictionary-style access::

        doc["attr1"] = "val1"
    """
    def __init__(self, property_types):
        properties = self._properties if hasattr(self, "_properties") else {}
        for name, property_type in property_types.iteritems():
            properties[name] = property_type()
        self._properties = properties
    def __contains__(self, name):
        return name in self._properties
    def __getitem__(self, name):
        return self._properties[name].get_val()
    def __setitem__(self, name, val):
        self._properties[name].set_val(val)
    def __getattribute__(self, name):
        if not name.startswith('_') and name in self._properties:
            return self._properties[name].get_val()
        else:
            return super(BaseDocument, self).__getattribute__(name)
    __getattr__ = __getattribute__
    def __setattribute__(self, name, val):
        if not name.startswith('_') and name in self._properties:
            self._properties[name].set_val(val)
        else:
            super(BaseDocument, self).__setattr__(name, val)
    __setattr__ = __setattribute__
    def to_json(self):
        return {k:v.to_json() for k,v in self._properties.iteritems()}

class Document(BaseDocument):
    """
    Main document class for :mod:`apibuilder.client`. Represents a type of
    documents stored on an :class:`~apibuilder.server.APIServer` instance.

    :class:`~apibuilder.document.Document` inherits from
    :class:`~apibuilder.document.BaseDocument`, so attributes can be accessed
    with attribute-style access::

        doc.attr1 = "val1"

    Or dictionary style acccess::

        doc["attr1"] = "val1"
    """
    __metaclass__ = DocumentMeta
    @classmethod
    def get_by_id(cls, _id):
        """
        Retreive a specific instance of this document type from an
        :class:`~apibuilder.server.APIServer` instance using the connection
        associated with the handle stored in the :attr:`_conn_handle` class
        attribute.

        :param _id: The ID of the object to retreive
        """
        return cls(**get_client(cls._conn_handle).get_object(cls._name, _id))
    @classmethod
    def list(cls, **kwargs):
        """
        Retreive a list of instances of this document type from an
        :class:`~apibuilder.server.APIServer` instance using the connection
        associated with the handle stored in the :attr:`_conn_handle` class
        attribute.
        """
        return [cls(**obj) for obj in
                get_client(cls._conn_handle).list_object(cls._name, **kwargs)]
    def __init__(self, _id=None, **kwargs):
        super(Document, self).__init__(self._field_types)
        id_property = properties.IdProperty(_id)
        self._properties["_id"] = id_property
        setattr(self, "_id", id_property)
        for k,v in kwargs.iteritems():
            if k in self:
                self[k] = v
            else:
                raise ValueError("{} is not a valid property name".format(k))
    @property
    def id(self):
        """
        Returns the ID of this object.
        """
        return self._properties["_id"].get_val()
    def save(self):
        """
        Saves this document by pushing its information to an
        :class:`~apibuilder.server.APIServer` instance using the connection
        associated with the handle stored in the :attr:`_conn_handle` class
        attribute.
        """
        conn_handle = self.__class__._conn_handle
        cls_name = self.__class__._name
        if self._id.get_val():
            if not get_client(conn_handle).update_object(cls_name, self.to_json()):
                raise ValueError("{} was not found on the server".format(cls_name))
        else:
            vals = get_client(conn_handle).create_object(cls_name,
                    self.to_json())
            if not vals:
                raise RuntimeError("Failed to create {} type" % cls_name);
            self.__init__(**vals)
    def delete(self):
        """
        Deletes this document from an :class:`~apibuilder.server.APIServer`
        instance  using the connection associated with the handle stored in the
        :attr:`_conn_handle` class attribute.
        """
        if self._id.get_val():
            conn_handle = self.__class__._conn_handle
            cls_name = self.__class__._name
            if not get_client(conn_handle).delete_object(cls_name,
                    self._id.get_val()):
                raise ValueError("{} was not found on the server".format(cls_name))

class EmbeddedDocument(BaseDocument):
    """
    A class for embedded documents, that is, documents stored as a property of
    a :class:`~apibuilder.client.document.Document` type in an
    :func:`~apibuilder.client.properties.EmbeddedDocumentProperty`.
    """
    __metaclass__ = DocumentMeta
    def __init__(self, **kwargs):
        super(EmbeddedDocument, self).__init__(self._field_types)
        for k,v in kwargs.iteritems():
            if k in self:
                self[k] = v
            else:
                raise ValueError("{} is not a valid property name".format(k))
