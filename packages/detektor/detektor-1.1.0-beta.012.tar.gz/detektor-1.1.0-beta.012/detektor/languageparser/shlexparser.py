import shlex

from detektor.languageparser.base import LanguageParserBase
from detektor.parseresult import EditableParseResult


class ShlexLanguageParserBase(LanguageParserBase):
    #: Set of operators supported by the language.
    #: # E.g.: ``operators = {'<', '==', '>', '&&'}``
    operators = None

    #: Set of keywords supported by the language.
    #: # E.g.: ``keywords = {'if', 'for', 'and', 'or'}``
    keywords = None

    def __init__(self):
        super(ShlexLanguageParserBase, self).__init__()

    def get_parseresultclass(self):
        return EditableParseResult

    def make_parseresult(self, codeblocktype='program', label=None):
        parseresult_class = self.get_parseresultclass()
        return parseresult_class(
            set_of_all_operators=self.operators,
            set_of_all_keywords=self.keywords,
            codeblocktype=codeblocktype,
            label=label)

    def get_shlexobject(self, sourcecode):
        """
        Get a ``shlex.shlex`` object. Can be overridden to
        customize the lexer.
        """
        lexer = shlex.shlex(sourcecode)
        lexer.wordchars += ''.join(self.operators)
        return lexer

    def shlex_parse_token(self, parseresult, token):
        if token in self.keywords:
            parseresult.add_keyword(token)
        elif token in self.operators:
            parseresult.add_operator(token)

    def parse_program(self, parseresult, sourcecode):
        lexer = self.get_shlexobject(sourcecode)
        while True:
            try:
                token = lexer.get_token()
            except ValueError:
                break
            else:
                if not token:
                    break
                self.shlex_parse_token(parseresult, token)
