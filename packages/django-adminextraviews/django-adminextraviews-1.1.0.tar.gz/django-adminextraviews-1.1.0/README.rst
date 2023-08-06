django-adminextraviews
======================

.. image:: https://travis-ci.org/fusionbox/django-adminextraviews.png?branch=master
    :target: https://travis-ci.org/fusionbox/django-adminextraviews

Mixin for adding class-based views to ModelAdmin.


Why
---

Class-based views are really useful, but it's difficult to add them to the
admin center. This makes it easy to add class-based views to the Django admin.


Installation
------------

Install django-adminextraviews::

    pip install django-adminextraviews


Usage
-----

Add the ``ExtraViewsMixin`` to your ``ModelAdmin`` and define the
``extra_views`` attribute.

.. code:: python

    from adminextraviews import ExtraViewsMixin

    class MyModelAdmin(ExtraViewsMixin, admin.ModelAdmin):
        extra_views = [
            ('login_as_user', r'(?P<pk>\d+)/login/', LoginAsUserView),
        ]

Now you can use it like a normal view, you can reverse it.

.. code:: python

    >>> urlresolvers.reverse('admin:myapp_mymodel_login_as_user', kwargs={'pk': 12})
    '/admin/myapp/mymodel/12/login/'

If your view is a subclass of ``ModelFormMixin`` (like ``CreateView``,
``UpdateView``), ``ExtraViewsMixin`` will wrap the form class with the admin
center widgets. It will also set the ``model`` attribute if it's not set.
