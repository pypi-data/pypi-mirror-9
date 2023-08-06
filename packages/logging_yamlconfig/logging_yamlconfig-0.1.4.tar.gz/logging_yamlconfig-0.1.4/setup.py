import os

from setuptools import setup, find_packages, findall

def get_version():
    with open(os.path.join(thisdir, 'VERSION'), 'r') as fh:
        return fh.readline().strip()

def get_requires(filename='requirements.txt'):
    requires = []
    with open(os.path.join(thisdir, filename), 'r') as fh:
        for line in fh.readlines():
            requires += [ line.strip() ]
    return requires

thisdir = os.path.dirname(os.path.realpath(__file__))

# parse version number from text file
VERSION = get_version()

# find packages and binaries
ALL_PACKAGES = find_packages()
SCRIPTS = findall('bin')

# parse requirements from text files
ALL_INSTALL_REQUIRES = get_requires()
ALL_TEST_REQUIRES = get_requires('test_requirements.txt')
ALL_SETUP_REQUIRES = get_requires('setup_requirements.txt')

setup(
    name='logging_yamlconfig',
    version=VERSION,
    description='Python dictconfig helpers for yaml config files',
    author='IBM',
    author_email='jdye@us.ibm.com',
    url='https://github.com/dyejon/python_logging_yamlconfig',
    download_url='https://github.com/dyejon/python_logging_yamlconfig/tarball/%s' % VERSION,
    packages=ALL_PACKAGES,
    provides=ALL_PACKAGES,
    scripts=SCRIPTS,
    include_package_data=True,
    setup_requires=ALL_SETUP_REQUIRES,
    install_requires=ALL_INSTALL_REQUIRES,
    tests_require=ALL_TEST_REQUIRES,
    test_suite='nose.collector'
)

# vim: set ts=4 sw=4 expandtab:
