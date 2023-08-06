Pydentifier
===========

Generates Python identifiers from English text. Useful for code generation.


Class name:

.. code-block:: python

   >>> pydentifier.upper_camel("I'm a class", prefix='')
   'IAmAClass'


Function name:

.. code-block:: python

   >>> pydentifier.lower_underscore('This is a function', prefix='')
   'this_is_a_function'


Reserved keyword:

.. code-block:: python

   >>> pydentifier.lower_underscore('class', prefix='')
   'class_'


Internal method:

.. code-block:: python

   >>> pydentifier.lower_underscore("Shouldn't touch this", prefix='_')
   '_should_not_touch_this'


Private method:

.. code-block:: python

   >>> pydentifier.lower_underscore("Can't touch this", prefix='__')
   '__cannot_touch_this'
