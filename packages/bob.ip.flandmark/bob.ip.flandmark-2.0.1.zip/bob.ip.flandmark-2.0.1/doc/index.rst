.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Thu  3 Apr 13:47:28 2014 CEST
..
.. Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

.. _bob.ip.flandmark:

=======================================================================
 Python Bindings to the Flandmark Keypoint Localizer for Frontal Faces
=======================================================================

.. todolist::


This package is a simple Python wrapper to the (rather quick) open-source
facial landmark detector Flandmark_, **version 1.0.7** (or the github state
as of 10/february/2013).  If you use this package, the author asks you to cite
the following paper:

.. code-block:: latex

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

You should also cite `Bob`_, as a core framework, in which these bindings are
based on:

.. code-block:: latex

  @inproceedings{Anjos_ACMMM_2012,
    author = {Anjos, Andr\'e AND El Shafey, Laurent AND Wallace, Roy AND G\"unther, Manuel AND McCool, Christopher AND Marcel, S\'ebastien},
    title = {Bob: a free signal processing and machine learning toolbox for researchers},
    year = {2012},
    month = oct,
    booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
    publisher = {ACM Press},
    url = {http://publications.idiap.ch/downloads/papers/2012/Anjos_Bob_ACMMM12.pdf},
  }

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

.. include:: links.rst
