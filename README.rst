==============================================
_msg: Python Library Logging Facility
==============================================

_msg, pronounced 'you-message', is a module level logging utility intended for
libraries, which works just as well for normal logging scenarios.
The package name replaces the '_' with a 'u' to conform with PEP8 standards.


Installation
============

pip install umsg


Usage
=====

Class Logging Made Easy
-----------------------

.. code:: python

   from umsg import LoggingMixin

   class MyClass(LoggingMixin):
       def __init__(self):
           super().__init__(prefix='MyClass')
           self.log('Logging initiated', level='debug')


Programmatic log message levels
-------------------------------

.. code:: python

  from umsg import log

  msg_level = 'debug'
  log('Default level is INFO')
  log('This message is DEBUG', level=msg_level)

  log_level = 'warn'
  log('Warnings are now in style', level=msg_level)


Documentation
=============

Detailed documentation is available `here <https://rastern.github.io/umsg>`_.
