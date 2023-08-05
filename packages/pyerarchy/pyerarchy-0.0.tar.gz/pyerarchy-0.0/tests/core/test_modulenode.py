import os
import shutil
from unittest import TestCase
from nose.tools import eq_, ok_
from pyerarchy.ex import BadValueError
from pyerarchy.modulenode import ModuleNode, ThisModuleNode

__author__ = 'bagrat'


class ModuleNodeTest(TestCase):
    test_module_name = 'testmodule'
    module_dir = os.path.join(os.path.dirname(__file__), '../../' + test_module_name)

    @classmethod
    def setUpClass(cls):
        super(ModuleNodeTest, cls).setUpClass()

        os.makedirs(cls.module_dir)

        with open(os.path.join(cls.module_dir, '__init__.py'), 'w') as init:
            init.write('# nothing')

    @classmethod
    def tearDownClass(cls):
        super(ModuleNodeTest, cls).tearDownClass()

        shutil.rmtree(cls.module_dir)

    def test_module(self):
        ls = ModuleNode(self.test_module_name).ls()

        eq_(len(ls), 2)
        ok_('__init__.py' in ls)
        ok_('__init__.pyc' in ls)

        raises_bad_value = False
        try:
            ModuleNode(1)
        except BadValueError:
            raises_bad_value = True

        ok_(raises_bad_value)

    def test_this_module(self):
        this = ThisModuleNode()

        eq_(this._pyerarchy_path, __file__)
