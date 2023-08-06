============
python-phabricator3
============

***************
About
***************
Python3 port/fork of disqus/python-phabricator (Phabricator Conduit wrapper)

***************
Installation
***************
pip
===============
    pip install phabricator3

without pip
===============
Download/clone the code and then run:

    python setup.py install

***************
Usage
***************
See examples/ for more examples.

.. code-block:: python

    from phabricator import Phabricator
    phab = Phabricator()  # This will use your ~/.arcrc file
    phab.user.whoami()
	
Parameters are passed as keyword arguments to the resource call:

.. code-block:: python

    phab.user.find(aliases=["sugarc0de"])

Documentation on all methods is located at https://secure.phabricator.com/conduit/

***************
Thanks
***************
*Disqus* for python-phabricator

*vilhelmk*, *lifeisstillgood*, *marcqualie* for pull requests
