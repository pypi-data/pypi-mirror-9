import sys
import os
from setuptools import setup

if sys.version_info.major == 3:
    base_dir = 'py3'
else:
    assert sys.version_info.major == 2
    assert sys.version_info.minor >= 7
    base_dir = 'py2'

setup(
    name='dispy',
    version='3.23',
    description='Distributed and Parallel Computing Framework with/for Python.',
    long_description=open('README.rst').read(),
    keywords='distributed computing, parallel processing, mapreduce, hadoop, job scheduler',
    url='http://dispy.sourceforge.net',
    author='Giridhar Pemmasani',
    author_email='pgiri@yahoo.com',
    package_dir={'':base_dir},
    py_modules=['asyncoro', 'dispy'],
    scripts=[os.path.join(base_dir, script) for script in \
             ['dispy.py', 'dispynode.py', 'dispynetrelay.py', 'dispyscheduler.py']],
    license='MIT',
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
        ]
    )
