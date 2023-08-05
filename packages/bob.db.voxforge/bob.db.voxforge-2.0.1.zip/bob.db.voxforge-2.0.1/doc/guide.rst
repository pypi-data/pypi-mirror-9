.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Thu Dec  6 12:28:25 CET 2012

==============
 User's Guide
==============

This package contains the access API and descriptions for the Voxforge_ database.
It only contains the Bob_ accessor methods to use the database directly from python, with our certified protocols.

The Database Interface
----------------------

The :py:class:`bob.db.voxforge.Database` complies with the standard biometric verification database as described in :ref:`commons`, by implementing the  :py:class:`bob.db.verification.filelist.Database`.


.. todo::
   Explain the particularities of the :py:class:`bob.db.voxforge.Database` database.

.. _bob: https://www.idiap.ch/software/bob
.. _voxforge: http://www.voxforge.org

