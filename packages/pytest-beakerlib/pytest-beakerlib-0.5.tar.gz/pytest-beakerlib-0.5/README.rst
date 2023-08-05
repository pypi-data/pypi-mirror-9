A pytest plugin that reports test results to the BeakerLib framework.

* pytest: http://pytest.org/latest/
* BeakerLib: https://fedorahosted.org/beakerlib/

Once installed, this plugin can be activated via the --with-beakerlib ooption.
This requires a BeakerLib session (i.e. rlJournalStart should have been run,
so that $BEAKERLIB is set)


Downloading
-----------

Release tarballs are available for download from Fedora Hosted:
    https://fedorahosted.org/released/python-pytest-beakerlib/

The goal is to include this project in Fedora repositories. Until that happens,
you can use testing builds from COPR – see "Developer links" below.

You can also install using pip:
    https://pypi.python.org/pypi/pytest-beakerlib/0.2


Operation
---------

A Bash process is run on the side, and BeakerLib commands (rlPhaseStart,
rlPhaseEnd, rlPass, rlFail, ...) are fed to it.
This is not very elegant, but since BeakerLib commands are Bash functions,
there is no way around running Bash.


Integration
-----------

Other plugins may integrate with this using pytest's
config.pluginmanager.getplugin('BeakerLibPlugin'). If this is None,
BeakerLib integration is not active, otherwise the result's
run_beakerlib_command method can be used to run additional commands.


Contributing
------------

The project is happy to accept patches!
Please format your contribution using the ​FreeIPA `patch guidelines`_,
and send it to ​<freeipa-devel@redhat.com>.
Any development discussion is welcome there.

Someday the project might get its own list, but that seems premature now.


Developer links
---------------

  * Bug tracker: https://fedorahosted.org/python-pytest-beakerlib/report/3
  * Code browser: ​https://git.fedorahosted.org/cgit/python-pytest-beakerlib
  * git clone ​https://git.fedorahosted.org/git/python-pytest-beakerlib.git
  * Unstable packages for Fedora: https://copr.fedoraproject.org/coprs/pviktori/pytest-plugins/

To release, update version in setup.py, add a Git tag like "v0.3",
and run `make tarball`.
Running `make upload` will put the tarball to Fedora Hosted and PyPI,
and a SRPM on Fedorapeople, if you have the rights.
Running `make release` will upload and fire a COPR build.

.. _patch guidelines: http://www.freeipa.org/page/Contribute/Patch_Format
