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

	$ python setup.py test





