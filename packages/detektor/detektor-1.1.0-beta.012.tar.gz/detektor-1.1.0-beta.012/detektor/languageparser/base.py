

class LanguageParserBase(object):
    """
    Abstract base class for parsing sourcecode.

    A parser is typically initialized once and used multiple times
    in the same thread.


    Example of how to use an implementation of LanguageParserBase::

        parser = SomeLanguageParser()
        sourcecodes = [
            'print "hello world"',
            'print "This is a test"'
        ]

        # Treat both the sourcecodes as a single "program",
        # and collect the results in a single EditableParseResult object:
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


    An important thing to notice here is that the parser is
    initialized once and used many times. Some parsers may do
    expensive optimizations when initialized, so it is a
    good idea to re-use the parser instance instead of recreating
    it each time.

    .. warning::

        A LanguageParserBase instance is not thread safe. It
        stores state on the object during each call to :meth:`.parse`.
    """

    #: List of preprocessors
    sourcecode_preprocessor_classes = []

    def __init__(self):
        """
        Parameters:
            sourcecode: The source code to parse.
            codeblocktype: Describes what the sourcecode is. Must be one of: "program", "function".
            label: A label that can be set to give the EditableParseResult a name/context.
                Typically used to give functions a name, but can also be used when
                ``codeblocktype`` is ``program``.
        """
        self.sourcecode_preprocessors = [cls(self) for cls in self.sourcecode_preprocessor_classes]

    def preprocess_sourcecode(self, sourcecode):
        """
        You can override this to preprocess the sourcecode before
        the parsing is started.
        """
        for sourcecode_preprocessor in self.sourcecode_preprocessors:
            sourcecode = sourcecode_preprocessor.filter(sourcecode)
        return sourcecode

    def make_parseresult(self, codeblocktype, label):
        """
        Parameters:
            codeblocktype: Describes what the sourcecode is. Must be one of: "program", "function".
            label: A label that can be set to give the EditableParseResult a name/context.
                Typically used to give functions a name, but can also be used when
                ``codeblocktype`` is ``program``.

        Returns:
            A :class:`detektor.parseresult.EditableParseResult` object.
        """
        raise NotImplementedError()

    def parse_program(self, sourcecode, parseresult):
        raise NotImplementedError()

    def get_function_sourcecode_parser_class(self):
        """
        Returns the class to use to parse functions.
        Can be overridden if you need to use a different class
        to parse functions than the one you use to parse the
        """
        return self.__class__

    def extract_functionsourcecode(self, sourcecode):
        """
        Extract the sourcecode of functions from the ``sourcecode`` and
        return a list of ``(functionname, functionsourcecode)`` tuples.
        """
        return []

    def parse_functions(self, sourcecode):
        function_sourcecode_parser_class = self.get_function_sourcecode_parser_class()
        parsed_functions = []
        for extractedfunction in self.extract_functionsourcecode(sourcecode):
            parseresult = self.make_parseresult(
                codeblocktype='function', label=extractedfunction.name)
            function_sourcecode_parser_class().parse(parseresult, extractedfunction.sourcecode)
            parsed_functions.append(parseresult)
        return parsed_functions

    def parse(self, parseresult, sourcecode):
        """
        Parse the ``sourcecode``, add the results to parseresult. Must be
        overridden in subclasses.

        Parameters:
            sourcecode: The sourcecode to parse as a string/unicode.
            parseresult: A :class:`detector.parser_result.EditableParseResult` object.
        """
        sourcecode = self.preprocess_sourcecode(sourcecode)
        self.parse_program(parseresult, sourcecode)
        if parseresult.is_program():
            parseresult.parsed_functions = self.parse_functions(sourcecode)
