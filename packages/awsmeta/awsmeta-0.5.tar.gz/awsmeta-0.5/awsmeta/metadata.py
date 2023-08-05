from urllib2 import (
    urlopen,
    HTTPError,
    URLError,
)

BASEURL = 'http://169.254.169.254/'

DEFAULT_TIMEOUT = 2
DEFAULT_API_VERSION = 'latest'


class MetadataError(Exception):
    pass


def path(path=None, api_version=DEFAULT_API_VERSION, timeout=DEFAULT_TIMEOUT):
    if not api_version:
        api_version = 'latest'
    md_path = api_version
    if path:
        md_path = md_path + "/" + path
    try:
        u = urlopen(BASEURL + md_path, timeout=timeout)
    except HTTPError as e:
        if e.code == 404:
            raise MetadataError("Path not found: /%s" % path)
        else:
            raise MetadataError(e)
    except URLError as e:
        raise MetadataError(e)
    if not path:
        return "\n".join(map(lambda p: p.strip() + "/", u.readlines()))
    return u.read()


class ShortNames(object):
    '''Provide commonly-used metadata values by name'''
    names = {
        'az': '/meta-data/placement/availability-zone',
        'instance-id': '/meta-data/instance-id',
    }

    def __init__(self, api_version=None, timeout=DEFAULT_TIMEOUT):
        self.api_version = api_version
        self.timeout = timeout

    def list(self):
        return self.names.keys()

    def get(self, name):
        if name not in self.names:
            raise MetadataError('The shortname "{}" is not defined'.format(name))

        return path(self.names[name], self.api_version, self.timeout)
