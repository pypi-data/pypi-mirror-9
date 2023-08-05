==============
pydl Changelog
==============

0.3.0 (2015-02-20)
------------------

* Use `astropy_helpers`_/v0.4.3, package-template_/v0.4.1.
* Avoided (but did not fix) a bug in chunks.py that occurs when operating on
  a list of coordinates of length 1.
* Fixed a typo in bspline.py, added documentation.
* Simplify documentation files.
* sdss_flagname now accepts more types of numeric input.
* Added credits file.

0.2.3 (2014-07-22)
------------------

* Added photoop/window.
* Added stub photoop/sdssio/sdss_calib, updated sdss_score.
* Added photoop/photoobj/unwrap_objid.
* Merged pull request #4, fixing some Python3 issues.

0.2.2 (2014-05-07)
------------------

* Updated to latest package-template_ version.
* Added ability to `write multiple ndarray to yanny files`_.
* Fixed struct_print test for older Numpy versions.
* Fixed failing yanny file test.
* Improve test infrastructure, including Travis builds.
* Allow comment characters inside quoted strings in yanny files.

0.2.1 (2013-10-06)
------------------

* Added sdss_sweep_circle.
* Added first few photoop functions.
* Clean up some import statements.

0.2.0 (2013-04-22)
------------------

* Using the astropy package-template_ to bring pydl into astropy-compatible form.
* Some but not all tests are re-implemented.

0.1.1 (2013-03-06)
------------------

* Creating a tag representing the state immediately after creation of the
  `git repository`_.

0.1 (2010-11-10)
----------------

* Initial tag (made in svn, not visible in git).  Visible at
  http://www.sdss3.org/svn/repo/pydl/tags/0.1 .

.. _`astropy_helpers`: https://github.com/astropy/astropy-helpers
.. _package-template: https://github.com/astropy/package-template
.. _`git repository`: https://github.com/weaverba137/pydl
.. _`write multiple ndarray to yanny files`: https://github.com/weaverba137/pydl/pull/3
