"""build and install the python modules and command line scripts."""
from setuptools import setup, find_packages
import os


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as fp_:
        return fp_.read()

setup(
    name='decent-tools',
    version='0.2.3',
    description='decentnode tools',
    long_description=(read('README.rst')),
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Systems Administration',
        ],
    url='http://www.decentlab.com',
    author='hashiname',
    author_email='hashiname@gmail.com',
    license='Apache License 2.0',
    packages=find_packages(exclude='tests'),
    entry_points={
        'console_scripts': [
            'dnbsl = dn.bsl:main',
            'dntc65i = dn.tc65i.__main__:main',
            'dnmotes = dn.lusb.common:print_motes'
            ],
        },
    install_requires=[
        'pyserial>=2.7, <3.0',
        'pyftdi>=0.10.0',
        'pyusb>=1.0.0b2',
        'python-msp430-tools>=0.7, <1.0',
        'python-dateutil>=2.0, <3.0',
        ],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False,
    )
