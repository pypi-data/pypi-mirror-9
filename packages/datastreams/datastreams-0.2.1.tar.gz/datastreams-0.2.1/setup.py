from distutils.core import setup
setup(
  name = 'datastreams',
  packages = ['datastreams'],
  version = '0.2.1',
  description = 'A module for managing data in streams.',
  author = 'Christopher Su',
  author_email = 'chris+py@christopher.su',
  url = 'https://github.com/csu/datastreams',
  install_requires=[
      "pymongo == 2.7.2"
  ]
)