from setuptools import setup

execfile('foxtrot/version.py')

def readme():
  # Generated with `pandoc --from=markdown --to=rst --output=README.rst README.md`
  with open('README.rst') as f:
    return f.read()

setup(
  name = 'foxtrot-client',
  packages = ['foxtrot'],
  version = VERSION,
  description = 'Foxtrot Client Library',
  long_description = readme(),
  author = 'Yasyf Mohamedali',
  author_email = 'yasyf@foxtrot.io',
  url = 'https://github.com/FoxtrotSystems/api-client-python',
  download_url = 'https://github.com/FoxtrotSystems/api-client-python/tarball/' + VERSION,
  license = 'MIT',
  keywords = ['foxtrot', 'route optimization'],
  install_requires = ['requests'],
  classifiers= [
    'License :: OSI Approved :: MIT License',
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4'
  ],
  use_2to3 = True
)
