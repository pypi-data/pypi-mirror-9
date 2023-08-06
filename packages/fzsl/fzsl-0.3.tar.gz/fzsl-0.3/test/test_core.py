import os
import sys
import unittest

TESTDIR = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.realpath(os.path.join(TESTDIR, '..')))

import fzsl

class SimpleScannerTest(unittest.TestCase):
    def setUp(self):
        self.fm = fzsl.FuzzyMatch()

    def test_library(self):
        self.assertEqual(0, self.fm.n_matches)
        self.assertEqual(0, self.fm.n_files)
        self.assertEqual([], self.fm.top_matches())

        with self.assertRaises(KeyError):
            self.fm.score('a')

        self.fm.add_files(['a', 'b', 'c'])
        self.assertEqual(3, self.fm.n_matches)
        self.assertEqual(3, self.fm.n_files)
        self.assertEqual(['a', 'b', 'c'], sorted(self.fm.top_matches()))

        self.assertEqual(0, self.fm.score('a'))
        self.assertEqual(0, self.fm.start('a'))
        self.assertEqual(0, self.fm.end('a'))

        self.fm.reset_files([])
        self.assertEqual(0, self.fm.n_matches)
        self.assertEqual(0, self.fm.n_files)
        self.assertEqual([], self.fm.top_matches())

    def test_update_scores(self):
        files = ['abc/def/ghi', 'abc/d', 'abc/ggg', 'z/1', 'z/2', 'zz/3']

        self.fm.add_files(files)

        self.fm.update_scores("abc")
        self.assertEqual(3, self.fm.n_matches)
        matches = self.fm.top_matches()

        self.fm.update_scores("abcd")
        self.assertEqual(2, self.fm.n_matches)

        self.fm.update_scores("abc")
        self.assertEqual(3, self.fm.n_matches)
        self.assertEqual(matches, self.fm.top_matches())

        self.fm.update_scores("ab")
        self.fm.update_scores("a")
        self.fm.update_scores("")
        self.assertEqual(self.fm.n_matches, self.fm.n_files)

    def test_prefer_latter(self):
        files = ['prefix/abc/stuff', 'abc/d', 'some/prefix/abc']

        self.fm.add_files(files)
        self.fm.update_scores("abc")
        self.assertEqual("some/prefix/abc", self.fm.top_matches(1)[0])

    def test_prefer_shorter(self):
        files = ["a/z/b/z/c", "a/b/c", "a/bbbbb/c"]
        
        self.fm.add_files(files)
        self.fm.update_scores("abc")
        self.assertEqual("a/b/c", self.fm.top_matches(1)[0])

    def test_start_end(self):
        files = ['abc/def/ghi', 'ggg/a/b/ggg/c/d', 'ggg/abc']

        self.fm.add_files(files)
        self.fm.update_scores("abc")

        self.assertEqual(0, self.fm.start('abc/def/ghi'))
        self.assertEqual(2, self.fm.end('abc/def/ghi'))

        self.assertEqual(4, self.fm.start('ggg/a/b/ggg/c/d'))
        self.assertEqual(12, self.fm.end('ggg/a/b/ggg/c/d'))

        self.assertEqual(4, self.fm.start('ggg/abc'))
        self.assertEqual(6, self.fm.end('ggg/abc'))

    def test_ignorecase(self):
        files = ['abc/def/ghi', 'abc/d', 'abc/ggg', 'z/1', 'z/2', 'zz/3']

        self.fm.add_files(files)

        self.fm.update_scores("ABC")
        self.assertEqual(3, self.fm.n_matches)


def main():
    unittest.main()

if __name__ == '__main__':
    main()

