#!/usr/bin/env python

# Tests for the pip accelerator.
#
# Author: Peter Odding <peter.odding@paylogic.eu>
# Last Change: April 6, 2015
# URL: https://github.com/paylogic/pip-accel

"""
:py:mod:`pip_accel.tests` - Test suite for the pip accelerator
==============================================================

I've decided to include the test suite in the online documentation of the pip
accelerator and I realize this may be somewhat unconventional... My reason for
this is to enforce the same level of code quality (which obviously includes
documentation) for the test suite that I require from myself and contributors
for the other parts of the pip-accel project (and my other open source
projects).

A second and more subtle reason is because of a tendency I've noticed in a lot
of my projects: Useful "miscellaneous" functionality is born in test suites and
eventually makes its way to the public API of the project in question. By
writing documentation up front I'm saving my future self time. That may sound
silly, but consider that writing documentation is a lot easier when you *don't*
have to do so retroactively.
"""

# Standard library modules.
import logging
import operator
import os
import pipes
import random
import shutil
import signal
import sys
import tempfile
import unittest

# External dependencies.
import coloredlogs
from humanfriendly import coerce_boolean
from pip.commands.install import InstallCommand
from pip.exceptions import DistributionNotFound

# Modules included in our package.
from pip_accel import PatchedAttribute, PipAccelerator
from pip_accel.cli import main
from pip_accel.compat import StringIO
from pip_accel.config import Config
from pip_accel.deps import DependencyInstallationRefused, SystemPackageManager
from pip_accel.exceptions import EnvironmentMismatchError
from pip_accel.utils import uninstall

# Initialize a logger for this module.
logger = logging.getLogger(__name__)

# A list of temporary directories created by the test suite.
TEMPORARY_DIRECTORIES = []

def setUpModule():
    """Initialize verbose logging to the terminal."""
    coloredlogs.install(level=logging.DEBUG)

def tearDownModule():
    """Cleanup any temporary directories created by :py:func:`create_temporary_directory()`."""
    while TEMPORARY_DIRECTORIES:
        directory = TEMPORARY_DIRECTORIES.pop(0)
        logger.debug("Cleaning up temporary directory: %s", directory)
        shutil.rmtree(directory)

def create_temporary_directory():
    """
    Create a temporary directory that will be cleaned up when the test suite ends.

    :returns: The pathname of a directory created using
              :py:func:`tempfile.mkdtemp()` (a string).
    """
    directory = tempfile.mkdtemp()
    logger.debug("Created temporary directory: %s", directory)
    TEMPORARY_DIRECTORIES.append(directory)
    return directory

class PipAccelTestCase(unittest.TestCase):

    """
    Container for the tests in the pip-accel test suite.
    """

    def setUp(self):
        """Reset logging verbosity before each test."""
        coloredlogs.set_level(logging.DEBUG)

    def initialize_pip_accel(self, load_environment_variables=False, **overrides):
        """
        Construct an isolated pip accelerator instance.

        The pip-accel instance will not load configuration files but it may
        load environment variables because that's how FakeS3 is enabled on
        Travis CI (and in my local tests).

        :param load_environment_variables: If ``True`` the pip-accel instance
                                           will load environment variables (not
                                           the default).
        :param overrides: Any keyword arguments are set as properties on the
                          :py:class:`~.Config` instance (overrides for
                          configuration defaults).
        """
        config = Config(load_configuration_files=False,
                        load_environment_variables=load_environment_variables)
        for name, value in overrides.items():
            setattr(config, name, value)
        accelerator = PipAccelerator(config)
        return accelerator

    def test_environment_validation(self):
        """
        Test the validation of :py:data:`sys.prefix` versus ``$VIRTUAL_ENV``.

        This tests the :py:func:`~pip_accel.PipAccelerator.validate_environment()` method.
        """
        original_value = os.environ.get('VIRTUAL_ENV')
        try:
            os.environ['VIRTUAL_ENV'] = generate_nonexisting_pathname()
            self.assertRaises(EnvironmentMismatchError, self.initialize_pip_accel)
        finally:
            os.environ['VIRTUAL_ENV'] = original_value

    def test_config_file_handling(self):
        """
        Test error handling during loading of configuration files.

        This tests the :py:func:`~pip_accel.config.Config.load_configuration_file()` method.
        """
        # Create a dummy configuration object.
        config = Config(load_configuration_files=False, load_environment_variables=False)
        # Check that loading of non-existing configuration files raises the expected exception.
        self.assertRaises(Exception, config.load_configuration_file, generate_nonexisting_pathname())
        # Check that loading of invalid configuration files raises the expected exception.
        directory = create_temporary_directory()
        config_file = os.path.join(directory, 'pip-accel.ini')
        with open(config_file, 'w') as handle:
            handle.write('[a-section-not-called-pip-accel]\n')
            handle.write('name = value\n')
        self.assertRaises(Exception, config.load_configuration_file, config_file)

    def test_cleanup_of_broken_links(self):
        """
        Verify that broken symbolic links in the source index are cleaned up.

        This tests the :py:func:`~pip_accel.PipAccelerator.clean_source_index()` method.
        """
        source_index = create_temporary_directory()
        broken_link = os.path.join(source_index, 'this-is-a-broken-link')
        os.symlink(generate_nonexisting_pathname(), broken_link)
        assert os.path.islink(broken_link), "os.symlink() doesn't work, what the?!"
        self.initialize_pip_accel(source_index=source_index)
        assert not os.path.islink(broken_link), "pip-accel didn't clean up a broken link in its source index!"

    def test_empty_download_cache(self):
        """
        Verify pip-accel's "keeping pip off the internet" logic using an empty cache.

        This test downloads, builds and installs verboselogs 1.0.1 (a trivial
        Python package I created once) to verify that pip-accel keeps pip off
        the internet when intended.
        """
        pip_install_args = ['--ignore-installed', 'verboselogs==1.0.1']
        # Initialize an instance of pip-accel with an empty cache.
        accelerator = self.initialize_pip_accel(data_directory=create_temporary_directory())
        # First we do a simple sanity check that unpack_source_dists() does not
        # connect to PyPI when it's missing distributions (it should raise a
        # DistributionNotFound exception instead).
        try:
            accelerator.unpack_source_dists(pip_install_args)
            assert False, "This line should not be reached! (unpack_source_dists() is expected to raise DistributionNotFound)"
        except Exception as e:
            # We expect a `DistributionNotFound' exception.
            if not isinstance(e, DistributionNotFound):
                # If we caught a different type of exception something went
                # wrong so we want to propagate the original exception, not
                # obscure it!
                raise
        # Download the source distribution from PyPI and validate the resulting requirement object.
        requirements = accelerator.download_source_dists(pip_install_args)
        assert isinstance(requirements, list), "Unexpected return value type from download_source_dists()!"
        assert len(requirements) == 1, "Expected download_source_dists() to return one requirement!"
        assert requirements[0].name == 'verboselogs', "Requirement has unexpected name!"
        assert requirements[0].version == '1.0.1', "Requirement has unexpected version!"
        assert os.path.isdir(requirements[0].source_directory), "Requirement's source directory doesn't exist!"
        # Test the build and installation of the binary package.
        num_installed, num_already_satisfied = accelerator.install_requirements(requirements, ignore_installed=True)
        assert num_installed == 1, "Expected pip-accel to install exactly one package!"
        assert num_already_satisfied == 0, "Expected no requirements to be already satisfied!"
        # Make sure the `verboselogs' module can be imported after installation.
        __import__('verboselogs')
        # We now have a non-empty download cache and source index so this
        # should not raise an exception (it should use the source index).
        accelerator.unpack_source_dists(pip_install_args)

    def test_package_upgrade(self):
        """Test installation of newer versions over older versions."""
        accelerator = self.initialize_pip_accel()
        # Install version 1.0 of the `verboselogs' package.
        num_installed, num_already_satisfied = accelerator.install_from_arguments(['--ignore-installed', 'verboselogs==1.0'])
        assert num_installed == 1, "Expected pip-accel to install exactly one package!"
        assert num_already_satisfied == 0, "Expected no requirements to be already satisfied!"
        # Install version 1.0.1 of the `verboselogs' package.
        num_installed, num_already_satisfied = accelerator.install_from_arguments(['--ignore-installed', 'verboselogs==1.0.1'])
        assert num_installed == 1, "Expected pip-accel to install exactly one package!"
        assert num_already_satisfied == 0, "Expected no requirements to be already satisfied!"

    def test_s3_backend(self):
        """
        Verify the successful usage of the S3 cache backend.

        This test downloads, builds and installs verboselogs 1.0.1 (a trivial
        Python package I created once) to verify that the S3 cache backend
        works. It depends on FakeS3 (refer to the shell script
        ``scripts/collect-full-coverage`` in the pip-accel git repository).

        This test uses a temporary binary index which it wipes after a
        successful installation and then it installs the exact same package
        again to test the code path that gets a cached binary distribution
        archive from the S3 cache backend.

        .. warning:: This test involves the **termination** of FakeS3 to force
                     a failure in the S3 cache backend. This verifies that
                     pip-accel handles this failure gracefully.
        """
        fakes3_pid = int(os.environ.get('PIP_ACCEL_FAKES3_PID', '0'))
        if not fakes3_pid:
            logger.warning("Skipping S3 cache backend test (it looks like FakeS3 isn't running).")
            return
        pip_install_args = ['--ignore-installed', 'verboselogs==1.0.1']
        # Initialize an instance of pip-accel with an empty cache.
        accelerator = self.initialize_pip_accel(load_environment_variables=True,
                                                data_directory=create_temporary_directory())
        # Run the installation three times.
        for i in [1, 2, 3]:
            if i > 1:
                logger.debug("Resetting binary index to force binary distribution download from S3 ..")
                shutil.rmtree(accelerator.config.binary_cache)
                os.mkdir(accelerator.config.binary_cache)
            if i == 3:
                logger.debug("Killing FakeS3 (%i) to force S3 cache backend failure ..", fakes3_pid)
                os.kill(fakes3_pid, signal.SIGKILL)
            # Install the verboselogs package using the S3 cache backend.
            num_installed, num_already_satisfied = accelerator.install_from_arguments(pip_install_args)
            assert num_installed == 1, "Expected pip-accel to install exactly one package!"
            assert num_already_satisfied == 0, "Expected no requirements to be already satisfied!"

    def test_wheel_install(self):
        """
        Test the installation of a package from a wheel distribution.

        This test installs Paver 1.2.4 (a random package without dependencies
        that I noticed is available as a Python 2.x and Python 3.x compatible
        wheel archive on PyPI).
        """
        accelerator = self.initialize_pip_accel()
        wheels_already_supported = accelerator.setuptools_supports_wheels()
        # Test the installation of Paver (and the upgrade of Setuptools?).
        num_installed, num_already_satisfied = accelerator.install_from_arguments([
            # Ugly way to force pip to install from a wheel archive (there is a
            # --no-use-wheel option but there is nothing like --force-wheel).
            '--ignore-installed', 'https://pypi.python.org/packages/2.7/P/Paver/Paver-1.2.4-py2.py3-none-any.whl'
        ])
        if wheels_already_supported:
            assert num_installed == 1, "Expected pip-accel to install exactly one package!"
        else:
            assert num_installed == 2, "Expected pip-accel to install exactly two packages!"
        assert num_already_satisfied == 0, "Expected no requirements to be already satisfied!"
        # Make sure the Paver program works after installation.
        try_program('paver')

    def test_bdist_fallback(self):
        """
        Verify that fall back from ``bdist_dumb`` to ``bdist`` action works.

        This test verifies that pip-accel properly handles ``setup.py`` scripts
        that break ``python setup.py bdist_dumb`` but support ``python setup.py
        bdist`` as a fall back. This issue was originally reported based on
        ``Paver==1.2.3`` in `issue 37`_, so that's the package used for this
        test.

        .. _issue 37: https://github.com/paylogic/pip-accel/issues/37
        """
        # Install Paver 1.2.3 using pip-accel.
        accelerator = self.initialize_pip_accel()
        num_installed, num_already_satisfied = accelerator.install_from_arguments([
            '--ignore-installed', '--no-use-wheel', 'paver==1.2.3'
        ])
        assert num_installed == 1, "Expected pip-accel to install exactly one package!"
        assert num_already_satisfied == 0, "Expected no requirements to be already satisfied!"
        # Make sure the Paver program works after installation.
        try_program('paver')

    def test_installed_files_tracking(self):
        """
        Verify that tracking of installed files works correctly.

        This tests the :py:func:`~pip_accel.bdist.BinaryDistributionManager.update_installed_files()`
        method.

        When pip installs a Python package it also creates a file called
        ``installed-files.txt`` that contains the pathnames of the files that
        were installed. This file enables pip to uninstall Python packages
        later on. Because pip-accel implements its own package installation it
        also creates the ``installed-files.txt`` file, in order to enable the
        user to uninstall a package with pip even if the package was installed
        using pip-accel.
        """
        # Prevent unsuspecting users from accidentally running the find_files()
        # tests below on their complete `/usr' or `/usr/local' tree :-).
        if not hasattr(sys, 'real_prefix'):
            logger.warning("Skipping installed files tracking test (not running in a recognized virtual environment).")
            return
        # Install the iPython 1.0 source distribution using pip.
        command = InstallCommand()
        opts, args = command.parse_args([
            '--ignore-installed', '--no-use-wheel', 'ipython==1.0'
        ])
        command.run(opts, args)
        # Make sure the iPython program works after installation using pip.
        try_program('ipython3' if sys.version_info[0] == 3 else 'ipython')
        # Find the iPython related files installed by pip.
        files_installed_using_pip = set(find_files(sys.prefix, 'ipython'))
        assert len(files_installed_using_pip) > 0, \
            "It looks like pip didn't install iPython where we expected it to do so?!"
        logger.debug("Found %i files installed using pip: %s",
                     len(files_installed_using_pip), files_installed_using_pip)
        # Remove the iPython installation.
        uninstall('ipython')
        # Install the iPython 1.0 source distribution using pip-accel.
        accelerator = self.initialize_pip_accel()
        num_installed, num_already_satisfied = accelerator.install_from_arguments([
            '--ignore-installed', '--no-use-wheel', 'ipython==1.0'
        ])
        assert num_installed == 1, "Expected pip-accel to install exactly one package!"
        assert num_already_satisfied == 0, "Expected no requirements to be already satisfied!"
        # Make sure the iPython program works after installation using pip-accel.
        try_program('ipython3' if sys.version_info[0] == 3 else 'ipython')
        # Find the iPython related files installed by pip-accel.
        files_installed_using_pip_accel = set(find_files(sys.prefix, 'ipython'))
        assert len(files_installed_using_pip_accel) > 0, \
            "It looks like pip-accel didn't install iPython where we expected it to do so?!"
        logger.debug("Found %i files installed using pip-accel: %s",
                     len(files_installed_using_pip_accel), files_installed_using_pip_accel)
        # Test that pip and pip-accel installed exactly the same files.
        assert files_installed_using_pip == files_installed_using_pip_accel, \
            "It looks like pip and pip-accel installed different files for iPython!"
        # Test that pip knows how to uninstall iPython installed by pip-accel
        # due to the installed-files.txt file generated by pip-accel.
        uninstall('ipython')
        # Make sure all files related to iPython were uninstalled by pip.
        assert len(list(find_files(sys.prefix, 'ipython'))) == 0, \
            "It looks like pip didn't properly uninstall iPython after installation using pip-accel!"

    def test_requirement_objects(self):
        """
        Test the public properties of :py:class:`pip_accel.req.Requirement` objects.

        This test confirms (amongst other things) that the logic which
        distinguishes transitive requirements from non-transitive (direct)
        requirements works correctly (and keeps working as expected :-).
        """
        # Download and unpack rotate-backups.
        accelerator = self.initialize_pip_accel()
        requirements = accelerator.get_requirements([
            '--ignore-installed', 'rotate-backups==0.1.1'
        ])
        # Separate direct from transitive requirements.
        direct_requirements = [r for r in requirements if r.is_direct]
        transitive_requirements = [r for r in requirements if r.is_transitive]
        # Enable remote debugging of test suite failures (should they ever happen).
        logger.debug("Direct requirements: %s", direct_requirements)
        logger.debug("Transitive requirements: %s", transitive_requirements)
        # Validate the direct requirements (there should be just one; rotate-backups).
        assert len(direct_requirements) == 1, \
            "pip-accel reported more than one direct requirement! (I was expecting only one)"
        assert direct_requirements[0].name == 'rotate-backups', \
            "pip-accel reported a direct requirement with an unexpected name!"
        # Validate the transitive requirements.
        expected_transitive_requirements = set([
            'coloredlogs', 'executor', 'humanfriendly', 'naturalsort',
            'python-dateutil', 'six'
        ])
        actual_transitive_requirements = set(r.name for r in transitive_requirements)
        assert expected_transitive_requirements.issubset(actual_transitive_requirements), \
            "Requirement set reported by pip-accel is missing expected transitive requirements!"
        # Make sure Requirement.wheel_metadata raises the expected exception
        # when the requirement isn't a wheel distribution.
        self.assertRaises(TypeError, operator.attrgetter('wheel_metadata'), direct_requirements[0])
        # Make sure Requirement.sdist_metadata raises the expected exception
        # when the requirement isn't a source distribution.
        requirements = accelerator.get_requirements([
            # Ugly way to force pip to install from a wheel archive (there is a
            # --no-use-wheel option but there is nothing like --force-wheel).
            '--ignore-installed', 'https://pypi.python.org/packages/2.7/P/Paver/Paver-1.2.4-py2.py3-none-any.whl'
        ])
        self.assertRaises(TypeError, operator.attrgetter('sdist_metadata'), requirements[0])

    def test_cli_install(self):
        """
        Test the pip-accel command line interface by installing a trivial package.

        This test provides some test coverage for the pip-accel command line
        interface, to make sure the command line interface works on all
        supported versions of Python.
        """
        returncode = test_cli('pip-accel', 'install',
                              # Make sure the -v, --verbose option is supported.
                              '-v', '--verbose',
                              # Make sure the -q, --quiet option is supported.
                              '-q', '--quiet',
                              # Ignore packages that are already installed.
                              '--ignore-installed',
                              # Install the naturalsort package.
                              'naturalsort')
        assert returncode == 0, "pip-accel command line interface exited with nonzero return code!"
        # Make sure the `natsort' module can be imported after installation.
        __import__('natsort')

    def test_cli_usage_message(self):
        """Test the pip-accel command line usage message."""
        with CaptureOutput() as stream:
            returncode = test_cli('pip-accel')
            assert returncode == 0, "pip-accel command line interface exited with nonzero return code!"
            assert 'Usage: pip-accel' in str(stream), "pip-accel command line interface didn't report usage message!"

    def test_empty_requirements_file(self):
        """
        Test handling of empty requirements files.

        Old versions of pip-accel would raise an internal exception when an
        empty requirements file was given. This was reported in `issue 47`_ and
        it was pointed out that pip reports a warning but exits with return
        code zero. This test makes sure pip-accel now handles empty
        requirements files the same way pip does.

        .. _issue 47: https://github.com/paylogic/pip-accel/issues/47
        """
        returncode = test_cli('pip-accel', 'install', '--requirement', '/dev/null')
        assert returncode == 0, "pip-accel command line interface failed on empty requirements file!"

    def test_system_package_dependency_installation(self):
        """
        Test the (automatic) installation of required system packages.

        This test installs lxml 3.2.1 to confirm that the system packages
        required by lxml are automatically installed by pip-accel to make the
        build of lxml succeed.

        .. warning:: This test forces the removal of the system package
                     ``libxslt1-dev`` before it tries to install lxml, because
                     without this nasty hack the test would only install
                     required system packages on the first run, because on
                     later runs the required system packages would already be
                     installed. Because of this very non conventional behavior
                     the test is skipped unless the environment variable
                     ``PIP_ACCEL_TEST_AUTO_INSTALL=yes`` is set (opt-in).
        """
        # Test system package dependency handling.
        if not coerce_boolean(os.environ.get('PIP_ACCEL_TEST_AUTO_INSTALL')):
            logger.warning("Skipping system package dependency installation test (set the environment variable"
                           " PIP_ACCEL_TEST_AUTO_INSTALL=true to allow the test suite to use `sudo').")
            return
        # Force the removal of a system package required by `lxml' without
        # removing any (reverse) dependencies (we don't actually want to
        # break the system, thank you very much :-). Disclaimer: you opt in
        # to this with $PIP_ACCEL_TEST_AUTO_INSTALL...
        os.system('sudo dpkg --remove --force-depends libxslt1-dev')
        # Make sure that when automatic installation is disabled the system
        # package manager refuses to install the missing dependency.
        accelerator = self.initialize_pip_accel(auto_install=False, data_directory=create_temporary_directory())
        self.assertRaises(DependencyInstallationRefused, accelerator.install_from_arguments, [
            '--ignore-installed', 'lxml==3.2.1'
        ])
        # Try to ask for permission but make the prompt fail because standard
        # input cannot be read (this test suite obviously needs to be
        # non-interactive) and make sure the system package manager refuses to
        # install the missing dependency.
        with PatchedAttribute(sys, 'stdin', open(os.devnull)):
            accelerator = self.initialize_pip_accel(auto_install=None, data_directory=create_temporary_directory())
            self.assertRaises(DependencyInstallationRefused, accelerator.install_from_arguments, [
                '--ignore-installed', 'lxml==3.2.1'
            ])
        # Install lxml while a system dependency is missing and automatic installation is allowed.
        accelerator = self.initialize_pip_accel(auto_install=True,
                                                data_directory=create_temporary_directory())
        num_installed, num_already_satisfied = accelerator.install_from_arguments([
            '--ignore-installed', 'lxml==3.2.1'
        ])
        assert num_installed == 1, "Expected pip-accel to install exactly one package!"
        assert num_already_satisfied == 0, "Expected no requirements to be already satisfied!"

    def test_system_package_dependency_failures(self):
        this_script = os.path.abspath(__file__)
        pip_accel_directory = os.path.dirname(this_script)
        deps_directory = os.path.join(pip_accel_directory, 'deps')
        dummy_deps_config = os.path.join(deps_directory, 'unsupported-platform-test.ini')
        # Create an unsupported system package manager configuration.
        with open(dummy_deps_config, 'w') as handle:
            handle.write('[commands]\n')
            handle.write('supported = false\n')
            handle.write('list = false\n')
            handle.write('installed = false\n')
        try:
            # Validate that the unsupported configuration is ignored (gracefully).
            manager = SystemPackageManager(Config())
            assert manager.list_command != 'false' and manager.install_command != 'false', \
                "System package manager seems to have activated an unsupported configuration!"
        finally:
            # Never leave the dummy configuration file behind.
            os.remove(dummy_deps_config)

def find_files(directory, substring):
    """
    Find files whose pathname contains the given substring.

    :param directory: The pathname of the directory to be searched (a string).
    :param substring: The substring that pathnames should contain (a string).
    :returns: A generator of pathnames (strings).
    """
    substring = substring.lower()
    for root, dirs, files in os.walk(directory):
        for filename in files:
            pathname = os.path.join(root, filename)
            if substring in pathname.lower():
                yield pathname

def try_program(program_name):
    """
    Test that a Python program (installed in the current environment) runs successfully.

    This assumes that the program supports the ``--help`` option, because the
    program is executed with the ``--help`` argument to verify that the program
    runs (``--help`` was chose because it implies a lack of side effects).

    :param program_name: The base name of the program to test (a string). The
                         absolute pathname will be calculated by combining
                         :py:data:`sys.prefix` and this argument.
    :raises: :py:exc:`~exceptions.AssertionError` when a test fails.
    """
    program_path = os.path.join(sys.prefix, 'bin', program_name)
    logger.debug("Making sure %s is installed ..", program_path)
    assert os.path.isfile(program_path), \
        ("Missing program file! (%s)" % program_path)
    logger.debug("Making sure %s is executable ..", program_path)
    assert os.access(program_path, os.X_OK), \
        ("Program file not executable! (%s)" % program_path)
    logger.debug("Making sure %s --help works ..", program_path)
    assert os.system('%s --help 1>/dev/null 2>&1' % pipes.quote(program_path)) == 0, \
        ("Program doesn't run! (%s --help failed)" % program_path)

def generate_nonexisting_pathname():
    """
    Generate a pathname that is expected not to exist.

    :returns: A pathname (string) that doesn't refer to an existing directory
              or file on the file system (assuming :py:func:`random.random()`
              does what it's documented to do :-).
    """
    return os.path.join(tempfile.gettempdir(),
                        'this-path-certainly-will-not-exist-%s' % random.random())

def test_cli(*arguments):
    """
    Test the pip-accel command line interface.

    Runs pip-accel's command line interface inside the current Python process
    by temporarily changing :py:data:`sys.argv`, invoking the
    :py:func:`pip_accel.cli.main()` function and catching
    :py:exc:`~exceptions.SystemExit`.

    :param arguments: The value that :py:data:`sys.argv` should be set to (a
                      list of strings).
    :returns: The exit code of ``pip-accel``.
    """
    original_argv = sys.argv
    try:
        sys.argv = list(arguments)
        main()
        return 0
    except SystemExit as e:
        return e.code
    finally:
        sys.argv = original_argv

class CaptureOutput(object):

    """Context manager that captures what's written to :py:data:`sys.stdout`."""

    def __init__(self):
        """Initialize a string IO object to be used as :py:data:`sys.stdout`."""
        self.stream = StringIO()

    def __enter__(self):
        """Start capturing what's written to :py:data:`sys.stdout`."""
        self.original_stdout = sys.stdout
        sys.stdout = self.stream
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        """Stop capturing what's written to :py:data:`sys.stdout`."""
        sys.stdout = self.original_stdout

    def __str__(self):
        """Get the text written to :py:data:`sys.stdout`."""
        return self.stream.getvalue()

if __name__ == '__main__':
    unittest.main()
