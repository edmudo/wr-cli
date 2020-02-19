from enum import Enum


class ParserError(Enum):
    EMPTY_STRING = 0
    KEY_VALUE_PAIR = 1
    INCOMPLETE_WRAP = 2
    INVALID_OPERATOR = 3


class Parser:
    VALID_COMPARISON_OPS = ['>=', '<=', '<', '>', '=']

    def __init__(self, wrap_chars='\'"', separator_chars=' '):
        self.wrap_chars = wrap_chars
        self.separator_chars = separator_chars
        self.comparison_chars = set(''.join(Parser.VALID_COMPARISON_OPS))

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
        separated_string = []

        stack = []
        comp_op = ''
        wrap_char = ''
        for token in user_input + ' ':
            if token in self.wrap_chars and not wrap_char:
                wrap_char = token
                continue
            elif token in self.comparison_chars and not wrap_char:
                comp_op += token
                continue
            elif token == wrap_char:
                wrap_char = ''
                continue

            if token in self.separator_chars and not wrap_char:
                string = "".join(stack)

                if comp_op and comp_op not in Parser.VALID_COMPARISON_OPS:
                    raise ValueError(ParserError.INVALID_OPERATOR)

                if string and comp_op:
                    separated_string.append((comp_op, string))
                    comp_op = ''
                elif string:
                    separated_string.append(string)

                stack.clear()
            else:
                stack.append(token)

        if wrap_char:
            raise ValueError(ParserError.INCOMPLETE_WRAP)

        return separated_string

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
        user_input = user_input.strip()

        if len(user_input) == 0:
            raise ValueError(ParserError.EMPTY_STRING)

        arr_user_string = self._separate_tokens(user_input)

        if len(arr_user_string) % 2 == 0 :
            raise ValueError(ParserError.KEY_VALUE_PAIR)
        
        keyword = arr_user_string.pop(0)
        keywords = dict(zip(arr_user_string[::2], arr_user_string[1::2]))
        keywords["_keyword"] = keyword

        return keywords
