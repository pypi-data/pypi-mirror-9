observer
==========

|PyPI| |Build Status| |Coverage Status|

A simple implementation of the observer pattern.

.. code-block:: python

	import observer
	# Create a subject and list the events it might fire
	foo = observer.Subject('bar', 'baz')

	# Add a listener
	def foo_bar_listener(*args):
	   print("heard 'bar'", args)
	   
	foo('bar', foo_bar_listener)

	# fire events
	foo.fire('bar', 1, 2, 3)
	# -> heard 'bar' (1, 2, 3)

	# Trying to listen to an unregistered event throws an error
	foo('snorble', lambda: None)
	# -> AssertionError: snorble is not a valid event for this subject

	# Same with trying to fire an unregistered event
	foo.fire('snorble')
	# -> AssertionError: snorble is not a valid event for this subject


.. |PyPI| image:: https://pypip.in/version/observer/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/observer/

.. |Build Status| image:: https://travis-ci.org/cooper-software/observer.svg
   :target: https://travis-ci.org/cooper-software/observer

.. |Coverage Status| image:: https://img.shields.io/coveralls/cooper-software/observer.svg
   :target: https://coveralls.io/r/cooper-software/observer
