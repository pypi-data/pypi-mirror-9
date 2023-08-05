.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Fri Oct 31 16:01:33 CET 2014

==============
 User's Guide
==============

This package contains the access API and descriptions for the `CAS-PEAL`_ R1 database.
The actual raw data for the database should be downloaded from the original URL.

The CAS-PEAL database consists of several ten thousand images of Chinese people (CAS = Chinese Academy of Science).
Overall, there are 1040 identities contained in the database.
For these identities, images with different Pose, Expression, Aging and Lighting (PEAL) conditions, as well as accessories, image backgrounds and camera distances are provided.

Included in the database, there are file lists defining identification experiments.
All the experiments rely on a gallery that consists of the frontal and frontally illuminated images with neutral expression and no accessories.
For each of the variations, probe sets including exactly that variation are available.

The training set consists of a subset of the frontal images (some images are both in the training and in the development set).
This also means that there is no training set defined for the pose images.
Additionally, the database defines only a development set, but no evaluation set.

This package only contains the Bob_ accessor methods to use the DB directly from python, with our certified protocols, which are defined in [Gao2008]_.
We have implemented the default face identification protocols ``'accessory'``, ``'aging'``, ``'background'``, ``'distance'``, ``'expression'`` and ``'lighting'``.
We do not provide the ``'pose'`` protocol (yet) since the training set of the `CAS-PEAL`_ database does not contain pose images.


.. [Gao2008] **Wen Gao, Bo Cao, Shiguang Shan, Xilin Chen, Delong Zhou, Xiaohua Zhang, Debin Zhao**. *The CAS-PEAL Large-Scale Chinese Face Database and Baseline Evaluations*. IEEE Transactions on System Man, and Cybernetics (Part A). vol.38, no.1, pages 149-161. 2008.


The Database Interface
----------------------

The :py:class:`bob.db.caspeal.Database` complies with the standard biometric verification database as described in :ref:`commons`, implementing the interface :py:class:`bob.db.verification.utils.SQLiteDatabase`.

.. todo::
   Explain the particularities of the :py:class:`bob.db.caspeal.Database` database.


.. _cas-peal: http://www.jdl.ac.cn/peal/
.. _bob: https://www.idiap.ch/software/bob
