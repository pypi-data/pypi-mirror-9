from detektor.languageparser.java import JavaLanguageParser
from detektor.languageparser.python import PythonLanguageParser


default_languageparsers = {
    'java': JavaLanguageParser,
    'python': PythonLanguageParser,
}

def make_parser(language):
    """
    Make a Detektor language parser for the given language.

    Example::

        parser = make_parser('python')
        sourcecodes = [
            'print "hello world"',
            'print "This is a test"'
        ]

        # Treat both the sourcecodes as a single "program",
        # and collect the results in a single ParseResult object:
        parseresult = parser.make_parseresult()
        for sourcecode in sourcecodes:
            parser.parse(sourcecode, parseresult)
        print parseresult

        # ... or treat them as separate programs:
        results = []
        for sourcecode in sourcecodes:
            parseresult = parser.make_parseresult()
            parser.parse(sourcecode, parseresult)
            results.append(parseresult)

    """
    return default_languageparsers[language]()
