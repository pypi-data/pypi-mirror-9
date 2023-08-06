Changelog
=========

0.4.1 (2015-04-03)
------------------

- 115down: added range support for argument ``sub_num`` (#14)
- 115down: added size display for file and task entries

0.4.0 (2015-03-23)
------------------

- Added persistent session (cookies) feature
- Added search API
- Added CLI commands: 115down and 115up
- Fixed #10

0.3.1 (2015-02-03)
------------------

- Fixed broken release 0.3.0 due to a missing dependency

0.3.0 (2015-02-03)
------------------

- Used external package "homura" to replace downloader utility
- Merge #8: added add_task_url  API 

0.2.4 (2014-10-09)
------------------

- Fixed #5: add isatty() so progress refreshes less frequently on non-tty
- Fixed parse_src_js_var

0.2.3 (2014-09-23)
------------------

- Fixed #2: ``show_progress`` argument
- Added resume download feature

0.2.2 (2014-09-20)
------------------

- Added system dependencies to documentation

0.2.1 (2014-09-20)
------------------

- Fixed ``Task.status_human`` error

0.2.0 (2014-09-20)
------------------

- Added download feature to the API and ``download`` method to ``u115.File``
- Added elaborate exceptions
- Added ``auto_logout`` optional argument to ``u115.API.__init__``
- Updated Task status info


0.1.1 (2014-09-11)
------------------

- Fixed broken sdist release of v0.1.0.


0.1.0 (2014-09-11)
------------------

- Initial release.

