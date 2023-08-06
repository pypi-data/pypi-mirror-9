#!/usr/bin/env python
#
# fatdisk.py - Unit test cases for COT.helpers.fatdisk submodule.
#
# March 2015, Glenn F. Matthews
# Copyright (c) 2014-2015 the COT project developers.
# See the COPYRIGHT.txt file at the top-level directory of this distribution
# and at https://github.com/glennmatthews/cot/blob/master/COPYRIGHT.txt.
#
# This file is part of the Common OVF Tool (COT) project.
# It is subject to the license terms in the LICENSE.txt file found in the
# top-level directory of this distribution and at
# https://github.com/glennmatthews/cot/blob/master/LICENSE.txt. No part
# of COT, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE.txt file.

"""Unit test cases for the COT.helpers.fatdisk module."""

import logging

from distutils.version import StrictVersion

from .test_helper import HelperUT
from COT.helpers.helper import Helper
from COT.helpers.fatdisk import FatDisk

logger = logging.getLogger(__name__)


class TestFatDisk(HelperUT):

    """Test cases for FatDisk helper class."""

    def setUp(self):
        """Test case setup function called automatically prior to each test."""
        self.helper = FatDisk()
        super(TestFatDisk, self).setUp()

    def test_get_version(self):
        """Validate .version getter."""
        self.fake_output = "fatdisk, version 1.0.0-beta"
        self.assertEqual(StrictVersion("1.0.0"), self.helper.version)

    def test_install_helper_already_present(self):
        """Trying to re-install is a no-op."""
        self.helper.install_helper()
        self.assertEqual([], self.last_argv)
        self.assertLogged(**self.ALREADY_INSTALLED)

    def test_install_helper_apt_get(self):
        """Test installation via 'apt-get'."""
        Helper.find_executable = self.stub_find_executable
        Helper.PACKAGE_MANAGERS['port'] = False
        Helper.PACKAGE_MANAGERS['apt-get'] = True
        self.system = 'Linux'
        self.helper.install_helper()
        self.assertEqual([
            ['sudo', 'apt-get', '-q', 'install', 'make'],
            ['sudo', 'apt-get', '-q', 'install', 'gcc'],
            ['./RUNME'],
            ['sudo', 'cp', 'fatdisk', '/usr/local/bin/fatdisk'],
        ], self.last_argv)

    def test_install_helper_port(self):
        """Test installation via 'port'."""
        Helper.find_executable = self.stub_find_executable
        Helper.PACKAGE_MANAGERS['port'] = True
        self.helper.install_helper()
        self.assertEqual(self.last_argv[0],
                         ['sudo', 'port', 'install', 'fatdisk'])

    def test_install_helper_yum(self):
        """Test installation via 'yum'."""
        Helper.find_executable = self.stub_find_executable
        Helper.PACKAGE_MANAGERS['port'] = False
        Helper.PACKAGE_MANAGERS['apt-get'] = False
        Helper.PACKAGE_MANAGERS['yum'] = True
        self.system = 'Linux'
        self.helper.install_helper()
        self.assertEqual([
            ['sudo', 'yum', '--quiet', 'install', 'make'],
            ['sudo', 'yum', '--quiet', 'install', 'gcc'],
            ['./RUNME'],
            ['sudo', 'cp', 'fatdisk', '/usr/local/bin/fatdisk'],
        ], self.last_argv)

    def test_install_helper_linux_need_make_no_package_manager(self):
        """Linux installation requires yum or apt-get if 'make' missing."""
        Helper.find_executable = self.stub_find_executable
        Helper.PACKAGE_MANAGERS['port'] = False
        Helper.PACKAGE_MANAGERS['apt-get'] = False
        Helper.PACKAGE_MANAGERS['yum'] = False
        self.system = 'Linux'
        with self.assertRaises(NotImplementedError):
            self.helper.install_helper()

    def test_install_helper_linux_need_compiler_no_package_manager(self):
        """Linux installation requires yum or apt-get if 'gcc' missing."""
        def new_stub_find_executable(self, name):
            """Stub for Helper.find_executable - returns a fixed response."""
            logger.info("stub_find_executable({0})".format(name))
            if name == 'make':
                return "/bin/make"
            else:
                return None
        Helper.find_executable = new_stub_find_executable
        Helper.PACKAGE_MANAGERS['port'] = False
        Helper.PACKAGE_MANAGERS['apt-get'] = False
        Helper.PACKAGE_MANAGERS['yum'] = False
        self.system = 'Linux'
        with self.assertRaises(NotImplementedError):
            self.helper.install_helper()

    def test_install_helper_unsupported(self):
        """No support for installation under Windows."""
        Helper.find_executable = self.stub_find_executable
        Helper.PACKAGE_MANAGERS['port'] = False
        self.system = 'Windows'
        with self.assertRaises(NotImplementedError):
            self.helper.install_helper()
