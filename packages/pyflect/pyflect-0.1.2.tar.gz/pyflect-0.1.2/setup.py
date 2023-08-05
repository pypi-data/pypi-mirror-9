__author__ = 'bagrat'

from setuptools import setup, find_packages

tests_require = ['nose', 'coverage']

install_requires = []

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
               'Programming Language :: Java',
               'Topic :: Software Development :: Libraries :: Python Modules']

config = {
    'description': 'Put on your Java suit and go get_methods',
    'author': 'Bagrat Aznauryan',
    'url': 'https://github.com/n9code/pyflect',
    'download_url': 'https://github.com/n9code/pyflect',
    'author_email': 'bagrat@aznauryan.org',
    'version': '0.1.2',
    'install_requires': install_requires,
    'tests_require': tests_require,
    'classifiers': classifiers,
    'packages': find_packages(),
    'name': 'pyflect',
    'license': 'MIT',
    'keywords': 'reflection java getmethods getfields'
}

setup(**config)