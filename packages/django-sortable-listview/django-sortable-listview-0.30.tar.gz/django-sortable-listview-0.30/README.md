django-sortable-listview
========================
An extension of django's ListView that provides sorting.

Features:
- Works with django's built in pagination.
- Contains templates & css for pagination and sort buttons (or just use the context_data and build your own).
- Adds an arrow to show the sort direction on the active sort.
- Knows what the next sort is (i.e. if you're already sorted by title in one direction, clicking on the title button/link again will sort it in the other direction).
- Lets you specify default sort for your list (defaults to -id) and for each of the sortable fields.
- Modifies the queryset, so your database does your sorting.

Install
=======
Using pip::

    pip install django-sortable-listview

If you want to use the provided temaplates and CSS add ``'sortable_listview'`` to your INSTALLED_APPS in your django settings.

To see how to include the css and templates in your application, look at the example project. The css is just standard bootstrap.


Example Project
===============
![Screenshot of example project](/example_project/screenshot.png)

To run the example project. First make sure django and django-sortable-listview are on your python path. For example, from inside a virtualenv::

    pip install django
    pip install django-sortable-listview

Then from your cloned folder::

    cd example_project
    python manage.py runserver

You should be able to see the example project at localhost:8000. A database is provided with some sample content. The username and password is admin/admin

Development and Tests
=====================

To run the tests::

    python setup.py test
