
class ExtractedFunction(object):
    def __init__(self, name, sourcecode):
        """
        Parameters:
            name (unicode): The name of the function.
             Should contain as much unique info as possible about
             the function. This means that for languages where
             a function with the same name but different arguments
             or return types denotes separate functions, the arguments and return
             type should be included in the name. Should not contain any newlines,
             and all whitespace should be collapsed to a single space.
            description (unicode): The sourcecode of the function.
              This should not include the signature, only the body of the
              function.
        """
        self.name = name
        self.sourcecode = sourcecode

    def __unicode__(self):
        return u'{} {}'.format(self.name, self.sourcecode)

    def __str__(self):
        return unicode(self).encode('ascii', 'replace')

    def __repr__(self):
        return 'ExtractedFunction({})'.format(self)


class BaseFunctionExtractor(object):
    """
    Abstract base class for function extractors.

    A function extractor takes a sourcecode blob and
    extracts a list of functions and methods from it.
    """
    def extract(self, sourcecode):
        """
        Extract the functions in ``sourcecode`` and return the result as a
        list of :class:`ExtractedFunction` objects.

        Must be overridden in subclasses.
        """
        raise NotImplementedError()
