setuptools-version-command -- get version from VCS

Instead of hardcoding the version in setup.py like this:

    setup(
        name='some-dist-name',
        version='1.0',
        ...)

This package allows specifying a VCS command like this:

    setup(
        name='some-dist-name',
        version_command='git describe')

Which will then update the version into some-dist-name.egg-info/version.txt,
so that the version can also be found if setup.py is being run from a sdist
or something.

When it can find the version from either some-dist-name.egg-info/version.txt
or the output of the version_command, it will update the version key that is
normally used for the version, such as what's used in the sdist filename and
so on.

To use it, just do this:

    pip install setuptools-version-command

With the pip of the global python.


