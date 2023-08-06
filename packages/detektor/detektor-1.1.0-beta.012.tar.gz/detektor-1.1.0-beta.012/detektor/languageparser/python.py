from detektor.codefilter.normalizeoperatorwhitespace import NormalizeOperatorWhitespace
from detektor.languageparser.shlexparser import ShlexLanguageParserBase
import keyword


class PythonLanguageParser(ShlexLanguageParserBase):
    operators = {
        '!', '+', '-', '*', '**', '/', '//', '%', '<<', '>>', '&', '|',
        '=', '%=', '/=', '//=', '**=', '*=', '-=',
        '^', '~', '<', '>', '<=', '>=', '==', '!=', '<>',
    }
    keywords = set(keyword.kwlist)
    sourcecode_preprocessor_classes = [
        NormalizeOperatorWhitespace
    ]
