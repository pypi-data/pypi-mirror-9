import os
from types import ModuleType
from pyflect.core.instor import get_caller_module

from pyerarchy import Node
from pyerarchy.ex import BadValueError


__author__ = 'bagrat'


class ModuleNode(Node):
    def __init__(self, module='', depth=1):
        """Initializes a node by module name or module object.

        Creates an node object that represents the path of a module specified by name or by module object. If no module
         is specified, the caller module is assumed.

        :param module: Module name or module object
        :param depth: The depth od levels to go for assuming caller module
        :return:
        """
        if not isinstance(module, ModuleType):
            if not isinstance(module, (str, unicode)):
                raise BadValueError('Not a module or module name: {module}'.format(module=module))
            else:
                if not len(module) == 0:
                    module = __import__(module)
                else:
                    module = get_caller_module(depth=depth)

        name = os.path.basename(module.__file__)

        if name == '__init__.py':
            path = os.path.dirname(module.__file__)
        else:
            path = module.__file__

        super(ModuleNode, self).__init__(path, create=False, strict=True)


class ThisModuleNode(ModuleNode):
    def __init__(self):
        super(ThisModuleNode, self).__init__(depth=2)