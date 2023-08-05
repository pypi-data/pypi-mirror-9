# -*- coding: utf-8 -*-

from django import template
import urllib2

from django.conf import settings as conf
from django.contrib.sites.models import Site

register = template.Library()

@register.inclusion_tag('elements/backlinks_list.html')
def backlinks_list():
    OpenInNewWindow = "1"
    BLKey = conf.KEY_BACKLINKS
    current_site = Site.objects.get(id=conf.SITE_ID)
    myurl = "http://"+current_site.domain

    QueryString = "LinkUrl=" + myurl
    QueryString = QueryString + "&Key=" + BLKey
    QueryString = QueryString + "&OpenInNewWindow=" + OpenInNewWindow

    req = urllib2.Request('http://www.backlinks.com/engine.php?' + QueryString)
    try:
        resp = urllib2.urlopen(req)
    except HTTPError, e:
        print e.code
        print e.read()

    links = resp.read()
    output_code = '%s' % links

    return {
        'links': output_code
    }

"""
Template:

Now:
{{ backlinks_list }}

Before:
{% cache 21600 backlinks %}
{{ links|safe }}
{% endcache %}
"""
