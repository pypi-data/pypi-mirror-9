=============
EEA Relations
=============
.. image:: http://ci.eionet.europa.eu/job/eea.relations-www/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.relations-www/lastBuild
.. image:: http://ci.eionet.europa.eu/job/eea.relations-plone4/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.relations-plone4/lastBuild

Introduction
============
EEA Relations package redefines relations in Plone. Right now in Plone any
object can be in relation with any other object. EEA Relations lets you to
define possible relations between objects. EEA Relations also comes with a nice,
customizable faceted navigable popup for relations widget.

Once installed from "Add-ons", the package will add an utility
called "Possible relations" under "Control Panel".

.. contents::

Main features
=============

Main goal of EEA Relations is to be an alternative to the default Plone
related item widget.

EEA Relations features:

1. Define/restrict what kind of content types a certain content can relate to
2. Set restrictions on possible relations (e.g. relations can be made
   only with published content)
3. You can define easy to use faceted searches (using EEA Faceted navigation)
   on the relate items popup
4. Nice visual diagram showning all the relations and restrictions you defined
   (Control Panel -> Possible relations)

Install
=======

.. warning ::

  Never do this directly on production servers and always backup your data
  before installing Plone add-ons.

- Add eea.relations to your eggs and zcml section in your buildout
  and re-run buildout.
- To use eea.relations widget for all default Plone Content-Types you'll also
  need to add 'eea.relations.default' within zcml section like::

    eggs +=
      eea.relations

    zcml +=
      eea.relations
      eea.relations.default

- Install EEA Possible Relations within Site Setup > Add-ons

Uninstall
=========

.. warning ::

  This will not uninstall EEA Relations dependencies. See **Dependencies**
  section within this document and mannually uninstall them as described
  by their own documentation before uninstalling EEA Relations.

- Backup your data.
- Go to ZMI > PloneSite and remove portal_relations object.
- Uninstall EEA Possible Relations within Site Setup > Add-ons
- Remove eea.relations from your eggs and zcml section within your buildout and
  re-run buildout
- Restart Zope


Getting started
===============

Once you install the package from "Control Panel Add-ons", the package will add
an utility called "Possible relations" under "Control Panel" from where you can start
define the relations, the constraints between contents etc.


Dependencies
============
`EEA Relations`_ has the following dependencies:

* graphviz

  ::

    $ yum install graphviz
    $ apt-get install graphviz

* pydot
* eea.facetednavigation
* collective.js.jqueryui normally installed by eea.facetednavigation. Make sure
  that you are using the proper version for your plone installation and that 
  the following effects are enabled::

      1. transfer
      2. pulsate

API Doc
=======

http://apidoc.eea.europa.eu/eea.relations-module.html


Source code
===========

Latest source code (Plone 4 compatible):
- `Plone Collective on Github <https://github.com/collective/eea.relations>`_
- `EEA on Github <https://github.com/eea/eea.relations>`_


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Relations (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Funding
=======

EEA_ - European Environment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
.. _`plone.recipe.zope2instance`: http://pypi.python.org/pypi/plone.recipe.zope2instance
.. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout
