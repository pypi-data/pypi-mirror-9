ddh_django_utils
================

Provides a number of useful utilities for Django projects,
particularly within the context of DDH projects.

Pagination
----------

``ddh_utils.utils`` provides the ``create_pagination`` function to
generate Paginator and Page objects from the supplied parameters,
handling any problems with the supplied page number. This just avoids
repeating the example view code from the Django documentation.

The ``ddh_utils_tags`` template tag library provides the
``display_pagination`` inclusion tag, which outputs the navigation for
a set of results, based on the supplied page::

  {% load ddh_utils_tags %}
  {% display_pagination querydict page %}

This includes the template ``includes/pagination.html``.


Haystack
--------

``ddh_utils.views`` provides ``SearchView`` and ``FacetedSearchView``
classes that have better pagination than those in Haystack's own views
(making use of the ``create_pagination`` function), and also add the
request's GET parameters to the context (under the variable name
``querydict``) for use in pagination and facetting.

``ddh_util_tags`` provides simple tags for creating URLs by adding and
removing facets::

  {% load ddh_utils_tags %}
  <a href="{% add_facet_link querydict name value %}">Add</a>

  <a href="{% remove_facet_link querydict "name:value" %}">Remove</a>
