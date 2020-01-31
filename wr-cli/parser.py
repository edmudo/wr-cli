from enum import Enum


class ParserError(Enum):
    EMPTY_STRING = 0
    KEY_VALUE_PAIR = 1


class Parser:
    def _separate_tokens(self, user_input):
        """
        Helper to separate parts of the string according to some rules.

        Parameters
        ----------
        user_input : string
            input string

        Returns
        -------
        list
            array of separated string tokens
        """
        arr_user_string = user_input.split()

        stack = []
        final_arr_user_string = []
        for token in arr_user_string:
            # keep the original token for comparisons, modified token for
            # inserting into stack
            modified_token = token.replace("\"", "")

            if len(stack) != 0 and "\"" in token:
                stack.append(modified_token)

                final_token = " ".join(stack)
                final_arr_user_string.append(final_token)

                stack.clear()
            elif len(stack) != 0 or ("\"" in token and token[-1] != "\""):
                stack.append(modified_token)
            else:
                final_arr_user_string.append(modified_token)

        return final_arr_user_string

    def parse_input(self, user_input):
        """
        Map keys to values from a user_input.

        Parameters
        ----------
        user_input : string
            input string

        Returns
        -------
        dict
            key-value pairs from the user input string
        """
        user_input = user_input.rstrip()

        if len(user_input) == 0:
            return ValueError(ParserError.EMPTY_STRING)

        arr_user_string = self._separate_tokens(user_input)
        if len(arr_user_string) % 2 == 0:
            return ValueError(ParserError.KEY_VALUE_PAIR)
        
        keyword = arr_user_string.pop(0)
        keywords = dict(zip(arr_user_string[::2], arr_user_string[1::2]))
        keywords["_keyword"] = keyword

        return keywords


def test():
    parser = Parser()
    print(parser.parse_input('review city "Burlington"'))
    print(parser.parse_input('review city "Las Vegas"'))
    print(parser.parse_input(' review city Burlington '))
    print(parser.parse_input('review city'))
    print(parser.parse_input(''))


if __name__ == "__main__":
    test()
