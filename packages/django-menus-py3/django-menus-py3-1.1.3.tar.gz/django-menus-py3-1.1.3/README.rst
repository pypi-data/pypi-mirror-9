django-menus
============

django-menus is an app that provides some useful template helpers for
rendering and handling menus within django projects.

To use in in your django project, it needs to be installed:

::

    $ pip install django-menus

And ``"menus"`` needs to be in your ``settings.INSTALLED_APPS``.

menu\_item
----------

An inclusion template tag that will create a single instance of a menu
item, which will only be rendered if the logged in user can access the
referenced view. Secondly, the currently active view will have a CSS
class of ``active`` in it's menu item.

::

    {% load menu_item %}

    {% menu_item "/foo/" "Foo" %}
    {% menu_item "/bar/" "Bar" %}
    {% menu_item "http://example.com" "Baz" %}

If we were viewing ``/foo/``, this renders to:

::

    <a class="active" href="/foo/">Foo</a>
    <a href="/bar/">Bar</a>
    <a href="http://example.com">Baz</a>

Using the standard template. If you want, you can override the
``menus/item.html`` template to change the display format.

You may also pass in a string like ``"url:foo_name"`` to the first
argument. This will do a ``reverse('foo_name')`` call (with no args or
kwargs) to find a matching url.

If the menu item title is ``'home'`` (case insensitive), or the url path
is ``'/'``, then an exact match will be required to mark it as active,
otherwise a prefix match is done. This means that if you had a menu item
as above, and were viewing the url ``/foo/bar/``, then the first
menu\_item would be marked as active.

tree\_menu
----------

An extension to
`django-mptt <https://github.com/django-mptt/django-mptt/>`_, this is a
template that you can use to have a dynamic tree menu, where selecting
items with children expands them, and selecting a leaf node follows the
link. To use it, you'll need to have mptt installed into your project as
well as this package.

You use it like:

::

    {% load mptt_tags %}

    {% block tree_menu %}
      {% full_tree_for_model app_label.ModelName as menu %}
      {% include "menu/tree-menu.html" %}
    {% endblock %}

If you want it to dynamically hide/show nested data, then you will want
to have:

::

        <script src="{{ STATIC_URL }}menus/js/tree-menu.js"></script>
        <link rel="stylesheet" href="{{ STATIC_URL }}menus/style/tree-menu.css" 
              type="text/css" media="screen" title="no title" charset="utf-8">

Somewhere in your page.

This part is currently in use in one small part of a project, and may
change if I start to use it more. This README is a little light on
because I haven't touched this code in a long, long time.

Changes
-------


1.1.2 - Python 3 support

1.1.1 - Pass through args and kwargs to the test function if it accepts them.

1.0.9 - Allow for adding classes, and buttons as menu items.

1.0.8 - Allow for absolute urls, ie, pointing to another server. We never
try to validate these for permission to view, it is assumed the user can.

1.0.7 - Change how version number is stored. Include a new li-item.html
template, and refactor how the template is found. Check func\_code
exists before accessing it. Refactor some of the handling of paths.
Better handle quoting issues.

1.0.6 - Documentation fix only.

1.0.5 - Actually install all of the static media/templates.

1.0.4 - Don't fail on install if README.md missing.

1.0.3 - Repackaged to include README.rst [Thanks to John Bazik
jsb@cs.brown.edu]
