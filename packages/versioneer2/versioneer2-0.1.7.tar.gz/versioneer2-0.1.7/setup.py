# -*- coding: utf-8 -*-
import sys
import io
import imp

fp, pathname, description = imp.find_module('versioneer')

try:
    versioneer = imp.load_module('versioneer', fp, pathname, description)
finally:
    if fp: fp.close()

versioneer.VCS = 'git'
versioneer.versionfile_source = 'versioneer2/_version.py'
versioneer.versionfile_build = 'versioneer2/_version.py'
versioneer.tag_prefix = ''  # tags are like 1.2.0
versioneer.parentdir_prefix = 'versioneer2-'  # dirname like 'myproject-1.2.0'

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install or upgrade setuptools or pip")
    sys.exit(1)

readme = io.open('README.rst', mode='r', encoding='utf-8').read()

history = io.open('HISTORY.rst', mode='r',
                  encoding='utf-8').read().replace('.. :changelog:', '')

# Use cmdclass.update to add additional commands as necessary. See
# https://docs.python.org/2/distutils/extending.html#integrating-new-commands
cmdclass = versioneer.get_cmdclass()

setup(
    name='versioneer2',
    version=versioneer.get_version(),
    description='An updated, simplified version of versioneer"',
    long_description=readme + '\n\n' + history,
    license='MIT',
    author='Ryan Dwyer',
    author_email='ryanpdwyer@gmail.com',
    url='https://github.com/ryanpdwyer/versioneer2',
    zip_safe=False,
    include_package_data=True,
    # This lets setuptools include_package_data work with git
    setup_requires=["setuptools_git >= 0.3"],
    packages=find_packages(),

    # Add requirements here. If the requirement is difficult to install,
    # add to docs/conf.py MAGIC_MOCK, and .travis.yml 'conda install ...'
    install_requires=[],
    tests_require=['nose'],
    test_suite='nose.collector',
    cmdclass=cmdclass,
    entry_points="""
        [console_scripts]
        versioneer2installer=versioneer2.installer:main
        """,
    keywords='versioneer2',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
