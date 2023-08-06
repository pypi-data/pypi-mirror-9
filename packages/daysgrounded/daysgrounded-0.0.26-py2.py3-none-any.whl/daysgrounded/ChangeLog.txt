0.0.26 2015-03-24 ::

	Changed setup_utils.py to update copyright in doc/conf.py.

	
0.0.25 2015-03-24 ::

	Added new function to setup_utils.py to create pythonhosted.org/doc.zip.
	Changed build.cmd to use it and remember the user to upload it to PyPI.
	Added twine to build.cmd.
	Added some comments with requirements for build.cmd.
	build.cmd internal reorganization.


0.0.23 2015-03-24 ::

	Reverted the Sphinx theme to 'classic' because otherwise it does not build the html documentation.
	Opened issue in RTD for them to update their system for the new name ('classic') of the old 'default' theme.

	
0.0.22 2015-03-24 ::

	Reverted the Sphinx theme to the old 'default' because ReadTheDocs isn't compatible yet.


0.0.21 2015-03-24 ::

	Updated doc/*.rst and daysgrounded/__init__.py to solve Sphinx problem.

	
0.0.20 2015-03-24 ::

	General code cleanup.
	Cleared __input__.py.
	Create appinfo.py with basic application information to be used by the application, setup.py and setup_utils.py.
	Compatibility testing with Py3 and necessary changes. All good now.
	Renamed build.bat to build.cmd.
	Improved build.cmd.
	Improved setup.py to be universal.
	Created setup_utils.py to aid build.cmd.
	Created utils.py.
	Added copyright to all source code.
	Updated MANIFEST.in.
	and many more.
	BUG: Sphinx docs stopped working.


0.0.19 2014-06-02 ::

    Added end user documentation to .gitignore.
    Added option PROJ_TYPE to build.bat to distinguish between modules and
    applications.
    Added pythonhosted.org files to MANIFEST.in.
    Changed __init__.py to use glob to select data files.
    Changed shared.py to use .decode('cp1252') when reading text files.
    Added options to py2exe config in setup.py.


0.0.18 2014-05-31 ::

    Cleanup several files.
    Fill some Docstrings.
    Translation to English.


0.0.17 2014-05-31 ::

    Added zip_safe to setup.py.
    Added PyPI documentation in dir pythonhosted.org (redirects to
    ReadTheDocs).
    Changed doc\index.rst to include README.rst.
    Updated build.bat.
    Corrected classifiers in __init__.py. Added ReadTheDocs doc.
    Added py_app_ver.py and prep_rst2pdf.py to help build.bat.
    Changed build.bat.
    Made changes recommended by Pylint.
    Changed packaging. Removed globalconf.py.


0.0.16 2014-05-24 ::

    Added sphinx and ReadTheDocs documentation.


0.0.15 2014-05-07 ::

    Forgot to update globalcfg.py. :)


0.0.14 2014-05-07 ::

    build.bat - added cxf and py2exe options.
    gui.py - corrected function error.
    created cxfreeze_setup.py.
    shared.py - corrected data_path for frozen dists.


0.0.13 2014-04-27 ::

    Changed __main__ to call cli or gui modules.
    Created open_create_datafile, auto_upd_datafile and version in shared module.
    Corrected usage.txt and usage_en.txt.


0.0.12 ::

    Forgot to update CHANGES.txt. :)


0.0.11 2014-04-21 ::

   Corrected MANIFEST.in, excluded venv from git.
   Started cfg of cx_freeze in setup.py but it isn't working yet.


0.0.10 2014-04-19 ::

    Finalize py2exe cfg, create globalcfg.py.


0.0.9 ::

    Correct path used for datafiles and path for modules.


0.0.8 ::

    Prepare setup.py for py2exe, changes to run in both Py2 and Py3.


0.0.7 ::

    Add README.rst.


0.0.6 ::

    Some cleanup.


0.0.5 ::

    Updated README.txt.


0.0.4 ::

    Updated README.txt, CHANGES.txt, __init__.py Trove classifiers, created AUTHORS.txt.


0.0.3 ::

    Packaging metadata files, fake rst files, start Py3 compat, separate code into sep files.
    Added more packaging and build/pub files to ease PyPI integration, added some fake rst.
    Created a build.bat to automate process, moved some banner and usage to text files.
    Separate code into 3+1 files, changed code to start testing Py3 compatibility.


0.0.2 ::

    Changed file struc to match PyPI packaging.


0.0.1 2014-04-18 ::

    Basic func, CLI and GUI (Tkinter).
