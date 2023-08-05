# -*- coding: utf-8 -*-

import re
import pygments

from django import template

from BeautifulSoup import BeautifulSoup
from pygments.lexers import *
from pygments.formatters import *

register = template.Library()

@register.filter(name='pygmentize')
def pygmentize(content):

    tree = BeautifulSoup(content)

    for pre in tree.findAll('pre'):
        try:
            lex = pre['class']
        except:
            lex = 'text'
        print lex
        lexer = get_lexer_by_name(lex, startinline=True)
        newpre = pygments.highlight(pre.string, lexer, HtmlFormatter())
        pre.replaceWith(BeautifulSoup(newpre ,convertEntities=BeautifulSoup.HTML_ENTITIES))

    return str(tree)
