"""Package definition."""

from setuptools import setup


with open('requirements.txt') as f:
    required_libs = f.readlines()

with open('readme.md') as f:
    readme = f.read()

setup(
    name='sms_utilities',
    version='0.0.1',
    description='SMS encoding and decoding utilities',
    long_description=readme,
    url='http://github.com/endaga/sms_utilities',
    download_url='https://github.com/endaga/sms_utilities/tarball/'
                 '0.0.1',
    author='Matt Ball',
    author_email='matt@endaga.com',
    license='MIT',
    packages=['sms_utilities'],
    install_requires=required_libs,
    zip_safe=False
)
