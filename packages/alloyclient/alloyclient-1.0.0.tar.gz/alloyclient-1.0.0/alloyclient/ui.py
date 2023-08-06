"""Alloy command line UI.

Copyright 2014 Archive Analytics Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
from __future__ import absolute_import, print_function

import errno
import os
import sys
import urllib2

try:
    import cPickle as pickle
except ImportError:
    # Slower, but still effective
    import pickle

from operator import methodcaller
from pprint import pformat, pprint
from textwrap import dedent

from blessings import Terminal

try:
    from alloy.arguments import AlloyArgumentParser
except ImportError:
    # Client only installed
    from argparse import ArgumentParser as AlloyArgumentParser

from .cdmi import CDMIClient
from .exceptions import (
    AlloyClientException,
    NoSuchObjectException,
    NotAContainerException,
    DataObjectAlreadyExistsException,
    ContainerAlreadyExistsException
)

SESSION_PATH = os.path.join(os.path.expanduser('~/.alloy'),
                            'session.pickle'
                            )


def get_client(args):
    """Return a CDMIClient.

    This may be achieved by loading a CDMIClient with a previously saved
    session.
    """
    global SESSION_PATH, parent_parser
    if not str(args.api).endswith(('/api/cdmi', '/api/cdmi/')):
        args.api = "{}/api/cdmi".format(args.api.strip('/'))

    try:
        # Load existing session, so as to keep current dir etc.
        with open(SESSION_PATH, 'rb') as fh:
            client = pickle.load(fh)
    except (IOError, pickle.PickleError):
        # Init a new CDMIClient
        client = CDMIClient(args.api)

    if args.api != parent_parser.get_default('api'):
        if client.cdmi_url != args.api:
            # Init a fresh CDMIClient
            client = CDMIClient(args.api)
    # Test for client connection errors here
    try:
        client.get_CDMI('/', children="0-0")
    except ValueError:
        # The API does not appear to return valid JSON
        # It is probably not a CDMI API - this will be a problem!
        raise AlloyClientException(errno.EBADMSG,
                                   "Invalid response format"
                                   )
    except urllib2.HTTPError as e:
        if e.code in [401, 403]:
            # Allow for authentication to take place later
            return client

        raise e

    return client


def save_client(client):
    """Save the status of the CDMIClient for subsequent use."""
    global SESSION_PATH
    if not os.path.exists(os.path.dirname(SESSION_PATH)):
        os.makedirs(os.path.dirname(SESSION_PATH))
    # Load existing session, so as to keep current dir etc.
    with open(SESSION_PATH, 'wb') as fh:
        pickle.dump(client, fh, pickle.HIGHEST_PROTOCOL)


def _init(args):
    """Initialize a CDMI client session.

    Optionally log in using HTTP Basic username and password credentials.
    """
    global terminal
    client = get_client(args)
    if args.username:
        if not args.password:
            # Request password from interactive prompt
            from getpass import getpass
            args.password = getpass("Password: ")

        success = client.authenticate(args.username, args.password)

        if success:
            print('Successfully logged in as {0.bold}{1}{0.normal}'
                  ''.format(terminal, args.username)
                  )
        else:
            # Failed to log in
            # Exit without saving client
            print('{0.bold_red}Failed{0.normal} - Login credentials not '
                  'recognized'.format(terminal)
                  )
            return 401
    print(terminal.green("Connected"))
    # Save the client for future use
    save_client(client)
    return 0


def _exit(args):
    "Close CDMI client session"
    global SESSION_PATH
    try:
        os.remove(SESSION_PATH)
    except OSError:
        # No saved client to log out
        pass


def _pwd(args):
    client = get_client(args)
    print(client.pwd())


def _ls(args):
    """List a container or object."""
    global terminal
    client = get_client(args)
    try:
        cdmi_info = client.get_CDMI(args.path,
                                    value="0-0"
                                    )
    except NoSuchObjectException as e:
        print ("ls: cannot access {0}: No such object or container"
               "".format(args.path))
        return e.errno
    if cdmi_info[u'objectType'] == u'application/cdmi-container':
        containers = [x for x in cdmi_info[u'children'] if x.endswith('/')]
        objects = [x for x in cdmi_info[u'children'] if not x.endswith('/')]
        for child in sorted(containers, key=methodcaller('lower')):
            print(terminal.blue(child))
        for child in sorted(objects, key=methodcaller('lower')):
            print(child)
    else:
        print(cdmi_info[u'objectName'])
    return 0


def _cd(args):
    "Move into a different container."
    client = get_client(args)
    try:
        client.chdir(args.path)
    except NoSuchObjectException as e:
        print ("cd: {0}: No such object or container"
               "".format(args.path))
        return e.errno
    except NotAContainerException as e:
        print ("cd: {0}: Not a container"
               "".format(args.path))
        return e.errno
    # Save the client for future use
    save_client(client)


def _mkdir(args):
    "Create a new container."
    client = get_client(args)
    try:
        client.mkdir(args.path)
    except NoSuchObjectException as e:
        print ("mkdir: cannot create container '{0}': "
               "No such object or container"
               "".format(args.path))
        return e.errno
    except (NotAContainerException, DataObjectAlreadyExistsException) as e:
        print ("mkdir: cannot create container '{0}': "
               "Not a container"
               "".format(args.path))
        return e.errno
    except ContainerAlreadyExistsException as e:
        print ("mkdir: cannot create container '{0}': "
               "Container exists"
               "".format(args.path))
        return e.errno


def _put(args):
    "Put a file to a path."
    # Absolutize local path
    localpath = os.path.abspath(args.path)
    try:
        with open(localpath, 'rb') as fh:
            client = get_client(args)
            if args.dest:
                path = args.dest
            else:
                # PUT to same name in pwd on server
                path = os.path.basename(localpath)

            try:
                # To avoid reading large files into memory, client.put()
                # accepts file-like objects
                cdmi_info = client.put(path, fh, mimetype=args.mimetype)
            except NoSuchObjectException as e:
                print ("put: cannot put data '{0}': "
                       "No such object or container"
                       "".format(path))
                return e.errno

            print(cdmi_info[u'parentURI'] + cdmi_info[u'objectName'])

    except IOError as e:
        print ("put: local file {0}: "
               "No such file or directory"
               "".format(args.path)
               )
        return e.errno


def _get(args):
    "Fetch a data object from the archive to a local file."
    # Determine local filename
    if args.dest:
        localpath = args.dest
    else:
        localpath = args.path.rsplit('/')[-1]

    # Check for overwrite of existing file, directory, link
    if os.path.isfile(localpath):
        if not args.force:
            print ("get: {0}: "
                   "File exists, --force option not used"
                   "".format(localpath)
                   )
            return errno.EEXIST
    elif os.path.isdir(localpath):
        print ("get: {0}: "
               "Is a directory"
               "".format(localpath))
        return errno.EISDIR
    elif os.path.exists(localpath):
        print ("get: {0}: "
               "Exists but not a file"
               "".format(localpath))
        return errno.EEXIST

    client = get_client(args)
    try:
        with client.open(args.path) as cfh, open(localpath, 'wb') as lfh:
            lfh.write(cfh.read())
    except NoSuchObjectException as e:
        print ("get: {0}: No such object or container"
               "".format(args.path))
        return e.errno
    else:
        print(localpath)


def _rm(args):
    "Remove a data object."
    # Check for container without recursive
    if args.path.endswith('/') and not args.recursive:
        print ("rm: cannot remove '{0}': "
               "Is a container"
               "".format(args.path))
        return errno.EISDIR

    client = get_client(args)
    try:
        client.delete(args.path)
    except NoSuchObjectException:
        # Possibly a container given without the trailing
        # Try fetching in order to give correct response
        try:
            cdmi_info = client.get_CDMI(args.path,
                                        value="0-0"
                                        )
        except NoSuchObjectException as e:
            # It really does not exist!
            print ("rm: cannot remove '{0}': "
                   "No such object or container"
                   "".format(args.path)
                   )
            return e.errno

        # Fixup path and recursively call this function (_rm)
        args.path = cdmi_info['parentURI'] + cdmi_info['objectName']
        return _rm(args)


def _rmdir(args):
    "Remove a container."
    client = get_client(args)
    # Fetch the info for checking (e.g. not empty, not a container)
    try:
        cdmi_info = client.get_CDMI(args.path,
                                    value="0-0"
                                    )
    except NoSuchObjectException as e:
        raise
        print ("rmdir: cannot remove '{0}': "
               "No such object or container"
               "".format(args.path))
        return e.errno

    if not cdmi_info['objectType'] == 'application/cdmi-container':
        print ("rmdir: cannot remove '{0}': "
               "Not a container"
               "".format(args.path))
        return errno.ENOTDIR
    else:
        # Check for not empty
        if len(cdmi_info['children']):
            print ("rmdir: cannot remove '{0}': "
                   "Container not empty"
                   "".format(args.path))
            return errno.ENOTEMPTY

    client.delete(cdmi_info['parentURI'] + cdmi_info['objectName'])

from collections import defaultdict

def _meta(args):
    """List, read, add or replace metadata."""
    client = get_client(args)
    if args.path == '.' or args.path == './':
        args.path = ''
    # Determine mode
    is_put = bool(
        args.metadata and
        ('+=' in args.metadata[0] or '=' in args.metadata[0])
    )
    metadata = defaultdict(list)
    for spec in args.metadata:
        if is_put and '+=' in spec:
            attr, val = spec.split('+=', 1)
            try:
                metadata[attr].append(val)
            except AttributeError:
                metadata[attr] = [metadata[attr], val]
        elif is_put and '=' in spec:
            attr, val = spec.split('=', 1)
            metadata[attr] = val
        elif spec not in metadata:
            metadata[spec] = None
    cdmi_info = client.get_CDMI(args.path, value='0-0')
    if is_put:
        # Filter out setting to None (i.e. GET specified after 1 or more PUTs)
        metadata = {
            k: v
            for k, v
            in metadata.iteritems()
            if v is not None
        }
        # Handle adding to existing fields
        existing_md = cdmi_info['metadata']
        for attr, val in metadata.iteritems():
            if isinstance(val, list):
                try:
                    existing_val = existing_md[attr]
                except KeyError:
                    pass
                else:
                    if isinstance(existing_val, list):
                        metadata[attr] = existing_val + val
                    else:
                        metadata[attr] = [existing_val] + val
        cdmi_info = client.put(args.path, metadata=metadata)

    for attr, val in cdmi_info['metadata'].iteritems():
        if attr.startswith(('cdmi_', 'com.archiveanalytics.alloy_')):
            # Ignore non-user defined metadata
            continue
        elif metadata and attr not in metadata:
            # Ignore unrequested fields (assuming 1 or more requested)
            continue
        if isinstance(val, list):
            for v in val:
                print('{0}:{1}'.format(attr, v))
        else:
            print('{0}:{1}'.format(attr, val))


def main(argv=None):
    global main_parser, terminal
    if argv is None:
        args = main_parser.parse_args()
    else:
        args = main_parser.parse_args(argv)
    # Call the appropriate function
    try:
        return args.func(args)
    except AlloyClientException as e:
        print("{0.red}Failed{0.normal} - {1}".format(terminal, e.args[1]))
        return e.args[0]


terminal = Terminal()


docbits = __doc__.split('\n\n')

# Create a parent parser with inheritable arguments
parent_parser = AlloyArgumentParser(add_help=False)
parent_parser.add_argument('--api',
                           dest='api',
                           default='https://127.0.0.1/api/cdmi',
                           help='location of Alloy CDMI API'
)
parent_parser.add_argument('--username',
                           dest='username'
                           )
parent_parser.add_argument('--password',
                           dest='password'
                           )

main_parser = AlloyArgumentParser(conflict_handler='resolve',
                                  description=docbits[0]
                                  )

# Sub-parsers for specific actions
subparsers = main_parser.add_subparsers(title="Commands",
                                        help='Actions'
                                        )

# init
parser_init = subparsers.add_parser(
    'init',
    help=dedent('   ' + _init.__doc__),
    parents=[parent_parser]
)
parser_init.set_defaults(func=_init)

# exit
parser_exit = subparsers.add_parser(
    'exit',
    help=dedent('   ' + _exit.__doc__),
)
parser_exit.set_defaults(func=_exit)

# ls
parser_ls = subparsers.add_parser(
    'ls',
    help=dedent('   ' + _ls.__doc__),
    parents=[parent_parser]
)
parser_ls.set_defaults(func=_ls)
parser_ls.add_argument('path',
                       nargs='?',
                       action='store',
                       default='',
                       help=("path to list, relative to current path")
                       )

# pwd
parser_pwd = subparsers.add_parser(
    'pwd',
    help=dedent('   ' + _ls.__doc__),
    parents=[parent_parser]
)
parser_pwd.set_defaults(func=_pwd)

# cd
parser_cd = subparsers.add_parser(
    'cd',
    help=dedent('   ' + _cd.__doc__),
    parents=[parent_parser]
)
parser_cd.set_defaults(func=_cd)
parser_cd.add_argument(
    'path',
    nargs='?',
    action='store',
    default='/',
    help=("path to cd into, relative to current path")
)

# mkdir
parser_mkdir = subparsers.add_parser(
    'mkdir',
    help=dedent('   ' + _mkdir.__doc__),
    parents=[parent_parser]
)
parser_mkdir.set_defaults(func=_mkdir)
parser_mkdir.add_argument(
    'path',
    help="path to container to create relative to current path"
)

# put
parser_put = subparsers.add_parser(
    'put',
    help=dedent('   ' + _put.__doc__),
    parents=[parent_parser]
)
parser_put.set_defaults(func=_put)
parser_put.add_argument(
    'path',
    help="path to local file to put."
)
parser_put.add_argument(
    'dest',
    nargs='?',
    help=("target path. If not supplied, data object will be put relative "
          "to current path."
          )
)
parser_put.add_argument(
    '-t', '--mimetype',
    dest="mimetype",
    help=("MIME type of object. If not supplied 'put' will attempt to guess "
          "based on the object path."
          )
)

# get
parser_get = subparsers.add_parser(
    'get',
    help=dedent('   ' + _get.__doc__),
    parents=[parent_parser]
)
parser_get.set_defaults(func=_get)
parser_get.add_argument(
    'path',
    help="path to archive file to get."
)
parser_get.add_argument(
    'dest',
    nargs='?',
    help=("target path. If not supplied, data object will be downloaded "
          "with the same name into the current local working directory."
          )
)
parser_get.add_argument(
    '-f', '--force',
    dest="force",
    action="store_true",
    help="Overwrite local file if present."
)

# rm
parser_rm = subparsers.add_parser(
    'rm',
    help=dedent('   ' + _rm.__doc__),
    parents=[parent_parser]
)
parser_rm.set_defaults(func=_rm)
parser_rm.add_argument('path',
                       help=("path to remove, relative to current path")
                       )
parser_rm.add_argument('-r', '--recursive',
                       dest='recursive',
                       action='store_true',
                       help=("recursively remove a container")
                       )

# rmdir
parser_rmdir = subparsers.add_parser(
    'rmdir',
    help=dedent('   ' + _rmdir.__doc__),
    parents=[parent_parser]
)
parser_rmdir.set_defaults(func=_rmdir)
parser_rmdir.add_argument('path',
                          help=("path to container to remove, relative to "
                                "current path"
                                )
                          )


# meta
parser_meta = subparsers.add_parser(
    'meta',
    help=dedent('   ' + _meta.__doc__),
    parents=[parent_parser]
)
parser_meta.set_defaults(func=_meta)
parser_meta.add_argument('path',
                         nargs='?',
                         default='.',
                         help=("path of object or container, relative to "
                               "current path"
                               )
                         )
parser_meta.add_argument('metadata',
                         nargs='*',
                         help=("metadata specifier. If specifier contains "
                               "'+=' it is treated as a request to add "
                               "(append NOT sum). If the specifier contains "
                               "'=' it is treated as a request to set. "
                               "Otherwise it is treated as a request to "
                               "get specific metadata field(s). It is possible "
                               "to delete a metadata field by setting it to "
                               "empty, e.g. `com.example.attr=`. It is "
                               "not possible to combine add/set/delete "
                               "specifiers with get specifiers. If a add/set "
                               "specifier is given first, get specifiers will "
                               "be ignored, if a get specifier to given first, "
                               "subsequent add/set specifiers will be ignored"
                               )
                         )


if __name__ == '__main__':
    sys.exit(main())
