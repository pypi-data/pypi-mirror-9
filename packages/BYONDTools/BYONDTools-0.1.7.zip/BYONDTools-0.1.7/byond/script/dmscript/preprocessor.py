'''
Copyright (c)2015 Rob "N3X15" Nelson

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

:author: Rob "N3X15" Nelson <nexisentertainment@gmail.com>
'''

import pyparsing as pyp

class Preprocessor(object):
    def __init__(self):
        self.macros = {}
        self.includedFiles = []
        
        self.syntax = self.buildPreprocessorSyntax()
    
    def buildPreprocessorSyntax(self):
        # Literals
        singlelineString = pyp.QuotedString('"','\\').setResultsName('string').setParseAction(self.makeListString)
        fileRef = pyp.QuotedString("'",'\\').setResultsName('fileRef').setParseAction(self.makeFileRef)
        multilineString = pyp.QuotedString(quoteChar='{"',endQuoteChar='"}',multiline=True).setResultsName('string').setParseAction(self.makeListString)
        number = pyp.Regex(r'\d+(\.\d*)?([eE]\d+)?').setResultsName('number').setParseAction(self.makeListNumber)
        
        macroDef = pyp.lineStart + pyp.Suppress('#define') + pyp.ident.setResultsName('name') + pyp.restOfLine.setResultsName('content')
        macroDef.setParseAction(self.handleDefine)
        
        macroUndef = pyp.lineStart + pyp.Suppress('#undef') + pyp.ident.setResultsName('name')
        macroUndef.setParseAction(self.handleUndef)
        
        include = pyp.lineStart + pyp.Literal('#include') + pyp.QuotedString.setResultsName('filename')
        include.setParseAction(self.handleInclude)
        
        ifDef = pyp.lineStart + pyp.Suppress('#ifdef') + pyp.ident.setResultsName('name') \
              + pyp.Optional(pyp.SkipTo(pyp.Keyword('#else'), include=True, failOn='#endif')) \
              + pyp.SkipTo(pyp.Keyword('#endif'), include=True)
              
        preprocessorDirective = macroDef | macroUndef | include | ifDef
        preprocessor = pyp.ZeroOrMore(preprocessorDirective)
        return preprocessor