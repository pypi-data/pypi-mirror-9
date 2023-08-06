v1.3 (2015-03-04)
===================

1. Add `site.time` variable, the generated time.
2. Improve encoding
3. Add `--update-them` when generate to improve generation speed
4. Fix #36, add attach directory to put attachments.
5. Fix #33, only show color logging message on Linux/MacOS


v1.2.4 (2014-12-23)
===================

* Fix #31 encode/decode problems
* Fix image overflow in simple themes


v1.2.3 (2014-09-15)
===================

* Fix #28 add '--ignore-root' option in generate mode
* Fix CustomCatalogGenerator arguments number error


v1.2.2 (2014-08-22)
===================

* Fix #26 Universal newline in open file
* Fix #27 Fix extension is not md


v1.2.1 (2014-07-13)
===================

* Fix #25 unicode problem when path contains Chinese


v1.2 (2014-07-06)
===================

* Support Python2.6
* Fix: init site with specific path


v1.1 (2014-07-04)
===================

* Template support multiple level catalog in Index
* Sort index structure in lower-case, alphabetical order
* Fix error on nav in wiki page
* Fix unicode in emptytree
* Fix #16 set literals not support in Python < 2.7


v1.0.3 (2014-06-10)
===================

* Fix #14 Chinese filename problem


v1.0.2 (2014-06-10)
===================

* Fix #13 system path separator problem on Windows


v1.0.1 (2014-06-10)
===================

* Fix serious problem using rsync


v1.0.0 (2014-05-28)
===================

* Support Chinese directory and file name
* Simplify the default configuration file
* Add introduction page when init site
* Fix some bugs

v0.5.0 (2014-04-30)
===================

* fabric: rsync output to remote server
* fabric: remote update simiki
* get fabfile when init site
* fix: do not overwrite _config.yml while init site again

v0.4.1 (2014-04-28)
===================

* change font-family and code highlight class to hlcode
* fix bug: not use the right code highlight css file in base.html
* default theme change pygments style from autumn to tango
* remove repetitive index setting in config template


v0.4.0 (2014-04-20)
===================

* Add custom index feature


v0.3.1 (2014-04-13)
===================

* Fixed "socket.error: [Errno 48] Address already in use" problem in preview


v0.3.0 (2014-04-06)
===================

* Move all static files to static/ dir in theme
* Fixed #4 Reinstall theme every generate action
* Fixed #1 add generate option to empty output directory first


v0.2.2 (2014-03-29)
===================

* Fixed #5 css path error when there is no wiki
* Fixed #6 ignore hidden dirs and files when use os.walk or os.listdir
* support table of contents(toc) both generator and default theme

v0.2.1 (2014-03-23)
===================

* Change catalog order from date to title letter


v0.2.0 (2014-03-19)
===================

* Simplify _config.yml and add debug mode
* Put themes under wiki directory
* Add root url function
* Add statistic in default theme
* Change default theme style
* Use log instead of print


v0.1.0 (2013-12-8)
==================

* Initial release.
