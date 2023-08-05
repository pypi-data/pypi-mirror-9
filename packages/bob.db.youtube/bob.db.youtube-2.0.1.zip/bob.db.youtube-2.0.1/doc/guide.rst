.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Mon Sep  8 15:37:06 CEST 2014


.. doc-tests will work only when the .sql3 database file is available... Hence, here we only have code-blocks...
.. testsetup:: *

  import os
  YOUR_DATABASE_DIRECTORY = '/idiap/resource/database/YouTubeFaces/frame_images_DB'

==============
 User's Guide
==============

This package contains the access API and descriptions for the `YouTube Faces`_ database.
It only contains the Bob_ accessor methods to use the DB directly from python, with our certified protocols.
The actual raw data for the `YouTube Faces`_ database should be downloaded from the original URL (though we were not able to contact the corresponding Professor).


The Database Interface
----------------------

The :py:class:`bob.db.youtube.Database` complies with the standard biometric verification database as described in :ref:`commons`, implementing the interface :py:class:`bob.db.verification.utils.SQLiteDatabase`.


The Protocols
-------------

To use the protocol interface, you have to create an instance of the :py:class:`bob.db.youtube.Database`:

.. .. doctest::
.. code-block:: python

   >>> import bob.db.youtube
   >>> db = bob.db.youtube.Database(YOUR_DATABASE_DIRECTORY)

where ``YOUR_DATABASE_DIRECTORY`` is the base directory, where the original images from the database can be found, e.g., ``'/path/to/YouTubeFaces/frame_images_DB'``.

The database interface contains several functions to query the database.
For example, to get the list of supported protocols, you can query the list of supported protocols:

.. .. doctest::
.. code-block:: python

   >>> db.protocol_names()
   ('fold1', 'fold2', 'fold3', 'fold4', 'fold5', 'fold6', 'fold7', 'fold8', 'fold9', 'fold10')

These protocol names define the 10 different splits of the `YouTube Faces`_ protocol, for which experiments can be run.
Some of the remaining query functions require a protocol to be selected.

For each protocol, the splits of the database are distributed into three different groups: ``('world', 'dev', 'eval')``.

* The ``eval`` group contains exactly the split that is requested for the protocol.
  For this group, the final evaluation should be run, e.g., by classifying the corresponding pairs to be same class or different class.

* The ``dev`` group contains two splits, which contain different identities than the ``eval`` group.
  This group can be used, e.g., to select a threshold that is used to classify the pairs.

* Finally, the ``world`` group contains up to seven splits of the database, with identities distinct from the ``dev`` and ``eval`` groups.
  This split can be used to train your classifier.

For the final evaluation it is required that 10 different experiments are executed, e.g., by training 10 different classifiers on the according ``world`` splits, selecting 10 different thresholds on the ``dev`` set and compute 10 different classification results.
Finally, the classification accuracy is reported as an average of the 10 classification results.


The Directory Objects
---------------------

The most important method of the interface is the :py:func:`bob.db.youtube.Database.objects` function.
You can use this function to query the *information* for the protocols.
For the YouTube database, the information consists of a list of :py:class:`bob.db.youtube.models.Directory`.
Each ``Directory`` contains information about a video, such as the identity of the client, the shot id and the (relative) path of the directory in the database:

.. .. doctest::
.. code-block:: python

   >>> objects = db.objects(protocol='fold1')
   >>> type(objects)
   <type 'list'>
   >>> d = objects[0]
   >>> type(d)
   <class 'bob.db.youtube.models.Directory'>
   >>> d.client_id
   1
   >>> d.shot_id
   0
   >>> d.path                   #doctest:+SKIP
   u'AJ_Cook/0'

These ``Directory`` objects can be used to get the path for the image data.
Since the videos are stored as a list of frames, the ``Directory`` interface will return a list of image file names, sorted by frame number:

.. .. doctest::
.. code-block:: python

   >>> file_names = db.original_file_name(d)
   >>> print (file_names[0])    #doctest:+SKIP
   [...]/AJ_Cook/0/0.123.jpg

.. warning::
  Please note that -- in opposition to most other bob.db database interfaces -- the :py:meth:`bob.db.youtube.Database.original_file_name` function returns a **list** of file names.
  Likewise, :py:meth:`bob.db.youtube.Database.original_file_names` returns a list of lists of file names.


Finally, bounding boxes are annotated in the images.
To get these bounding boxes for a specific (set of) images, you can use the :py:func:`bob.db.youtube.Database.annotations` function.
In the example below, the annotations for the first 20 images are read and returned:

.. code-block:: python

  >>> file_name_stems = [os.path.basename(f) for f in file_names[:20]]
  >>> annotations = db.annotations(d, file_name_stems)
  >>> sorted(annotations.keys()) == file_name_stems
  True
  >>> bounding_box = annotations[file_name_stems[0]]
  >>> print (bounding_box)
  {'topleft': (56.0, 205.0), 'bottomright': (112.0, 261.0)}

The annotations for one image can, for example, be used to cut out the face region from the image, using default functionality from other Bob_ packages:

.. code-block:: python

  >>> import bob.io.base
  >>> import bob.io.image
  >>> import bob.ip.color
  >>> color_image = bob.io.base.load(file_names[0])
  >>> gray_image = bob.ip.color.rgb_to_gray(color_image)
  >>> face_region = gray_image[bounding_box['topleft'][0] : bounding_box['bottomright'][0],
                               bounding_box['topleft'][1] : bounding_box['bottomright'][1]]


.. _bob: https://www.idiap.ch/software/bob
.. _youtube faces: http://www.cs.tau.ac.il/~wolf/ytfaces

