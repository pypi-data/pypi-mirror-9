class CompareTwo(object):
    matchmap = {
        'operators_and_keywords_string_equal': {
            'points': 10,
            'label': 'Programs very similar. Look for use of query-replace.'
        },
        'operators_string_equal': {
            'points': 3,
            'label': 'Equal number of each operator used.'
        },
        'keywords_string_equal': {
            'points': 3,
            'label': 'Equal number of each keyword used.'
        },
        'total_operatorcount_equal': {
            'points': 1,
            'label': 'Equal number of total operators.'
        },
        'total_keywordcount_equal': {
            'points': 1,
            'label': 'Equal number of total keywords.'
        },
        'similar_functions': {
            # NOTE: No points for similar functions, they are collected
            # for each similarity, and scaled according to
            'label': 'Some of the functions look similar.'
        }
    }

    def __init__(self, parseresult1, parseresult2, scale=100, functionscale=1):
        """
        Parameters:
            parseresult1: A obj:`detektor.parseresult.ParseResults` object.
            parseresult2: A obj:`detektor.parseresult.ParseResults` object.
            scale (int): A number to multiply all the points produced on
                matches.
            functionscale (int): A number to multiply all the points produced on
                matches in functions. Should normally be a fair bit smaller
                than ``scale``.
        """
        self.parseresult1 = parseresult1
        self.parseresult2 = parseresult2
        self.scale = scale
        self.functionscale = functionscale

        # Points are collected by the _compare() function.
        # When the comparison has completed, the number of points indicates
        # how similar the two programs are.
        # You normally get this via meth:`.get_scaled_points`.
        self.points = 0

        # Just like ``self.points``, but collected when comparing functions.
        # You normally get this via meth:`.get_scaled_points`.
        self.functionpoints = 0

        #: List of matchids. We use get_description_for_matchid() to get a human
        #: readable string for a matchid.
        self.summary = []

        #: List of :obj:`.CompareTwo` objects for all
        #: functions within the two ParseResult objects.
        self.comparetwo_for_functions = []

    def __unicode__(self):
        return u'{parseresult1},{parseresult2} - Points: {points}, summary: {summary}'.format(
            parseresult1=self.parseresult1.get_label(),
            parseresult2=self.parseresult2.get_label(),
            points=self.get_scaled_points(),
            summary=self.get_summary_descriptions_as_string())

    def __str__(self):
        return unicode(self).encode('ascii', 'replace')

    def __repr__(self):
        return str(self)

    def get_parseresults_as_tuple(self):
        return (self.parseresult1, self.parseresult2)

    def get_scaled_points(self):
        return self.points * self.scale + self.functionpoints * self.functionscale

    def get_summary_descriptions_as_list(self):
        return [self.get_description_for_matchid(matchid) for matchid in self.summary]

    def get_summary_descriptions_as_string(self):
        return u' '.join(self.get_summary_descriptions_as_list())

    def get_description_for_matchid(self, matchid):
        return self.matchmap[matchid]['label']

    def get_points_for_matchid(self, matchid):
        return self.matchmap[matchid]['points']

    def _add_match_if_matched(self, matchid):
        if matchid is not None:
            self.summary.append(matchid)
            self.points += self.matchmap[matchid].get('points', 0)

    def compare(self):
        self._add_match_if_matched(self._compare_operators_and_keywords_string_equal())
        self._add_match_if_matched(self._compare_operators_string_equal())
        self._add_match_if_matched(self._compare_keywords_string_equal())
        self._add_match_if_matched(self._compare_total_operatorcount_equal())
        self._add_match_if_matched(self._compare_total_keywordcount_equal())
        if self.parseresult1.get_codeblocktype() == 'program' and self.parseresult2.get_codeblocktype() == 'program':
            self._add_match_if_matched(self._compare_functions())

    def compares_parseresults(self, parseresulta, parseresultb):
        """
        Returns True if the given ParseResult objects are the ones beeing compared
        by this CompareTwo. Order does not matter.
        """
        return {parseresulta, parseresultb} == {self.parseresult1, self.parseresult2}

    #
    #
    # Compare-methods
    # ===============
    # Each of them return a key from :obj:`.matchmap` if they find a match.
    # If they do not return None, we use :meth:`._add_match_if_matched` to
    # look them up in :obj:`.matchmap` to find the points awarded for the
    # match.
    #
    #

    def _compare_operators_and_keywords_string_equal(self):
        a = self.parseresult1
        b = self.parseresult2
        if a.get_operators_and_keywords_string() == b.get_operators_and_keywords_string():
            return 'operators_and_keywords_string_equal'
        else:
            return None

    def _compare_operators_string_equal(self):
        if self.parseresult1.get_operators_string() == self.parseresult2.get_operators_string():
            return 'operators_string_equal'
        else:
            return None

    def _compare_keywords_string_equal(self):
        if self.parseresult1.get_keywords_string() == self.parseresult2.get_keywords_string():
            return 'keywords_string_equal'
        else:
            return None

    def _compare_total_operatorcount_equal(self):
        if self.parseresult1.get_number_of_operators() == self.parseresult2.get_number_of_operators():
            return 'total_operatorcount_equal'
        else:
            return None

    def _compare_total_keywordcount_equal(self):
        if self.parseresult1.get_number_of_keywords() == self.parseresult2.get_number_of_keywords():
            return 'total_keywordcount_equal'
        else:
            return None

    def _compare_functions(self):
        self.comparetwo_for_functions = []
        functionparseresults = self.parseresult1.get_parsed_functions()
        for functionparseresult1 in self.parseresult1.get_parsed_functions():
            for functionparseresult2 in self.parseresult2.get_parsed_functions():
                comparetwo = CompareTwo(
                    functionparseresult1, functionparseresult2,
                    scale=self.functionscale)
                comparetwo.compare()
                self.comparetwo_for_functions.append(comparetwo)
                self.functionpoints += comparetwo.points
        if self.functionpoints:
            return 'similar_functions'
        else:
            return None


class CompareMany(object):
    """
    Used to compare many :class:`detektor.parseresult.ParseResult` objects.
    """
    def __init__(self, parseresults):
        """
        Parameters:
            parseresults (iterable):
                List/iterable of :class:`detektor.parseresult.ParseResult` objects.
        """
        self.results = []
        for index1, parseresult1 in enumerate(parseresults):
            for index2 in xrange(index1 + 1, len(parseresults)):
                parseresult2 = parseresults[index2]
                self.compare(parseresult1, parseresult2)

    def sort_by_points_descending(self):
        """
        Sort by points in place.
        """
        self.results.sort(cmp=lambda a, b: cmp(b.get_scaled_points(), a.get_scaled_points()))

    def __iter__(self):
        return self.results.__iter__()

    def compare(self, parseresult1, parseresult2):
        """
        Called once for each combination of all the ParseResult objects.
        Can be overridden to tune the comparison code.
        """
        comparetwo = CompareTwo(parseresult1, parseresult2)
        comparetwo.compare()
        self.add_to_results(comparetwo)

    def add_to_results(self, comparetwo):
        """
        Called once after each comparison of two parseresults are
        completed.

        Defaults to adding the given :class:`.CompareTwo`
        object to :obj:`.results`, but you can override this to
        limit what to add to results.

        Typically you may want to override this to avoid adding
        results with zero points::

            class MyCompareMany(detektor.comparer.CompareMany):
                def add_to_results(self, comparetwo):
                    if comparetwo.get_scaled_points() > 0:
                        super(MyCompareMany, self).add_to_results(comparetwo)
        """
        self.results.append(comparetwo)
