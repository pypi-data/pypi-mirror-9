
Changelog
---------

0.28 (2015-03-02)
~~~~~~~~~~~~~~~~~

- Check permissions in constrain types. Fixes #38.
  [msom]

0.27 (2015-02-05)
~~~~~~~~~~~~~~~~~

- Make sure "False" values are rendered and not omitted.
  [href]

- Adds a renderer for choices.
  [msom]

- Import/export translated titles of vocabularies instead of values. Closes #36.
  [msom]

- Use unicode for selectable fields. Fixes #29.
  [msom]

- Fix unicode error in import.
  [msom]

0.26 (2015-01-21)
~~~~~~~~~~~~~~~~~

- Fix metadata being out of sync. Fixes #34.
  [href]

0.25 (2015-01-19)
~~~~~~~~~~~~~~~~~

- Removed autofilter in XLSX files. This lead to problems with Excel.
  [href]

0.24 (2015-01-09)
~~~~~~~~~~~~~~~~~

- People types are now globally allowed - without hackery. Fixes #32.
  [href]

- Fixes unicode decode error when searching for organizations with non-ASCII
  characters in their title.
  [href]

0.23 (2014-12-18)
~~~~~~~~~~~~~~~~~

- Adds a custom catalog to manage generated indexes and metadata.

  WARNING!

  This change will leave the new catalog empty as we didn't find a way to
  setup the new catalog and reindex it at the upgrade stage. To fix this
  go into the ZMI->seantis_portal_catalog->Advanced->Clean & Rebuild!

  Closes #23.

  [href]

- Adds a mechanism to define "export variants". Export variants can adjust
  the dataset of any people type. It's used to add specific exports that build
  on the standard people export.
  [href]

- Adds the ability to exluce inactive people from the export.
  [href]

- Adds the ability to export by workflow state.
  [href]

- Exported XLSX files now automatically have the autofilter columns set.
  [href]

- Adds localized date/datetime rendering.
  [href]

0.22 (2014-12-12)
~~~~~~~~~~~~~~~~~

- Fixes error when deleting a person with at least one membership. See #27.
  [href]

0.21 (2014-10-24)
~~~~~~~~~~~~~~~~~

- Adds a renderer for decimal numbers.
  [href]

- Add a type css body class to the list view that contains the used type of
  the list (if any).
  [href]

- List fields can now be rendered using 'comma-separated' (default) or 'ul',
  the latter creates a ul in html.
  [href]

- Adds the ability to define render options on the list and detail view.
  [href]

- Adds support for Set Choices and List Textlines in the import.
  [href]

- Adds renderer for Bool field type.
  [href]

0.20 (2014-10-09)
~~~~~~~~~~~~~~~~~

- Adds a permanent work-around for the long standing issue #10.
  [href]

- Makes sure that the persons are only available on the list of people.
  [href]

0.19 (2014-06-24)
~~~~~~~~~~~~~~~~~

- Adds a navigation bar to the person detail view. Fixes #17.
  [href]

- The export now also works with richtext fields. Fixes #18.
  [href]

0.18 (2014-05-08)
~~~~~~~~~~~~~~~~~

- Adds the ability to do an unrestricted search on the people's list.
  [href]

0.17 (2014-03-31)
~~~~~~~~~~~~~~~~~

- Adds support for url, date and datetime fields to the import.
  [href]

- Adds the ability to export people to csv, xls, xlsx or json.
  [href]

- Adds 'is_active_person' property which if present and False hides the given
  person from the person list for anonymous users.
  [href]

- Removes start/end on memberships. This module will no longer deal with
  memberships over time. Where this is required, external modules like
  seantis.kantonsrat have to do this themselves.
  [href]

- Images on the people's list are rendered smaller and in the detail view they
  are rendered larger. Renderes now have custom options for this case.
  [href]

- Adds the ability to define custom titles on the person. Currently the custom
  title is only relevant for the detail view. To use add a custom_titles
  dictionary to the person object with the key being the field anme and the
  value being the title that should be used in the detail view.
  [href]

- Adds a new LinkList type which may be used returned by person attributes.
  The link list will be rendered using ul > li > a.
  [href]

- Organization memberships are now queried by interface in the ZODB, rather
  than by portal_type to support inheritance.

- Changes membership id/title to include the role as well as the name of
  the referenced person. Closes #13.
  [href]

- Fixes a crash when viewing a public directory with private organisations.
  Closes #12.
  [href]

- Adds a note field to the membership.
  [href]

- Adds the ability to define the years_range for plone.formwidget.datetime
  widgets used in the schemas. Fixes #11.
  [href]

0.16 (2013-12-31)
~~~~~~~~~~~~~~~~~

- Fixes a number of issues with zodb membership source.
  [href]

- Adds the ability to define custom membership functions on the detail view.
  [href]

- Adds the ability to define custom compound columns in other packages.
  [href]

- Adds missing profile dependencies for membership type.
  [href]

- Hides start/end on memberships, until it is properly implemented.
  [href]


0.15
~~~~

- Adds very basic json export people list.
  [href]

0.14
~~~~

- Adds the ability to import images through urls.
  [href]

- Organizations defined through memberships are now clickable in the list
  view. This is the default in the standard type.
  [href]

- Adds a standard profile which is more or less compatible with
  egov.contactdirectory. Fixes #6.
  [href]

- Rename responsive-table to responsive to be compatible with latest
  plonetheme.onegov release.
  [href]

- Adds custom event to signal changes in memberships.
  [href]

- Updates German translation.
  [href]

0.13
~~~~

- Adds the ability to install and upgrade profiles with custom people types.
  This can be done using the new seantis people controlpanel.
  [href]

- Removes import action from PHZ type.
  [href]

- Renames PHZ to PH Zug.
  [href]

- Ensures that imported strings are stripped of their whitespace in front and
  at the end.
  [href]

- Redirect to person list after succesful import.
  [href]

- Fixes required fields error not showing up on import.
  [href]

0.12
~~~~

- PHZ portrait should be optional.
  [href]

0.11
~~~~

- Supports new responsive-table helper in plonetheme.onegov.
  [href]

- Hides first-/lastname on PHZ detail view.
  [href]

- Adds link to a detailed portrait of the employee for the PHZ.
  [href]

0.10
~~~~

- Changes German translation of "Organisation Unit 2" for PHZ.
  [href]

0.9
~~~

- Adds membership rendering to detail view.
  [href]

0.8
~~~

- Adds collective.cover support as an extra
  [href]

- Memberships can now be defined dynamically through the MembershipSource
  adapter.
  [href]

0.7
~~~

- Hide label of images in the detail view.
  [href]

- Adds rendering support for these field types: Text, RichText, Lists.
  [href]

- Adds custom type for Pädagogische Hochschule Zug.
  [href]

- Adds ability to filter attributes returning lists in the table.
  [href]

- Adds ability to use custom titles on columns.
  [href]

0.6
~~~

- Adds detail view with configurable positioning through schema attributes.
  [href]

- Fixes not showing the selected filter after a refresh.
  [href]

0.5
~~~

- Supports supermodel security permissions in the people's list (giving the
  ability to hide certain fields in the table depending on the user).
  [href]

- Fixes filter.js being unable to filter for empty values.
  [href]

0.4
~~~

- Ensures that the title is updated when the object is modified.
  [href]

- The first letters are now taken from the sorted title.
  [href]

- The title attributes order is now independent of the field order.
  [href]

- Fixes a number of unicode issues.
  [href]

0.3
~~~

(skipped by accident)

0.2
~~~

- People are now sorted by unicode collation.
  [href]

- The people can be filtered by the first litter of the title.
  [href]

0.1
~~~

- Initial release.
  [href]
