from enum import Enum


class ParserError(Enum):
    EMPTY_STRING = 0
    KEY_VALUE_PAIR = 1
    INCOMPLETE_WRAP = 2


class Parser:
    def strip_ends(self, s, chars):
        match_start = any([c == s[0] for c in chars])
        match_end = any([c == s[-1] for c in chars])

        if match_start:
            s = s[1:]

        if match_end:
            s = s[:-1]

        return s

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
        valid_wrap_characters = "'\""
        arr_user_string = user_input.split()

        stack = []
        final_arr_user_string = []
        wrap_character= ""
        for token in arr_user_string:
            # keep the original token for comparisons, modified token for
            # inserting into stack
            modified_token = self.strip_ends(token, "\"'")

            contain_start_wrap = any([token[0] == character
                                      for character in valid_wrap_characters])

            if contain_start_wrap:
                contain_close_wrap = any([token[-1] == token[0] or token[-1] == wrap_character
                                          for character in valid_wrap_characters])
            else:
                contain_close_wrap = False

            if len(stack) != 0 and contain_close_wrap:
                stack.append(modified_token)
                final_token = " ".join(stack)
                final_arr_user_string.append(final_token)
                stack.clear()
            elif len(stack) != 0 or (contain_start_wrap and not contain_close_wrap):
                if contain_start_wrap:
                    wrap_character = token[0]
                stack.append(modified_token)
            else:
                final_arr_user_string.append(modified_token)

        if len(stack) != 0:
            raise ValueError(ParserError.INCOMPLETE_WRAP)

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

        try:
            arr_user_string = self._separate_tokens(user_input)
        except ValueError as e:
            return e

        if len(arr_user_string) % 2 == 0 :
            return ValueError(ParserError.KEY_VALUE_PAIR)
        
        keyword = arr_user_string.pop(0)
        keywords = dict(zip(arr_user_string[::2], arr_user_string[1::2]))
        keywords["_keyword"] = keyword

        return keywords


def test():
    parser = Parser()
    print(parser.parse_input("review city 'Burlington'"))
    print(parser.parse_input('review city "Las Vegas"'))
    print(parser.parse_input('review city "Burlington"'))
    print(parser.parse_input(" review city 'Burlington' 'Las Vegas' 'London' "))
    print(parser.parse_input('review city "Burlington" "Las Vegas"'))

    # print(parser.parse_input('review city'))
    # print(parser.parse_input(''))


if __name__ == "__main__":
    test()
