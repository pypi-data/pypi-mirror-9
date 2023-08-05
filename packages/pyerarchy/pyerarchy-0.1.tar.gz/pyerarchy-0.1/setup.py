__author__ = 'bagrat'

from setuptools import setup, find_packages

tests_require = ['nose', 'coverage']

install_requires = ['pyflect']

classifiers = ['License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Natural Language :: English',
               'Programming Language :: Python',
               'Programming Language :: Python :: 2',
               'Programming Language :: Python :: 3',
               'Operating System :: POSIX',
               'Operating System :: POSIX :: Linux',
               'Operating System :: MacOS',
               'Operating System :: Microsoft :: Windows',
               'Topic :: Software Development :: Libraries :: Python Modules']

config = {
    'description': 'Access directories like objects',
    'author': 'Bagrat Aznauryan',
    'url': 'git@github.com:n9code/pyerarchy.git',
    'download_url': 'git@github.com:n9code/pyerarchy.git',
    'author_email': 'bagrat@aznauryan.org',
    'version': '0.1',
    'install_requires': install_requires,
    'tests_require': tests_require,
    'classifiers': classifiers,
    'packages': find_packages(),
    'name': 'pyerarchy',
    'license': 'MIT',
    'keywords': 'directory file object'
}

setup(**config)
