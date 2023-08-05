.. image:: https://badge.fury.io/py/aldryn_faq.svg
    :target: http://badge.fury.io/py/aldryn_faq
.. image:: https://travis-ci.org/aldryn/aldryn-faq.svg
    :target: https://travis-ci.org/aldryn/aldryn-faq
.. image:: https://coveralls.io/repos/aldryn/aldryn-faq/badge.svg
    :target: https://coveralls.io/r/aldryn/aldryn-faq

==========
Aldryn FAQ
==========

Description
~~~~~~~~~~~

Simple faq application. It allows you to:

- write a questions and answers in categories


Installation & Usage
--------------------

Aldryn Platform Users
~~~~~~~~~~~~~~~~~~~~~

1) Choose a site you want to install the add-on to from the dashboard.

2) Go to **Apps** -> **Install App**

3) Click **Install** next to **FAQ** app.

4) Redeploy the site.


Manual Installation
~~~~~~~~~~~~~~~~~~~

1) Run ``pip install aldryn-faq``.

2) Add below apps to ``INSTALLED_APPS``: ::

       INSTALLED_APPS = [
           …
           'aldryn_faq',
           'djangocms_text_ckeditor',
           'adminsortable',
           'sortedm2m',
           'parler',
           …
       ]


3) Run migrations: `python manage.py migrate aldryn_faq`.

   NOTE: aldryn_faq supports both South and Django 1.7 migrations. However, if
   your project uses a version of South older than 1.0.2, you may need to add
   the following to your settings: ::

       MIGRATIONS_MODULES = [
           …
           'aldryn_faq': 'aldryn_faq.south_migrations',
           …
       ]

4) (Re-)Start your application server.


Listing
~~~~~~~

You can add question/answer in the admin interface now. Search for the label
``Aldryn_Faq``.

In order to display them, create a CMS page and install the app there (choose
``FAQ`` from the ``Advanced Settings -> Application`` dropdown).

Now redeploy/restart the site again.

The above CMS site has become a faq list view.
