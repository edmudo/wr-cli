import argparse
import cmd
import os
import sys

from parser import Parser, ParserError
from database import Database


class WineReview(cmd.Cmd):
    DEFAULT_INTRO = ('Wine Review CLI. Type help or ? to list commands and '
                     'print documentation.')
    DEFAULT_PROMPT = '> '

    def __init__(self, *args, prompt_symbol=None, db_kwargs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.intro = self.DEFAULT_INTRO
        if prompt_symbol is None:
            self.prompt = self.DEFAULT_PROMPT
        else:
            self.prompt = prompt_symbol

        self.quit = False

        if db_kwargs is None:
            db_kwargs = {}

        self.parser = Parser()
        self.database = Database()

    def _format_reviewer_result(self, result):
        with open('format/format_reviewer.txt', 'r') as f:
            out_string = f.read().format(**result)
        return out_string

    def _format_wine_result(self, result):
        with open('format/format_wine.txt', 'r') as f:
            out_string = f.read().format(**result)
        return out_string

    def _format_review_result(self, result):
        result_wine = self._format_wine_result(result)
        result_reviewer = self._format_reviewer_result(result)

        with open('format/format_review.txt', 'r') as f:
            out_string = f.read().format(result_wine=result_wine,
                                         result_reviewer=result_reviewer,
                                         **result)

        return out_string

    def _output_results(self, kw, results):
        if not results:
            print('No results.')
            return

        for result in results:
            rows, cols = os.popen('stty size', 'r').read().split()
            sep = ''.join(['-' for i in range(int(cols))])

            if kw["_keyword"].lower() == "wine":
                output = self._format_wine_result(result)
            elif kw['_keyword'].lower() == "reviewer":
                output = self._format_reviewer_result(result)
            elif kw['_keyword'].lower() == "review":
                output = self._format_review_result(result)

            print(output.strip())

            if result is not results[-1]:
                print(sep)

    def _handle_errors(self, error):
        if error == ParserError.EMPTY_STRING:
            print('ERROR: Empty input.')
        elif error == ParserError.KEY_VALUE_PAIR:
            print('ERROR: Invalid key-value pair.')
        elif error == ParserError.INCOMPLETE_WRAP:
            print('ERROR: Unclosed quote.')

    def do_quit(self, arg):
        """Quit Wine Review CLI"""
        print('Quitting...')
        self.quit = True
        self.database.close()
        sys.exit()

    def do_load(self, arg):
        """Load data into the database."""
        self.database.load_data()

    def do_help(self, arg):
        """Show the help menu."""
        super().do_help(arg)

        if not arg:
            with open("../doc/help.txt", "r") as f:
                print(f.read())

    def default(self, line):
        try:
            keywords = self.parser.parse_input(line)
        except ValueError as e:
            error = e.args[0]
            self._handle_errors(error)
            return

        results = self.database.do_query(keywords)
        self._output_results(keywords, results)

    def cmdloop(self, intro=None):
        if intro:
            print(intro)
        else:
            print(self.intro)

        try:
            super().cmdloop(intro='')
        except KeyboardInterrupt:
            print()
            self.do_quit(None)


def main():
    ap = argparse.ArgumentParser(description='Start the Wine Review CLI.')
    ap.add_argument('-p', '--prompt-symbol', type=str, default=None,
                    help='The default prompt symbol.')
    ap.add_argument('-s', '--schema-path', type=str, default=None,
                    help='The schema path.')
    ap.add_argument('-d', '--data-dir', type=str, default=None,
                    help='The data directory of containing the CSV files.')
    ap.add_argument('--database-path', type=str, default=None,
                    help='The database path to read and write the database.')
    args = ap.parse_args()

    db_kwargs = dict(schema_path=args.schema_path,
                     data_path=args.data_dir,
                     database_path=args.database_path
                     )

    wine_review = WineReview(prompt_symbol=args.prompt_symbol,
                             db_kwargs=db_kwargs)
    wine_review.cmdloop()


if __name__ == '__main__':
    main()
