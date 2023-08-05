========================
DPaW Django web template
========================

.. image:: https://pypip.in/version/webtemplate-dpaw/badge.svg
    :target: https://pypi.python.org/pypi/webtemplate-dpaw/
    :alt: Latest Version

.. image:: https://pypip.in/status/webtemplate-dpaw/badge.svg
    :target: https://pypi.python.org/pypi/webtemplate-dpaw/
    :alt: Development Status

.. image:: https://pypip.in/py_versions/webtemplate-dpaw/badge.svg
    :target: https://pypi.python.org/pypi/webtemplate-dpaw/
    :alt: Supported Python versions

.. image:: https://pypip.in/license/webtemplate-dpaw/badge.svg
    :target: https://pypi.python.org/pypi/webtemplate-dpaw/
    :alt: License

.. image:: https://pypip.in/download/webtemplate-dpaw/badge.svg
    :target: https://pypi.python.org/pypi/webtemplate-dpaw/
    :alt: Downloads

.. image:: https://drone.io/bitbucket.org/dpaw/webtemplate-dpaw/status.png
    :target: https://drone.io/bitbucket.org/dpaw/webtemplate-dpaw
    :alt: Builds

This project consists of a basic Django application containing HTML
templates that provide a starting point for web applications used by the
`Department of Parks and Wildlife`_. The base template consists of a mobile-friendly
HTML5 template with a fixed top navbar containing the DPaW logo, plus static
assets. The project also contains functional examples of **login** and
**logged out** templates.

The base template is based upon `HTML5 Boilerplate`_ styled with `Bootstrap 3`_,
with some additional styling via the `Bootflat UI kit`_.

Installation
============

#. Install via pip: ``pip install webtemplate-dpaw``.
#. Add ``'webtemplate_dpaw'`` to ``INSTALLED_APPS``.
#. Ensure that the ``staticfiles`` application is included and configured
   correctly.
#. Ensure that you have defined the following named URLs: ``login`` and
   ``logout`` (this requirement can be overriden, see below).
#. Extend the included base template by placing the following at the head
   of your own templates: ``{% extends "webtemplate_dpaw/base.html" %}``
#. Place page content within the required blocks (see below).

Included CSS and JavaScript
===========================

The base template currently includes the following CSS and JavaScript assets
(served via `JSDelivr`_):

#. Modernizr 2.8.3 (HTML5 polyfills)
#. Bootstrap 3.3.2 (CSS & JS)
#. Bootflat UI kit 2.0.4 (Bootstrap style extension)
#. jQuery 2.1.3 (DOM traversal, etc.)

Additional styling can be included using the ``extra_style`` or ``extra_js``
blocks, like so::

    {% load static from staticfiles %}

    {% block extra_style %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'css/custom.css' %}">
    {% endblock %}

You can also overide the ``base_style`` and ``base_js`` blocks completely to
use different CSS or JS libraries. Note that you will also need to replace the
``top_navbar`` block contents if you replace the base Bootstrap CSS & JS.

Template blocks
===============

The base template contains a number of block tags that are used to render the
content of your project. The main template content blocks are as follows:

- ``navbar_links`` - used to define navigation links in the top navbar.
- ``navbar_auth`` - used to display either a **Login** or **Logout** link.
- ``page_content`` - used to contain the page's main content.
- ``page_footer`` - used to contain a page footer area.

Note that the ``navbar_auth`` block contains ``{% url %}`` templatetags with
named URLs called *login* and *logout*. If this is not required or
inappropriate for your project, simply override the ``navbar_auth`` block.

In addition, a number of context variables are defined:

- ``page_title`` - used to populate the page **<title>** tags.
- ``site_title`` - used to populate the projects's title in the top navbar.

Context variables should be passed to templates in every view.

Examples
========

To populate the main content area with a narrow left sidebar and content
area that fills the whole screen width and will collapse elegantly on
narrow or mobile displays::

    {% block page_content %}
    <div class="container-fluid">
        <div class="row">
            <div class="col-xs-12 col-sm-4 col-md-3 col-lg-2" id="sidebar">
                {% include "sidebar.html" %}
            </div>
            <div class="col-xs-12 col-sm-8 col-md-9 col-lg-10">
                {% block page_content_inner %}{% endblock %}
            </div>
        </div>
    </div>
    {% endblock %}

To include a right-aligned copyright line in the footer area::

    {% block page_footer %}
    <div class="container-fluid">
        <div class="row">
            <div class="col-xs-12">
                <hr>
                <p class="pull-right">&copy; 2015 Department of Parks and Wildlife</p>
            </div>
        </div>
    </div>
    {% endblock %}

To include no navigation links in the top navbar and to prevent the automatic
"navbar button" from showing on narrow displays, overide the ``navbar_button``
and ``navbar_links`` blocks to be empty::

    {% block navbar_button %}{% endblock %}
    {% block navbar_links %}{% endblock %}

If you don't want to use the Bootflat UI kit (and reduce your page load), you
can override the relevant blocks to be empty, like so::

    {% block bootflat_style %}{% endblock %}
    {% block bootflat_js %}{% endblock %}

.. _Department of Parks and Wildlife: http://www.dpaw.wa.gov.au
.. _HTML5 Boilerplate: https://html5boilerplate.com/
.. _Bootstrap 3: http://getbootstrap.com/
.. _Bootflat UI kit: https://bootflat.github.io/
.. _JSDelivr: http://www.jsdelivr.com/
