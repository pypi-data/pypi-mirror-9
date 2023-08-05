.. _django-guardian: https://github.com/lukaszb/django-guardian
.. _djangorestframework: http://www.django-rest-framework.org
.. _PO-Projects-client: https://github.com/sveetch/PO-Projects-client

PO Projects
===========

**PO Projects** is a PO file management factory.

Goal
****

Have a clean and ergonomic frontend to manage PO files for webapp projects and enable a REST API to deploy PO files into webapp projects.

Features
********

* View to create new project from a PO/POT file;
* View to create new project translation and edit them;
* View to export project translations as PO files;
* View to export an archive (zip/tarball) of all translations as PO files (and their compiled MO files) from a project;
* Manage fuzzy mode for translations;
* Form to import a catalog (PO) to update a catalog;
* Nice frontend with Foundation;
* Permission restriction;
* Restricted API access with `djangorestframework`_ to get PO files or global project 
  archive from external tools (like Optimus or a Django app from an external site) ?

Links
*****

* Read the documentation on `Read the docs <https://po-projects.readthedocs.org/>`_;
* Download his `PyPi package <http://pypi.python.org/pypi/PO-Projects>`_;
* Clone it on his `Github repository <https://github.com/sveetch/PO-Projects>`_;
