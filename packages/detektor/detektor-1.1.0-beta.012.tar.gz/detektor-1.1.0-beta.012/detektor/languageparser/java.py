from detektor.codefilter.normalizeoperatorwhitespace import NormalizeOperatorWhitespace
from detektor.languageparser.shlexparser import ShlexLanguageParserBase
from detektor.functionextractor.clike import ClikeFunctionExtractor


class JavaLanguageParser(ShlexLanguageParserBase):
    # http://docs.oracle.com/javase/tutorial/java/nutsandbolts/opsummary.html
    operators = {
        '!', '+', '-', '*', '**', '/', '//', '%', '<<', '>>', '>>>', '&', '|',
        '++', '--', '&&', '||', '?:',
        '=', '+=', '-=', '*=',
        '^', '~', '<', '>', '<=', '>=', '==', '!=',
    }

    # http://docs.oracle.com/javase/tutorial/java/nutsandbolts/_keywords.html
    keywords = {
        'abstract', 'continue', 'for', 'new', 'switch',
        'assert', 'default', 'package', 'synchronized',
        'boolean', 'do', 'if', 'private', 'this',
        'break', 'double', 'implements', 'protected', 'throw',
        'byte', 'else', 'import', 'public', 'throws',
        'case', 'enum', 'instanceof', 'return', 'transient',
        'catch', 'extends', 'int', 'short', 'try',
        'char', 'final', 'interface', 'static', 'void',
        'class', 'finally', 'long', 'strictfp', 'volatile',
        'float', 'native', 'super', 'while',
    }

    sourcecode_preprocessor_classes = [
        NormalizeOperatorWhitespace
    ]

    def __init__(self, *args, **kwargs):
        super(JavaLanguageParser, self).__init__(*args, **kwargs)
        self.function_extractor = ClikeFunctionExtractor(keywords=self.keywords)

    def extract_functionsourcecode(self, sourcecode):
        return self.function_extractor.extract(sourcecode)
