"""Package definition."""

from setuptools import setup


with open('requirements.txt') as f:
    required_libs = f.readlines()

with open('readme.md') as f:
    readme = f.read()

github_url = 'https://github.com/endaga/sms_utilities'
version = '0.0.2'
download_url = '%s/%s' % (github_url, version)

setup(
    name='sms_utilities',
    version=version,
    description='SMS encoding and decoding utilities',
    long_description=readme,
    url=github_url,
    download_url=download_url,
    author='Matt Ball',
    author_email='matt@endaga.com',
    license='MIT',
    packages=['sms_utilities'],
    install_requires=required_libs,
    zip_safe=False
)
