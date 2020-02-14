import os

from parser import Parser, ParserError
from database import Database


class WineReview:
    def __init__(self):
        self.quit = False

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

    def run(self):
        self.quit = False
        parser = Parser()
        database = Database()

        try:
            while not self.quit:
                print('> ', end='')
                x = input().strip()
                print('', end='', flush=True)

                try:
                    if not x:
                        continue
                    keywords = parser.parse_input(x)

                    if keywords["_keyword"].lower() == "help":
                        f = open("../doc/help.txt", "r")
                        print(f.read())
                        f.close()
                        continue
                    elif keywords['_keyword'].lower() == "load":
                        database.load_data()
                        continue

                except ValueError as e:
                    error = e.args[0]
                    self._handle_errors(error)
                    continue

                results = database.do_query(keywords)
                self._output_results(keywords, results)

        except KeyboardInterrupt:
            print('Quitting...')
            self.quit = True


if __name__ == '__main__':
    wine_review = WineReview()
    wine_review.run()
