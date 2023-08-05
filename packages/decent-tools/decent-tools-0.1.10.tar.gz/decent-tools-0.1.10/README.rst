============
decent-tools
============
Command-line tools for programming and reconfiguring wireless sensor nodes from Decentlab GmbH.

Description
-----------
Development of command-line tools to manage *decentnode*. Currently, the following tools are completed:

- *dn-bsl* - msp430 bsl programmer
- *dn-tc65i* - tc65i manager
- *dn-ftdi-cbus* - ftdi cbus settings

Tools which are in active development:

- dn-serialer - serial manager for decentnode. serial id is stored on both ftdi and msp430.
- udev rule for automatic symbolic link generation (ttyUSB0 -> tty.usbserial-XXXXXXX) for linux systems.

Developed on MacOSX 10.9 and tested on Debian GNU/Linux testing (jessie).

Installation
------------
Before installing with *pip*, please make sure that you remove any previous (either installed manually or with *apt-get*) *decent-tools* package.

*ftdi* dependency can be installed with::

    sudo apt-get install python-ftdi #debpkg (debian) based
    brew install libftdi --build-from-source # homebrew (macosx) based, make sure the python binding is built

The *python-msp430-tools* dependency is not correctly packaged for *pypi*; therefore it can be installed using this command from the trunk::

    sudo apt-get install bzr # needed for the following
    sudo pip install bzr+lp:python-msp430-tools/trunk/@python-msp430-tools-0.7#egg=python_msp430_tools-0.7

Finally, the decent-tools can be installed as follows::

    sudo pip install decent-tools

That's all folks. By the way, I hope you won't use *sudo* with the homebrew *pip* commands.
