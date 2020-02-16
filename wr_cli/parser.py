from enum import Enum


class ParserError(Enum):
    EMPTY_STRING = 0
    KEY_VALUE_PAIR = 1
    INCOMPLETE_WRAP = 2


class Parser:
    def __init__(self, wrap_chars='\'"', separator_chars=' '):
        self.wrap_chars = wrap_chars
        self.separator_chars = separator_chars

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
        state = None
        for token in user_input + ' ':
            if token in self.wrap_chars and state is None:
                state = token
                continue
            elif token == state:
                state = None
                continue

            if token in self.separator_chars and state is None:
                string = "".join(stack)
                if string:
                    separated_string.append(string)
                stack.clear()
            else:
                stack.append(token)

        if state is not None:
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