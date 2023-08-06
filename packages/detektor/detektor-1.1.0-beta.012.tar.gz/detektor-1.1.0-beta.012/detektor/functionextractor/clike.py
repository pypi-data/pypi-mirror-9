from pprint import pprint
import re
from detektor.functionextractor.base import BaseFunctionExtractor
from detektor.functionextractor.base import ExtractedFunction


class ClikeFunctionExtractor(BaseFunctionExtractor):
    functionstartpattern = re.compile(
        r'(?P<returntype>(//[ \t]*)?\w+[^ ]*)?\s+(?P<name>\w+)\w*\((?P<arguments>.*?)\)\s*\{')

    def __init__(self, keywords):
        self.keywords = keywords

    def _find_function_end(self, sourcecode, startindex):
        blocklevel = 1
        for index in xrange(startindex, len(sourcecode)):
            character = sourcecode[index]
            if character == '{':
                blocklevel += 1
            elif character == '}':
                blocklevel -= 1
            if blocklevel == 0:
                return index
        return len(sourcecode) - 1

    def extract(self, sourcecode):
        functions = []
        for match in self.functionstartpattern.finditer(sourcecode):
            groupdict = match.groupdict()
            if groupdict['name'] not in self.keywords:
                function_startindex = match.end()
                function_endindex = self._find_function_end(sourcecode, function_startindex)
                function_sourcecode = sourcecode[function_startindex:function_endindex]
                matches = match.groupdict()
                if matches['returntype']:
                    returntype = unicode(matches['returntype'], 'utf-8', 'replace').strip()
                    if returntype.startswith('//'):
                        returntype = ''
                else:
                    returntype = ''
                name = unicode(matches['name'], 'utf-8', 'replace')
                arguments = unicode(matches['arguments'], 'utf-8', 'replace')
                functions.append(ExtractedFunction(
                    name=u'{returntype} {name}({arguments})'.format(
                        returntype=returntype, name=name, arguments=arguments).strip(),
                    sourcecode=function_sourcecode
                ))
        return functions
