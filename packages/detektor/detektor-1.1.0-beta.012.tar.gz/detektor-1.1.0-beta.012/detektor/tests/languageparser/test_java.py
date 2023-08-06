import unittest
from detektor.languageparser.java import JavaLanguageParser


class TestJavaLanguageParser(unittest.TestCase):

    def test_keywords_sanity(self):
        parser = JavaLanguageParser()

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'if(true)')
        self.assertEquals(parseresult.keywords['if'], 1)
        for keyword in parser.keywords:
            if keyword != 'if':
                self.assertEquals(parseresult.keywords[keyword], 0)

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'if(x == 10) return')
        self.assertEquals(parseresult.keywords['if'], 1)
        self.assertEquals(parseresult.keywords['return'], 1)

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'while(true) return')
        self.assertEquals(parseresult.keywords['while'], 1)
        self.assertEquals(parseresult.keywords['return'], 1)

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, 'for(int x: somelist) return')
        self.assertEquals(parseresult.keywords['for'], 1)
        self.assertEquals(parseresult.keywords['int'], 1)
        self.assertEquals(parseresult.keywords['return'], 1)

    def test_operators_sanity(self):
        parser = JavaLanguageParser()

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
        parser.parse(parseresult, 'a != 10')
        self.assertEquals(parseresult.operators['!='], 1)

    def test_parsed_functions(self):
        # Note: Only a sanity test. This only needs to ensure that
        # the function extracter is configured correctly, and that
        # the parser is exectuted on the extracted functions. The function
        # extracter and parser has their own tests.
        parser = JavaLanguageParser()

        parseresult = parser.make_parseresult()
        parser.parse(parseresult, '''
        public class Test {
            public void main(String[] args) {
                printHello();
            }

            private void printHello() {
                System.out.println("Hello World!");
            }

            void test(int i) {
                if(i > 10) {
                    return 1;
                } else {
                    return 2;
                }
            }
        }
        ''')
        self.assertEquals(len(parseresult.parsed_functions), 3)
        self.assertEquals(parseresult.parsed_functions[0].label, 'void main(String[] args)')
        self.assertEquals(parseresult.parsed_functions[1].label, 'void printHello()')
        self.assertEquals(parseresult.parsed_functions[2].label, 'void test(int i)')
        self.assertEquals(parseresult.parsed_functions[2].keywords['if'], 1)
        self.assertEquals(parseresult.parsed_functions[2].keywords['else'], 1)
        self.assertEquals(parseresult.parsed_functions[2].keywords['return'], 2)
