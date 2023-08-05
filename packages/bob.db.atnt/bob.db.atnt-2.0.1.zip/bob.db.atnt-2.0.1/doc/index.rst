.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Tue Aug 26 09:42:18 CEST 2014

.. _bob.db.atnt:

==============================================
 AT&T Database of Faces Verification Protocol
==============================================

.. todolist::

This module contains the interface to query the face verification protocol for the AT&T database of faces (formerly known as the ORL face database).

.. warning::
  The AT&T Database of Faces is a small, old and outdated facial image database.
  According to [LiJain2005]_, the *algorithm performance over this database has been saturated*.
  This database should only be used for development or testing purposes, and **not** to publish scientific papers based on its results!


.. [LiJain2005] **Stan Z. Li and Anil K. Jain**, *Handbook of Face Recognition*, Springer, 2005.

Documentation
-------------

.. toctree::
   :maxdepth: 2

   guide
   py_api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

