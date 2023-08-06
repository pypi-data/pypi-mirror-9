# -*- coding: utf-8 -*-

import unittest
import os

from advanced_ssh_config.utils import (safe_makedirs, value_interpolate,
                                       construct_proxy_commands, shellquote,
                                       shellquotemultiple)
from advanced_ssh_config.exceptions import ConfigError

from . import PREFIX


class TestContructProxyCommand(unittest.TestCase):

    def test_no_arg(self):
        self.assertRaises(TypeError, construct_proxy_commands)

    def test_empty_arg(self):
        self.assertRaises(ValueError, construct_proxy_commands, {})

    def test_minimal_valid(self):
        command = construct_proxy_commands({
            'hostname': 'aaa',
            'port': 42,
        })
        self.assertEqual(
            command, [['nc', '-w', 180, '-G', 5, 'aaa', 42], ['nc', 'aaa', 42]]
        )

    def test_minimal_nc(self):
        command = construct_proxy_commands({
            'hostname': 'aaa',
            'proxy_type': 'nc',
            'port': 42,
        })
        self.assertEqual(
            command, [['nc', '-w', 180, '-G', 5, 'aaa', 42], ['nc', 'aaa', 42]]
        )

    def test_full_nc(self):
        command = construct_proxy_commands({
            'hostname': 'aaa',
            'port': 42,
            'verbose': True,
            'proxy_type': 'nc',
            'timeout': 45,
        })
        self.assertEqual(
            command, [
                ['nc', '-v', '-w', 45, '-G', 5, 'aaa', 42],
                ['nc', 'aaa', 42]
            ]
        )

    def test_invalid_proxy_type(self):
        args = {
            'hostname': 'aaa',
            'port': 42,
            'proxy_type': 'fake',
            }
        self.assertRaises(ValueError, construct_proxy_commands, args)

    def test_minimal_socat(self):
        command = construct_proxy_commands({
            'hostname': 'aaa',
            'proxy_type': 'socat',
            'port': 42,
        })
        self.assertEqual(command, [['socat', 'STDIN', 'TCP:aaa:42']])

    def test_minimal_socat_http_proxy(self):
        command = construct_proxy_commands({
            'hostname': 'aaa',
            'proxy_type': 'socat_http_proxy',
            'http_proxy_host': 'bbb',
            'http_proxy_port': 43,
            'port': 42,
        })
        self.assertEqual(
            command, [['socat', 'STDIN', 'PROXY:bbb:aaa:42,proxyport=43']]
        )

    def test_minimal_socat_socks(self):
        command = construct_proxy_commands({
            'hostname': 'aaa',
            'proxy_type': 'socat_socks',
            'socks_host': 'bbb',
            'socks_port': 43,
            'port': 42,
        })
        self.assertEqual(
            command, [['socat', 'STDIN', 'SOCKS:bbb:aaa:42,socksport=43']]
        )

    # FIXME: test_custom_handler


class TestSafeMakedirs(unittest.TestCase):

    def setUp(self):
        if os.path.exists(PREFIX):
            os.system('rm -rf {}'.format(PREFIX))
        os.makedirs(PREFIX)

    def test_already_exists(self):
        safe_makedirs('{}/dir'.format(PREFIX))
        safe_makedirs('{}/dir'.format(PREFIX))

    def test_invalid(self):
        for path in ('/dev/null/test',):
            self.assertRaises(OSError, safe_makedirs, path)

    def test_makedirs_on_file(self):
        open('{}/file'.format(PREFIX), 'w').write('hello')
        self.assertRaises(OSError, safe_makedirs, '{}/file/dir'.format(PREFIX))


class TestValueInterpolate(unittest.TestCase):

    def setUp(self):
        if os.environ.get('TEST_INTERPOLATE'):
            del os.environ['TEST_INTERPOLATE']

    def test_interpolate_success(self):
        os.environ['TEST_INTERPOLATE'] = 'titi'
        self.assertEquals(value_interpolate('$TEST_INTERPOLATE'), 'titi')

    def test_interpolate_no_match(self):
        self.assertEquals(
            value_interpolate('$TEST_INTERPOLATE'), '$TEST_INTERPOLATE'
        )

    def test_interpolate_not_interpolable(self):
        os.environ['TEST_INTERPOLATE'] = 'titi'
        self.assertEquals(
            value_interpolate('TEST_INTERPOLATE'), 'TEST_INTERPOLATE'
        )

    def test_interpolate_interpolate_recursive(self):
        os.environ['TEST_INTERPOLATE'] = '$TEST_INTERPOLATE_2'
        os.environ['TEST_INTERPOLATE_2'] = '$TEST_INTERPOLATE_3'
        os.environ['TEST_INTERPOLATE_3'] = '$TEST_INTERPOLATE_4'
        os.environ['TEST_INTERPOLATE_4'] = 'tutu'
        self.assertEquals(value_interpolate('$TEST_INTERPOLATE'), 'tutu')

    def test_interpolate_interpolate_loop(self):
        os.environ['TEST_INTERPOLATE'] = '$TEST_INTERPOLATE'
        self.assertRaises(ConfigError, value_interpolate, '$TEST_INTERPOLATE')

    def test_interpolate_interpolate_loop_complex(self):
        os.environ['TEST_INTERPOLATE'] = '$TEST_INTERPOLATE_2'
        os.environ['TEST_INTERPOLATE_2'] = '$TEST_INTERPOLATE_3'
        os.environ['TEST_INTERPOLATE_3'] = '$TEST_INTERPOLATE'
        self.assertRaises(ConfigError, value_interpolate, '$TEST_INTERPOLATE')


class TestShellQuote(unittest.TestCase):

    def test_shellquote_simple(self):
        self.assertEquals(shellquote(["aaa"]), 'aaa')
        self.assertEquals(shellquote(["aaa", "bbb"]), 'aaa bbb')
        self.assertEquals(shellquote(["aaa", "bbb", 42]), 'aaa bbb 42')

    def test_shellquote_empty(self):
        self.assertEquals(shellquote([]), '')

    def test_shellquote_escape(self):
        self.assertEquals(shellquote(["test'test"]), "'test\\'test'")
        self.assertEquals(shellquote(["test\\test"]), "'test\\\\test'")
        self.assertEquals(shellquote(["test\"test"]), "test\"test")

    def test_shellquote_complex(self):
        self.assertEquals(
            shellquote(["ssh", "manfred's imac", '-p', 4242]),
            "ssh 'manfred\\'s imac' -p 4242"
        )

    def test_shellquote_not_list(self):
        self.assertRaises(ValueError, shellquote, 'aaa')


class TestShellQuoteMultiple(unittest.TestCase):

    def test_shellquote_multiple_simple(self):
        self.assertEquals(
            shellquotemultiple([['aaa', 'bbb', 42], ['ccc', 'ddd', 43]]),
            '(aaa bbb 42 2>/dev/null || ccc ddd 43)'
        )

    def test_shellquote_not_list_of_list(self):
        self.assertRaises(ValueError, shellquotemultiple, [42, 42])
        self.assertRaises(ValueError, shellquotemultiple, 42)
        self.assertRaises(ValueError, shellquotemultiple, "42")
