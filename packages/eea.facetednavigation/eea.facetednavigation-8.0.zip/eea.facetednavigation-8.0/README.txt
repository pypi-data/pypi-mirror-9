======================
EEA Faceted Navigation
======================
.. image:: http://ci.eionet.europa.eu/job/eea.facetednavigation-www/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.facetednavigation-www/lastBuild
.. image:: http://ci.eionet.europa.eu/job/eea.facetednavigation-plone4/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.facetednavigation-plone4/lastBuild

The EEA Faceted Navigation **(FacetedNav)** gives you a
**very powerful interface to improve search within large collections of items.**
No programming skills are required by the website manager to configure the
faceted navigation interface, `configuration is done TTW <http://svn.eionet.europa.eu/projects/Zope/attachment/wiki/FacetedNavigationScreenshots/screenshot7.png>`_.
It lets you gradually select and explore different facets (metadata/properties)
of the site content and narrow down you search quickly and dynamically.

On the contrary, plone collections are static, in a way that the site admin
decides the search criteria and the end user is not able to further sort or
filter the presented results.

**FacetedNav is fully customizable**, site admin may decide that some criteria
(facets) must have fixed values while other may be presented as filter options
to the web visitor.

**FacetedNav may very well replace the standard collection content type**, since
it covers same functionality and it adds a lot more features.

**FacetedNav can also be used as an advanced search for your site**.


.. contents::


Main features
=============
It comes with plenty of configuration options and features like:

1. Easy customizable GUI via drag-n-drop, no restart needed.
2. Facets can be set to fixed default values and hidden.
3. Facets can be placed in standard search or extended search panels,
   to not intimidate novice users and have cleaner interface
4. Facets can be displayed via several widgets like select, radio,
   text input, tag cloud, date range and more
5. Expandable and collapsible widgets with many values
6. Automatically counts number of content items beside each facet value
7. Possibility to show or hide the options with zero results
   (show only the facets which return content)
8. Ability to create your custom content types definition to be used as a
   combination of interface and portal type, presented in a single widget.
9. Export of search result in RSS.
10. Pleasant user interface based on Ajax JQuery, implemented with "deep linking",
    so bookmarking a faceted query works, browser history supported.
11. Export / Import of faceted settings as XML. Useful to replicate same facets
    navigation on another site.
12. Search engine friendly, disabling javascript acts as a normal collection
    batch list.
13. Synchronization of settings across multiple languages, I18N support.
14. High performance by caching faceted catalog queries via `distributed memory
    object caching system: memcached <http://www.danga.com/memcached/>`_
15. Smart facets hiding - hide facets criteria if there is only one page of
    results (This can be explicitly disabled/enabled from version 4.6.
    It is also disabled by default for new faceted navigable pages starting
    with version 5.2)
16. Ability to transform faceted navigable items in search forms by
    putting them in the 'search mode' (starting with version 4.6)
17. Ability to enable/disable Plone portlets left and right columns within
    faceted navigable contexts (starting with version 4.1. Both disabled by
    default for new faceted navigable pages starting with version 5.2)

Faceted settings
================
(*New in version 4.1*)

**Faceted settings** is a menu that appears once you enable Faceted navigation
within your context next to the **Actions** menu and it allows you to perform
the following actions:

Enable/disable left portlets
----------------------------
This allows you to gain more space for faceted navigation pages by disabling
Plone portlets left column.

Default: **disabled** (*starting with version 5.2*)

Enable/disable right portlets
-----------------------------
This allows you to gain more space for faceted navigation pages by disabling
Plone portlets right column.

Default: **disabled** (*starting with version 5.2*)

Enable/disable smart facets hiding
----------------------------------
Hide facets criteria if there is only one page of results.

Default: **disabled** (*starting with version 5.2*)

Extra
=====
You can extend faceted navigation functionality by installing the following
addons:

* Customized vocabularies

  - Products.ATVocabularyManager

* Multilingual/translation solution

  - Products.LinguaPlone

* Cache (memcache)

  - plone.memoize
  - eea.cache

* Relations

  - eea.relations

* Faceted extensions

  - eea.faceted.tool
  - eea.faceted.inheritance

* Faceted themes

  - eea.faceted.blue


Screenshots
===========
See more `FacetedNavigationScreenshots <http://svn.eionet.europa.eu/projects/Zope/wiki/FacetedNavigationScreenshots>`_.


Live demo
=========
Here some live production demos:

- `EEA Publications <http://www.eea.europa.eu/publications>`_
- `EEA Multimedia <http://www.eea.europa.eu/multimedia/all-videos>`_
- `University of Minnesota - Explore Books <http://upress.umn.edu/explore>`_


Buildout installation
=====================

- `Plone 2 and 3 <https://github.com/collective/eea.facetednavigation/tree/master/buildouts/plone3>`_
- `Plone 4+ <https://github.com/collective/eea.facetednavigation/tree/master/buildouts/plone4>`_


Source code
===========

- `Plone 2 and 3 on github <https://github.com/collective/eea.facetednavigation/tree/plone3>`_
- `Plone 4+ on github <https://github.com/collective/eea.facetednavigation>`_


Eggs repository
===============

- http://eggrepo.eea.europa.eu/simple


Plone versions
==============
It has been developed and tested for Plone 2, 3 and 4. See buildouts section above.


Known bugs and ongoing development
==================================
Bugs and new features are entered on our Trac server at EEA.

- `open bugs / tasks <http://taskman.eionet.europa.eu/projects/zope/issues?utf8=%E2%9C%93&set_filter=1&f%5B%5D=category_id&op%5Bcategory_id%5D=%3D&v%5Bcategory_id%5D%5B%5D=120&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id%5D%5B%5D=1&v%5Btracker_id%5D%5B%5D=4&f%5B%5D=status_id&op%5Bstatus_id%5D=o&f%5B%5D=&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=tracker&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=done_ratio&c%5B%5D=fixed_version&c%5B%5D=project&c%5B%5D=category&c%5B%5D=parent&c%5B%5D=author&c%5B%5D=updated_on&c%5B%5D=start_date&c%5B%5D=due_date&c%5B%5D=estimated_hours&c%5B%5D=created_on&c%5B%5D=closed_on&c%5B%5D=relations&c%5B%5D=cf_4&group_by=>`_
- `complete list of bugs / features including fixed and open <http://taskman.eionet.europa.eu/projects/zope/issues?utf8=%E2%9C%93&set_filter=1&f%5B%5D=category_id&op%5Bcategory_id%5D=%3D&v%5Bcategory_id%5D%5B%5D=120&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id%5D%5B%5D=2&v%5Btracker_id%5D%5B%5D=1&v%5Btracker_id%5D%5B%5D=4&f%5B%5D=&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=tracker&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=done_ratio&c%5B%5D=fixed_version&c%5B%5D=project&c%5B%5D=category&c%5B%5D=parent&c%5B%5D=author&c%5B%5D=updated_on&c%5B%5D=start_date&c%5B%5D=due_date&c%5B%5D=estimated_hours&c%5B%5D=created_on&c%5B%5D=closed_on&c%5B%5D=relations&c%5B%5D=cf_4&group_by=>`_
- `open bugs / tasks on collective <https://github.com/eea/eea.facetednavigation/issues?sort=updated&state=open>`_

Copyright and license
=====================

The EEA Faceted Navigation (the Original Code) is free software; you can
redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc., 59
Temple Place, Suite 330, Boston, MA 02111-1307 USA.

The Initial Owner of the Original Code is European Environment Agency (EEA).
Portions created by Eau de Web are Copyright (C) 2009 by
European Environment Agency. All Rights Reserved.


Other resources
===============

- `Faceted navigation pattern <http://www.welie.com/patterns/showPattern.php?patternID=faceted-navigation>`_
- `Faceted classification <http://www.webdesignpractices.com/navigation/facets.html>`_
- `Flamenco faceted navigation <http://flamenco.berkeley.edu/demos.html>`_ made at University of Berkeley
- `A simpler Faceted plone 3 product made 2008 <http://plone.org/products/faceted-navigation>`_
- `Folder navigation (GSoC) <http://plone.org/support/forums/core#nabble-td3165375>`_ A new product Folder Navigation in early development]
- `Exhibit <http://www.simile-widgets.org/exhibit/>`_ Client based faceted navigation via javascript
