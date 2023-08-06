# Used to store the rest_endpoints dictionary.
# It could go somewhere else, but this is an easy storage method.
# We could also offer this as a JSON object in a file to support
# other implementations.

cloudfs_version = '1.0'

class Values(object):

    allowed = []
    _name = ''

    @classmethod
    def legal_value(cls, value):
        return value in cls.allowed

    @classmethod
    def raise_exception(cls, value):
        from ..errors import invalid_argument
        raise invalid_argument(cls._name, cls.allowed, value)

class ExistValues(Values):
    overwrite = 'overwrite'
    fail = 'fail'
    rename = 'rename'
    _name = 'exists'

    allowed = [overwrite,
               fail,
               rename]


class VersionConflictValue(Values):
    fail = 'fail'
    ignore = 'ignore'
    _name = 'version conflict'

    allowed = [fail, ignore]


class RestoreValue(Values):
    fail = 'fail'
    rescue = 'rescue'
    recreate = 'recreate'

    allowed = [fail, rescue, recreate]


rest_endpoints = {
    # layout:
    # '<friendly name>': {
    #   'params': <dictionary of required parameters>
    #   'url': <url used, with {path} entry if necessary
    #   'data': <required post parameters>
    #   'method': <method string for request>

    # :note: paths are assumed to include a leading / to represent the root.
    # REST Documentation Root: https://developer.bitcasa.com/cloudfs-rest-documentation/
    'ping':{
        'params': {},
        'url':    '/v2/ping',
        'data':   {},
        'method': 'GET'
    },
    'get oauth token':{
        'params': {},
        'url':    '/v2/oauth2/token',
        'data':   {'grant_type':'password'},
        'method': 'POST'
    },
    'create account': {
        'params': {},
        'url':    '/v2/admin/cloudfs/customers/',
        'data':   {},
        'method': 'POST'
    },
    'get user profile':{
        'params': {},
        'url':    '/v2/user/profile/',
        'data':   {},
        'method': 'GET'
    },
    'list folder':{
        'params': {},
        'url':    '/v2/folders{path}',
        'data':   {},
        'method': 'GET'
    },
    'create folder':{
        'params': {'operation':'create'},
        'url':    '/v2/folders{path}',
        'data':   {},
        'method': 'POST'
    },
    'delete folder':{
        'params': {'commit':'false', 'force':'false'},
        'url':    '/v2/folders{path}',
        'data':   {},
        'method': 'DELETE'
    },
    'delete file':{
        'params': {'commit':'false'},
        'url':    '/v2/files{path}',
        'data':   {},
        'method': 'DELETE'
    },
    'move file':{
        'params': {'operation':'move'},
        'url':    '/v2/files{path}',
        'data':   {'to':'','exists':ExistValues.rename},
        'method': 'POST'
    },
    'move folder':{
        'params': {'operation':'move'},
        'url':    '/v2/folders{path}',
        'data':   {'to':'','exists':ExistValues.rename},
        'method': 'POST'
    },
    'copy file':{
        'params': {'operation':'copy'},
        'url':    '/v2/files{path}',
        'data':   {'to':'','exists':ExistValues.rename},
        'method': 'POST'
    },
    'copy folder':{
        'params': {'operation':'copy'},
        'url':    '/v2/folders{path}',
        'data':   {'to':'','exists':ExistValues.rename},
        'method': 'POST'
    },
    'alter file meta':{
        'params': {},
        'url':    '/v2/files{path}/meta',
        'data':   {'version-conflict': VersionConflictValue.fail},
        'method': 'POST'
    },
    'alter folder meta':{
        'params': {},
        'url':    '/v2/folders{path}/meta',
        'data':   {'version-conflict': VersionConflictValue.fail},
        'method': 'POST'
    },
    'get generic meta':{
        'params': {},
        'url':    '/v2/filesystem/root{path}/meta',
        'data':   {},
        'method': 'GET'
    },
    'get file meta':{
        'params': {},
        'url':    '/v2/files{path}/meta',
        'data':   {},
        'method': 'GET'
    },
    'get folder meta':{
        'params': {},
        'url':    '/v2/folders{path}/meta',
        'data':   {},
        'method': 'GET'
    },
    'upload file':{
        'params': {},
        'url':    '/v2/files{path}',
        'data':   {'exists':ExistValues.fail},
        'method': 'POST'
    },
    'download file':{
        'params': {},
        'url':    '/v2/files{path}',
        'data':   {},
        'method': 'GET'
    },
    'list trash':{
        'params': {},
        'url':    '/v2/trash{path}',
        'data':   {},
        'method': 'GET'
    },
    'delete trash item':{
        'params': {},
        'url':    '/v2/trash{path}',
        'data':   {},
        'method': 'DELETE'
    },
    'recover trash item':{
        'params': {},
        'url':    '/v2/trash{path}',
        'data':   {'restore': RestoreValue.fail},
        'method': 'POST'
    },
    'create share':{
        'params': {},
        'url':    '/v2/shares/',
        'data':   {},
        'method': 'POST'
    },
    'download share':{
        'params': {},
        'url':    '/v2/shares/{share_key}{path}/',
        'data':   {},
        'method': 'GET'
    },
    'browse share':{
        'params': {'share_key':''},
        'url':    '/v2/shares/{share_key}{path}/meta',
        'data':   {},
        'method': 'GET'
    },
    'delete share':{
        'params': {},
        'url':    '/v2/shares/{share_key}/',
        'data':   {},
        'method': 'DELETE'
    },
    'list shares':{
        'params': {},
        'url':    '/v2/shares/',
        'data':   {},
        'method': 'GET'
    },
    'receive share':{
        'params': {},
        'url':    '/v2/shares/{share_key}/',
        'data':   {'exists':ExistValues.rename, 'path':'/'},
        'method': 'POST'
    },
    'unlock share':{
        'params': {},
        'url':    '/v2/shares/{share_key}/unlock',
        'data':   {'password':''},
        'method': 'POST'
    },
    'alter share info':{
        'params': {},
        'url':    '/v2/shares/{share_key}/info',
        'data':   {},
        'method': 'POST'
    },
    'list file versions':{
        'params': {},
        'url':    '/v2/files{path}/versions',
        'data':   {},
        'method': 'GET'
    },
    'list single file version':{
        'params': {},
        'url':    '/v2/files{path}/versions/{version}',
        'data':   {},
        'method': 'POST'
    },
    'promote file version':{
        'params': {'operation':'promote'},
        'url':    '/v2/files{path}/versions/{version}',
        'data':   {},
        'method': 'POST'
    },
    'action history':{
        'params': {},
        'url':    '/v2/history',
        'data':   {},
        'method': 'GET'
    }


}