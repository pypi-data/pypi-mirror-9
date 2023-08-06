from __future__ import print_function
import argparse
import json
import logging
import logging.config
import os
import os.path
import shutil
import sys
import tarfile
import tempfile
import urllib
import urllib2
import xmlrpclib

PYPI_XMLRPC_URL = 'https://pypi.python.org/pypi'

ARCHIVE_URL = 'https://s3.amazonaws.com/pypi-data/data.tar.bz2'

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', default=False, action='store_true')

    subparsers = parser.add_subparsers()
    
    init_parser = subparsers.add_parser('init')
    init_parser.set_defaults(handler=command_init)
    init_parser.add_argument('path')

    update_parser = subparsers.add_parser('update')
    update_parser.set_defaults(handler=command_update)
    update_parser.add_argument('path')

    full_download_parser = subparsers.add_parser('full-download')
    full_download_parser.set_defaults(handler=command_full_download)
    full_download_parser.add_argument('path')
    full_download_parser.add_argument('--confirm', dest='confirmed', default=False, action='store_true')
    
    args = parser.parse_args()

    log_level_name = 'DEBUG' if args.debug else 'INFO'

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                'format': '%(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'console',
                'level': log_level_name
            }
        },
        'loggers': {
            __name__: {
                'handlers': ['console'],
                'level': log_level_name,
                'propagate': True
            }
        }
    })

    kwargs = vars(args)
    kwargs.pop('debug')
    kwargs.pop('handler')(**kwargs)

def command_init(path):
    init(path)

def command_update(path):
    update(path)

def command_full_download(path, confirmed):
    if not confirmed:
        print((
            'WARNING: Will download ALL metadata.\n'
            '         This is time-consuming, and places a load on the PyPI servers.\n'
            '\n'
            'Alternatively, you can use `{program} init` to download a pregenerated\n'
            'archive.\n'
            '\n'
            'If you definitely want to download ALL metadata, type \'download\' below,\n'
            'or \'exit\' to abort.\n'
        ).format(program=os.path.basename(sys.argv[0])), file=sys.stderr)

        if raw_input('> ') != 'download':
            print('Aborting', file=sys.stderr)
            return

    full_download(path)

def init(path):
    with tempfile.NamedTemporaryFile() as fp:
        logger.info('Downloading from {}'.format(ARCHIVE_URL))
        response = urllib2.urlopen(ARCHIVE_URL)
        shutil.copyfileobj(response, fp)

        fp.seek(0)
        tar = tarfile.open(fileobj=fp, mode='r:bz2')
        for info in tar:
            logger.info('Extracting {}'.format(info.name))
            tar.extract(info, path)

    update(path)

def update(path):
    client = get_client()

    serial = get_serial(path)
    
    logger.debug('Fetching changelog since serial {}'.format(serial))

    serials = dict()
    for package, _, _, _, serial in client.changelog_since_serial(serial):
        serials[package] = serial

    logger.info('{} package(s) to update'.format(len(serials)))

    package_serials = sorted(serials.iteritems(), key=lambda (package, serial): serial)

    for package, serial in package_serials:
        update_package(path, package)
        set_serial(path, serial)

def full_download(path):
    client = get_client()

    logger.info('Listing packages')
    packages = client.list_packages()
    logger.info('{} packages available'.format(len(packages)))

    for package in packages:
        if not package_metadata_exists(path, package):
            update_package(path, package)
        else:
            logger.info('{}: package metadata already exists, skipping'.format(package))

def update_package(path, package):
    logger.info('{}: downloading package metadata'.format(package))

    filename = get_package_metadata_filename(path, package)

    url = 'https://pypi.python.org/pypi/{}/json'.format(package)

    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError as exc:
        if exc.code == 404:
            try:
                os.remove(filename)
                logger.info('{}: returned 404, deleted local data'.format(package))
            except OSError:
                if os.path.isfile(filename):
                    raise
                else:
                    logger.info('{}: returned 404, local data was previously removed'.format(package))
            return
        else:
            raise

    data = json.load(response)

    dirname = os.path.dirname(filename)
    try:
        os.makedirs(dirname)
    except OSError:
        if not os.path.isdir(dirname):
            raise

    with open(filename, 'w') as fp:
        json.dump(data, fp, indent=4)

def get_client():
    return xmlrpclib.ServerProxy(PYPI_XMLRPC_URL)

def get_serial(path):
    with open(get_serial_filename(path), 'r') as fp:
        return int(fp.read().strip())

def set_serial(path, serial):
    if not isinstance(serial, int):
        raise ValueError

    with open(get_serial_filename(path), 'w') as fp:
        fp.write(str(serial))

def get_serial_filename(path):
    return os.path.join(path, 'serial')

def get_package_metadata_filename(path, package):
    return os.path.join(*([path] + [
        urllib.quote(component)
        for component in (package[0], package)
    ]))

def package_metadata_exists(path, package):
    return os.path.isfile(get_package_metadata_filename(path, package))

if __name__ == '__main__':
    main()
