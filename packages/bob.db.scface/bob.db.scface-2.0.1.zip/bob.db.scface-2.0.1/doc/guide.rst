.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Thu Dec  6 12:28:25 CET 2012

==============
 User's Guide
==============

This package contains the access API and descriptions for the SCface_ database.
It only contains the Bob_ accessor methods to use the DB directly from python, with our certified protocols.
The actual raw data for the SCface_ database should be downloaded from the original URL.


The Database Interface
----------------------

The :py:class:`bob.db.scface.Database` complies with the standard biometric verification database as described in :ref:`commons`, implementing both interfaces :py:class:`bob.db.verification.utils.SQLiteDatabase` and :py:class:`bob.db.verification.utils.ZTDatabase`.

.. todo::
   Explain the particularities of the :py:class:`bob.db.scface.Database`.


.. _scface: http://www.scface.org
.. _bob: https://www.idiap.ch/software/bob
