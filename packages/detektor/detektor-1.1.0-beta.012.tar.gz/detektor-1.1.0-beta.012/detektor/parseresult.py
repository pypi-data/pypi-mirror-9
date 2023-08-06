
class ParseResult(object):
    """
    Parse result abstract class.

    The parsers produce subclasses of :class:`.EditableParseResult`. That is OK for
    small datasets, but when you compare huge amounts of code you will want to
    serialize the results to avoid re-processing the same peace of code. To do
    this, you use meth:`EditableParseResult.serialize_as_dict`, and
    load it later with :meth:`.UneditableParseResult`.

    All code for comparing parse results should use the methods in this interface,
    not the attributes made available by EditableParseResult or UneditableParseResult.
    """
    def __unicode__(self):
        return \
            u'{classname}('\
            u'keywords={keywords!r}, '\
            u'operators={operators!r})'.format(
                classname=self.__class__.__name__,
                keywords=self.get_keywords_string(),
                operators=self.get_operators_string())

    def __str__(self):
        return unicode(self).encode('ascii', 'replace')

    def __repr__(self):
        return str(self)

    def get_codeblocktype(self):
        raise NotImplementedError()

    def get_label(self):
        raise NotImplementedError()

    def get_operators_string(self):
        raise NotImplementedError()

    def get_keywords_string(self):
        raise NotImplementedError()

    def get_number_of_operators(self):
        raise NotImplementedError()

    def get_number_of_keywords(self):
        raise NotImplementedError()

    def get_operators_and_keywords_string(self):
        raise NotImplementedError()

    def get_normalized_sourcecode(self):
        raise NotImplementedError()

    def get_parsed_functions(self):
        raise NotImplementedError()


class UneditableParseResult(object):
    """

    """
    def __init__(self, dumped_dict):
        """
        Parameters:
            dumped_dict: A dict produced by
        """
        self._dumped_dict = dumped_dict
        self._parsed_functions = None

    def get_codeblocktype(self):
        return self._dumped_dict['codeblocktype']

    def get_label(self):
        return self._dumped_dict['label']

    def get_operators_string(self):
        return self._dumped_dict['operators_string']

    def get_keywords_string(self):
        return self._dumped_dict['keywords_string']

    def get_number_of_operators(self):
        return self._dumped_dict['number_of_operators']

    def get_number_of_keywords(self):
        return self._dumped_dict['number_of_keywords']

    def get_operators_and_keywords_string(self):
        return self._dumped_dict['operators_and_keywords_string']

    def get_normalized_sourcecode(self):
        return self._dumped_dict['normalized_sourcecode']

    def get_parsed_functions(self):
        if self._parsed_functions is None:
            self._parsed_functions = map(UneditableParseResult, self._dumped_dict['parsed_functions'])


class EditableParseResult(ParseResult):
    """
    Language parsers create objects of this class to store their results.
    """

    def __init__(self, codeblocktype, label, set_of_all_operators, set_of_all_keywords):
        """
        Parameters:
            codeblocktype: The type of code this result is for. Must be one of: "program", "function".
            label: A label that can be set to give the ParseResult a name/context.
                Used to name functions in the list of functions
                when the codeblocktype is ``function``.
            set_of_all_keywords (set): A set of keywords supported by this language.
                used to create stable digest of keywords and the number of occurrences.
            set_of_all_operators (set): A set of operators supported by this language.
                used to create stable digest of operators and the number of occurrences.
        """
        self.codeblocktype = codeblocktype
        self.label = label

        # Dict mapping operators to the number of occurrences of that operator.
        self.operators = dict.fromkeys(set_of_all_operators, 0)

        # Dict mapping keywords to the number of occurrences of that keyword.
        self.keywords = dict.fromkeys(set_of_all_keywords, 0)

        self.number_of_operators = 0
        self.number_of_keywords = 0

        # A string with all the operators and keywords appended in the order
        # they occur in the code. Handled automatically in :meth:`.add_keyword`
        # and :meth:`.add_operator`, so you should not have to edit this.
        self.operators_and_keywords_string = u''

        # Should be a string that when compared with another ParseResult
        # means that the ParseResults are very similar if they match.
        # This is typically populated by a smart language parser that
        # normalizes sourcecode in a way that makes it very unlikely that
        # programs differ if this string is 100% equal in two programs.
        # If the language does not use this, it should be left as ``None``,
        # to indicate that this should be ignored when comparing programs.
        self.normalized_sourcecode = None

        # List of class:`.ParseResult` objects - one for each parsed function.
        # This is only used when ``codeblocktype`` is ``program``.
        self.parsed_functions = []

    def is_program(self):
        return self.codeblocktype == 'program'

    def add_keyword(self, keyword):
        self.number_of_keywords += 1
        self.keywords[keyword] += 1
        self.operators_and_keywords_string += keyword

    def add_operator(self, operator):
        self.number_of_operators += 1
        self.operators[operator] += 1
        self.operators_and_keywords_string += operator

    def _make_string_from_count_dict(self, dct):
        return '_'.join([str(dct[key]) for key in sorted(dct.keys())])

    def get_codeblocktype(self):
        return self.codeblocktype

    def get_label(self):
        return self.label

    def get_operators_string(self):
        return self._make_string_from_count_dict(self.operators)

    def get_keywords_string(self):
        return self._make_string_from_count_dict(self.keywords)

    def get_number_of_operators(self):
        return self.number_of_operators

    def get_number_of_keywords(self):
        return self.number_of_keywords

    def get_operators_and_keywords_string(self):
        return self.operators_and_keywords_string

    def get_normalized_sourcecode(self):
        return self.normalized_sourcecode

    def get_parsed_functions(self):
        return self.parsed_functions

    def serialize_as_dict(self):
        return {
            'codeblocktype': self.get_codeblocktype(),
            'label': self.get_label(),
            'operators_string': self.get_operators_string(),
            'keywords_string': self.get_keywords_string(),
            'number_of_operators': self.get_number_of_operators(),
            'number_of_keywords': self.get_number_of_keywords(),
            'operators_and_keywords_string': self.get_operators_and_keywords_string(),
            'normalized_sourcecode': self.get_normalized_sourcecode(),
            'parsed_functions': [function.serialize_as_dict() for function in self.parsed_functions],
        }
