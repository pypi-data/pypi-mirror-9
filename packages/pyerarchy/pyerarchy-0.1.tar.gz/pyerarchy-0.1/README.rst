Pyerarchy
=========

Pyerarchy is a Python package for easy file system surfing and manipulation. It enables to interact with the file system
directly as Python objects without making implicit calls to ``os`` package. Finally it makes the code much more readable
and nice.


Basic Usage
-----------

The central point of Pyerarchy is the Node. The basic usage starts by initializing an entry point Node and manipulating
it further::

    node = Node('entry/point/path')  # Initialize a new node

    children = node.ls()  # List all child entities of the node
    node.mkdir('newdir').mkdir('anotherdir')  # Create a new directory under node, and another one under the new one :)

    # Now access the newly created directories
    anotherdir = node/'newdir'/'anotherdir'  # This is the most common way to access nodes
    children = node.newdir.anotherdir.ls()  # This method can be used to invoke an operation on the result node

    # What about files?
    myfile = node.myfile

    # And even...
    myfile = node.myfile.open('w')

    # Or...
    contents = node.myfile.read()  # ...which handles everything

    # What if the filename contains a dot, dash, etc?
    # Well...
    myfile_node = node/'filename.with.dots-and-dashes'

    # And then do your stuff on myfile_node
    with myfile_node.open('r') as f:
        ...

    # Or again...
    contents = myfile_node.read()

Another useful feature of Pyerarchy is very handy in Python modules to interact with static files included in the module::

    static_data_node = ThisModuleNode()/'path/to/the/static/data/relative/to/module'

    some_file_node = static_data_node/'some/static/text/file'

    contents = some_file_node.read()

