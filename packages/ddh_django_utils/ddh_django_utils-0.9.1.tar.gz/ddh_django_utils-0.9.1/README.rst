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
a set of results, based on the supplied page.

Haystack
--------

``ddh_utils.views`` provides ``SearchView`` and ``FacetedSearchView``
classes that have better pagination than those in Haystack's own
views, and also add the request's GET parameters to the context for
use in pagination and facetting.

``ddh_util_tags`` provides simple tags for creating URLs by adding and
removing facets.
