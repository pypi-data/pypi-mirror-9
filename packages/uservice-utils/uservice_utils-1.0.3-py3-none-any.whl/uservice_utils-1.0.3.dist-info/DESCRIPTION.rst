uservice-utils
##############


This python library provides common utuilities we use when building 
micro-services.

Hacking Notes:
==============

This library is designed to contain useful components for building micro-services. 
We aim to guarantee backwards compatibility. All code in this library must:

 * ...be tested to a reasonable degree.
 * ...be genericly useful to several services.

To hack on the library, create a python3 virtual environment::

	$ virtualenv -p python3 ve
	$ . ve/bin/activate

To run the tests::

	$ pip install -r test_requirements.txt
	$ python setup.py test

Dependencies:
=============

This library contains many different parts, and we don't want to force users to
install all the dependencies for all the parts in order to use any one piece.
For that reason, setup.py does not list any install-time dependencies, and users
of this library must ensure they have the required dependencies configured.



