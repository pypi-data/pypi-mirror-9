"""gitlab-copy-id v{version}

Usage:
    gitlab-copy-id [--force] [--identity-file=<file>] [--token=<token>] [--user=<user>] <gitlab-address>

Options:
    -f, --force                     force update if key already exists
    -i, --identity-file=<file>      path of the private key [default: ~/.ssh/id_rsa]
    -t, --token=<token>             GitLab API Token
    -u, --user=<user>               GitLab username [default: {user}]

"""

__import__("pkg_resources").declare_namespace(__name__)


class Token(object):  # so the token will not appear in tracebacks
    def __init__(self, value):
        super(Token, self).__init__()
        self.value = value

    def __str__(self):
        return self.value


def read_public_key(identity_file):
    from os import path
    with open(path.expanduser(identity_file) + '.pub') as fd:
        return fd.read().strip()


def parse_gitlab_address(gitlab_address):
    from urlparse import urlparse
    url_info = urlparse(gitlab_address)
    hostname = url_info.hostname or url_info.path
    use_ssl = url_info.scheme == 'https'
    return hostname, use_ssl


def get_api(gitlab_address, token):
    from json_rest import JSONRestSender
    gitlab_address, use_ssl = parse_gitlab_address(gitlab_address)
    api = JSONRestSender("{0}://{1}/api/v3".format("https" if use_ssl else "http", gitlab_address))
    api.set_header("PRIVATE-TOKEN", str(token))
    return api


def get_used_ip_address(gitlab_address):
    from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM
    gitlab_address, use_ssl = parse_gitlab_address(gitlab_address)
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect((gethostbyname(gitlab_address), 443 if use_ssl else 80))
    return s.getsockname()[0]


def resolve_ptr_record(ip_address):
    from dns.resolver import get_default_resolver, NXDOMAIN
    from dns.reversename import from_address
    from socket import gethostbyname
    resolver = get_default_resolver()
    query = from_address(ip_address)
    try:
        return resolver.query(query, "PTR")[0].to_text().strip('.')
    except NXDOMAIN:
        logger.debug("No such PTR record: {}".format(query))
    return 'unknown'


def reverse_lookup_address_to_gitlab(gitlab_address):
    ip_address = get_used_ip_address(gitlab_address)
    return resolve_ptr_record(ip_address)


def ensure_key_exists(gitlab_address, token, key, force):
    from getpass import getuser
    api = get_api(gitlab_address, token)
    existing_keys = api.get("/user/keys")
    title = key.split()[-1] if key.count(' ') == 2 else \
            "{0}@{1}".format(getuser(), reverse_lookup_address_to_gitlab(gitlab_address))
    for item in existing_keys:
        if force and item['title'] == title or key in item['key']:
            api.delete("/user/keys/{0}".format(item['id']))
    api.post("/user/keys", data=dict(title=title, key=key))


def main(argv=None):
    import sys
    from docopt import docopt
    from getpass import getuser, getpass
    from .__version__ import __version__
    doc = __doc__.format(user=getuser(), version=__version__)
    argv = sys.argv[1:] if argv is None else argv
    arguments = docopt(doc=doc, argv=argv, version=__version__,)
    token = Token(arguments.pop("--token", None) or getpass("Token: "))
    key = read_public_key(arguments["--identity-file"])
    ensure_key_exists(arguments["<gitlab-address>"], token, key, arguments['--force'])
