.. include:: ../../CHANGES.rst

.. # Note: CHANGES.rst is the current changelog, the older entries are in here.

3.22 (2011-05-05)
-----------------

- Allow specifying a tag on the command line when using lasttaglog or
  lasttagdiff, to show the log or diff since that tag instead of the
  latest.  Useful when you are on a branch and the last tag was from
  trunk.
  [maurits]


3.21 (2011-04-20)
-----------------

- Added lasttaglog command that list the log since the last tag.
  [maurits]

- Fix Mercurial (hg) support. As spreaded_internal should be set
  to False (as it happens with git)
  [erico_andrei]

- Accept a twiggle (or whatever '~' is called) when searching for
  headers in a changelog; seen in some packages (at least
  zopeskel.dexterity).
  [maurits]


3.20 (2011-01-25)
-----------------

- Also allowing CHANGES.rst and CHANGES.markdown in addition to
  CHANGES.txt.


3.19 (2011-01-24)
-----------------

- No longer refuse to register and upload a package on pypi if it is
  not there yet, forcing people to do this manually the first time.
  Instead, we ask the question and simply have 'No' as the default
  answer.  If you specify an answer, we require exactly typing 'yes'
  or 'no'.  The idea is still to avoid making it too easy to release
  an internal package on pypi by accident.  [maurits]


3.18 (2010-12-08)
-----------------

- Added ``--non-interactive--`` option to the ``svn diff`` command used in
  lasttagdiff.  This makes it usable in cronjobs and post-commit hooks.
  Fixes https://bugs.launchpad.net/zest.releaser/+bug/687530


3.17 (2010-11-17)
-----------------

- When the package that is being released neither has a setup.py nor a
  setup.cfg, use No as default answer for creating a checkout of the
  tag.
  [maurits]


3.16 (2010-11-15)
-----------------

- For (pypi) output, also show the first few lines instead of only the
  last few.
  [maurits]

- See if pypirc or setup.cfg has a [zest.releaser] section with option
  release = yes/no.  During the release stage, this influences the
  default answer when asked if you want to make a checkout of the tag.
  The default when not set, is 'yes'.  You may want to set this to
  'no' if most of the time you only make releaser of internal packages
  for customers and only need the tag.
  [maurits]

- Specify bazaar (bzr) tag numbers using the 'tag' revision specifier
  (like 'tag:0.1') instead of only the tag number (0.1) to add
  compatibility with earlier bzr versions (tested with 2.0.2).
  [maurits]


3.15 (2010-09-10)
-----------------

- Read pypi config not only from the .pypirc file, but also from the
  setup.cfg file of the package.  Patch by Erico Andrei.
  [maurits]


3.14 (2010-08-26)
-----------------

- experimental support for git svn tagging, fully test-covered
  [chaoflow]

- fail if no tag was created, not test-covered
  [chaoflow]

- svn available_tags method: intercept 'Repository moved' note in svn
  info and stop processing then.
  [maurits]


3.13 (2010-08-16)
-----------------

- Fixed check that tested whether a package was already available on
  pypi, as the pypi implementation changed slightly.  We now just
  check for a 404 status.  Patch by Wolfgang Schnerring.
  [maurits]


3.12 (2010-07-22)
-----------------

- Added extra entry point for the release step: ``after_checkout``.
  When this is run, the middle entry point has been handled, the tag
  has been made, a checkout of that tag has been made and we are now
  in that checkout directory.  Idea: Jan-Wijbrand Kolman.
  [maurits]

- Fix: in the zest.releaser.releaser.after entry point data, pass the
  'tagdir' value (if a checkout has been made).  Patch by Wolfgang
  Schnerring, thanks!
  [maurits]

- Fixed tests to also pass with slightly newer git.
  [maurits]


3.11 (2010-06-25)
-----------------

- Small tweak: allowing zc.rst2's "rst2 html" in addition to docutils' own
  "rst2html".


3.10 (2010-06-15)
-----------------

- Fix : when running 'release' with python2.6 against a private egg server,
  the distutils 'register' command would run against PyPI
  while 'upload' command would run against private server.
  (-r option needs to be stated twice)
  [gotcha]


3.9 (2010-06-11)
----------------

- Again at the end of a fullrelease report the location of the
  directory containing the checkout of the tag, if it has been made.
  [maurits]


3.8 (2010-05-28)
----------------

- Also allowing ``CHANGES`` in addition to ``HISTORY.txt`` and ``CHANGES.txt``
  as a history filename.  Keeps several Django packages happy.


3.7 (2010-05-07)
----------------

- Added support for bzr.  Fixes
  https://bugs.launchpad.net/zest.releaser/+bug/490816  [menesis]


3.6 (2010-04-13)
----------------

- A ``version='1.0',`` string inside the ``setup()`` call no longer has
  non-pep8 spaces around the ``=``.  Fixes
  https://bugs.launchpad.net/zest.releaser/+bug/562122  [reinout]

- Got rid of ugly setup.py hack with UltraMagicString that was meant
  to avoid encoding errors when registering this package at pypi but
  which was not working for python2.4 (at least with collective.dist).
  Only ascii is allowed in the long_description if you want to avoid
  problems at one point or another.
  [maurits]


3.5 (2010-02-26)
----------------

- Treat CHANGES.txt and HISTORY.txt the same: the first that is found
  in a directory is chosen for changing, instead of first looking
  everywhere for a HISTORY.txt and then for a CHANGES.txt.
  [maurits]


3.4 (2010-02-02)
----------------

- Always build zip files if using python2.4 [do3cc]

- bugfix: added 'spreaded_internal' property to BaseVersionControl
  objects, so filefind() does not exclude a directory just because
  there is no '.git' folder in it. It still excludes directory where
  there is no '.svn' folder in SVN repositories. [vincent]


3.3 (2009-12-29)
----------------

- Fixed test failures when run on a computer with a new style pypi
  config.  We now always use an old style config when running the
  tests.
  [maurits]

- Fixed the release command for hg 1.1 (e.g. Ubuntu 9.04).
  [maurits]


3.2 (2009-12-22)
----------------

- Replaced commands.getoutput() with a system() function grabbed from buildout
  on suggestion by Adam Groszer.  Goal: make zest.releaser work also on
  windows.

- Improved entry point documentation.

- Added launchpad bugtracker at https://bugs.launchpad.net/zest.releaser (and
  pointing at that in the documentation).


3.1 (2009-11-27)
----------------

- Added documentation for entry points.  [reinout]


3.0 (2009-11-27)
----------------

- Added support for extension by means of entry points.  There is no
  documentation that advertises it yet as I want to treat it as experimental
  till I've used it a few times.  [reinout]


2.12 (2009-11-26)
-----------------

- Fixed mercurial sdist creation.  [reinout]

- A missing history file does not result anymore in a keyerror in prerelease.
  [reinout]

- Added lots of test output normalization so that errors aren't hidden by
  the large number of ``...`` in the doctests.  [reinout]


2.11 (2009-11-25)
-----------------

- Added /tag besides /tags for subversion [gotcha]

- Fixed tests failures. [gotcha]


2.10 (2009-10-22)
-----------------

- Added support for git.  [reinout]

- Lots of internal refactoring and small fixes.  [reinout]

- Started tests.  zest.releaser went from 0 to 94% coverage.  [reinout]


2.9.3 (2009-09-22)
------------------

- Uploading to multiple package indexes should now work in python2.6
  (though ironically it now does not work for me on python2.4, but that
  has nothing to do with zest.releaser.)  Added documentation for this.
  [maurits]

- Make sure the next version suggestion for 1.0rc6 is 1.0rc7.
  [maurits]

- In subversion, first try to get the package from the setup.py before
  falling back to the svn info, just like for mercurial.  This fixes
  the problem that e.g. Products.feedfeeder was not recognized as
  being on pypi as the svn directory name was feedfeeder.
  [maurits]


2.9.2 (2009-09-17)
------------------

- Umlauts in a changelog don't break the logger anymore when using python2.6.2
  when the umlauts turn up in the diff.  This is due to a 2.6.2 regression
  bug, see http://bugs.python.org/issue5170.  Should be fixed in 2.6.3 when it
  comes out.  [reinout]

- (Release 2.9 and 2.9.1 are unreleased because of a setuptools bug with,
  sigh, non-ascii characters which made a dirty setup.py hack necessary).
  [reinout]


2.8 (2009-08-27)
----------------

- Fixed the release command when used in a french environment.
  In French "svn info" returns 'URL :', not 'URL:'.
  [vincentfretin]


2.7 (2009-07-08)
----------------

- Before asking setup.py for its version or name, first run egg_info,
  as that may get rid of some warnings that otherwise end up in the
  extracted version or name, like UserWarnings.
  [maurits]


2.6 (2009-05-25)
----------------

- Small change: the questions don't print a newline anymore after the question
  (and before the user pressed enter).  This makes it clearer if enter has
  been pressed yet.  Suggestion by jkolman.  [reinout]


2.5 (2009-05-20)
----------------

- Revert to previous behaviour: when a package has not been released
  yet on pypi, decline to register it: the first time should be
  deliberate and manual, to avoid accidentally uploading client
  packages to pypi.
  [maurits]


2.4 (2009-05-15)
----------------

- Factored release.py out into a new pypi.py, solving a few possible
  problems with missing or misconfigured .pypirc files.  [maurits]


2.3 (2009-05-11)
----------------

- Fixed release script when the .pypirc file does not contain a
  distutils section or that section does not contain a index-servers
  option.  [maurits]


2.2 (2009-05-11)
----------------

- postrelease: suggestion for next version after 1.1.19 is not
  1.1.110, but 1.1.20.  [maurits]

- Make it work with collective.dist (mregister/mupload) [WouterVH]
  see http://plone.org/documentation/tutorial/how-to-upload-your-package-to-plone.org/installing-collective.dist


2.1 (2009-04-09)
----------------

- Fix lasttagdiff command to work with Mercurial by truncating the '+'
  character from the revision id, since that only indicates uncommitted
  changes exist.

- Make sure we find package/name/HISTORY.txt before we find
  docs/HISTORY.txt.  [maurits]

- Fixed checking for self.internal_filename: we would incorrectly
  check ('.', 's', 'v', 'n') instead of '.svn'.  [maurits]


2.0 (2009-04-01)
----------------

- Added tag_url method to get lasttagdiff (and zest.stabilizer)
  working again.  [maurits]

- Merged kteague-multi-vcs branch with, woohoo, mercurial support!  [reinout]

- Mercurial support by Kevin Teague.  [kteague]

- ``postrelease`` put a space in the new version number in
  ``setup.py`` (between version number and ``dev``). Removed this
  space as it is not necessary (in best case). [icemac]


1.13 (2009-03-17)
-----------------

- Also looking for ``CHANGES`` in addition to ``HISTORY.txt`` and
  ``CHANGES.txt`` as some packages use that convention.  [reinout]

- Added ``lasttagdiff`` command that shows the diff between the last release
  and the currently committed trunk.  Handy for checking whether the changelog
  is up to date.  [reinout]


1.12 (2009-03-17)
-----------------

- When doing a fullrelease and if the release step made a checkout of the tag
  into an temp directory, that temp directory is again printed after
  fullrelease finishes. Otherwise you've got to do a lot of scrolling.
  [reinout]


1.11 (2009-03-04)
-----------------

- When the found history file contains no version headings, look for a
  second history file: more than once I have the standard
  docs/HISTORY.txt that paster creates and I just add a pointer there
  to the real package/name/HISTORY.txt.  [maurits]


1.10 (2009-02-25)
-----------------

- A ``    version = '1.0',`` in setup.py is now also rewritten
  correctly.  Previously just a ``version = '1.0'`` would be injected,
  so without indentation and comma.  [reinout]

- Ask before checking out the tag. Sometimes the checkout is huge and
  you know you don't want it. You don't get asked for a pypi upload,
  though if you don't check out the tag.  [reinout]


1.9 (2009-02-24)
----------------

- 'release' now also makes a tag checkout in a temporary directory.
  [Reinout]

- Made 'longtest' work on Linux as there the command is 'rst2html' and
  apparently on the Mac it is 'rst2html.py'.  [maurits]


1.8 (2009-02-23)
----------------

- Added 'longtest' command that renders a setup.py's long description
  and opens it in a web browser.  [reinout]


1.7 (2009-02-16)
----------------

- Supporting alternative history version header format: 'version - date'.
  [reinout]


1.6 (2009-02-14)
----------------

- Patch by Michael Howitz: sys.executable is used instead of a string that
  doesn't work on every system.  [reinout]


1.5 (2009-02-11)
----------------

- Changed y/n into Y/n, so defaulting to 'yes'.  [reinout]

- Improved the documentation.  [reinout]

- When a yes/no question is asked, do not treat 'no' as the default
  but explicitly ask for an input -- it was too easy to press enter
  and wrongly expect 'yes' as default.  [maurits]


1.4 (2008-10-23)
----------------

- Fixed missing import of utils.  [maurits]


1.3 (2008-10-23)
----------------

- Moved stabilize script to zest.stabilizer so that zest.releaser is just for
  releasing individual packages. Nice, tidy, reusable.  [reinout]

- Allowing '-v' option on all commands: it gives you debug-level logging.
  [reinout]


1.2 (2008-10-16)
----------------

- We now prefer the version from setup.py over any version.txt file
  found.  When getting or changing the version we get/change the
  setup.py version when it differs from the found version.txt version.
  [maurits]


1.1 (2008-10-15)
----------------

- Cleaned out zest-specific stuff. Cleaned up 'release'. [reinout]


1.0 (2008-10-15)
----------------

- Stabilize looks up the most recent tag of our development packages and uses
  gp.svndevelop to allow svn checkouts as development eggs. [reinout]

- Do not look for version.txt in directories that are not handled by
  subversion.  Use case: Products.feedfeeder, which has a buildout.cfg
  and so can have a parts directory with lots of version.txt files...
  [maurits]


0.9 (2008-10-02)
----------------

- release: offer to register and upload the egg to the cheese shop.
  After that you still have the option to upload to our own tgz
  server.  [maurits]

- postrelease: for the suggestion of a new version simply try add 1 to
  the last character in the version; the previous logic failed for
  example for '1.0b3'.  [maurits]

- prerelease: ask user to enter next version (give him a suggestion).
  Handy when you want to change '1.0b3 dev' into '1.0'.  [maurits]

- Started 'stabilize'. [reinout]


0.8 (2008-09-26)
----------------

- fullrelease: change back to the original directory after each
  pre/actual/post release step.  [maurits]

- release: switch back to original directory when ready to fix 'commit
  to tag' error.  [maurits]

- prerelease: quit when no version is found.  [maurits]

- Reverted sleeping fix from 0.7 as it did not work.  [maurits]


0.7 (2008-09-26)
----------------

- fullrelease: hopefully fix a 'commit on tag' bug by sleeping three
  seconds before doing the post release.  [maurits]


0.6 (2008-09-26)
----------------

- Added fullrelease script that does a prerelease, actual release and
  post release in one go.  [maurits]


0.5 (2008-09-26)
----------------

- Factored part of prerelease.check_version() out into
  utils.cleanup_version().  We now use that while setting the version
  in the history during postrelease.  [maurits]

- Add newline at the end of the generated version.txt.  [maurits]


0.4 (2008-09-26)
----------------

- Made the logging userfriendly.


0.3 (2008-09-26)
----------------

- Postrelease: Better injection of history. Various other robustness fixes.


0.2 (2008-09-26)
----------------

- postrelease: added suggestion for new version (a plain enter is enough to
  accept it). [reinout]

- prerelease: ask before changing version + solidified regex for heading
  detection. [reinout]

- prerelease: detect non-development versions better and change them.
  [maurits]

- prerelease: made the commit message read: 'Preparing release xxx'.
  [maurits]

- postrelease: made the new version something like '1.0 dev'.
  [maurits]

- postrelease: we now add some lines to the history now.  [maurits]

- prerelease: try changing the version to a non-development version,
  stripping off something like '(...)'.  [maurits]

- release: Refactored so release.py has the 'main' function required
  by setup.py.  [maurits]


0.1 (2008-09-24)
----------------

- Got a basic version of the prerelease script working (version check, history
  file updating, committing). [reinout]

- Started by copying the guidelines script. [reinout]
