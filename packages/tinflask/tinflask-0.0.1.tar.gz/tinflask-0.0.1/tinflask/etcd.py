import requests
import ujson as json


def _keys(nodes):
    """Returns a list of keys from the given nodes.

    eg.
    ---------------------------------------------------------------------------
        For a node like the below:
    ---------------------------------------------------------------------------
            [
                {
                    "createdIndex": 137,
                    "key": "/dev/xx.ABC001/authorizedKeys/yy.DEF001",
                    "modifiedIndex": 137,
                    "value": ""
                }, {
                    "createdIndex": 192,
                    "key": "/dev/xx.ABC001/authorizedKeys/zz.GHI001",
                    "modifiedIndex": 192,
                    "value": ""
                }
            ]
    ---------------------------------------------------------------------------
        The return would be:
    ---------------------------------------------------------------------------
            ["yy.DEF001", "zz.GHI001"]

    """
    keys = {}
    for node in nodes:
        if 'key' not in node:
            continue

        # The key is the value after the last `/`.
        # eg:
        #   for this value `/prod/ci.MPP001/privateKey`
        #   the key would be `privateKey`
        i = node['key'].rfind('/')+1
        key = node['key'][i:]
        # Append the key to the list.
        keys[key] = node['value']
    return keys

def _data(etcd_url):
    """Invokes the given URL, parses the JSON response, and returns
    either a node list, or the value of a node.

    ---------------------------------------------------------------------------
    # For the below etcd response:
    ---------------------------------------------------------------------------
        {
            "action": "get",
            "node": {
                "createdIndex": 132,
                "dir": true,
                "key": "/prod/ci.USR001/authorizedKeys",
                "modifiedIndex": 132,
                "nodes": [
                    {
                      "createdIndex": 137,
                      "key": "/prod/ci.USR001/authorizedKeys/ci.PCP001",
                      "modifiedIndex": 137,
                      "value": ""
                    },
                    {
                      "createdIndex": 192,
                      "key": "/prod/ci.USR001/authorizedKeys/ci.SIT001",
                      "modifiedIndex": 192,
                      "value": ""
                    }
                ]
            }
        }
    ---------------------------------------------------------------------------
    # The nodes list would be returned:
    ---------------------------------------------------------------------------
        "nodes": [
            {
              "createdIndex": 137,
              "key": "/prod/ci.USR001/authorizedKeys/ci.PCP001",
              "modifiedIndex": 137,
              "value": ""
            },
            {
              "createdIndex": 192,
              "key": "/prod/ci.USR001/authorizedKeys/ci.SIT001",
              "modifiedIndex": 192,
              "value": ""
            }
        ]
    ---------------------------------------------------------------------------
    # For the below etcd response:
    ---------------------------------------------------------------------------
        {
            "action": "get",
            "node": {
                "createdIndex": 133,
                "key": "/prod/ci.USR001/privateKey",
                "modifiedIndex": 133,
                "value": "b2c30cfd-4f34-4c2d-9af0-c69fe1eb338a"
            }
        }
    ---------------------------------------------------------------------------
    # The value would be returned:
    ---------------------------------------------------------------------------
        "b2c30cfd-4f34-4c2d-9af0-c69fe1eb338a"

    """
    r = requests.get(etcd_url)
    if r.status_code != 200:
        err = 'Invalid status {status} from etcd.'.format(status=r.status_code)
        raise Exception(err)

    j = r.json()
    if 'node' not in j:
        raise Exception('"node" missing from etcd response.')

    node = j['node']
    # Either have a collection of nodes or a value.
    if 'nodes' in node:
        return _keys(node['nodes'])
    elif 'value' not in node:
        raise Exception('"value" missing from etcd response node.')
    return node['value']

def authorized_key(etcd_url, key):
    """Gets the private key matching the given key from etcd.

    This is used to grab a private key that has been hard-set within
    an entries `authorizedKeys` collection.
    """
    return _data('{0}/authorizedKeys/{1}'.format(etcd_url, key))

def authorized_keys(etcd_url):
    """Returns a list of authorized keys for the entry.
    """
    return _data(etcd_url+'/authorizedKeys')

def private_key(etcd_url):
    """Returns the private key for the entry.
    """
    return _data(etcd_url+'/privateKey')

def config(etcd_url):
    """Returns the configuration for the entry.
    """
    data = _data(etcd_url+'/configuration')
    if data:
        return json.loads(data)
    return {}
