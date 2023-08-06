import unittest
import mock
from detektor.comparer import CompareTwo, CompareMany


class TestCompareTwo(unittest.TestCase):

    def test_compare_operators_and_keywords_string_equal_nomatch(self):
        a = mock.MagicMock()
        a.get_operators_and_keywords_string.return_value = 'a'
        b = mock.MagicMock()
        b.get_operators_and_keywords_string.return_value = 'b'
        self.assertEqual(
            CompareTwo(a, b)._compare_operators_and_keywords_string_equal(),
            None)

    def test_compare_operators_and_keywords_string_equal(self):
        a = mock.MagicMock()
        a.get_operators_and_keywords_string.return_value = 'x'
        b = mock.MagicMock()
        b.get_operators_and_keywords_string.return_value = 'x'
        self.assertEqual(
            CompareTwo(a, b)._compare_operators_and_keywords_string_equal(),
            'operators_and_keywords_string_equal')

    def test_compare_operators_string_equal_nomatch(self):
        a = mock.MagicMock()
        a.get_operators_string.return_value = 'a'
        b = mock.MagicMock()
        b.get_operators_string.return_value = 'b'
        self.assertEqual(
            CompareTwo(a, b)._compare_operators_string_equal(),
            None)

    def test_compare_operators_string_equal(self):
        a = mock.MagicMock()
        a.get_operators_string.return_value = 'x'
        b = mock.MagicMock()
        b.get_operators_string.return_value = 'x'
        self.assertEqual(
            CompareTwo(a, b)._compare_operators_string_equal(),
            'operators_string_equal')

    def test_compare_keywords_string_equal_nomatch(self):
        a = mock.MagicMock()
        a.get_keywords_string.return_value = 'a'
        b = mock.MagicMock()
        b.get_keywords_string.return_value = 'b'
        self.assertEqual(
            CompareTwo(a, b)._compare_keywords_string_equal(),
            None)

    def test_compare_keywords_string_equal(self):
        a = mock.MagicMock()
        a.get_keywords_string.return_value = 'x'
        b = mock.MagicMock()
        b.get_keywords_string.return_value = 'x'
        self.assertEqual(
            CompareTwo(a, b)._compare_keywords_string_equal(),
            'keywords_string_equal')

    def test_compare_total_operatorcount_equal_nomatch(self):
        a = mock.MagicMock()
        a.get_number_of_operators.return_value = 10
        b = mock.MagicMock()
        b.get_number_of_operators.return_value = 20
        self.assertEqual(
            CompareTwo(a, b)._compare_total_operatorcount_equal(),
            None)

    def test_compare_total_operatorcount_equal(self):
        a = mock.MagicMock()
        a.get_number_of_operators.return_value = 5
        b = mock.MagicMock()
        b.get_number_of_operators.return_value = 5
        self.assertEqual(
            CompareTwo(a, b)._compare_total_operatorcount_equal(),
            'total_operatorcount_equal')

    def test_compare_total_keywordcount_equal_nomatch(self):
        a = mock.MagicMock()
        a.get_number_of_keywords.return_value = 10
        b = mock.MagicMock()
        b.get_number_of_keywords.return_value = 20
        self.assertEqual(
            CompareTwo(a, b)._compare_total_keywordcount_equal(),
            None)

    def test_compare_total_keywordcount_equal(self):
        a = mock.MagicMock()
        a.get_number_of_keywords.return_value = 5
        b = mock.MagicMock()
        b.get_number_of_keywords.return_value = 5
        self.assertEqual(
            CompareTwo(a, b)._compare_total_keywordcount_equal(),
            'total_keywordcount_equal')

    def test_compare_functions(self):
        parsedfunction1 = mock.MagicMock()
        parsedfunction1.get_number_of_keywords.return_value = 5
        parsedfunction2 = mock.MagicMock()
        parsedfunction2.get_number_of_keywords.return_value = 2
        parsedfunction3 = mock.MagicMock()
        parsedfunction3.get_number_of_keywords.return_value = 3
        parsedfunction4 = mock.MagicMock()
        parsedfunction4.get_number_of_keywords.return_value = 5

        a = mock.MagicMock()
        a.codeblocktype = 'program'
        a.get_parsed_functions.return_value = [parsedfunction1, parsedfunction2]
        b = mock.MagicMock()
        b.codeblocktype = 'program'
        b.get_parsed_functions.return_value = [parsedfunction3, parsedfunction4]
        comparetwo = CompareTwo(a, b)
        functioncompare_summary = comparetwo._compare_functions()
        self.assertEqual(functioncompare_summary, 'similar_functions')
        self.assertEqual(comparetwo.functionpoints, 1)
        self.assertEqual(comparetwo.points, 0)
        self.assertEqual(comparetwo.get_scaled_points(), 1)

    def test_compare_functions_complex(self):
        parsedfunctionA1 = mock.MagicMock()
        parsedfunctionA1.get_number_of_keywords.return_value = 5  # 1 point
        parsedfunctionA1.get_operators_and_keywords_string.return_value = 'ifreturn'  # 10 points
        parsedfunctionA2 = mock.MagicMock()
        parsedfunctionA2.get_number_of_keywords.return_value = 2
        parsedfunctionA2.get_operators_string.return_value = 'x'  # 3 points

        parsedfunctionB1 = mock.MagicMock()
        parsedfunctionB1.get_number_of_keywords.return_value = 3
        parsedfunctionB1.get_operators_and_keywords_string.return_value = 'ifreturn'  # 10 points
        parsedfunctionB2 = mock.MagicMock()
        parsedfunctionB2.get_number_of_keywords.return_value = 5  # 1 point
        parsedfunctionB2.get_operators_string.return_value = 'x'  # 3 points

        a = mock.MagicMock()
        a.codeblocktype = 'program'
        a.get_parsed_functions.return_value = [parsedfunctionA1, parsedfunctionA2]
        b = mock.MagicMock()
        b.codeblocktype = 'program'
        b.get_parsed_functions.return_value = [parsedfunctionB1, parsedfunctionB2]
        comparetwo = CompareTwo(a, b)
        functioncompare_summary = comparetwo._compare_functions()
        self.assertEqual(functioncompare_summary, 'similar_functions')
        self.assertEqual(comparetwo.functionpoints, 14)


class TestParseResultCompareMany(unittest.TestCase):
    def test_all_compared_single(self):
        parseresult1 = mock.MagicMock()
        comparemany = CompareMany([parseresult1])
        self.assertEquals(comparemany.results, [])

    def test_all_compared_two(self):
        parseresult1 = mock.MagicMock()
        parseresult2 = mock.MagicMock()
        comparemany = CompareMany([parseresult1, parseresult2])
        self.assertEquals(len(comparemany.results), 1)
        self.assertEquals(comparemany.results[0].parseresult1, parseresult1)
        self.assertEquals(comparemany.results[0].parseresult2, parseresult2)

    def test_all_compared_three(self):
        parseresult1 = mock.MagicMock()
        parseresult2 = mock.MagicMock()
        parseresult3 = mock.MagicMock()
        comparemany = CompareMany([parseresult1, parseresult2, parseresult3])
        results = comparemany.results
        self.assertEquals(len(results), 3)
        self.assertTrue(results[0].compares_parseresults(parseresult1, parseresult2))
        self.assertTrue(results[1].compares_parseresults(parseresult1, parseresult3))
        self.assertTrue(results[2].compares_parseresults(parseresult2, parseresult3))

    def test_all_compared_four(self):
        parseresult1 = mock.MagicMock()
        parseresult2 = mock.MagicMock()
        parseresult3 = mock.MagicMock()
        parseresult4 = mock.MagicMock()
        comparemany = CompareMany([parseresult1, parseresult2, parseresult3, parseresult4])
        results = comparemany.results
        self.assertEquals(len(results), 6)
        self.assertTrue(results[0].compares_parseresults(parseresult1, parseresult2))
        self.assertTrue(results[1].compares_parseresults(parseresult1, parseresult3))
        self.assertTrue(results[2].compares_parseresults(parseresult1, parseresult4))
        self.assertTrue(results[3].compares_parseresults(parseresult2, parseresult3))
        self.assertTrue(results[4].compares_parseresults(parseresult2, parseresult4))
        self.assertTrue(results[5].compares_parseresults(parseresult3, parseresult4))

    def test_compare_many_results_sanity(self):
        parseresult1 = mock.MagicMock()
        parseresult1.label = '1'
        parseresult1.get_operators_and_keywords_string.return_value = 'x'

        parseresult2 = mock.MagicMock()
        parseresult2.label = '2'
        parseresult2.get_operators_and_keywords_string.return_value = 'x'
        parseresult2.get_number_of_operators.return_value = 10

        parseresult3 = mock.MagicMock()
        parseresult3.label = '3'
        parseresult3.get_number_of_operators.return_value = 10

        comparemany = CompareMany([parseresult1, parseresult2, parseresult3])
        # for comparetwo in comparemany:
        #     print comparetwo
        results = comparemany.results
        self.assertTrue(results[0].compares_parseresults(parseresult1, parseresult2))
        self.assertEquals(results[0].points, 10)
        self.assertEquals(results[0].get_scaled_points(), 1000)
        self.assertEquals(results[0].summary, ['operators_and_keywords_string_equal'])
        self.assertTrue(results[1].compares_parseresults(parseresult1, parseresult3))
        self.assertEquals(results[1].points, 0)
        self.assertEquals(results[1].get_scaled_points(), 0)
        self.assertEquals(results[1].summary, [])
        self.assertTrue(results[2].compares_parseresults(parseresult2, parseresult3))
        self.assertEquals(results[2].points, 1)
        self.assertEquals(results[2].get_scaled_points(), 100)
        self.assertEquals(results[2].summary, ['total_operatorcount_equal'])
