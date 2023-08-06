============
decent-tools
============
Command-line tools for programming and reconfiguring wireless sensor nodes from Decentlab GmbH.

Description
-----------
Development of command-line tools to manage *decentnode*. Currently, the following tools are completed:

- *dnbsl* - msp430 bsl programmer
- *dntc65i* - tc65i manager
- *dnmotes* - list decentnodes

Developed on MacOSX 10.10 and tested on Debian GNU/Linux (jessie).

Installation
------------
Before installing with *pip*, please make sure that you remove any previous (either installed manually or with *apt-get*) *decent-tools* package.

The *python-msp430-tools* dependency is not correctly packaged for *pypi*; therefore it can be installed using this command from the trunk::

    sudo apt-get install bzr # needed for the following
    sudo pip install bzr+lp:python-msp430-tools/trunk/@python-msp430-tools-0.7#egg=python_msp430_tools-0.7

Finally, the decent-tools can be installed as follows::

    sudo pip install decent-tools

That's all folks.
