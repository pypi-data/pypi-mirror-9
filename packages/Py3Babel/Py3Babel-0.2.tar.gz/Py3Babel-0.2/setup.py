# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from setuptools import setup

sys.path.append(os.path.join('doc', 'common'))
try:
    from doctools import build_doc, test_doc
except ImportError:
    build_doc = test_doc = None


from distutils.cmd import Command


class import_cldr(Command):
    description = 'imports and converts the CLDR data'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        c = subprocess.Popen([sys.executable, 'scripts/download_import_cldr.py'])
        c.wait()


setup(
    name='Py3Babel',
    version='0.2',
    description='Internationalization utilities',
    long_description=\
"""A collection of tools for internationalizing Python applications.""",
    author='William Wu',
    author_email='william@pylabs.org',
    license='BSD',
    url='http://github.com/williamwu0220/py3babel/',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['py3babel', 'py3babel.messages', 'py3babel.localtime'],
    package_data={'py3babel': ['global.dat', 'localedata/*.dat']},
    install_requires=[
        # This version identifier is currently necessary as
        # pytz otherwise does not install on pip 1.4 or
        # higher.
        'pytz>=0a',
    ],

    cmdclass={'build_doc': build_doc, 'test_doc': test_doc,
              'import_cldr': import_cldr},

    zip_safe=False,

    # Note when adding extractors: builtin extractors we also want to
    # work if packages are not installed to simplify testing.  If you
    # add an extractor here also manually add it to the "extract"
    # function in py3babel.messages.extract.
    entry_points="""
    [console_scripts]
    py3babel = py3babel.messages.frontend:main

    [distutils.commands]
    compile_catalog = py3babel.messages.frontend:compile_catalog
    extract_messages = py3babel.messages.frontend:extract_messages
    init_catalog = py3babel.messages.frontend:init_catalog
    update_catalog = py3babel.messages.frontend:update_catalog

    [distutils.setup_keywords]
    message_extractors = py3babel.messages.frontend:check_message_extractors

    [py3babel.checkers]
    num_plurals = py3babel.messages.checkers:num_plurals
    python_format = py3babel.messages.checkers:python_format

    [py3babel.extractors]
    ignore = py3babel.messages.extract:extract_nothing
    python = py3babel.messages.extract:extract_python
    javascript = py3babel.messages.extract:extract_javascript
    """
)
