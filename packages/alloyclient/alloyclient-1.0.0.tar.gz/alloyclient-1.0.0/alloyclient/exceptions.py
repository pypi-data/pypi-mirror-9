"""Alloy Client Exceptions.

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


class AlloyClientException(Exception):
    """Base Class for Alloy client Exceptions.

    Abstract Base Class from which more specific Exceptions are derived.
    """
    pass


class AlloyConnectionException(IOError, AlloyClientException):
    """Alloy client connection Exception.

    An Exception raised due to a failure to connect to the Alloy API.
    """
    pass


class NoSuchObjectException(EnvironmentError, AlloyClientException):
    """Alloy client no such object Exception.

    An Exception raised due to request to carry out an action on an object
    that does not exist.
    """
    pass


class NotAContainerException(EnvironmentError, AlloyClientException):
    """Alloy client not a container Exception.

    An Exception raised due to request to carry out a container action on an
    object that is not a container.
    """
    pass


class ContainerAlreadyExistsException(EnvironmentError, AlloyClientException):
    """Alloy storage resource already exists Exception.

    An Exception raised due to request to create a resource on a path that
    is already present as a container on the storage resource.
    """

    def __str__(self):
        return "Container already exists at {0}".format(self.path)


class DataObjectAlreadyExistsException(EnvironmentError, AlloyClientException):
    """Alloy storage resource already exists Exception.

    An Exception raised due to request to create a resource on a path that
    is already present as a data object on the storage resource.
    """

    def __str__(self):
        return "Data object already exists at {0}".format(self.path)
