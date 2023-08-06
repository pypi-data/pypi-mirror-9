from contextlib import contextmanager
import re
from bson.objectid import ObjectId
from imagination.loader import Loader
from imagination.decorator.validator import restrict_type
from passerine.db.driver.interface import DriverInterface
from passerine.db.session import Session
from passerine.db.exception import InvalidUrlError, UnknownDriverError

class ManagerFactory(object):
    def __init__(self, protocol_to_driver_map = None):
        self._protocol_to_driver_map = {}
        self._alias_to_url_map       = {}
        self._alias_to_manager_map   = {}
        self._re_url = re.compile('(?P<protocol>[a-zA-Z]+)://(?P<address>.+)')

        p2d_map = (protocol_to_driver_map or self._default_protocol_to_driver_map)

        for protocol in p2d_map:
            self.register(protocol, p2d_map[protocol])

    @property
    def _default_protocol_to_driver_map(self):
        return {
            'mongodb': 'passerine.db.driver.mongodriver.Driver',
            #'riak':    'passerine.db.driver.riakdriver.Driver'
        }

    def register(self, protocol, driver_class):
        """ Register the protocol to the driver class.

            :param str protocol:     the protocol string (e.g., mongodb, riak)
            :param passerine.db.driver.interface.DriverInterface driver_class: a DriverInterface-based class (type)
        """
        self._protocol_to_driver_map[protocol] = driver_class \
            if isinstance(driver_class, type) \
            else Loader(driver_class).package

    def analyze_url(self, url):
        index = 0
        connection_info = {}

        matches = self._re_url.match(url)

        if matches:
            return matches.groupdict()

        raise InvalidUrlError('Invalid URL to {}'.format(url))

    def driver(self, url):
        config = self.analyze_url(url)

        if not config:
            raise UnknownDriverError('Unable to connect to {} due to invalid configuration'.format())

        if config['protocol'] in self._protocol_to_driver_map:
            return self._protocol_to_driver_map[config['protocol']](url)

        raise UnknownDriverError('Unable to connect to {}'.format(url))

    def set(self, alias, url):
        self._alias_to_url_map[alias] = url

    def get(self, alias):
        return self.connect(self._alias_to_url_map[alias], alias)

    def connect(self, url, alias = None):
        if alias in self._alias_to_manager_map:
            return self._alias_to_manager_map[alias]

        driver  = self.driver(url)
        manager = Manager(driver)

        if alias:
            self._alias_to_manager_map[alias] = manager

        return manager

class Manager(object):
    """ Entity Manager

        :param driver: the driver interface
        :type  driver: passerine.db.driver.interface.DriverInterface
    """
    def __init__(self, driver):
        assert isinstance(driver, DriverInterface) or issubclass(driver, DriverInterface), \
            'The given driver must implement DriverInterface, {} given.'.format(driver)
        self._driver      = driver
        self._session_map = {}
        self._driver      = driver

    @property
    def driver(self):
        """ Driver API

        :rtype: passerine.db.driver.interface.DriverInterface
        """
        return self._driver

    @contextmanager
    def session(self, id=None, supervised=False):
        """ Open a session in the context manager.

            :param id: the session ID
            :param bool supervised: the flag to indicate that the opening session
                                    will be observed and supervised by the manager.
                                    This allows the session to be reused by multiple
                                    components. However, it is not **thread-safe**.
                                    It is disabled by default.

            .. note:: The end of the context will close the open session.
        """
        session = self.open_session(id, supervised)

        yield session

        self.close_session(id)

    def open_session(self, id=None, supervised=False):
        """ Open a session

            :param id: the session ID
            :param bool supervised: the flag to indicate that the opening session
                                    will be observed and supervised by the manager.
                                    This allows the session to be reused by multiple
                                    components. However, it is not **thread-safe**.
                                    It is disabled by default.
        """
        if not supervised:
            return Session(self.driver)

        if not id:
            id = ObjectId()

        if id in self._session_map:
            return self._session_map[id]

        session = Session(self.driver)

        if supervised:
            self._session_map[id] = session

        return session

    def close_session(self, id):
        """ Close the managed session

            .. warning::

                This method is designed to bypass errors when the given ID is
                unavailable or already closed.
        """
        if id not in self._session_map:
            return

        del self._session_map[id]
