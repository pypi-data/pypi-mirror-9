.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Thu Oct 30 19:25:28 CET 2014

.. _verification_databases:

=================================================
 Databases that Implement the Database Interface
=================================================

There are quite a number of databases that implement the :py:class:`bob.db.verification.utils.Database` interface.
Here, we provide a (possibly incomplete) list of databases, sorted by name.

Face Recognition Databases without ZT-norm
------------------------------------------

The following face recognition databases implement the :py:class:`bob.db.verification.utils.Database` interface:

* :ref:`AR Face <bob.db.arface>`
* :ref:`The AT&T database of Faces <bob.db.atnt>`
* :ref:`BioSecure <bob.db.biosecure>`
* :ref:`CAS-PEAL <bob.db.caspeal>`
* :ref:`Face Recognition Grand Challenge ver2.0 <bob.db.frgc>`
* :ref:`The Good, The Bad & The Ugly <bob.db.gbu>`
* :ref:`Labeled Faces in the Wild <bob.db.lfw>`
* :ref:`SCface <bob.db.scface>`
* :ref:`XM2VTS <bob.db.xm2vts>`
* :ref:`YouTube faces (video) <bob.db.youtube>`

Face Recognition Databases with ZT-norm
---------------------------------------

The following face recognition databases implement the :py:class:`bob.db.verification.utils.ZTDatabase` interface:

* :ref:`BANCA <bob.db.banca>`
* :ref:`MOBIO (image and video) <bob.db.mobio>`
* :ref:`Multi-PIE <bob.db.multipie>`


Speaker Recognition Databases
-----------------------------

The following speaker recognition databases implement the :py:class:`bob.db.verification.utils.ZTDatabase` interface:

* :ref:`MOBIO <bob.db.mobio>`
* :ref:`NIST SRE 2012 Database <bob.db.nist_sre12>`
* :ref:`Voxforge <bob.db.voxforge>`

Generic Databases
-----------------

The following generic biometric recognition database implement the :py:class:`bob.db.verification.utils.ZTDatabase` interface:

* :ref:`FileList Database <bob.db.verification.filelist>`

