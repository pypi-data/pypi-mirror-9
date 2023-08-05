# -*- coding: utf-8 -*-
"""
Tests for `versioneer2` module.
"""
from __future__ import unicode_literals
import unittest
import versioneer2

release_type_string = 'post0.dev'

class PEP440Versions(unittest.TestCase):
    def check_git_ver_str(self, git_ver_str, exp_pep440_str):
        self.assertEqual(versioneer2.git2pep440(git_ver_str), exp_pep440_str)

    def test_tag(self):
        self.check_git_ver_str('0.2.1', '0.2.1')

    def test_tag_dirty(self):
        self.check_git_ver_str('0.2.1-dirty', '0.2.1.post0.dev0+dirty')

    def test_commit_after_tag(self):
        self.check_git_ver_str('0.2.1-4-g2g433f2', '0.2.1.post0.dev4+g2g433f2')

    def test_commit_after_tag_dirty(self):
        self.check_git_ver_str('0.2.1-4-g2g433f2-dirty',
                               '0.2.1.post0.dev4+g2g433f2.dirty')