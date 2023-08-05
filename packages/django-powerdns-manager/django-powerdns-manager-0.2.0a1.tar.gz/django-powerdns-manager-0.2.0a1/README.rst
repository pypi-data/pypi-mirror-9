django-powerdns-manager
=======================

| **Author**: `George Notaras <http://www.g-loaded.eu/>`_
| **Development Web Site**: `django-powerdns-manager project <http://www.codetrax.org/projects/django-powerdns-manager>`_
| **Source Code Repository**: `django-powerdns-manager source code <https://bitbucket.org/gnotaras/django-powerdns-manager>`_
| **Documentation**: `django-powerdns-manager documentation <http://packages.python.org/django-powerdns-manager>`_
| **Downloads**: `django-powerdns-manager releases <http://pypi.python.org/pypi/django-powerdns-manager>`_


django-powerdns-manager is a web based PowerDNS_ administration panel.

.. _PowerDNS: http://www.powerdns.com

Licensed under the *Apache License version 2.0*. More licensing information
exists in the license_ section.

.. note::

   *django-powerdns-manager*, since version *0.2.0a1*, supports database migrations
   using the internal migrations mechanism of Django *1.7.3*. It is recommended
   to use the following commands instead of manually altering the database tables::
   
       manage.py migrate
       manage.py migrate --database=powerdns
   
   *django-powerdns-manager* should be considered **work in progress**. The
   *0.2.Xa1* releases should be considered experimental. If you use it in
   production, please make sure you test new releases before upgrading your
   production systems.
   
   This software comes without any warranty of any kind. You are on your own.


Features
========

- Supports Django 1.7.X and PowerDNS 3.4.1.
- Web based administration interface based on the *admin* Django app.
- Easy management of all records of a zone from a single web page.
- Support for multiple users.
- Database schema is DNSSEC enabled.
- Automatic zone-rectify support, including support for empty non-terminals,
  using native python code.
- The application can be configured to support a user-defined subset of the
  resource records supported by PowerDNS and customize the order in which they
  appear in the administration panel.
- Zone cloning (experimental).
- Zone transfers between users.
- Zone file import through web form.
- Zone file export.
- Basic zone templates.
- Command-line interfaces to import and export zones in bulk.
- Support for secure updating of dynamic IP addresses in A and AAAA records.
- Supports using a dedicated database to store the tables needed by PowerDNS.
  This database may use a different backend than the main database of the
  Django project.
- Contains demo project for quick start and experimentation.


Quickstart Guide
================

The distribution package of *django-powerdns-manager* contains an example
project that can help you check out the features of the software and also
quickly experiment with the source code.

Although, the example project has already been configured for you, there are
still some required steps before you are able to run it using the development
server. These steps are discussed in detail in the `Quickstart Guide`_.

.. _`Quickstart Guide`: http://pythonhosted.org/django-powerdns-manager/quickstart.html


Development
===========

The source code of this project is available at the following official repositories.

Main repository (*mercurial*)::

    https://bitbucket.org/gnotaras/django-powerdns-manager

Mirror repository (*git*)::

    https://github.com/gnotaras/django-powerdns-manager

Pull requests are welcome. Please note that it may take a long time before pull
requests are reviewed.


Donations
=========

This software is released as free-software and provided to you at no cost. However,
a significant amount of time and effort has gone into developing this software
and writing this documentation. So, the production of this software has not
been free from cost. It is highly recommended that, if you use this software
*in production*, you should consider making a donation_.

.. _donation: http://bit.ly/19kIb70


Documentation
=============

Apart from the `django-powerdns-manager Online Documentation`_, more information about the
installation, configuration and usage of this application may be available
at the project's wiki_.

.. _`django-powerdns-manager Online Documentation`: http://packages.python.org/django-powerdns-manager
.. _wiki: http://www.codetrax.org/projects/django-powerdns-manager/wiki


Bugs and feature requests
=========================

In case you run into any problems while using this application or think that
a new feature should be implemented, it is highly recommended you submit_ a new
report about it at the project's `issue tracker`_.

Using the *issue tracker* is the recommended way to notify the authors about
bugs or make feature requests. Also, before submitting a new report, please
make sure you have read the `new issue guidelines`_.

.. _submit: http://www.codetrax.org/projects/django-powerdns-manager/issues/new
.. _`issue tracker`: http://www.codetrax.org/projects/django-powerdns-manager/issues
.. _`new issue guidelines`: http://www.codetrax.org/NewIssueGuidelines


Support
=======

CodeTRAX does not provide support for django-powerdns-manager.

You can still get community support at the `Community Support Forums`_:

.. _`Community Support Forums`: http://www.codetrax.org/projects/django-powerdns-manager/boards


License
=======

Copyright 2012-2015 George Notaras <gnot@g-loaded.eu>

Licensed under the *Apache License, Version 2.0* (the "*License*");
you may not use this file except in compliance with the License.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

A copy of the License exists in the product distribution; the *LICENSE* file.
For copyright and other important notes regarding this release please read
the *NOTICE* file.

