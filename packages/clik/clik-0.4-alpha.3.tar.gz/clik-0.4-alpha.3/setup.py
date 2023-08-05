from setuptools import setup
import sys


version = '0.4-alpha.3'
requires = (
)


if sys.version_info < (2, 7):
    requires += ('argparse',)


setup(
    author='Joe Strickler',
    author_email='joe@decafjoe.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.3',
    ],
    description='Command line interface kit.',
    install_requires=requires,
    keywords='clik',
    license='BSD',
    name='clik',
    package_dir={'': 'src'},
    packages=['clik'],
    test_suite='test',
    url='https://github.com/jds/clik',
    version=version,
)
