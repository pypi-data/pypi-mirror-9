import re
from detektor.codefilter.base import CodeFilterBase


class NormalizeOperatorWhitespace(CodeFilterBase):
    """
    Filter to make put a single space between all operators
    and their surrounding code.

    Makes simple lexers like shlex treat the opeators as words.

    Requires the language parser object to have ``operators`` and
    ``keywords`` attributes (see :class:`detektor.languageparser.shlexparser.ShlexLanguageParserBase`)
    """
    def __init__(self, languageparser):
        super(NormalizeOperatorWhitespace, self).__init__(languageparser)
        normalize_whitespace_operators = [re.escape(operator) \
                                          for operator in languageparser.operators]
        self.normalize_whitespace_pattern = re.compile(
            r'(\w)\s*(' +
            '|'.join(normalize_whitespace_operators) +
            r')\s*(\w)')

    def filter(self, sourcecode):
        return self.normalize_whitespace_pattern.sub(r'\1 \2 \3', sourcecode)
