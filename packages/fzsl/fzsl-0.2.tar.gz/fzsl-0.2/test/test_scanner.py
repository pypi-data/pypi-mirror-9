import os
import sys
import tempfile
import unittest

try:
    import configparser
    import io
    StringIO = io.StringIO
except ImportError:
    import ConfigParser as configparser
    configparser.RawConfigParser.read_file = configparser.RawConfigParser.readfp
    import cStringIO
    StringIO = cStringIO.StringIO

TESTDIR = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.realpath(os.path.join(TESTDIR, '..')))

import fzsl

class SimpleScannerTest(unittest.TestCase):
    def setUp(self):
        self.bn = os.path.basename(__file__)

    def test_sort(self):
        s1 = fzsl.SimpleScanner('test', 'echo', priority=1)
        s2 = fzsl.SimpleScanner('test', 'echo', priority=2)

        l = [s2, s1]
        l.sort()

        self.assertEqual(l[0], s1)
        self.assertEqual(l[1], s2)

    def test_root_path_match(self):
        s = fzsl.SimpleScanner('test', 'echo', root_path=TESTDIR)
        self.assertTrue(s.is_suitable(TESTDIR))
        self.assertTrue(s.is_suitable('%s/test/stuff' % (TESTDIR,)))
        self.assertFalse(s.is_suitable(os.path.dirname(TESTDIR)))
        self.assertFalse(s.is_suitable('%s/../' % (TESTDIR,)))

    def test_detect_cmd_match(self):
        cmd = '[ -f %s ]' % (self.bn,)
        s = fzsl.SimpleScanner('test', 'echo', detect_cmd=cmd)
        self.assertTrue(s.is_suitable(TESTDIR))
        self.assertFalse(s.is_suitable('%s/../' % (TESTDIR,)))

        cmd = '[ -f thisfileisnothere ]'
        s2 = fzsl.SimpleScanner('test', 'echo', detect_cmd=cmd)
        self.assertFalse(s2.is_suitable(TESTDIR))

    def test_cmd(self):
        cmd = 'find . -name %s' % (self.bn,)
        s = fzsl.SimpleScanner('test', cmd)
        self.assertIn('./' + self.bn, s.scan(TESTDIR))
        self.assertNotIn('.git' + self.bn, s.scan(TESTDIR))

        self.assertEqual(0, len(s.scan('%s/../bin' % (TESTDIR,))))

    def test_fallthrough(self):
        s = fzsl.SimpleScanner('test', 'echo')
        self.assertTrue(s.is_suitable(TESTDIR))

    def test_scanner(self):
        cache = tempfile.NamedTemporaryFile(dir=TESTDIR, mode='w')

        with open(os.path.join(TESTDIR, 'files'), 'r') as src:
            cache.write(u'\n'.join(src.read().split()))
        cache.flush()

        s = fzsl.SimpleScanner('test', 'echo hi', cache=cache.name)
        results = s.scan()
        self.assertEqual(len(results), 49168)

        results = s.scan(rescan=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], 'hi')

    def test_load_rule(self):
        buf = "[some-rule]\n"

        parser = configparser.RawConfigParser()
        parser.read_file(StringIO(buf))

        with self.assertRaises(fzsl.NoTypeError):
            fzsl.scanner_from_configparser('some-rule', parser)

        buf += "type: junk\n"
        parser.read_file(StringIO(buf))
        with self.assertRaises(fzsl.UnknownTypeError):
            fzsl.scanner_from_configparser('some-rule', parser)

        buf = "[some-rule]\ntype = simple\n"
        parser.read_file(StringIO(buf))
        with self.assertRaises(configparser.NoOptionError):
            fzsl.scanner_from_configparser('some-rule', parser)

        buf += "cmd = echo\n"
        parser.read_file(StringIO(buf))
        r = fzsl.scanner_from_configparser('some-rule', parser)
        self.assertIsInstance(r, fzsl.Scanner)

    def test_load_plugin(self):
        buf = '[rule]\ntype=python\npath=%s/plugins/test_plugin.py\n' % (
                TESTDIR,)

        parser = configparser.RawConfigParser()

        parser.read_file(StringIO(buf + "object=UnsuitableScanner\n"))
        scanner = fzsl.scanner_from_configparser('rule', parser)
        self.assertFalse(scanner.is_suitable(''))

        parser = configparser.RawConfigParser()
        parser.read_file(StringIO(buf + "object=ABCScanner\n"))
        scanner = fzsl.scanner_from_configparser('rule', parser)
        self.assertTrue(scanner.is_suitable(''))
        self.assertEqual(scanner.scan(''), ['a', 'b', 'c'])

        b = buf + "object=KwdsScanner\n"
        b += 'arg1=1\narg2=abc\narg3=some string\n'
        parser = configparser.RawConfigParser()
        parser.read_file(StringIO(b))
        scanner = fzsl.scanner_from_configparser('rule', parser)
        self.assertEqual(scanner.scan(''), ['1', 'abc', 'some string'])

        with self.assertRaises(fzsl.ConfigError):
            parser = configparser.RawConfigParser()
            parser.read_file(StringIO(buf + "object=BrokenScanner1\n"))
            scanner = fzsl.scanner_from_configparser('rule', parser)
                
        with self.assertRaises(fzsl.ConfigError):
            parser = configparser.RawConfigParser()
            parser.read_file(StringIO(buf + "object=BrokenScanner2\n"))
            scanner = fzsl.scanner_from_configparser('rule', parser)

        with self.assertRaises(fzsl.ConfigError):
            parser = configparser.RawConfigParser()
            parser.read_file(StringIO(buf + "object=BrokenScanner3\n"))
            scanner = fzsl.scanner_from_configparser('rule', parser)
 
def main():
    unittest.main()

if __name__ == '__main__':
    main()

