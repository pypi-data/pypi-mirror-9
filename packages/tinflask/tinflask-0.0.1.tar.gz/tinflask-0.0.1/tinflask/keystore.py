from tinflask import etcd


class KeyStore(object):
    """Store/cache for public/private key pairs for endpoint signing.
    """

    def __init__(self, key, config):
        """Creates a new key store for the given key and configuration.
        """
        self.key = key
        self.private_key = None
        self._keys = {}
        self._config = config

    
    def has_key(self, key):
        """Returns wether the given key is present in the store.
        """
        return key in self._keys

    def keys(self):
        """Returns a list of all keys within the store.
        """
        return list(self._keys)

    def get(self, key):
        """Gets the private key for the given key.
        """
        return self._keys.get(key)

    def load_keys(self):
        """Not Implemented.
        """
        pass

    def load_private_key(self):
        """Not Implemented.
        """
        pass


class File(KeyStore):
    """Configuration file backed KeyStore.

    load functions are side effect free.
    """

    def __init__(self, key, config):
        """Reads private and public keys from configuration file based on environment.
        """
        super(File, self).__init__(key, config)

        self._keys = self._config.get("authorizedKeys", {})
        self.private_key = self._config.get("privateKey")


class ETCD(KeyStore):
    """Etcd backed KeyStore.
    """

    def __init__(self, key, config, etcd_url):
        """Creates a new etcd backed KeyStore.
        """
        super(ETCD, self).__init__(key, config)

        # Load both the private and public keys.
        self._etcd_url = etcd_url
        self.load_private_key()
        self.load_keys()

    def get_etcd(self, key):
        """Returns the the private key from etcd directly.
        """
        url = "%s/%s" % (self._etcd_url, key)
        private_key = etcd.private_key(url)
        return private_key

    def get(self, key):
        """Lazy loads the matching private_key for the given public key.
        """
        private_key = self._keys.get(key, -1)
        if private_key == -1:   # Public key doesn't exist.
            return None
        elif private_key != '': # Private key is already set, return it.
            return private_key

        # Lazy load the private key from etcd.
        private_key = self.get_etcd(key)
        self._keys[key] = private_key
        return private_key

    def load_keys(self):
        """Loads authorized public keys from etcd.
        """
        url = "%s/%s" % (self._etcd_url, self.key)
        try:
            self._keys = etcd.authorized_keys(url)
        except Exception as ex:
            #TODO log this
            print(ex)

    def load_private_key(self):
        """Loads private key from etcd.
        """
        url = "%s/%s" % (self._etcd_url, self.key)
        try:
            self.private_key = etcd.private_key(url)
        except Exception as ex:
            #TODO log this
            print(ex)
