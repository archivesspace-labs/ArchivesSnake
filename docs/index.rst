.. ArchivesSnake documentation master file, created by
   sphinx-quickstart on Thu Jan 25 20:12:19 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ArchivesSnake's documentation!
=========================================

.. toctree::
   :maxdepth: 4
   :caption: Contents:



.. automodule:: asnake.aspace
   :members:
   :inherited-members:

   .. autoclass:: asnake.aspace.ASpace

      .. automethod:: asnake.aspace.ASpace.__getattr__

.. automodule:: asnake.jsonmodel
   :members:

   .. autoclass:: asnake.jsonmodel.JSONModelObject
      :members:

   .. autoclass:: asnake.jsonmodel.ComponentObject
      :members:
      :inherited-members:

   .. autoclass:: asnake.jsonmodel.JSONModelRelation
      :members:

      .. automethod:: asnake.jsonmodel.JSONModelRelation.__getattr__

      .. automethod:: asnake.jsonmodel.JSONModelRelation.__call__

   .. autoclass:: asnake.aspace.AgentRelation

      .. automethod:: asnake.aspace.AgentRelation.__getitem__


.. automodule:: asnake.client
   :members:
   :inherited-members:

   .. autoclass:: asnake.client.ASnakeClient
      :members:
      :inherited-members:

.. automodule:: asnake.client.web_client
   :members:
   :inherited-members:

.. automodule:: asnake

   .. autoclass:: ASnakeConfig
      :members:
      :inherited-members:

      .. automodule:: asnake.logging
         :members:
         :inherited-members:

.. automodule:: asnake.utils
   :members:
   :inherited-members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
