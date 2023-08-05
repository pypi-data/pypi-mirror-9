from setuptools import setup, find_packages

version = '1.9.15'

setup(
  name='python-appengine',
  version=version,
  author='Jon San Miguel',
  author_email='jon.sanmiguel@optimizely.com',
  packages=find_packages(),
  include_package_data=True,
  url='https://github.com/optimizely/python-appengine',
  download_url='https://github.com/optimizely/python-appengine/tarball/%s' % version,
  license='Apache License',
  description='GAE SDK Pip installable Mirror',
  long_description=open('README').read(),
  keywords=['google', 'appengine'],
)
