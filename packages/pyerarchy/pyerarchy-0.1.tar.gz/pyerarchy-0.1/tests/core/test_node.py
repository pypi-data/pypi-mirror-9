from unittest import TestCase
import shutil
from pyerarchy.ex import NoSuchFunctionError, NotDirectoryError, BadValueError
from pyerarchy.modulenode import ModuleNode

__author__ = 'bagrat'

from nose.tools import *
import os

from pyerarchy.core.node import Node


class NodeTest(TestCase):
    folders = ['anotherdir', 'yetanother', 'isfilecase']
    files = ['file']
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    testfile_contents = 'testfilecontents'

    @classmethod
    def setUp(cls):
        super(NodeTest, cls).setUpClass()

        if os.path.exists(cls.static_path):
            shutil.rmtree(cls.static_path)

        os.makedirs(cls.static_path)

        for folder in cls.folders:
            os.makedirs(os.path.join(cls.static_path, folder))

        for f in cls.files:
            cls.touch(f)

        cls.touch('isfilecase/isfile')
        cls.touch('yetanother/isdir')

    @classmethod
    def touch(cls, path):
        with open(os.path.join(cls.static_path, path), 'w') as f:
            f.write(cls.testfile_contents)

    @classmethod
    def tearDown(cls):
        super(NodeTest, cls).tearDownClass()

        shutil.rmtree(cls.static_path)

    def test_attribute(self):
        node = Node(self.static_path)

        ok_(node)

        attr_value = 'somevalue'
        node.attr = attr_value

        eq_(node.attr, attr_value)

    def test_node(self):
        node = Node(self.static_path)

        ls = node.ls()

        ok_(node.isdir())
        ok_(not node.isfile())
        ok_(len(ls) == (len(self.folders) + len(self.files)))
        eq_(len(set(self.folders + self.files).symmetric_difference(set(ls))), 0)

        node = Node(os.path.join(self.static_path, 'file'))

        raises_not_dir = False
        try:
            node.ls()
        except NotDirectoryError:
            raises_not_dir = True

        ok_(node.isfile())
        ok_(not node.isdir())
        ok_(raises_not_dir)

        node = Node(os.path.join(self.static_path, 'yetanother'))

        ok_(node.isdir())
        ok_(not node.isfile())

        node = Node(os.path.join(self.static_path, 'isfilecase'))

        ok_(node.isdir())
        ok_(not node.isfile())

        raises_not_exists = False
        try:
            Node(os.path.join(self.static_path, 'notexistingnode'), strict=True)
        except OSError:
            raises_not_exists = True

        ok_(raises_not_exists)

    def test_with_create(self):
        nonexisting = os.path.join(self.static_path, 'abracadabra1234')

        ok_(not os.path.exists(nonexisting))

        Node(nonexisting, create=True)

        ok_(os.path.exists(nonexisting))

    def test_mkdir(self):
        node = Node(self.static_path)

        child1 = node.mkdir('child1')

        ok_(os.path.exists(os.path.join(self.static_path, 'child1')))
        ok_(isinstance(child1, Node))

        child1.mkdir('hey/you')

        ok_(os.path.exists(os.path.join(child1._pyerarchy_path, 'hey/you')))

        child1.mkdir(['out', 'there'])

        ok_(os.path.exists(os.path.join(child1._pyerarchy_path, 'out')))
        ok_(os.path.exists(os.path.join(child1._pyerarchy_path, 'there')))

        raises_bad_value = False
        try:
            node.mkdir('/tmp/newdir')
        except BadValueError:
            raises_bad_value = True

        ok_(raises_bad_value)

    def test_name_collisions(self):
        node = Node(self.static_path)

        ls = node.ls()

        ok_(len(ls) == (len(self.folders) + len(self.files)))
        eq_(len(set(self.folders + self.files).symmetric_difference(set(ls))), 0)

        new_dirs = ['newdir', 'newdir2', 'ls']
        node.mkdir(new_dirs)

        ls = node.ls()

        ok_(len(ls) == (len(self.folders) + len(self.files) + len(new_dirs)))
        eq_(len(set(self.folders + self.files + new_dirs).symmetric_difference(set(ls))), 0)

        raises_no_such_function = False
        try:
            node.ls.function()
        except NoSuchFunctionError:
            raises_no_such_function = True

        ok_(raises_no_such_function)

    def test_file_ops(self):
        node = Node(self.static_path)

        contents = node.file.read()

        eq_(contents, self.testfile_contents)

    def test_div(self):
        node = Node(self.static_path)

        child = node/self.folders[0]

        ok_(isinstance(child, Node))
        ok_(child.isdir())
        eq_(child._pyerarchy_path, os.path.join(node._pyerarchy_path, self.folders[0]))

        raises_type_error = False
        try:
            node/node
        except TypeError:
            raises_type_error = True

        ok_(raises_type_error)

        newdir_name = 'newdir'
        child.mkdir(newdir_name)

        newdir_node = node / self.folders[0] / newdir_name

        ok_(isinstance(newdir_node, Node))
        ok_(newdir_node.isdir())
        eq_(newdir_node._pyerarchy_path, os.path.join(child._pyerarchy_path, newdir_name))
