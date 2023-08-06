# Imports
from ..common import Error
from ..common import EqualityMixin
import json
import requests

# Globals
_clients = {}
JSON_HEADERS = {"content-type": "application/json"}

#: The default hostname for a connection to an :class:`~apibuilder.server.APIServer`
DEFAULT_HOSTNAME = "localhost"
#: The default port for a connection to an :class:`~apibuilder.server.APIServer`
DEFAULT_PORT = 80
#: The handle to which a connection is registered if no handle is supplied
DEFAULT_HANDLE = "default"

__all__ = ["NoSuchConnectionError", "AuthenticationError", "InternalServerError"]
__all__ += ["APIClient", "connect", "register_connection", "get_client"]
__all__ += ["DEFAULT_HOSTNAME", "DEFAULT_PORT", "DEFAULT_HANDLE"]

class NoSuchConnectionError(Error):
    """
    This error should be thrown when a client attempts to retreive a connection
    with a given handle and there is no registered connection for that handle

    :param handle: The requested connection handle
    """
    def __init__(self, handle):
        message = "There is no existing connection with the given handle %s" % \
            handle
        super(NoSuchConnectionError, self).__init__(message)
class AuthenticationError(Error):
    """
    This error should be thrown when a request to a server returns a 401 error
    """
    def __init__(self):
        super(AuthenticationError, self).__init__("Credentials rejected")
class InternalServerError(Error):
    """
    This error should be thrown when a request to a server returns a 500 error
    """
    def __init__(self):
        super(InternalServerError, self).__init__("Internal server error")

class MyRequests(object):
    """
    Wraps the important function calls from the requests library and provides
    some default error handling for them
    """
    def get(self, *args, **kwargs):
        """
        Wraps :func:`requests.get` and raises errors on 401s and 500s
        """
        return self.__check_result(requests.get(*args, **kwargs))
    def post(self, *args, **kwargs):
        """
        Wraps :func:`requests.post` and raises errors on 401s and 500s
        """
        return self.__check_result(requests.post(*args, **kwargs))
    def put(self, *args, **kwargs):
        """
        Wraps :func:`requests.put` and raises errors on 401s and 500s
        """
        return self.__check_result(requests.put(*args, **kwargs))
    def delete(self, *args, **kwargs):
        """
        Wraps :func:`requests.delete` and raises errors on 401s and 500s
        """
        return self.__check_result(requests.delete(*args, **kwargs))
    def __check_result(self, res):
        if res.status_code == 401:
            raise AuthenticationError()
        elif res.status_code == 500:
            raise InternalServerError()
        return res
myRequests = MyRequests()

class APIClient(EqualityMixin):
    """
    Represents a connection to an :class:`~apibuilder.server.APIServer`
    instance.

    Calls to an endpoint on the :class:`~apibuilder.server.APIServer`, will be
    formatted ``http://<hostname>:<port><prefix><endpoint>``, where
    ``<hostname>``, ``<port>``, and ``<prefix>`` are replaced with the values of
    their eponymous initialization parameters and ``<endpoint>`` is replaced by
    the target endpoint (e.g. "/sensor" for a class named ``Sensor`` registered
    to the :class:`~apibuilder.server.APIServer` instance).

    :param hostname: The hostname of the machine on which the
        :class:`~apibuilder.server.APIServer` instance is running
    :param port: The port on which the :class:`~apibuilder.server.APIServer`
        instance is running
    :param prefix: A prefix to apply to all URLs being requested
    :param auth: A (username, password) tuple of the credentials that should be
        used to access the server
    """
    def __init__(self, hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT,
            prefix=None, auth=None):
        self.requests = myRequests
        self.hostname = hostname
        self.port = str(port)
        self.prefix = prefix
        self.auth = auth
    def get_object(self, cls_name, _id):
        """
        Retreive information on an object of a given type with a given id.
        Returns a dictionary of the relevant information

        :param cls_name: The name of the object type that should be queried
        :param _id: The ID string of the desired object
        """
        url = self.build_url(cls_name, _id)
        res = self.requests.get(url, auth=self.auth)
        if res.status_code == 200:
            return res.json()
    def update_object(self, cls_name, obj_info):
        """
        Update the information on an object of a given type to the given
        information. Returns True if the operation succeeded and False otherwise

        :param cls_name: The name of the object type that should be queried

        :param obj_info: A dictionary of all of the attributes of the object
            being updated
        """
        url = self.build_url(cls_name, obj_info["_id"])
        res = self.requests.put(url, json.dumps(obj_info), headers=JSON_HEADERS,
                auth=self.auth)
        if res.status_code == 204:
            return True
        else:
            return False
    def delete_object(self, cls_name, _id):
        """
        Delete the object of the given type with the given id.

        :param cls_name: The name of the object type that should be queried
        :param _id: The ID string of the object to be deleted
        """
        url = self.build_url(cls_name, _id)
        res = self.requests.delete(url, auth=self.auth)
        if res.status_code == 204:
            return True
        else:
            return False
    def list_object(self, cls_name, **kwargs):
        """
        List all of the objects of the given type. Returns an array of
        dictionaries, each of which contains all of the attributes of an object
        on the server.

        :param cls_name: The name of the object type that should be queried
        :param kwargs: Additional arguments to be passed in the query. These
            can be used to filter the resulting list by some attribute. For the
            structure of these arguments, see the mongoengine `Querying the
            database <http://docs.mongoengine.org/guide/querying.html>`_ page
        """
        url = self.build_url(cls_name)
        return self.requests.get(url, auth=self.auth, params=kwargs,
                headers=JSON_HEADERS).json()
    def create_object(self, cls_name, obj_info):
        """
        Create a new object of the given type with the given set of attributes.
        Returns a dictionary of all of the attributes of the newly created
        object if the operation succeeded. Returns None if the operation failed.

        :param cls_name: The name of the object type that should be queried
        :param obj_info: A dictionary of all of the attributes of the object
            being created
        """
        url = self.build_url(cls_name)
        res = self.requests.post(url, data=json.dumps(obj_info),
                headers=JSON_HEADERS, auth=self.auth)
        if res.status_code == 201:
            return res.json()
    def build_url(self, *args):
        """
        Builds a url of the form ``http://<hostname>:<port><prefix><endpoint>``,
        where ``<hostname>``, ``<port>``, and ``<prefix>`` are replaced with the
        values of their eponymous initialization parameters and ``<endpoint>``
        is replaced with the list of endpoint arguments, separated by ``/``s.

        :param args: A list of strings that defines the endpoint to be visited.
        """
        url = "http://"
        url += self.hostname
        url += ":"
        url += self.port
        url += self.prefix or ""
        for arg in args:
            url += "/"
            url += arg
        return url

def connect(hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT, prefix=None,
        auth=None, handle=DEFAULT_HANDLE):
    """
    Create a connection to an :class:`apibuilder.server.APIServer` instance and
    register it.

    :param hostname: The hostname of the machine on which the
        :class:`~apibuilder.server.APIServer` instance is running
    :param port: The port on which the :class:`~apibuilder.server.APIServer`
        instance is running
    :param prefix: A prefix to apply to all URLs being requested
    :param auth: A (username, password) tuple of the credentials that should be
        used to access the server
    :param handle: The handle to associate wih the connection to this
        :class:`~apibuilder.server.APIServer` instance
    """
    register_connection(APIClient(hostname, port, prefix, auth), handle)

def register_connection(client, handle=DEFAULT_HANDLE):
    """
    Register an :class:`~apibuilder.client.connection.APIClient` instance

    :param client: The :class:`~apibuilder.client.connection.APIClient` instance
        to register
    :param handle: The handle to associate with the
        :class:`~apibuilder.client.connection.APIClient` instance
    """
    global _clients
    if not isinstance(client, APIClient):
        raise TypeError("client must be an APIClient instance")
    _clients[handle] = client

def get_client(handle=DEFAULT_HANDLE):
    """
    Retreive the stored :class:`~apibuilder.client.connection.APIClient`
    instance associated with a given handle

    :param handle: The handle of the
        :class:`~apibuilder.client.connection.APIClient` instance to retreive.
    """
    global _clients
    if not handle in _clients:
        raise NoSuchConnectionError(handle)
    return _clients[handle]
