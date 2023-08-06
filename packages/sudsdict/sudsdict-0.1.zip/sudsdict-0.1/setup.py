from distutils.core import setup

setup(
  name = 'sudsdict',
  packages = ['sudsdict'],
  version = '0.1',
  description = 'Module for converting suds objects into dicts',
  author = 'Konvexum',
  author_email = 'info@konvexum.se',
  url = 'https://github.com/konvexum/sudsdict',
  download_url = 'https://github.com/konvexum/sudsdict/tarball/0.1',
  keywords = ['suds', 'soap', 'dict', 'format', 'convert'],
  classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.4',
      'Topic :: Utilities',
  ],
)