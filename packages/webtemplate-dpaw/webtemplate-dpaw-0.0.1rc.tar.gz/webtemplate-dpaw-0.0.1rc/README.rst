========================
DPaW Django web template
========================

This project consists of a basic Django application containing HTML
templates that provide a starting point for web applications used by the
`Department of Parks and Wildlife`_. The base template consists of a mobile-friendly HTML5
template with a fixed top navbar containing the DPaW logo, plus static
assets. The project also contains functional examples of **login** and
**logged out** templates.

The base template is based upon `HTML5 Boilerplate`_ styled with `Bootstrap 3`_, with some
additional styling via the `Bootflat UI kit`_.

Installation and usage
======================

#. Install via pip: ``pip install webtemplate-dpaw``
#. Extend the included base template by placing the following at the head
   of your own templates: ``{% extends "webtemplate_dpaw/base.html" %}``
#. Place page content within the required blocks.

The main template blocks are as follows:

- ``navbar_links``
- ``page_content``
- ``page_footer``

.. _Department of Parks and Wildlife: http://www.dpaw.wa.gov.au
.. _HTML5 Boilerplate: https://html5boilerplate.com/
.. _Bootstrap 3: https://getbootstrap.com/
.. _Bootflat UI kit: https://bootflat.github.io/
