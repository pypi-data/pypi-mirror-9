import unittest
from detektor.languageparser.python import PythonLanguageParser


class TestPythonLanguageParser(unittest.TestCase):

    def test_keywords_sanity(self):
        parser = PythonLanguageParser()

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'print "Hello world"')
        self.assertEquals(parseresult.keywords['print'], 1)
        for keyword in parser.keywords:
            if keyword != 'print':
                self.assertEquals(parseresult.keywords[keyword], 0)

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'if x == 10: pass')
        self.assertEquals(parseresult.keywords['if'], 1)
        self.assertEquals(parseresult.keywords['pass'], 1)

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'while True: pass')
        self.assertEquals(parseresult.keywords['while'], 1)
        self.assertEquals(parseresult.keywords['pass'], 1)

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'for x in [1, 2]: pass')
        self.assertEquals(parseresult.keywords['for'], 1)
        self.assertEquals(parseresult.keywords['in'], 1)
        self.assertEquals(parseresult.keywords['pass'], 1)

    def test_operators_sanity(self):
        parser = PythonLanguageParser()

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'a == 10')
        self.assertEquals(parseresult.operators['=='], 1)

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'a==10')
        self.assertEquals(parseresult.operators['=='], 1)

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'a*10')
        self.assertEquals(parseresult.operators['*'], 1)

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'a ==10')
        self.assertEquals(parseresult.operators['=='], 1)

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'a== 10')
        self.assertEquals(parseresult.operators['=='], 1)

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'a > 10')
        self.assertEquals(parseresult.operators['>'], 1)

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'a <> 10')
        self.assertEquals(parseresult.operators['<>'], 1)
