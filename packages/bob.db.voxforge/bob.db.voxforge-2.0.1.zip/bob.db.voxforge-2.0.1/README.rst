.. vim: set fileencoding=utf-8 :
.. Manuel Guenther <manuel.guenther@idiap.ch>
.. Thu Sep  4 11:35:05 CEST 2014

.. image:: http://img.shields.io/badge/docs-stable-yellow.png
   :target: http://pythonhosted.org/bob.db.voxforge/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.db.voxforge/master/index.html
.. image:: https://travis-ci.org/bioidiap/bob.db.voxforge.svg?branch=v2.0.1
   :target: https://travis-ci.org/bioidiap/bob.db.voxforge
.. image:: https://coveralls.io/repos/bioidiap/bob.db.voxforge/badge.png
   :target: https://coveralls.io/r/bioidiap/bob.db.voxforge
.. image:: https://img.shields.io/badge/github-master-0000c0.png
   :target: https://github.com/bioidiap/bob.db.voxforge/tree/master
.. image:: http://img.shields.io/pypi/v/bob.db.voxforge.png
   :target: https://pypi.python.org/pypi/bob.db.voxforge
.. image:: http://img.shields.io/pypi/dm/bob.db.voxforge.png
   :target: https://pypi.python.org/pypi/bob.db.voxforge
.. image:: https://img.shields.io/badge/original-data--files-a000a0.png
   :target: http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/16kHz_16bit

=========================================
 Voxforge Toy Database Interface for Bob
=========================================

Voxforge_ offers a collection of transcribed speech for use with **Free** and **Open Source Speech Recognition Engines**.
In this package, we design a speaker recognition protocol that uses a **small subset of the english audio files** (only 6561 files) belonging to **30 speakers** randomly selected.
This subset is split into three equivalent parts: Training (10 speakers), Development (10 speakers) and Evaluation (10 speakers) sets.


Installation
------------
To install this package -- alone or together with other `Packages of Bob <https://github.com/idiap/bob/wiki/Packages>`_ -- please read the `Installation Instructions <https://github.com/idiap/bob/wiki/Installation>`_.
For Bob_ to be able to work properly, some dependent packages are required to be installed.
Please make sure that you have read the `Dependencies <https://github.com/idiap/bob/wiki/Dependencies>`_ for your operating system.


Getting the data
----------------
The data can be downloaded from its original URL (on Voxforge), or by running ``./scripts/download_and_untar.sh``, which takes as input the path in which the data will be stored::

  $ ./scripts/download_and_untar.sh PATH/TO/WAV/DIRECTORY


Documentation
-------------
For further documentation on this package, please read the `Stable Version <http://pythonhosted.org/bob.db.voxforge/index.html>`_ or the `Latest Version <https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.db.voxforge/master/index.html>`_ of the documentation.
For a list of tutorials on this or the other packages ob Bob_, or information on submitting issues, asking questions and starting discussions, please visit its website.


.. _bob: https://www.idiap.ch/software/bob
.. _voxforge: http://www.voxforge.org


