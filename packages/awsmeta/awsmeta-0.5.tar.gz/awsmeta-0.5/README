# awsmeta

A tool for querying the AWS metadata service

Requires Python 2.6+ (and must be run from an EC2 instance)

```
usage: awsmeta [-h] [-v API_VERSION] [--timeout TIMEOUT] [--version]
               [-n short-name] [--list-names]
               [path]

positional arguments:
  path

optional arguments:
  -h, --help            show this help message and exit
  -v API_VERSION        Metadata API version (default='latest')
  --timeout TIMEOUT     HTTP connection timeout in seconds (default: 2)
  --version             show the awsmeta version
  -n short-name, --by-name short-name
                        Look up a named metadata value
  --list-names          Print a list of known named metadata keys
```

# Installation

System-wide: `sudo pip install awsmeta`

User installation: `pip install --user awsmeta` (or use a virtualenv)

When installing as root, a bash completion script is installed to
/etc/bash_completion.d. As a non-root user, you'll need to install the
completion script yourself. You'll find it in the etc/bash_completion.d
subdirectory of the installation path.

# Packaging

[FPM](https://github.com/jordansissel/fpm) is recommended.

Example:

```
fpm -s python -t deb \
  --iteration <package_revision> \
  --after-install=extras/fpm/after-install \
  --before-remove=extras/fpm/before-remove \
  setup.py
```
