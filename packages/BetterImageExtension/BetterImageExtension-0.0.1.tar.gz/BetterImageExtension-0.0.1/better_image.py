#!/usr/bin/env python

from markdown.inlinepatterns import Pattern
from markdown.extensions import Extension
from markdown.util import etree
import re


class BetterImageExtension(Extension):
    """Adds an extension to handle different media types from a single tag"""
    def __init__(self, *args, **kwargs):
        self.config = {}
        self.pattern = r"~~\[(?P<alt>.*)\]\s?\((?P<src>.*)\)\s?@\((?P<printattr>.*)\)\s?@\((?P<webattr>.*)\);"

    def extendMarkdown(self, md, md_globals):
        config = self.getConfigs()
        md.registerExtension(self)
        md.inlinePatterns['betterimage'] = BetterImagePattern(self.pattern, md, self.config)


class BetterImagePattern(Pattern):
    def __init__(self, pattern, md, config):
        # Pass the pattern and markdown instance
        super(BetterImagePattern, self).__init__(pattern, md)
        self.pattern = pattern
        self.config = config

    def handleMatch(self, match):
        matchdict = match.groupdict()
        # print matchdict
        # create our new image element
        el = etree.Element("img")
        if matchdict.get('alt'):
            el.set('alt', matchdict.get('alt'))
        # if matchdict.get('caption'):
        #     el.set('caption', matchdict.get('caption'))
        if matchdict.get('src'):
            el.set('src', matchdict.get('src'))
        if matchdict.get('printattr'):
            webattrs = matchdict.get('printattr').split()
            for item in webattrs:
                an_attr = item.split('=')
                if an_attr[0].startswith('h'):
                    el.set('pheight', an_attr[1])
                if an_attr[0].startswith('w'):
                    el.set('pwidth', an_attr[1])
        if matchdict.get('webattr'):
            webattrs = matchdict.get('webattr').split()
            for item in webattrs:
                an_attr = item.split('=')
                if an_attr[0].startswith('h'):
                    el.set('height', an_attr[1])
                if an_attr[0].startswith('w'):
                    el.set('width', an_attr[1])

        return el


if __name__ == '__main__':
    import markdown
    markdown_string = "~~[an image] (pic.jpg) @(height=100 width=100) @(h=50 w=50);"
    extension_list = [BetterImageExtension()]
    html_fragment = markdown.markdown(markdown_string, extensions=extension_list)
    print html_fragment
