# coding=utf-8
from distutils.core import setup
setup(
    name="Chipster Job Manager",
    version='3.1.3',
    description='Manages long running jobs on Chipster platform',
    license='MIT',
    author='Harri Hämäläinen',
    author_email='harri.hamalainen@csc.fi',
    packages=['jobmanager'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ])
