import unittest

from wr_cli.wrparser import Parser, ParserError


class TestParser(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = Parser()

    def test_empty(self):
        try:
            self.parser.parse_input('')
        except ValueError as e:
            self.assertEqual(e.args[0], ParserError.EMPTY_STRING)

    def test_kvpair(self):
        try:
            self.parser.parse_input('review wine')
        except ValueError as e:
            self.assertEqual(e.args[0], ParserError.KEY_VALUE_PAIR)

    def test_badwrap(self):
        try:
            self.parser.parse_input('review "wine')
        except ValueError as e:
            self.assertEqual(e.args[0], ParserError.INCOMPLETE_WRAP)

    def test_other(self):
        # Map the input string and the expected result
        cases = {"review province 'Burlington'": None,
                 'review province "Burlington"': None,
                 'review province      "Burlington"': None,
                 'review province \'Burlington"': ParserError.INCOMPLETE_WRAP,
                 "review province 'Burlington' title \"Wine James'\"": None,
                 " review title \"Martha's Best Wine\" province 'Las Vegas' reviewer Mike ": None,
                 'review province "Burlington\' "VT"': ParserError.INCOMPLETE_WRAP
                 }

        for string, expected in cases.items():
            try:
                self.parser.parse_input(string)
            except ValueError as e:
                self.assertEqual(e.args[0], expected, msg=f'Failed on case `{string}`')
