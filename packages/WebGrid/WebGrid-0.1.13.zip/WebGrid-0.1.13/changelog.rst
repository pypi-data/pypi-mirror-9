Changelog
---------

0.1.13 released 2015-02-12
==========================

 - attempt to use column label for subtotaling if no SA expression is provided
 - allow callers to specify default arguments to filters

0.1.12 released 2014-11-18
==========================

 - allow filters to set additional html attributes on their table rows

0.1.11 released 2014-10-09
==========================

 - fixed setup to include only webgrid in install, without the test apps

0.1.10 released 2014-10-02
==========================

 - bug fix: hide_controls_box grid attribute used in rendering

0.1.9 released 2014-09-22
=========================

 - bug fix: corrected default_op processing on TextFilter

0.1.8 released 2014-09-22
=========================

 - enable default_op processing for all filter types

0.1.7 released 2014-09-18
=========================

 - BC break: replaced MultiSelect widget with multipleSelect plugin.
   Related JS and CSS must be included (available in webgrid static)
 - included missing images referenced by webgrid CSS

0.1.6 released 2014-08-22
=========================

 - updated filter tests to work with SA0.9
 - refactoring related to subtotaling feature
 - adjustments for SQLAlchemy 0.9+ (we now support 0.8+)
 - workaround for dateutils parsing bug
 - testing fixes
 - completed dev requirements list
 - fixed nose plugin bug, must not assume pathname case consistency (Windows)
 - added BlazeWeb adapter
 - xls_as_response now an adapter method, called by XLS renderer
 - render_template now an optional adapter method, falls back to Jinja2 call

0.1.5 released 2014-05-20
=========================

 - fix nose plugin setup to avoid warning message
 - fix javascript bug related to sorting & newer jQuery libraries
 - fix SA expression test to avoid boolean ambiguity
 - avoid accidental unicode to text conversion in filters

0.1.4 released 2014-05-18
=========================

  - fix string/unicode handling to avoid coercion of unicode to ascii

0.1.3 released 2014-05-18
=========================

  - adjust the way the Flask blueprint is created and registered
  - adjust route on blueprint so it has /static/... prefix for URL

0.1.0 - 0.1.2 released 2014-05-17
=================================

  - initial release
  - fix packaging issues (0.1.1)
  - adjust init so xlwt not required if not used
