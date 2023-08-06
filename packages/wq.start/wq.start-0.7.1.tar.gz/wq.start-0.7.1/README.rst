Project template for wq framework
=================================

This is the recommended Django project template for projects utilizing
the `wq framework <http://wq.io/>`__, with
`wq.app <http://wq.io/wq.app>`__ for the front end and
`wq.db <http://wq.io/wq.db>`__ as the backend component.

Usage
~~~~~

.. code:: sh

    pip3 install wq
    wq-start <projectname> [directory]

Rationale
~~~~~~~~~

This template is also useful as an example of how to build a web app
with `RequireJS <http://requirejs.org>`__ and a `Django REST
Framework <http://www.django-rest-framework.org>`__ backend. It differs
from the default Django project template in a few key ways:

-  A default Apache2 WSGI configuration is included in ``conf/``
-  All static files are kept in the ``app/`` folder, with the idea that
   they will be built with a RequireJS-powered `build
   process <http://wq.io/docs/build>`__. This clean separation between
   the front end and backend components makes it easier to wrap the
   front end in `PhoneGap <http://phonegap.com>`__ for release on app
   stores.
-  Because of this separation, the root of the Django project is in
   ``db/`` rather than at the top level of the project. ``db/`` is
   included on the Python path in the Apache config (and implicitly when
   running ``./manage.py``).
-  Mustache templates are kept at the top level, because they are
   `shared between the client and the
   server <http://wq.io/docs/templates>`__.

