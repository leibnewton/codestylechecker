#!/usr/bin/env python


from __future__ import unicode_literals

import io
import sys
import optparse
import os
import chardet


from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import HtmlFormatter
from xml.sax import parse as xml_parse
from xml.sax import SAXParseException as XmlParseException
from xml.sax.handler import ContentHandler as XmlContentHandler

encode_type = sys.getfilesystemencoding()

"""
Turns a cppcheck xml file into a browsable html report along
with syntax highlighted source code.
"""

STYLE_FILE = """
body {
    background-color: black;
    font: 13px Arial, Verdana, Sans-Serif;
    margin: 0;
    padding: 0;
}

.error {
    background-color: #ffb7b7;
}

.error2 {
    background-color: #faa;
    border: 1px dotted black;
    display: inline-block;
    margin-left: 4px;
}

.highlight .hll {
    padding: 1px;
}

#page {
    background-color: white;
    border: 2px solid #aaa;
    -webkit-box-sizing: content-box;
    -moz-box-sizing: content-box;
    box-sizing: content-box;
    margin: 30px;
    overflow: auto;
    padding: 5px 20px;
    width: auto;
}

#header {
    border-bottom: thin solid #aaa;
}

#menu {
    float: left;
    margin-top: 5px;
    text-align: left;
    width: 100px;
    height: auto;
}

#menu > a {
    display: block;
    margin-left: 10px;
}

#content {
    -webkit-box-sizing: content-box;
    -moz-box-sizing: content-box;
    box-sizing: content-box;
    border-left: thin solid #aaa;
    float: left;
    margin: 5px;
    padding: 0 10px 10px 10px;
    width: 80%;
}

.linenos {
    border-right: thin solid #aaa;
    color: lightgray;
    padding-right: 6px;
}

#footer {
    border-top: thin solid #aaa;
    clear: both;
    font-size: 90%;
    margin-top: 5px;
}

#footer ul {
    list-style-type: none;
    padding-left: 0;
}
"""

HTML_HEAD = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Cppcheck - HTML report - %s</title>
    <link rel="stylesheet" href="style.css">
    <style>
%s
    </style>
  </head>
  <body>
    <div id="page">
      <div id="header">
        <h1>Cpplint report - %s</h1>
      </div>
      <div id="menu">
        <a href="index.html">Defect list</a>
      </div>
      <div id="content">
"""

HTML_FOOTER = """
      </div>
      <div id="footer">
        <p>
          Cpplint - a tool for static C/C++ code analysis
        </p>
      </div>
    </div>
  </body>
</html>
"""

HTML_ERROR = "<span class='error2'>&lt;--- %s</span>\n"


class AnnotateCodeFormatter(HtmlFormatter):
    errors = []

    def wrap(self, source, outfile):
        line_no = 1
        for i, t in HtmlFormatter.wrap(self, source, outfile):
            # If this is a source code line we want to add a span tag at the
            # end.
            if i == 1:
                for error in self.errors:
                    if error['line'] == line_no:
                        t = t.replace('\n', HTML_ERROR % error['msg'])
                line_no = line_no + 1
            yield i, t


class CppCheckHandler(XmlContentHandler):

    """Parses the cppcheck xml file and produces a list of all its errors."""

    def __init__(self):
        XmlContentHandler.__init__(self)
        self.errors = []
        self.version = '1'

    def startElement(self, name, attributes):
        if name == 'results':
            self.version = attributes.get('version', self.version)

        if self.version == '1':
            self.handleVersion1(name, attributes)
        else:
            self.handleVersion2(name, attributes)

    def handleVersion1(self, name, attributes):
        if name != 'error':
            return

        self.errors.append({
            'file': attributes.get('file', ''),
            'line': int(attributes.get('line', 0)),
            'id': attributes['id'],
            'severity': attributes['severity'],
            'msg': attributes['msg']
        })

    def handleVersion2(self, name, attributes):
        if name == 'error':
            self.errors.append({
                'file': '',
                'line': 0,
                'id': attributes['id'],
                'severity': attributes['severity'],
                'msg': attributes['msg']
            })
        elif name == 'location':
            assert self.errors
            self.errors[-1]['file'] = attributes['file']
            self.errors[-1]['line'] = int(attributes['line'])


def main():
    # Configure all the options this little utility is using.
    parser = optparse.OptionParser()
    parser.add_option('--title', dest='title',
                      help='The title of the project.',
                      default='[project name]')
    parser.add_option('--file', dest='file',
                      help='The cppcheck xml output file to read defects '
                           'from. Default is reading from stdin.')
    parser.add_option('--report-dir', dest='report_dir',
                      help='The directory where the HTML report content is '
                           'written.')
    parser.add_option('--source-dir', dest='source_dir',
                      help='Base directory where source code files can be '
                           'found.')
    parser.add_option('--source-encoding', dest='source_encoding',
                      help='Encoding of source code.', default='utf-8')

    # Parse options and make sure that we have an output directory set.
    options, args = parser.parse_args()
    if not options.report_dir:
        parser.error('No report directory set.')

    # Get the directory where source code files are located.
    source_dir = os.getcwd()
    if options.source_dir:
        source_dir = options.source_dir

    # Get the stream that we read cppcheck errors from.
    input_file = sys.stdin
    if options.file:
        if not os.path.exists(options.file):
            parser.error('cppcheck xml file: %s not found.' % options.file)
        input_file = io.open(options.file, 'r')

    # Parse the xml file and produce a simple list of errors.
    print('Parsing xml report.')
    try:
        contentHandler = CppCheckHandler()
        xml_parse(input_file, contentHandler)
    except XmlParseException as msg:
        print('Failed to parse cppcheck xml file: %s' % msg)
        sys.exit(1)

    # We have a list of errors. But now we want to group them on
    # each source code file. Lets create a files dictionary that
    # will contain a list of all the errors in that file. For each
    # file we will also generate a HTML filename to use.
    files = {}
    file_no = 0
    error_sort = ["Info","Minor","Major","Critical","Blocker"]
    error_count = []
    error_total = 0
    Infonum = 0
    Minornum = 0
    Majornum = 0
    Criticalnum = 0
    Blockernum = 0

    for error in contentHandler.errors:
        filename = error['file']
        state = "unchanged"
        if filename not in files.keys():
            files[filename] = {
                'errors': [], 'htmlfile': str(file_no) + '.html'}
            file_no = file_no + 1
        files[filename]['errors'].append(error)
        severity = error['severity']
        if severity=='Info':
            Infonum = Infonum + 1
            error_total = error_total + 1
        elif severity=='Major':
            Majornum = Majornum + 1
            error_total = error_total + 1
        elif severity=='Critical':
            Criticalnum = Criticalnum + 1
            error_total = error_total + 1
            if state=='new':
                Criticalnumnew = Criticalnumnew +1
        elif severity=='Blocker':
            Blockernum = Blockernum + 1
            error_total = error_total + 1
        elif severity=='Minor':
            Minornum = Minornum + 1
            error_total = error_total + 1

    error_count.append(Infonum)
    error_count.append(Minornum)
    error_count.append(Majornum)
    error_count.append(Criticalnum)
    error_count.append(Blockernum)
    # Make sure that the report directory is created if it doesn't exist.
    print('Creating %s directory' % options.report_dir)
    if not os.path.exists(options.report_dir):
        os.mkdir(options.report_dir)

    # Generate a HTML file with syntax highlighted source code for each
    # file that contains one or more errors.
    print('Processing errors')
    for filename, data in files.items():
        htmlfile = data['htmlfile']
        errors = data['errors']

        lines = []
        for error in errors:
            lines.append(error['line'])

        if filename == '':
            continue

        source_filename = os.path.join(source_dir, filename)
        try:
            with open(source_filename, 'r') as input_file:
                Text = input_file.read()
                enc = chardet.detect(Text)['encoding']
                if enc is None:
                    enc=options.source_encoding
                content=Text.decode(enc,'ignore')
        except IOError:
            sys.stderr.write("ERROR: Source file '%s' not found.\n" %
                             source_filename)
            continue

        htmlFormatter = AnnotateCodeFormatter(linenos=True,
                                              style='colorful',
                                              hl_lines=lines,
                                              lineanchors='line',
                                              encoding=options.source_encoding)
        htmlFormatter.errors = errors
        with io.open(os.path.join(options.report_dir, htmlfile),
                     'w') as output_file:
            output_file.write(HTML_HEAD %
                              (options.title,
                               htmlFormatter.get_style_defs('.highlight'),
                               options.title))

            lexer = guess_lexer_for_filename(source_filename, '')
            if options.source_encoding:
                lexer.encoding = options.source_encoding

            output_file.write(
                highlight(content, lexer, htmlFormatter).decode(
                    options.source_encoding))

            output_file.write(HTML_FOOTER)

#       print('  ' + filename)

    # Generate a master index.html file that will contain a list of
    # all the errors created.
    print('Creating index.html')
    with io.open(os.path.join(options.report_dir, 'index.html'),
                 'w') as output_file:
        output_file.write(HTML_HEAD % (options.title, '', options.title))
        output_file.write('<table border="1px" bordercolor="#000000" cellspacing="0px" style="border-collapse:collapse">')
        output_file.write('<tr><th>Total</th></tr>')
        output_file.write("<tr><td>%s</td></tr>" %(error_total))
        output_file.write('</table>')
        output_file.write('</br>')
        output_file.write('</br>')
        output_file.write('<table border="1px" bordercolor="#000000" cellspacing="0px" style="border-collapse:collapse">')
        if error_total>0:
            output_file.write('<tr><th>File</th><th>Line</th><th>Type</th><th>Message</th></tr>')
        for filename, data in files.items():
            if filename.strip() != '':
                output_file.write(
                "<tr><td rowspan='%s'><a href='%s'>%s</a></td><td><a href='%s#line-%d'>%d</a></td> \
                <td>%s</td><td>%s</td></tr>" %
                (len(data['errors']),data['htmlfile'], filename,data['htmlfile'], data['errors'][0]['line'],data['errors'][0]['line'],
                data['errors'][0]['id'],data['errors'][0]['msg']))
                for i in range(1,len(data['errors'])):
                    output_file.write(
                    "<tr><td><a href='%s#line-%d'>%d</a></td><td>%s</td><td>%s</td></tr>" %
                    (data['htmlfile'], data['errors'][i]['line'], data['errors'][i]['line'],
                    data['errors'][i]['id'], data['errors'][i]['msg']))
        output_file.write('</table>')
        output_file.write(HTML_FOOTER)

    print('Creating style.css file')
    with io.open(os.path.join(options.report_dir, 'style.css'),
                 'w') as css_file:
        css_file.write(STYLE_FILE)

if __name__ == '__main__':
    main()
