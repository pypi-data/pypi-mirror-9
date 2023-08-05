.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Thu 17 Apr 16:59:12 2014 CEST

.. image:: http://img.shields.io/badge/docs-stable-yellow.png
   :target: http://pythonhosted.org/bob.ip.flandmark/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.ip.flandmark/master/index.html
.. image:: https://travis-ci.org/bioidiap/bob.ip.flandmark.svg?branch=v2.0.1
   :target: https://travis-ci.org/bioidiap/bob.ip.flandmark
.. image:: https://coveralls.io/repos/bioidiap/bob.ip.flandmark/badge.png
   :target: https://coveralls.io/r/bioidiap/bob.ip.flandmark
.. image:: https://img.shields.io/badge/github-master-0000c0.png
   :target: https://github.com/bioidiap/bob.ip.flandmark/tree/master
.. image:: http://img.shields.io/pypi/v/bob.ip.flandmark.png
   :target: https://pypi.python.org/pypi/bob.ip.flandmark
.. image:: http://img.shields.io/pypi/dm/bob.ip.flandmark.png
   :target: https://pypi.python.org/pypi/bob.ip.flandmark

==============================
 Python Bindings to Flandmark
==============================

This package is a simple Python wrapper to the (rather quick) open-source facial landmark detector Flandmark_, **version 1.0.7** (or the github state as of 10/february/2013).
If you use this package, the author asks you to cite the following paper::

  @inproceedings{Uricar-Franc-Hlavac-VISAPP-2012,
    author =      {U\v{r}i\v{c}\'a\v{r}, Michal and Franc, Vojt\v{e}ch and Hlav\'a\v{c}, V\'{a}clav},
    title =       {Detector of Facial Landmarks Learned by the Structured Output {SVM}},
    year =        {2012},
    pages =       {547-556},
    booktitle =   {VISAPP '12: Proceedings of the 7th International Conference on Computer Vision Theory and Applications},
    editor =      {Csurka, Gabriela and Braz, Jos{\'{e}}},
    publisher =   {SciTePress --- Science and Technology Publications},
    address =     {Portugal},
    volume =      {1},
    isbn =        {978-989-8565-03-7},
    book_pages =  {747},
    month =       {February},
    day =         {24-26},
    venue =       {Rome, Italy},
    keywords =    {Facial Landmark Detection, Structured Output Classification, Support Vector Machines, Deformable Part Models},
    prestige =    {important},
    authorship =  {50-40-10},
    status =      {published},
    project =     {FP7-ICT-247525 HUMAVIPS, PERG04-GA-2008-239455 SEMISOL, Czech Ministry of Education project 1M0567},
    www = {http://www.visapp.visigrapp.org},
  }

You should also cite `Bob`_, as a core framework, in which these bindings are based on::

  @inproceedings{Anjos_ACMMM_2012,
    author = {Anjos, Andr\'e AND El Shafey, Laurent AND Wallace, Roy AND G\"unther, Manuel AND McCool, Christopher AND Marcel, S\'ebastien},
    title = {Bob: a free signal processing and machine learning toolbox for researchers},
    year = {2012},
    month = oct,
    booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
    publisher = {ACM Press},
    url = {http://publications.idiap.ch/downloads/papers/2012/Anjos_Bob_ACMMM12.pdf},
  }

Installation
------------
To install this package -- alone or together with other `Packages of Bob <https://github.com/idiap/bob/wiki/Packages>`_ -- please read the `Installation Instructions <https://github.com/idiap/bob/wiki/Installation>`_.
For Bob_ to be able to work properly, some dependent packages are required to be installed.
Please make sure that you have read the `Dependencies <https://github.com/idiap/bob/wiki/Dependencies>`_ for your operating system.

Documentation
-------------
For further documentation on this package, please read the `Stable Version <http://pythonhosted.org/bob.ip.flandmark/index.html>`_ or the `Latest Version <https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.ip.flandmark/master/index.html>`_ of the documentation.
For a list of tutorials on this or the other packages ob Bob_, or information on submitting issues, asking questions and starting discussions, please visit its website.

.. _bob: https://www.idiap.ch/software/bob
.. _flandmark: http://cmp.felk.cvut.cz/~uricamic/flandmark/index.php

