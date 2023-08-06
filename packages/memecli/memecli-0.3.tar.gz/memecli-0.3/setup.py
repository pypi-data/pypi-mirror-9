import os
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = ['memecli']

requires = [
    'Click',
    'memeapi',
    'pyyaml',
    'tabulate',
]

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='memecli',
    version='0.3',
    description='Command line wrapper over http://memegenerator.net API.',
    author='Cabrera Cabrera',
    author_email='surrealcristian@gmail.com',
    url='https://github.com/surrealists/memecli',
    packages=packages,
    package_dir= {'memecli': 'memecli'},
    include_package_data=True,
    install_requires=requires,
    license='MIT',
    zip_safe=False,
    entry_points='''
        [console_scripts]
        memecli=memecli.main:cli
    ''',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet',
        'Topic :: Utilities',
    ],
    data_files=[
      ('/etc/bash_completion.d/', ['extras/memecli']),
    ],
)
