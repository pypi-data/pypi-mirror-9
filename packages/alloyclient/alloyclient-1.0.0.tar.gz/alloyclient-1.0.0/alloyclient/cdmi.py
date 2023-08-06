"""Alloy CDMI API Client.

This could be used for implementing command-line or other interfaces, and
for automated testing suites.

Example use:

>>> from alloy.client.cdmi import CDMIClient
>>> c = CDMIClient("https://127.0.0.1:4443/api/cdmi")
>>> print c.pwd()
/
>>> c.read_container()
{"objectName": "/", ...}   # CDMI Response as a Python dict
>>> c.mkdir("test")
>>> c.read_container()
{"objectName": "/","children": ["test/"], ...}
>>> c.chdir("test")
>>> print c.pwd()
/test/
>>> c.read_container()
{"objectName": "test/", ...}   # CDMI Response as a Python dict
>>> c.chdir("..")
>>> c.read_container("test")
{"objectName": "test/", ...}   # Same CDMI Response as before


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

from __future__ import absolute_import

import contextlib
import errno
import json
import mimetypes
import mmap
import os
import urllib2

from base64 import b64encode
from urllib import pathname2url, url2pathname

import alloyclient

from .exceptions import (
    AlloyConnectionException,
    NoSuchObjectException,
    NotAContainerException,
    DataObjectAlreadyExistsException,
    ContainerAlreadyExistsException
    )


CDMI_CONTAINER = 'application/cdmi-container'
CDMI_DATAOBJECT = 'application/cdmi-object'


class CDMIRequest(urllib2.Request):
    """Custom urllib2.Request subclass.

    urllib2.Request sub-classed in order to encapsulate boiler-plate and
    enable request using PUT and DELETE.
    """

    def __init__(self, *args, **kwargs):
        self._method = kwargs.pop('method', None)
        urllib2.Request.__init__(self, *args, **kwargs)
        # Add Accept header if one does not exist
        if not self.has_header('Accept'):
            if args[0].endswith('/'):
                self.add_header("Accept", CDMI_CONTAINER)
            else:
                self.add_header("Accept", CDMI_DATAOBJECT)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)


class CDMIClient(object):

    def __init__(self, base_url):
        """Create a new instance of ``CDMIClient``.

        :arg base_url: base URL of CDMI API to connect to.

        ::

            client = CDMIClient('https://alloy.example.com/api/cdmi')
        """
        self.cdmi_url = base_url
        # Create a urllib2.OpenerDirector
        opener = self.urlopener = urllib2.build_opener()
        opener.addheaders = [
            ('User-agent', 'Alloy Client {0}'.format(alloyclient.__version__)),
            ("X-CDMI-Specification-Version", "1.0.2")
        ]
        # pwd should always end with a /
        self._pwd = '/'

    def add_header(self, header):
        self.urlopener.addheaders.append(header)

    def pwd(self):
        """Get and return path of current container."""
        return self._pwd

    def getcwd(self):
        """Get and return path of current container."""
        return self.pwd()

    def normalize_url(self, path):
        """Normalize URL path relative to current path and return.

        :arg path: path relative to current path
        :returns: absolute CDMI URL
        """
        # Turn URL path into OS path for manipulation
        mypath = url2pathname(path)
        if not os.path.isabs(mypath):
            mypath = os.path.join(url2pathname(self.pwd()), mypath)
        # normalize path
        mypath = os.path.normpath(mypath)
        if path.endswith('/') and not mypath.endswith('/'):
            mypath += '/'
        url = self.cdmi_url + pathname2url(mypath)
        return url

    def get_CDMI(self, path, **params):
        """Return CDMI response a container or data object.

        Read the container or data object at ``path`` return the
        CDMI JSON as a dict. If path is empty or not supplied, read the
        current working container.

        :arg path: path to read CDMI
        :returns: CDMI JSON response
        :rtype: dict

        """
        req_url = self.normalize_url(path)
        p = ''.join(["{0}:{1};".format(k, v)
                           for k, v
                           in params.iteritems()
                           ])
        if p:
            req_url = req_url + '?' + p

        req = CDMIRequest(req_url)
        try:
            with contextlib.closing(self.urlopener.open(req)) as fh:
                return json.load(fh)
        except urllib2.HTTPError as e:
            if e.code == 404:
                raise NoSuchObjectException(errno.ENOENT,
                                            "Object {0} does not exist"
                                            "".format(path)
                                            )
            else:
                raise e
        except urllib2.URLError as e:
            raise AlloyConnectionException(e.reason.errno,
                                           e.reason.strerror
                                           )

    def authenticate(self, username, password):
        """Authenticate the client with ``username`` and ``password``.

        Return success status for the authentication

        :arg username: username of user to authenticate
        :arg password: plain-text password of user
        :returns: whether or not authentication succeeded
        :rtype: bool

        """
        auth_header = ('Authorization',
                       "Basic " + b64encode('{0}:{1}'
                                            ''.format(username, password)
                                            )
                       )
        req = CDMIRequest(self.cdmi_url + '/',
                          headers=dict([auth_header])
                          )
        try:
            urllib2.urlopen(req).read()
        except urllib2.HTTPError as e:
            if e.code == 401:
                # Unsuccessful authentication attempt
                return False
            # Another type of HTTP error raise it
            raise
        else:
            # Success!
            # Add Authorization header to subsequent requests
            self.add_header(auth_header)
            return True

    def chdir(self, path):
        """Move into a container at ``path``."""
        cdmi_info = self.get_CDMI(path, value="0-0")
        # Check that object is a container
        if not cdmi_info['objectType'] == CDMI_CONTAINER:
            raise NotAContainerException(errno.ENOTDIR,
                                         "{0} not a container"
                                         "".format(path)
                                         )
        try:
            self._pwd = cdmi_info['parentURI'] + cdmi_info['objectName']
        except KeyError:
            # No parentURI - probably root
            self._pwd = cdmi_info['objectName']

    def login(self, username, password):
        """Log in client with provided credentials.

        If client is already logged in, log out of current session before
        attempting to log in with new credentials.
        """
        # First log out any existing session
        self.logout()
        # Authenticate using provided credentials
        if self.authenticate(username, password):
            # Add "Authorization" header to subsequent requests
            auth_header = ('Authorization',
                           "Basic " + b64encode('{0}:{1}'
                                                ''.format(username, password)
                                                )
                           )
            self.urlopener.addheaders.append(auth_header)
            return True

        # Invalid credentials
        return False

    def logout(self):
        """Log out current client session."""
        self.urlopener.addheaders = [(head, val) for
                                     head, val in
                                     self.urlopener.addheaders
                                     if head.capitalize() != 'Authorization'
                                     ]

    def mkdir(self, path, metadata={}):
        """Create a container.

        Create a container at ``path`` and return the CDMI response. User
        ``metadata`` will also be set if supplied.

        :arg path: path to create
        :arg metadata: metadata for container
        :returns: CDMI JSON response
        :rtype: dict

        """
        if path and not path.endswith('/'):
            path = path + '/'
        req_url = self.normalize_url(path)
        req = CDMIRequest(req_url,
                          json.dumps({'metadata': metadata}),
                          headers={'Content-type': CDMI_CONTAINER},
                          method="PUT"
                          )

        try:
            with contextlib.closing(self.urlopener.open(req)) as fh:
                if fh.getcode() == 204:
                    # No response CDMI data - Container already exists
                    raise ContainerAlreadyExistsException(
                        errno.EEXIST,
                        "Container already exists at{0}"
                        "".format(path)
                    )
                return json.load(fh)
        except urllib2.HTTPError as e:
            if e.code == 404:
                raise NoSuchObjectException(errno.ENOENT,
                                            "Object {0} does not exist"
                                            "".format(path)
                                            )
            elif e.code == 409:
                raise DataObjectAlreadyExistsException(
                    errno.EEXIST,
                    "Object already exists at{0}"
                    "".format(path)
                )
            else:
                raise e

    def put(self, path, data='', mimetype=None, metadata={}):
        """Create or update a data object.

        Create or update the data object at ``path`` and return the CDMI
        response. Data object content is updated with ``data`` (defaults to
        empty). ``mimetype`` and user ``metadata`` will also be set if
        supplied.

        If ``mimetype`` is not supplied CDMIClient will attempt to do the
        most sensible thing based on the type of ``data`` argument and its
        attributes (e.g. use ``mimetypes`` module to guess for a file-like
        objects).

        :arg path: path to create
        :arg data: content for data object
        :type data: dict (of CDMI JSON) byte string or file-like object
        :arg mimetype: mimetype of data object to create.
        :arg metadata: metadata for object
        :returns: CDMI JSON response
        :rtype: dict

        """
        req_url = self.normalize_url(path)
        # Deal with missing mimetype
        if not mimetype:
            type_, enc_ = mimetypes.guess_type(path)
            if not type_:
                mimetype = "application/octet-stream"
            else:
                if enc_ == 'gzip' and type_ == 'application/x-tar':
                    mimetype = "application/x-gtar"
                elif enc_ == 'gzip':
                    mimetype = "application/x-gzip"
                elif enc_ == 'bzip2' and type_ == 'application/x-tar':
                    mimetype = "application/x-gtar"
                elif enc_ == 'bzip2':
                    mimetype = "application/x-bzip2"
                else:
                    mimetype = type_

        # Deal with varying data type
        if isinstance(data, dict):
            data = json.dumps(data)
        elif isinstance(data, unicode):
            data = data.encode('utf-8')
        elif not isinstance(data, (mmap.mmap, basestring)):
            # Read the file-like object as a memory mapped string. Looks like
            # a string, but accesses the file directly. This avoids reading
            # large files into memory
            try:
                data = mmap.mmap(data.fileno(), 0, access=mmap.ACCESS_READ)
            except ValueError:
                # Unable to memory map
                # Simply read in file
                data = data.read()

        if metadata:
            # PUT the data as a CDMI object
            if req_url.endswith('/'):
                headers = {'Content-type': CDMI_CONTAINER}
            else:
                headers = {'Content-type': CDMI_DATAOBJECT}
            # Create the CDMI Data Object Structure
            d = {'metadata': metadata}
            if data:
                d.update({
                    'value': b64encode(data),
                    'valuetransferencoding': "base64",
                    'mimetype': mimetype,
                })
            data = json.dumps(d)
            # Add the metadata parameters into the URL
            p = ''.join(["metadata:{0};".format(k)
                               for k
                               in metadata
                               ])
            req_url = req_url + '?' + p
        else:
            # PUT the data in non-CDMI to avoid unnecessary base64 overhead
            headers = {'Content-type': mimetype}

        req = CDMIRequest(req_url,
                          data,
                          headers=headers,
                          method="PUT"
                          )
        try:
            with contextlib.closing(self.urlopener.open(req)) as fh:
                return json.load(fh)
        except ValueError:
            # Possibly update which returns 204 No Content
            # Fetch a summary of the object to return
            req = CDMIRequest(self.normalize_url(path) + '?value:0-0' ,
                              headers={},
                              method="GET"
                              )
            with contextlib.closing(self.urlopener.open(req)) as fh:
                return json.load(fh)

        except urllib2.HTTPError as e:
            if e.code == 404:
                raise NoSuchObjectException(errno.ENOENT,
                                            "Object {0} does not exist"
                                            "".format(path)
                                            )
            else:
                raise e

    def read_container(self, path=''):
        """Read information and contents for a container.

        Read the container at ``path`` return the CDMI JSON as a dict. If
        path is empty or not supplied, read the current working container.

        :arg path: path to read
        :returns: CDMI JSON response
        :rtype: dict

        """
        if path and not path.endswith('/'):
            path = path + '/'
        return self.get_CDMI(path)

    def read_object(self, path):
        """Read and return the value for a data object.

        Read the data object at ``path`` and return its content.
        """
        with self.open(path) as fh:
            return fh.read()

    @contextlib.contextmanager
    def open(self, path):
        """Open a read-only file-like object for a data object.

        Read the data object at ``path`` and return a file-like object.

        This is suitable for use in a ``with`` statement context manager::

            c = CDMIClient('https://example.com:443/api/cdmi')
            with c.open('path/to/file') as filelike:
                # Do something with the file
                with open('localfile', 'wb') as fh:
                    fh.write(filelike.read())

        """
        req_url = self.normalize_url(path)
        # PUT the data in non-CDMI to avoid unnecessary base64 overhead
        headers = {'Accept': "application/octet-stream"}
        req = CDMIRequest(req_url,
                          headers=headers,
                          method="GET"
                          )
        try:
            with contextlib.closing(self.urlopener.open(req)) as fh:
                yield fh

        except urllib2.HTTPError as e:
            if e.code == 404:
                raise NoSuchObjectException(errno.ENOENT,
                                            "Object {0} does not exist"
                                            "".format(path)
                                            )
            else:
                raise e

    def delete(self, path):
        """Delete a container or data object.

        .. CAUTION::
            Use with extreme caution. THe CDMI Specification (v1.0.2)
            states that when deleting a container, this includes deletion of
            "all contained children and snapshots", so this is what this
            method will do.

        :arg path: path to delete
        :returns: whether or not the operation succeeded
        :rtype: bool

        """
        req_url = self.normalize_url(path)
        req = CDMIRequest(req_url,
                          method="DELETE"
                          )
        try:
            with contextlib.closing(self.urlopener.open(req)):
                pass

        except urllib2.HTTPError as e:
            if e.code == 404:
                raise NoSuchObjectException(errno.ENOENT,
                                            "Object {0} does not exist"
                                            "".format(path)
                                            )
            else:
                raise e

        return True
