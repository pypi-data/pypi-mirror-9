# -*- coding: utf-8 -*-

from setuptools import setup
import atkit
NAME = 'atkit'

# README.rst dynamically generated:
with open('README.rst', 'w') as f:
    f.write(atkit.__doc__)

def read(file):
    with open(file, 'r') as f:
        return f.read().strip()

console_scripts = []
for script in ('activate', 'sandbox', 'logview'):
    line = '%s.%s = %s.cli:%s' % (NAME, script, NAME, script)
    console_scripts.append(line)

setup(
    name=NAME,
    version=read('VERSION'),
    description=('%s (an Admin Took KIT) provides a suite of tools whose goal is "total knowledge" '
                 'regarding the python environment and process.') % NAME,
    long_description=read('README.rst'),
    author='Mike Burr',
    author_email='mburr@unintuitive.org',
    url='https://github.com/stnbu/{0}'.format(NAME),
    download_url='https://github.com/stnbu/{0}/archive/master.zip'.format(NAME),
    provides=[NAME],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    test_suite='test',
    packages=[NAME],
    requires=['npconf'],
    keywords=['logging', 'debugging', 'development', 'introspection', 'monkeypatching', 'hacking', 'usercustomize'],
    entry_points={'console_scripts': console_scripts},
)
