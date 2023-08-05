.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Thu Oct 30 19:25:28 CET 2014

.. _commons:

====================================================
 Common Functionality in all Verification Databases
====================================================

The verification database interface provides an interface and assures usability of common functionality, which is described in this section.


The ``File`` class
------------------

Commonly, a verification database contains several files in a certain directory structure.
This directory structure is usually based in a certain *base directory*, from where the files can be found using *relative* paths.
The base directory is different for every user of the database, while the relative paths are identical for each user.
Hence, the :py:class:`bob.db.verification.utils.File` interface stores only relative ``path``\s, and even without the file name extension.

To be unique and short, every file has its own *ID*.
Using this ID, each file can be identified.
In most cases, this ``file_id`` is of an integral type, though some databases use other hashable types such as ``str``.

Finally, each ``File`` contains the information, to which *client* identity in the database it belongs.
Again, the ``client_id`` is usually of an integral type, but some databases use other types such as ``str``.

The :py:class:`bob.db.verification.utils.File` class has two functions.
Since only relative paths without file name extension are stored, the :py:meth:`bob.db.verification.utils.File.make_path` function generates a full file name by pre-pending the given base directory, and appending the given file name extension.
Similarly, the :py:meth:`bob.db.verification.utils.File.save` function takes a given ``data`` object and saves it to the given directory with the given file name extension using the :py:func:`bob.io.base.save` function.


The ``Database``
----------------

A :py:class:`bob.db.verification.utils.Database` contains information about the whole database.
For example, the base directory and the file name extension of the original data files can be specified in the :py:class:`bob.db.verification.utils.Database` constructor.

The :py:class:`bob.db.verification.utils.Database` provides a common interface to *query* list of :py:class:`bob.db.verification.utils.File` objects based on certain criteria.
Some of these criteria are *dependent* on the database, but some criteria are common for all verification database.
Database dependent criteria can usually be specified be *keyword arguments*, which will directly be passed to the derived class :py:meth:`bob.db.verification.utils.Database.objects` function, see :ref:`objects`.

Each verification database defines different *groups*, i.e, a *training set* (usually called the ``world`` set) and a *development set* ``dev``.
Sometimes, also an independent *evaluation set* ``eval`` is provided.
Which kind of groups are available for the database, can be queried using the :py:meth:`bob.db.verification.utils.Database.groups` function.

Additionally, each database defines at least one *evaluation protocol*, which comprises information on which ``file_id`` belongs to which ``group``.
All functions of the :py:class:`bob.db.verification.utils.Database` interface accept a ``protocol``, which might be ``None`` in case the database defines only a single protocol, or in case some file lists are identical for each protocol.

The files for the development (and evaluation) set are usually split into two different *purposes*.
Some of the files are used to *enroll models* (aka *templates*, *targets*) for a given client, while other files are used to *probe* (aka *test*, *query*) some or all models to compute similarity *scores*.
Each enrolled model has a specific *model id*, a list of which can be queried by the :py:meth:`bob.db.verification.utils.Database.model_ids` method.
For most databases, one model is enrolled for each client, and thus, the :py:attr:`bob.db.verification.utils.File.client_id` is identical to the ``model_id``.
In any case, you can use the :py:meth:`bob.db.verification.utils.Database.get_client_id_from_model_id` function to obtain the ``client_id`` for a given ``model_id``.


Functions returning ``File`` lists
++++++++++++++++++++++++++++++++++

Several functions of the :py:class:`bob.db.verification.utils.Database` interface return lists of :py:class:`bob.db.verification.utils.File` objects, which can be used for several tasks of a biometric recognition experiment.
These lists are in general **unordered**, i.e, two subsequent calls to the same function might return the same list in a different order, and **unique**, i.e., no to files with the same ``file_id`` are returned.

The most simple function :py:meth:`bob.db.verification.utils.Database.all_files` will simply return a list of all files that fulfill the desired database dependent criteria.

The training set contains a list of :py:class:`bob.db.verification.utils.File`\s, which can be used to train a biometric recognition system.
This file list of the training set can be obtained using the :py:meth:`bob.db.verification.utils.Database.training_files` method.
Again, database dependent criteria can be specified using specialized keyword arguments.

Again, a list of all files (including the enrollment and probe files) for the ``dev`` or ``eval`` group can be queried by the :py:meth:`bob.db.verification.utils.Database.test_files`.
The list of enrollment and probe files can be obtained through the :py:meth:`bob.db.verification.utils.Database.enroll_files` and :py:meth:`bob.db.verification.utils.Database.probe_files`, respectively.

.. important::

  Both methods accept to specify an optional ``model_id``, but the usage of the ``model_id`` is different for both cases.
  If the ``model_id`` is not specified (i.e. ``None``), all files to enroll all models or all probe files are returned.
  Specifying a ``model_id`` in the :py:meth:`bob.db.verification.utils.Database.enroll_files` function, only the files used to enroll the model with the given ``model_id`` are returned.
  In opposition, querying the :py:meth:`bob.db.verification.utils.Database.probe_files` with a ``model_id`` will return a list of probe files, with which the model of the given ``model_id`` should be compared.
  **In most protocols of most databases, all models are compared with all probe files and, hence, the** ``model_id`` **is ignored in** :py:meth:`bob.db.verification.utils.Database.probe_files`.


.. _objects:

The ``objects`` function
++++++++++++++++++++++++

The most important function that needs to be implemented in each verification database is the :py:meth:`bob.db.verification.utils.Database.objects` function.
This function returns a list of objects, which are derived from the :py:class:`bob.db.verification.utils.File`.
The ``objects`` function has *at least* the following set of keyword parameters:

* ``groups``: to define different groups like ``world``, ``dev`` or ``eval``; accepts ``None``, a single group or a tuple of groups
* ``protocol``: to define a name of an evaluation protocol; accepts only a single protocol, might also accept ``None``
* ``purposes``: to define the purpose of the file; accepts at least one or both values ``'enroll'`` (in fact, most of the databases still expect the BE spelling ``'enrol'``) and ``'probe'``, or can be ``None``
* ``model_ids``: to limit the enroll or probe files to the given model id

In case, the database does not need those parameters, they might be simply ignored, e.g., the ``protocol`` is ignored in :py:meth:`bob.db.atnt.Database.objects` since only a single protocol is defined in the AT&T database.
Other keyword parameters might be present as well.
Commonly, the other keyword parameters limit **only the training files** since the development and evaluation files are strictly defined by the protocol.


General functions
+++++++++++++++++

Some more generic functions concerning file names are defined in the ``Database`` interface as well.
The :py:meth:`bob.db.verification.utils.Database.file_names` method returns the list of file name for the given list of files, the base directory and the extension.
When the ``original_directory`` and the ``original_extension`` where specified in the :py:class:`bob.db.verification.utils.Database` constructor, the :py:meth:`bob.db.verification.utils.Database.original_file_name` function will return the full path of the original data file for a given :py:class:`bob.db.verification.utils.File` object, while :py:meth:`bob.db.verification.utils.Database.original_file_names` iterates over a list of files.
Both functions accept a parameter ``check_existence`` to check, whether the original data file exists, **which is** ``True`` **by default**.

The :py:meth:`bob.db.verification.utils.Database.annotations` method will return a dictionary of annotations of any kind for the given :py:class:`bob.db.verification.utils.File`, see :ref:`annotations`.
In case, no annotation is available for the given file, or the database does not define any annotations, ``None`` is returned.

In some special cases (like the :py:class:`bob.db.frgc.Database`), a protocol requires that a single ``File`` object contains several actual data files.
In this case, the :py:meth:`bob.db.frgc.Database.provides_file_set_for_protocol` method returns ``True``, while most other databases use the default implementation :py:meth:`bob.db.verification.utils.Database.provides_file_set_for_protocol`, which returns ``False``.


Functions for ZT score normalization
++++++++++++++++++++++++++++++++++++

Several databases inside Bob provide a special subset of the training set that is used for score normalization, particularly ZT score normalization as described in [Auck00]_.
For a given protocol, these files can be obtained using the :py:class:`bob.db.verification.utils.ZTDatabase`, which is derived from the :py:class:`bob.db.verification.utils.Database`.
All keyword arguments in the constructor of  :py:class:`bob.db.verification.utils.ZTDatabase` (i.e., ``original_directory`` and ``original_extension``) are directly passed to the :py:class:`bob.db.verification.utils.Database` constructor.

The ZT database adds three query functions.
The method :py:meth:`bob.db.verification.utils.ZTDatabase.t_model_ids` returns the list of model ids for T-Norm, where the list of files to enroll a T-Norm model of a given model id can be obtained with the :py:meth:`bob.db.verification.utils.ZTDatabase.t_enroll_files` method.
Finally, :py:meth:`bob.db.verification.utils.ZTDatabase.z_probe_files` returns the list of probe files that are used for Z-Norm.

.. [Auck00] **Roland Auckenthaler, Michael Carey, Harvey Lloyd-Thomas** *Score Normalization for Text-Independent Speaker Verification Systems*, Digital Signal Processing, Pages 42-54, 2000,


SQLite Databases
----------------

Several database interfaces rely on SQLite_ to generate and query a *local SQL database file*, which stores information about the files, clients, protocols and -- if applicable -- annotations.
To simplify the handling of the SQLite_ query, the :py:class:`bob.db.verification.utils.SQLiteDatabase` is provided, which derives from :py:class:`bob.db.verification.utils.Database`
In the constructor if the :py:class:`bob.db.verification.utils.SQLiteDatabase`, simply specify the local SQLite database file.
For technical reasons, also the class derived from :py:class:`bob.db.verification.utils.File` needs to be given as a parameter.
All other keyword arguments (i.e., ``original_directory`` and ``original_extension``) are passed directly to the :py:class:`bob.db.verification.utils.Database` constructor.

The most important function in this class is :py:meth:`bob.db.verification.utils.SQLiteDatabase.query`, which is heavily used in derived classes to query objects from the local SQL database file.
Commonly, such a query looks somewhat like:

.. code-block:: py

   self.query(File).join(...).filter().order_by(...)

to retrieve a list (in fact, an *iterator*) of File objects that fulfill your requirements.
Internally, it will first check that the database :py:meth:`bob.db.verification.utils.SQLiteDatabase.is_valid`, i.e., that the local SQL database file exists and a session is opened for reading.

Three additional methods :py:meth:`bob.db.verification.utils.SQLiteDatabase.files`, :py:meth:`bob.db.verification.utils.SQLiteDatabase.paths` and :py:meth:`bob.db.verification.utils.SQLiteDatabase.reverse` exist in this database interface.
Both are mainly used in the command line interface of the databases, using the ``./bin/bob_dbmanage.py`` command set up in the :py:class:`bob.db.base.driver.Interface`.


.. _annotations:

Annotations
-----------

Many biometric databases come with annotations for each original data file.
For face biometrics, these annotations usually contain hand-labeled locations of several feature points in the face (so-called *facial landmarks*).
Most commonly, at least the locations of the two eyes are annotated.
For a given file object, the :py:meth:`bob.db.verification.utils.Database.annotations` method will return a dictionary of those annotations, which might differ from database to database.
Commonly, for face image biometrics the returned annotations look somewhat like:

.. code-block:: py

   {
     'reye' : (re_y, re_x),
     'leye' : (le_y, le_x),
     ...
   }

where ``'reye'`` and ``'leye'`` refer to the right and left eye of the subject shown in the image, where left and right is **in the perspective of the subject**.
``(re_y, re_x)`` contain the ``y`` and ``x`` coordinate of the right eye, the left eye is alike.

Annotations are stored in different format.
Some databases like the :py:class:`bob.db.banca.Database` store annotations as part of the SQLite_ database, i.e., as :py:class:`bob.db.banca.Annotation`.

Other databases read annotations from files, where usually one annotation file exists for each original data file.
Since most of the file formats are consistent between databases, we here provide the function :py:func:`bob.db.verification.utils.read_annotation_file` that can read various types of annotation files.
Currently, it supports three ``annotation_type``\s:

* ``'eyecenter'``: Four coordinates of the eyes are stored in a single line in the file, in the order: ``re_x re_y le_x le_y``
* ``'named'``: Each file contains a list of named annotations, one annotation per line.
               The names of the annotation will be used as keys in the ``annotations`` dictionary (e.g., 'reye').
               The value of the annotation is either two floats (i.e., each line contains 3 items: ``name name_x name_y``), or a single string (e.g., ``gender female``).
* ``'idiap'``: A special format for the 22pt facial image point annotations from Idiap.
               Additionally to the 22 labeled landmarks, also the ``'reye'`` and ``'leye'`` landmarks will be estimated by averaging the coordinated of the according inner and outer eye corners.

If your database stores annotations in a different way, e.g. as in :py:class:`bob.db.multipie.Database`, you need to write your own annotation file IO.


.. _sqlite: http://docs.sqlalchemy.org/en/rel_0_9/dialects/sqlite.html
