"""
.. image:: images/thread.png
   :align: right
   :target: http://dev.thread.com/

===================
django-force-logout
===================

-----------------------------------------------------------------
Framework to be able to forcibly log users out of Django projects
-----------------------------------------------------------------

This project provides the ability to log specific users out of your
`Django <http://www.djangoproject.com/>`_ project.

Whilst you can easily log all users out by clearing your session table or
similar blunt technique, due to the difficulty in enumerating specific user's
actual session entries from a user ID, logging-out troublemakers etc. is not
really feasible "out of the box".

You can iterate over all possible sessions and match them against a user, but
with a heavy-traffic site with long-lasting sessions this can be prohibitively
expensive.


Installation
------------

#. Add ``django_force_logout.middleware.ForceLogoutMiddleware`` to
   ``MIDDLEWARE_CLASSES``.

#. Configure ``FORCE_LOGOUT_CALLBACK`` in your settings to point to a method which,
   given a ``User`` instance, will return a nullable timestamp for that user.
   This would typically be stored on custom ``User``, profile or some other
   field depending on your setup.

   For example::

       def force_logout_callback(user):
           return user.some_profile_model.force_logout

       FORCE_LOGOUT_CALLBACK = 'path.to.force_logout_callback'

   Alternatively, you can just specify a lambda directly::

       FORCE_LOGOUT_CALLBACK = lambda x: x.some_profile_model.force_logout

.. important::

   This callback is executed on every request by a logged-in user. Therefore,
   it is advisable that you have some sort of caching preventing additional
   database queries. Remember to ensure that you clear the cached value when
   wish to log a user out, otherwise you will have to wait for the cache entry
   to expire before the user will actually be logged out.

You are not restricted to returning a field from a SQL database (`Redis
<http://redis.io/>`_ may suit your needs better and avoid the caching
requirement), but you must return a nullable timestamp.


Usage
-----

To forcibly log that user out, simply set your timestamp field to the current
time. For example::

   user.some_profile_model.force_logout = datetime.datetime.utcnow()
   user.some_profile_model.save()

That's it. The middleware will then log this user out on their next request.


Configuration
-------------

``FORCE_LOGOUT_CALLBACK``
~~~~~~~~~~~~~~~~~~~~~~~~~

A method which, when passed a User instance, will return a nullable timestamp for
that user. See **Installation** for more details.


Thanks
------

This project was inspired by a code snippet by
`Clement Nodet <http://clementnodet.com/>_`.


Links
-----

Homepage/documentation:
  https://django-force-logout.readthedocs.org/

View/download code
  https://github.com/thread/django-force-logout

File a bug
  https://github.com/thread/django-force-logout/issues

----

.. figure:: images/thread.png
   :align: center
   :target: http://dev.thread.com/

   `See more open source projects from Thread.com <http://dev.thread.com/>`_
"""
