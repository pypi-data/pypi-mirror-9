The BaseClass
=============

.. currentmodule:: iperflexer.baseclass

A module for base classes that have common methods to inherit.

Just logging for now.



.. ifconfig:: repository != 'rtfd'

   .. uml::

      BaseClass o-- logging.Logger
      BaseClass : Logger

.. autosummary::
   :toctree: api

   BaseClass

Example Use::

   class TestClass(BaseClass):
       def __init__(self):
           super(TestClass, self).__init__()

   t = TestClass()
   t.logger.info("This message will get sent to the logger as INFO")
   
