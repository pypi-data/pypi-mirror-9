Seantis People
==============

A list of people, optionally organized by organizations and positions.

Municiaplities for which we contribute to `OneGov`_ often require a public list
of contacts. For the customers and us this package needs to scratch the
following itches:

- The directory must not force a set of fields on the user. Each customer
  should have the option to create its own set of fields. At the same time
  there should be at least one reasonable standard.

- Some fields should only be visible with certain permissions.

- It must be possible to put people into various organizations and show the
  membership of those organizations.

Warning! There is currently an issue (https://github.com/seantis/seantis.people/issues/41)
which results in that publishing and expiration date of people are not working.

Design
------

This is how it is done:

- We give the user the possibility to define a list of people. Each list
  consists of a number of dexterity objects with IPerson behavior. Within
  one list only one dexterity type is allowed.

- This list of people is the same for all lists of people - it's just that
  the contained people must all have the same type.

- Through the schema of the dexterity type we define the fields, their
  required read and write permissions, the fields shown in the list, the order
  of those fields, the fields available for filtering in the list, and the
  fields shown in the detail view.

- These dexterity types may be installed by any package or they may be included
  in seantis.people, available through separate profiles. (It's technically
  even possible to create them through the web, but we don't recommend this
  approach for various reasons.)

- Any folderish type can be an organization. For people to be members of an
  organization, a membership type can be added to such a folderish type. This
  membership type links to the actual person object.

- We identify the organization solely by url and title. This makes
  organizations very flexible. For example, with `seantis.cover.people`_
  we implemented organizations using collective.cover.

Installation & Usage
--------------------

To see what it's all about install seantis.people using buildout (we assume
you know how to do that) and activate the add-on using the controlpanel.

Note that we don't provide any styling for seantis.people. We build on
`plonetheme.onegov`_ and try to keep our HTML as simple as possible.

Having installed seantis.people be sure to open the seantis.people controlpanel
found on the Plone controlpanel (under "Add-on Configuration").

There you can select the Person type you would like to use. Currently this
will without a doubt be "Seantis People - Standard". To use it, click
"Install":

.. image:: https://raw.githubusercontent.com/seantis/seantis.people/master/screenshots/readme-01-controlpanel.png
   :alt: Controlpanel Screenshot

Having done that, go to the front-page or to wherever you want to place a list
of people and add them:

.. image:: https://raw.githubusercontent.com/seantis/seantis.people/master/screenshots/readme-02-add-list.png
   :alt: Add List of People Screenshot

On the people's list you can now add people. You can only add people of the
same type together on the same list:

.. image:: https://raw.githubusercontent.com/seantis/seantis.people/master/screenshots/readme-03-add-contact.png
   :alt: Add Contact Screenshot

Going back to the list you will notice that this person does not belong to
an organization. To add a person to an organization you can simply create
a folder with the name of the organization as its title:

.. image:: https://raw.githubusercontent.com/seantis/seantis.people/master/screenshots/readme-04-add-folder.png
   :alt: Add Folder Screenshot

Finally, add the person to the organization by creating a membership and
referencing the person:

.. image:: https://raw.githubusercontent.com/seantis/seantis.people/master/screenshots/readme-05-add-membership.png
   :alt: Add Folder Screenshot

Your list of people should now look something like this:

.. image:: https://raw.githubusercontent.com/seantis/seantis.people/master/screenshots/readme-06-result.png
   :alt: Add Folder Screenshot

Status
------

Seantis.people is used in production already. Though it's one of our newer
modules so it hasn't been as battle tested as some of our other offerings.

Once we feel perfectly confident about this you'll see a 1.0 release.

Alternatives
------------

Close to our requirements (but no cigar):
https://github.com/collective/collective.contact.core

Requirements
------------

-  Python 2.7
-  Plone 4.3+
-  Linux / Posix (Windows may or may not work)

Build Status
------------

.. image:: https://travis-ci.org/seantis/seantis.people.png
  :target: https://travis-ci.org/seantis/seantis.people
  :alt: Build Status

Coverage
--------

.. image:: https://coveralls.io/repos/seantis/seantis.people/badge.png?branch=master
  :target: https://coveralls.io/r/seantis/seantis.people?branch=master
  :alt: Project Coverage

Latest PyPI Release
-------------------
.. image:: https://pypip.in/v/seantis.people/badge.png
  :target: https://crate.io/packages/seantis.people
  :alt: Latest PyPI Release

License
-------
seantis.people is released under GPL v2


.. -> external links

.. _OneGov: http://onegov.ch/
.. _seantis.cover.people: https://github.com/seantis/seantis.cover.people
.. _plonetheme.onegov: https://github.com/onegov/plonetheme.onegov
