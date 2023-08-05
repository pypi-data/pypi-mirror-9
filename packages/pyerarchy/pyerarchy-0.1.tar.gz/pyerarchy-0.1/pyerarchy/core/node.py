import inspect
import os

from pyerarchy.ex import NotDirectoryError, BadValueError, NoSuchFunctionError

__author__ = 'bagrat'


class Node(object):
    def __init__(self, path, create=False, strict=False):
        """Creates node object to walk through filesystem using attributes.

            :param path: The path to set the object to.
            :param create: If set to True, the specified path will be created if it does not exist.
            :param strict: If set to True, an exception will be raised if the path does not exist.
            :return:
            """
        super(Node, self).__init__()
        p = path
        p = os.path.abspath(p)
        p = os.path.expanduser(p)
        p = os.path.realpath(p)
        if not os.path.exists(p):
            if create:
                os.makedirs(p, mode=0o755)
            else:
                if strict:
                    raise OSError('No such file or directory: {path}'.format(path=p))

        self._pyerarchy_path = p

    def isfile(self):
        """Tells if the node is a file
        """
        return os.path.isfile(self._pyerarchy_path)

    def open(self, *args, **kwargs):
        """Opens the node as a file
        """
        return open(self._pyerarchy_path, *args, **kwargs)

    def read(self, *args, **kwargs):
        """Reads the node as a file
        """
        with self.open('r') as f:
            return f.read(*args, **kwargs)

    def isdir(self):
        """Tells if the node is a directory
        """
        return os.path.isdir(self._pyerarchy_path)

    def ls(self):
        """List the children entities of the directory.

        Raises exception if the object is a file.

        :return:
        """
        if self.isfile():
            raise NotDirectoryError('Cannot ls() on non-directory node: {path}'.format(path=self._pyerarchy_path))

        return os.listdir(self._pyerarchy_path)

    def mkdir(self, children, mode=0o0755, return_node=True):
        """Creates child entities in directory.

        Raises exception if the object is a file.

        :param children: The list of children to be created.
        :return: The child object, if one child is provided. None, otherwise.
        """
        result = None

        if isinstance(children, (str, unicode)):
            if os.path.isabs(children):
                raise BadValueError('Cannot mkdir an absolute path: {path}'.format(path=self._pyerarchy_path))

            rel_path = os.path.join(self._pyerarchy_path, children)
            os.makedirs(rel_path, mode)

            if return_node:
                result = Node(rel_path)
        else:
            for child in children:
                self.mkdir(child, mode, False)

        return result

    def __getattribute__(self, item):
        """Attribute name resolution

        Returns a child node with the name of the accessed attribute. If the object has an attribute with such a name
         return the attribute value.
        """
        result = None
        try:
            attr = super(Node, self).__getattribute__(item)
            if not inspect.isroutine(attr):
                result = attr
        except AttributeError:
            result = Node(os.path.join(self._pyerarchy_path, item))

        return result

    def __call__(self, *args, **kwargs):
        """Invokes corresponding function

        If the node is accessed as a callable and such function exists for the node, it is invoked.
        """
        name = os.path.basename(self._pyerarchy_path)

        if not hasattr(Node, name):
            raise NoSuchFunctionError('Node object does not have function "{name}"'.format(name=name))

        parent = os.path.dirname(self._pyerarchy_path)

        node = Node(parent, strict=False)
        function = getattr(Node, name)

        return function(node, *args, **kwargs)

    def __div__(self, other):
        """Division acts as a path separator

        :param other: The child entity name as a string
        :return: Child node with the provided name
        """
        if not isinstance(other, (str, unicode)):
            raise TypeError('Wrong type used with slash operation: {type}'.format(type=type(other)))

        return getattr(self, other)
