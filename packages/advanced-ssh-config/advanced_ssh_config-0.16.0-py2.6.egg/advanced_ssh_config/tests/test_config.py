# -*- coding: utf-8 -*-

import unittest
import os

from advanced_ssh_config.config import Config
from advanced_ssh_config.exceptions import ConfigError
from . import set_config, prepare_config, write_config, PREFIX, DEFAULT_CONFIG


class TestConfig(unittest.TestCase):

    def setUp(self):
        prepare_config()

    def test_initialize_config(self):
        config = Config([DEFAULT_CONFIG])
        self.assertIsInstance(config, Config)

    def test_include_existing_files(self):
        write_config('', name='include-1')
        write_config('', name='include-2')
        contents = """
[default]
Includes = {0}/include-1 {0}/include-2
"""
        config = set_config(contents)
        self.assertEquals(config.loaded_files, [
            DEFAULT_CONFIG,
            '{}/include-1'.format(PREFIX),
            '{}/include-2'.format(PREFIX),
        ])

    def test_include_not_exists(self):
        contents = """
[default]
Includes = {0}/include-1 {0}/include-2
"""
        set_config(contents, load=False)
        self.assertRaises(ConfigError, Config, [DEFAULT_CONFIG])

    def test_include_same_file(self):
        write_config('', name='include-1')
        contents = """
[default]
Includes = {0}/include-1 {0}/include-1
"""
        config = set_config(contents)
        self.assertEquals(config.loaded_files, [
            DEFAULT_CONFIG,
            '{}/include-1'.format(PREFIX),
        ])

    def test_sections_simple(self):
        contents = """
[hosta]
[default]
"""
        config = set_config(contents)
        self.assertEquals(config.sections, ['hosta', 'default'])

    def test_sections_with_double(self):
        contents = """
[hosta]
[hosta]
[default]
"""
        config = set_config(contents)
        self.assertEquals(config.sections, ['hosta', 'default'])

    def test_sections_with_case(self):
        contents = """
[hosta]
[hostA]
[default]
"""
        config = set_config(contents)
        self.assertEquals(config.sections, ['hosta', 'hostA', 'default'])

    def test_sections_with_regex(self):
        contents = """
[hosta]
[host.*]
[default]
"""
        config = set_config(contents)
        self.assertEquals(config.sections, ['hosta', 'host.*', 'default'])

    def test_get_simple(self):
        contents = """
[hosta]
hostname = 1.2.3.4
"""
        config = set_config(contents)
        self.assertEquals(config.get('Hostname', 'hosta'), '1.2.3.4')
        self.assertEquals(config.get('hostname', 'hosta'), '1.2.3.4')

    def test_get_key_not_found(self):
        contents = """
[hosta]
"""
        config = set_config(contents)
        self.assertEquals(config.get('Hostname', 'hosta'), None)
        self.assertEquals(
            config.get('Hostname', 'hosta', 'localhost'), 'localhost'
        )

    def test_get_host_not_found(self):
        contents = """
[default]
port = 22
"""
        config = set_config(contents)
        self.assertEquals(config.get('Port', 'hosta'), '22')

    def test_get_host_and_key_not_found(self):
        config = set_config('')
        self.assertEquals(config.get('Port', 'hosta'), None)

    def test_host_wildcard(self):
        contents = """
[aaa.*]
port = 25

[.*bbb]
port = 24

[ccc.*ddd]
port = 23

[.*eee.*]
port = 22

[default]
port = 21
"""
        config = set_config(contents)
        self.assertEquals(config.get('Port', 'aaa'), '25')
        self.assertEquals(config.get('Port', 'aaa42'), '25')
        self.assertEquals(config.get('Port', '42aaa'), '21')

        self.assertEquals(config.get('Port', 'bbb'), '24')
        self.assertEquals(config.get('Port', 'bbb42'), '24')  # strange
        self.assertEquals(config.get('Port', '42bbb'), '24')

        self.assertEquals(config.get('Port', 'cccddd'), '23')
        self.assertEquals(config.get('Port', 'ccc42ddd'), '23')

        self.assertEquals(config.get('Port', 'eee'), '22')
        self.assertEquals(config.get('Port', '42eee'), '22')
        self.assertEquals(config.get('Port', 'eee42'), '22')
        self.assertEquals(config.get('Port', '42eee42'), '22')

    def test_host_invalid_wildcard(self):
        contents = """
[aaa.+]
port = 25
"""
        set_config(contents, load=False)
        self.assertRaises(ConfigError, Config, [DEFAULT_CONFIG])

    def test_multiple_line(self):
        contents = """
[test]
localforward = 1 test 2 \n 2 test 3
"""
        config = set_config(contents)
        self.assertEquals(
            config.get('localforward', 'test'), ['1 test 2', '2 test 3']
        )

    def test_one_line_list(self):
        contents = """
[test]
localforward = 1 test 2
"""
        config = set_config(contents)
        self.assertEquals(config.get('localforward', 'test'), ['1 test 2'])
