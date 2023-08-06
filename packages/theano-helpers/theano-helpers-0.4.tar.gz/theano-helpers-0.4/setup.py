from distutils.core import setup

import version


setup(name='theano-helpers',
      version=version.getVersion(),
      description='Helper functions/classes for custom manipulation of Theano'
      ' graphs.',
      keywords='theano numerical',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='http://github.com/cfobel/theano-helpers.git',
      license='GPL',
      packages=['theano_helpers'],
      install_requires=['theano', 'nested_structures', 'pandas', 'jinja2'])
