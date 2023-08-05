
Changes
-------

0.31.5
~~~~~~

Enhanced method of source name creation to be more inline with common standards.
Note: This requires the nameparser package.


0.31.4
~~~~~~

Added support for using CharisSIL fonts when creating PDFs with Pisa.


0.31.3
~~~~~~

- Enhanced usability of helper functions.
- Cache db capabilities in collkey function.


0.31.2
~~~~~~

- Now that usage patterns have formed, a new (final) API of the pg_collkey support has been settled on.


0.31.1
~~~~~~

- refactored pg_collkey support to keep logic checking for availability of the feature within clld.


0.31
~~~~

- support for collation via pg_collkey (if installed for the database)


0.30
~~~~

- refactored adapter management


0.29
~~~~

- more convenient config directives


0.28
~~~~

- added AudioCol to support display of sentences with audio files in index.


0.27
~~~~

- new helper functions supporting easy creation of license links.
- enhanced DataTable to allow more flexibility in naming of models.



0.26
~~~~

New helper function, refactored imeji support.


0.25
~~~~

Multiple small fixes, see https://github.com/clld/clld/commits/develop for details.


0.24.1
~~~~~~

bugfix release: a test data file was not committed, leading to a failing test suite.


0.24
~~~~

- support for deferred column loading
- more flexible jsondump function
- support for external file storage with imeji


0.23.1
~~~~~~

bugfix release: fixed broken backwards compatibility of DownloadWidget.


0.23
~~~~

- better support for composite default_order in DataTable
- enhanced css
- bugfixes


0.22
~~~~

- icontains function does now provide support for prefix and suffix searches.
- initial basic support for non-local files is implemented.


0.21.1
~~~~~~

Bugfixes:
- corrected Identifier unique constraint
- fixed problem with backward compatibility of common models split.


0.21
~~~~

- more helpers, template functions and config defaults.


0.20
~~~~

- better support for LLOD/datahub.io integration
- new map option base_layer
- refactored clld.db.models.common


0.19.2
~~~~~~

- workaround for compatibility with python 3.4
- upgraded DataTables to 1.10.3


0.19.1
~~~~~~

- bugfix release.


0.19
~~~~

- value tables for parameter combinations are now sortable.


0.18
~~~~

- bug fixes
- work on docs, including pep257 conformance


0.17
~~~~

- enhanced support for zenodo and datahub.io integration


0.16
~~~~

- added support for filter legends which synch map and datatable.


0.15.5
~~~~~~

- better support in DataTable for resources which are not db models.


0.15.4
~~~~~~

- upgraded to DataTables 1.10.2.
- added map option to control height of map element.
- removed deployment-specific requirements from app scaffold.


0.15.3
~~~~~~

bugfix release.


0.15.2
~~~~~~

Minor new feature:

- support unfreeze, i.e. database initialization from csv dump.


0.15.1
~~~~~~

Minor new features:

- new db.util function as_int,
- added hook to GeoJson adapter to allow features with non-Point geometries,
- more flexible CLLD.Map API.


0.15
~~~~

- support for full-database dumps to csv via dataset.freeze.


0.14
~~~~

- upgraded leaflet, jquery, bootstrap and DataTables.
- support reading dictionaries in standard format (SFM).


0.13.3
~~~~~~

New feature: new block in default app layout to allow for addition of brand links in navbar.


0.13.2
~~~~~~

New feature: Support for JSON table schemas [1] for resource indexes.

[1] http://dataprotocols.org/json-table-schema/

Bugfix: Fixed #26 where JSON data column was not serialized correctly in csv export.


0.13.1
~~~~~~

bugfixing and cleanup


0.13
~~~~

clld does now run on python 2.7 and 3.4 from the same code base.


0.12.5
~~~~~~

Minor release to get the source code up to pep8 compliance.


0.12.4
~~~~~~

Minor feature

* bootstrap-slider.js upgraded

Bugfixes

* fixed bug where volume would appear twice in linearization of bibtex record;
* fixed bug where selecting more than 4 parameters for combination would result in HTTP 500 rather than a warning.



0.12.3
~~~~~~

Minor feature

* allow zoom option for maps to be used as default zoom when used in combination with bounds.


0.12.2
~~~~~~

Bugfix release

* linearization of sources better aligned with unified stylesheet.


0.12.1
~~~~~~

Bugfix release:

* fixes a bug when EnumSymbols were compared with None.


0.12
~~~~

* Added GeoJson adapter for the case where a parameter may have multiple valuesets for the same language.
* Integrate results from searches on Internet Archive into source views.


0.11
~~~~

* Support serialization/deserialization of objects as rows in csv files.


0.10
~~~~

* Better support for RDF dumps.
* Support for deselcting languages in map view.


0.9
~~~

* Support for icon selection.
* Map configuration via URL parameters.
* Upgraded JqTree lib.


0.8.1
~~~~~

Enhanced test utilities.
Better docs.


0.8
~~~

Added support for common tasks in Alembic migration scripts.
Fixed a bug in the RDF serialization of parameters with domain.


0.7
~~~

Added support for range-operators when filtering DataTables on numeric columns.
Fixed a couple of bugs in the serializations of the RDF data.


0.6
~~~

New API to access registered maps using a method of the request object.


0.5.1
~~~~~

Bugfix release, fixing a critical js bug, where a reserved word was used as property name.


0.5
~~~

- New hook which allows using custom leaflet map markers with clld maps.
- Fixed bug where wrong order of inclusion of translation dirs would make customized
  translations impossible.


0.4
~~~

Resources have a new representation as JSON encoded documents suitable for
indexing with Solr.

