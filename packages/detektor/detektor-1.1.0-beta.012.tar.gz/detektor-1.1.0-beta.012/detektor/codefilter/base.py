

class CodeFilterBase(object):
    """
    A codefilter is a peace of code that does something to some blob of
    sourcecode and returns the modified sourcecode.

    It is perfect for making reusable filters that normalized code
    as part of parsing the code.

    Note that functionally, you can just as easily override the
    :meth:`~detektor.languageparser.base.LanguageParserBase.parse` method
    of a parser and do this preprocessing, but that makes it hard-coupled
    to that parser (which is bad for filters/preprocessors that many
    languages may need).
    """

    def __init__(self, languageparser):
        """
        Parameters:
            languageparser: The :class:`detektor.languageparser.base.LanguageParserBase`
                this filter is to be applied to.
        """
        self.languageparser = languageparser

    def filter(self, sourcecode):
        """
        This method performs the filtering.
        Must be overridden in subclasses.

        Parameters:
            sourcecode: The sourcecode to filter.

        Returns:
            The modified ``sourcecode``.
        """
        raise NotImplementedError()
