from __future__ import print_function
import sys
from argparse import ArgumentParser

from . import (
    VERSION,
    metadata,
)


def define_args():
    ap = ArgumentParser()
    ap.add_argument('-v', metavar="API_VERSION", dest='api_version',
                    default=metadata.DEFAULT_API_VERSION, help="Metadata API "
                    "version (default='{}')".format(metadata.DEFAULT_API_VERSION))
    ap.add_argument('--timeout', default=metadata.DEFAULT_TIMEOUT, type=int,
                    help='HTTP connection timeout in seconds (default: '
                    '{})'.format(metadata.DEFAULT_TIMEOUT))
    ap.add_argument('--version', action='store_true',
                    help='show the awsmeta version')
    ap.add_argument('-n', '--by-name', nargs=1, metavar="short-name",
                    help='Look up a named metadata value')
    ap.add_argument('--list-names', action='store_true',
                    help='Print a list of known named metadata keys')
    ap.add_argument('path', nargs='?')

    return ap


def resolve_args(ap, args=sys.argv[1:]):
    args = ap.parse_args(args)
    return args


def main():
    ap = define_args()
    args = resolve_args(ap)

    if args.version:
        print("v%s" % VERSION)
        sys.exit(0)

    if args.list_names:
        for name in metadata.ShortNames().list():
            print(name)
        sys.exit(0)

    if args.by_name:
        try:
            sn = metadata.ShortNames(args.api_version, args.timeout)
            print(sn.get(args.by_name[0]))
            sys.exit(0)
        except metadata.MetadataError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

    try:
        print(metadata.path(
            path=args.path,
            api_version=args.api_version,
            timeout=args.timeout).strip(),
        )
    except metadata.MetadataError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
