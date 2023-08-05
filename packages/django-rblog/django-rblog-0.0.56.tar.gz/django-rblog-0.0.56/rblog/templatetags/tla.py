# -*- coding: utf-8 -*-

from datetime import timedelta
from elementtree.ElementTree import ElementTree
from urllib2 import urlopen

from django.template.defaultfilters import slugify
from django.conf import settings as conf

from django import template


register = template.Library()

class Link(object):
    def __init__(self,node):
        self.url = node[1].text
        self.text = node[2].text
        self.before_text = node[3].text
        self.after_text = node[4].text

@register.inclusion_tag('elements/tla_list.html', takes_context = True)
def tla_list(context):
    """
    """
    request = context['request']
    #ref = request.META.get('REQUEST_URI', request.META.get('PATH_INFO', '/'))
    ref = "/" + slugify(request.META.get('REQUEST_URI', request.META.get('PATH_INFO', '/')))
    url = 'http://www.text-link-ads.com/xml.php?inventory_key=' +  conf.KEY_TLA + '&referer=' + ref
    try:
        agent = '&user_agent=' + request.META['HTTP_USER_AGENT']
    except:
        agent = '&user_agent=Mozilla/5.0'
    try:
        links = ElementTree.parse(ElementTree(),urlopen(url+agent))
    except:
        links = None

    return {
        'links': [ Link(link) for link in links ]
    }


"""
Template:

Now:
{% tla_list %}

Before:
{% cache 21600 tla %}
<ul id="tla">
{% if links %}
    {% for link in links %}
    <li>{{ link.before_text }} <a href="{{ link.url }}">{{ link.text }}</a> {{ link.after_text }}</li>
    {% endfor %}
{% endif %}
</ul>
{% endcache %}
"""
