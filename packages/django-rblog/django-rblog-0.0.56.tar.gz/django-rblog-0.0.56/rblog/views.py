# -*- coding: utf-8 -*-

import json
import datetime
import urllib2
from BeautifulSoup import BeautifulSoup

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
import models as mymodels
import forms as myforms

from braces.views import LoginRequiredMixin, SuperuserRequiredMixin
from tagging.models import Tag, TaggedItem
from django.http import HttpResponse
from django.conf import settings as conf
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.contrib.sitemaps import Sitemap
from django.template.defaultfilters import slugify

from disqusapi import DisqusAPI

from engine import expire_view_cache


class BlogIndexView(ListView):

    template_name = "rblog/index.html"
    context_object_name = "myposts"
    paginate_by = 20

    def get_queryset(self):
        timenow = datetime.datetime.now()
        return mymodels.Post.objects.filter(
            status=1,
            creation_date__lte=timenow).order_by('-creation_date')

    def get_context_data(self, **kwargs):
        context = super(BlogIndexView, self).get_context_data(**kwargs)
        context.update({
            'title': _('Blog'),
            'description': _('This is the blog'),
        })
        return context


class LinkblogIndexView(ListView):

    template_name = "rblog/index.html"
    context_object_name = "myposts"
    paginate_by = 200

    def get_queryset(self):
        timenow = datetime.datetime.now()
        return mymodels.Post.objects.filter(
            status=1,
            ptype='link',
            creation_date__lte=timenow).order_by('-creation_date')

    def get_context_data(self, **kwargs):
        context = super(LinkblogIndexView, self).get_context_data(**kwargs)
        context.update({
            'title': _('Linkblog'),
            'description': _('Interesting links I\'ve found'),
        })
        return context


class PostDetailView(DetailView):

    template_name = "rblog/detail.html"
    context_object_name = "mypost"

    def get_object(self):
        self.obj = get_object_or_404(mymodels.Post, slug=self.kwargs['slug'],
                                     status=1)
        self.obj.hits = self.obj.hits + 1
        prefix = "http://"
        if self.request.is_secure():
            prefix = "https://"
        current_site = get_current_site(self.request)
        current_url = reverse('app_blog-post-detail',
                              kwargs={'slug': self.kwargs['slug']})
        # if DISQUS_SYNC is True it tries to fill thread_id vía Disqus API
        try:
            if conf.DISQUS_SYNC:
                if not self.obj.thread_id:
                    try:
                        api = DisqusAPI(conf.DISQUS_API_SECRET,
                                        conf.DISQUS_API_PUBLIC)
                        dq_response = api.threads.details(
                            forum=conf.DISQUS_WEBSITE_SHORTNAME,
                            thread='link:' + prefix + current_site.domain + vcurrent_url)
                        self.obj.thread_id = dq_response['id']
                    except:
                        pass
                    try:
                        api = DisqusAPI(conf.DISQUS_API_SECRET,
                                        conf.DISQUS_API_PUBLIC)
                        dq_response = api.threads.details(
                            forum=conf.DISQUS_WEBSITE_SHORTNAME,
                            thread='link:' + prefix + 'www.' +
                            current_site.domain+current_url)
                        self.obj.thread_id = dq_response['id']
                    except:
                        pass
        except:
            pass
        self.obj.save()
        return self.obj

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        comments = mymodels.Comments.objects.filter(
            thread_id=self.obj.thread_id, thread_id__isnull=False)
        context.update({
            'comments': comments,
        })
        return context

    def render_to_response(self, context):
        if self.obj.redirect:
            return redirect(self.obj.redirect)
        return super(PostDetailView, self).render_to_response(context)


class PostLinkAdd(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):

    model = mymodels.Post
    form_class = myforms.LinkForm
    success_url = '/'

    def form_valid(self, form):
        if self.request.is_ajax() and self.request.method == 'POST':
            link = json.loads(self.request.POST.get('link', None))
            soup = BeautifulSoup(urllib2.urlopen(link))
            try:
                title = soup.title.string
            except:
                title = 'No title'
            try:
                desc = soup.findAll(attrs={"name":"description"})[0]['content']
            except:
                desc = 'No description available'

            post = mymodels.Post(
                title=title,
                slug=slugify(title),
                text=desc,
                creation_date=datetime.datetime.now(),
                canonical=link,
                ptype='link',
                user=self.request.user)
            post.save()
            expire_view_cache("app_blog-index")
            return HttpResponse(1)


class PostTempView(DetailView):

    template_name = "rblog/detail.html"
    context_object_name = "mypost"

    def get_object(self):
        self.obj = get_object_or_404(mymodels.Post,
                                     slug=self.kwargs['slug'],
                                     status=0)
        return self.obj


class PostsWithTag(ListView):

    template_name = "rblog/index.html"
    context_object_name = "myposts"
    paginate_by = 20

    def get_queryset(self):
        query_tag = Tag.objects.get(name=self.kwargs['tag'])
        myposts = TaggedItem.objects.get_by_model(mymodels.Post, query_tag)
        datetimenow = datetime.datetime.now()
        return myposts.all().filter(
            status=1,
            creation_date__lte=datetimenow).order_by('-creation_date')

    def get_context_data(self, **kwargs):
        context = super(PostsWithTag, self).get_context_data(**kwargs)
        mydesc = _('Bunch of posts about tag') + ": " + self.kwargs['tag']
        context.update({
            'title': _('Tag') + " " + self.kwargs['tag'],
            'description': mydesc,
            'tag': self.kwargs['tag'],
        })
        return context


class PostsByDate(ListView):

    template_name = "rblog/index.html"
    context_object_name = "myposts"
    paginate_by = 20

    def get_queryset(self):
        archive = str(self.kwargs['month']) + '.' + str(self.kwargs['year'])
        return mymodels.Post.objects.all().filter(
            status=1,
            creation_date__lte=datetime.datetime.now(),
            creation_date__month=self.kwargs['month'],
            creation_date__year=self.kwargs['year']).order_by('-creation_date')

    def get_context_data(self, **kwargs):
        context = super(PostsByDate, self).get_context_data(**kwargs)
        mytit = u"%s %s.%s" % (_('Archive'), str(self.kwargs['month']),
                               str(self.kwargs['year']))

        mydesc = u"%s: %s.%s" % (
            _('Bunch of posts on the date'),
            str(self.kwargs['month']),
            str(self.kwargs['year']))
        myarch = str(self.kwargs['month']) + '.' + str(self.kwargs['year'])
        context.update({
            'title': mytit,
            'description': mydesc,
            'archive': myarch,
            'month': str(self.kwargs['month']),
            'byear': str(self.kwargs['year']),
        })
        return context


class AJAXArchive(ListView):

    template_name = "rblog/archive.html"
    model = mymodels.Post

    def get_context_data(self, **kwargs):
        context = super(AJAXArchive, self).get_context_data(**kwargs)
        datetimenow = datetime.datetime.now()
        first_post = mymodels.Post.objects.all().filter(
            status=1,
            creation_date__lte=datetimenow).order_by('creation_date')[0]
        year_ini = int(first_post.creation_date.strftime("%Y"))
        year_hoy = datetime.datetime.now().year
        mes_hoy = datetime.datetime.now().month
        meses = [_('January'), _('February'), _('March'), _('April'), _('May'),
                 _('June'), _('July'), _('August'), _('September'),
                 _('October'), _('November'), _('December')]
        years = range(year_ini, year_hoy+1)

        results = dict()
        for j in range(year_ini, year_hoy+1):
            for i in range(1, 13):
                num = mymodels.Post.objects.filter(
                    creation_date__year=j,
                    creation_date__month=i).count()
                results[j, i] = num

        context.update({
            'first_post': first_post,
            'year_ini': year_ini,
            'mes_hoy': mes_hoy,
            'meses': meses,
            'years': years,
            'year_hoy': year_hoy,
            'results': results,
        })
        return context


class BlogSitemap(Sitemap):

    changefreq = "never"
    priority = 0.5

    def items(self):
        timenow = datetime.datetime.now()
        return mymodels.Post.objects.filter(
            status=1,
            ptype='post',
            creation_date__lte=timenow).order_by('-creation_date')

    def lastmod(self, obj):
        return obj.creation_date
