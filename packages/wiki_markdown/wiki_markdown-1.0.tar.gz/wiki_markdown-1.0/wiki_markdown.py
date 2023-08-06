import markdown 
from markdown.extensions import Extension 
from markdown.extensions.toc import TocExtension
from markdown.inlinepatterns import Pattern 
from markdown.postprocessors import Postprocessor 
from markdown.util import etree
import os

API_RE = r'(@@[\w\d\s]*@@)(.*?)\2'
section_list = []
io_params = []

class WikiPostprocessor(Postprocessor):
    def run(self, text):
        contents = "[TOC]\n"
        for x in range(0, len(section_list)):
            contents = contents + "#" + section_list[x] + "\n"
        toc_html = markdown.markdown(contents, extensions=[TocExtension(baselevel=3, title='Article Contents')])
        html = toc_html + text
        try:
            os.chdir(io_params[0])
            fo = open(io_params[1], "a+")
            fo.write("\n" + html + "\n")
            fo.close()
        except IOError as (errno.strerror):
            print "I/O error({0}): {1}".format(errno, strerror)
        return html

class WikiPatterns(Pattern):
    def handleMatch(self, m):
        #parser = etree.HTMLParser()
        #root = etree.Element('editable')
        if m.group(2) == '@@subject@@':
            tag = 'h1'
            el = etree.Element(tag)
            el.set("class", "subject")
            el.text = m.group(3)
        elif m.group(2) == '@@section@@':
            tag = 'h2'
            el = etree.Element(tag)
            el.set("class", "section")
            el.text = m.group(3)
            section_list.append(m.group(3))
        #elif m.group(2) == '@@sub-section@@':
        elif m.group(2) == '@@article@@':
            el = etree.Element('a')
            el.set("href", "/wiki/" + m.group(3) + ".html")
            el.set("class", "aricle")
            el.text = m.group(3)
        #tree = etree.ElementTree(root)
        return el

class WikiExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.config = {'name' : ['test.html', 'output html file'],
                       'dir' : ['.', 'directory of file'] }
        super(WikiExtension, self).__init__(*args, **kwargs)
    def extendMarkdown(self, md, md_globals):
        wiki = WikiPatterns(API_RE)
        pp = WikiPostprocessor()
        md.inlinePatterns['wiki'] = wiki
        md.postprocessors.add('africanawiki_post_processor', pp, '_end')
        io_params.append(self.config['dir'][0])
        io_params.append(self.config['name'][0])

def makeExtension(*args, **kwargs):
    return WikiExtension(*args, **kwargs)
