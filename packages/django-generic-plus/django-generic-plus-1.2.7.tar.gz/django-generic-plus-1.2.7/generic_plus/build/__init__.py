"""Provides the entrypoint in setup.py for the create_readme_rst command"""

import os
import codecs
import setuptools
from distutils import log

from .rst_converter import PandocRSTConverter


class create_readme_rst(setuptools.Command):

    description = "Convert README.md to README.rst"
    user_options = []
    
    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        converter = PandocRSTConverter()
        rst = converter.convert('README.md')
        outfile = os.path.join(os.path.dirname(__file__), '..', '..', 'README.rst')
        with codecs.open(outfile, encoding='utf8', mode='w') as f:
            f.write(rst)
        log.info("Successfully converted README.md to README.rst")
