.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Tue Aug 26 09:42:18 CEST 2014

.. _bob.db.voxforge:

==========================================
 Voxforge Database Verification Protocols
==========================================

.. todolist::

=======================================================
 Speaker recognition protocol on the Voxforge Database
=======================================================

`Voxforge`_ offers a collection transcribed speech for use with **Free** and **Open Source Speech Recognition Engines**.
In this package, we design a speaker recognition protocol that uses a **small subset of the english audio files** (only 6561 files) belonging to **30 speakers** randomly selected.
This subset is split into three equivalent parts: Training (10 speakers), Development (10 speakers) and Test (10 speakers) sets.

This package serves as a toy example of speaker recognition database while testing :ref:`bob.spear <bob.spear>`.

:ref:`bob.spear <bob.spear>` is developed at Idiap_ during its participation to the `NIST SRE 2012 evaluation`_.
If you use this package and/or its results, please cite the following publications:

1. The original paper presented at the NIST SRE 2012 workshop:

   .. code-block:: latex

      @inproceedings{Khoury_NISTSRE_2012,
        author = {Khoury, Elie and El Shafey, Laurent and Marcel, S\'ebastien},
        title = {The Idiap Speaker Recognition Evaluation System at NIST SRE 2012},
        booktitle = {NIST Speaker Recognition Conference},
        year = {2012},
        month = dec,
        location = {Orlando, USA},
        organization = {NIST},
        pdf = {http://publications.idiap.ch/downloads/papers/2012/Khoury_NISTSRE_2012.pdf}
      }

2. Bob_ as the core framework used to run the experiments:

   .. code-block:: latex

      @inproceedings{Anjos_ACMMM_2012,
        author = {Anjos, Andr\'e and El Shafey, Laurent and Wallace, Roy and G\"unther, Manuel and McCool, Christopher and Marcel, S\'ebastien},
        title = {Bob: a free signal processing and machine learning toolbox for researchers},
        year = {2012},
        month = oct,
        booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
        publisher = {ACM Press},
        pdf = {http://publications.idiap.ch/downloads/papers/2012/Anjos_Bob_ACMMM12.pdf}
     }

Getting the data
----------------

The original data can be downloaded directly from Voxforge_, or by running ``./scripts/download_and_untar.sh`` that takes as input the path in which the data will be stored:

.. code-block:: sh

  $ ./scripts/download_and_untar.sh PATH/TO/WAV/DIRECTORY


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

.. _bob: https://www.idiap.ch/software/bob
.. _voxforge: http://www.voxforge.org
.. _nist sre 2012 evaluation: http://www.nist.gov/itl/iad/mig/sre12.cfm
.. _idiap: http://www.idiap.ch


