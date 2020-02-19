import argparse
import cmd
import os
import sys

from wrparser import Parser, ParserError
from database import Database, DatabaseError
from resources import ResourcePath as P


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
        self.parser = Parser()
        self.database = Database()

        if db_kwargs is None:
            db_kwargs = {}

        self.parser = Parser()
        self.database = Database(**db_kwargs)
        self.lastquery = ''

    def _format_result(self, path, result):
        with open(path, 'r') as f:
            out_string = f.read().format(**result)
        return out_string

    def _concat_results(self, kw, results):
        if not results:
            print('No results.')
            return

        try:
            cols, _ = os.get_terminal_size()
        except OSError:
            cols = 10
        sep = ''.join(['-' for i in range(int(cols))])

        output_all = ''
        for result in results:
            if kw["_keyword"].lower() == "wine":
                output = self._format_result(P.WINEF_PATH, result)
            elif kw['_keyword'].lower() == "reviewer":
                output = self._format_result(P.REVIEWERF_PATH, result)
            elif kw['_keyword'].lower() == "review":
                wine_out = self._format_result(P.WINEF_PATH, result)
                reviewer_out = self._format_result(P.REVIEWERF_PATH, result)

                result = dict(result_wine=wine_out, result_reviewer=reviewer_out,
                              **result)
                output = self._format_result(P.REVIEWF_PATH, result)

            output_all += output.strip() + '\n'

            if result is not results[-1]:
                output_all += sep + '\n'
        return output_all

    def _handle_errors(self, error):
        if error == ParserError.EMPTY_STRING:
            print('ERROR: Empty input.')
        elif error == ParserError.KEY_VALUE_PAIR:
            print('ERROR: Invalid key-value pair.')
        elif error == ParserError.INCOMPLETE_WRAP:
            print('ERROR: Unclosed quote.')
        elif error == ParserError.INVALID_OPERATOR:
            print('ERROR: Invalid comparison operator.')
        elif error == DatabaseError.NO_SUCH_TABLE:
            print('ERROR: Data table does not exist.')
        elif error == DatabaseError.NO_SUCH_COLUMN:
            print('ERROR: Data column does not exist.')
        elif error == DatabaseError.UNKNOWN_ERROR:
            print('ERROR: Database error.')
        elif error == DatabaseError.MISSING_DATA:
            print('ERROR: Missing data files.')
        elif error == DatabaseError.MISSING_SCHEMA:
            print('ERROR: Missing table schema.')

    def do_help(self, arg):
        """Show the help menu."""
        super().do_help(arg)

        if not arg:
            with open("../doc/help.txt", "r") as f:
                print(f.read())

    def do_load(self, arg):
        """Load data into the database."""
        try:
            self.database.load_data()
        except FileNotFoundError as e:
            error = e.args[2]
            self._handle_errors(error)
            return

    def do_max(self, arg):
        """MAX
        Set the maximum number of results to show.

        syntax: max <num>
        """
        if not arg:
            print('Current result maximum:', self.database.limit)
            return

        try:
            limit = int(arg)
            self.database.limit = limit
        except ValueError:
            print('Invalid argument(s)')
            self.do_help('max')

    def do_page(self, arg):
        """PAGE
        Show the next page of results up to the specified maximum.
        
        syntax: page <num>
        """
        try:
            page_offset = int(arg)
            if self.lastquery:
                self.default(self.lastquery, page_offset=page_offset)
        except ValueError:
            print('Invalid argument(s)')
            self.do_help('page')

    def do_quit(self, arg):
        """Quit Wine Review CLI"""
        print('Quitting...')
        self.quit = True
        self.database.close()
        sys.exit()

    def default(self, line, **kwargs):
        valid_keywords = ["wine", "reviewer", "review"]

        try:
            keywords = self.parser.parse_input(line)
            results = self.database.do_query(keywords, **kwargs)
        except ValueError as e:
            error = e.args[0]
            self._handle_errors(error)
            return

        if keywords['_keyword'] not in valid_keywords:
            print('Invalid keyword. Type help or ? to see valid keywords.')
            return

        output = self._concat_results(keywords, results)
        print(output)

        if results:
            self.lastquery = line

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

    db_kwargs = dict(data_dir=args.data_dir,
                     db_path=args.database_path,
                     schema_path=args.schema_path)

    wine_review = WineReview(prompt_symbol=args.prompt_symbol,
                             db_kwargs=db_kwargs)
    wine_review.cmdloop()


if __name__ == '__main__':
    main()
