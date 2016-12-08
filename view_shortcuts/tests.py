# -*- coding: utf-8 -*-

__doc__="""
>>> c1 = Category.objects.create(title='News', slug='news')
>>> c2 = Category.objects.create(title='Misc', slug='misc')
>>> a1 = Author.objects.create(name='John')
>>> a2 = Author.objects.create(name='Mary')
>>> a3 = Author.objects.create(name='joe')
>>> s1 = Story(title='s1', text='test', status=Story.PUBLISHED, paid=True)
>>> s1.save()
>>> s1.author=a1
>>> s1.categories=[c1,c2]
>>> s1.save()
>>> s2 = Story(title='s2', text='test', status=Story.PUBLISHED, paid=False)
>>> s2.save()
>>> s2.author=a2
>>> s2.categories=[c1]
>>> s2.save()
>>> s3 = Story(title='s3', text='test', status=Story.DRAFT, paid=True)
>>> s3.save()
>>> s3.author=a1
>>> s3.categories=[c2]
>>> s3.save()
>>> qs = Story.objects.all()
>>> from view_shortcuts.filters import FilterList, facet, RelationFilter
>>> filter_settings = (
...     facet('categories__slug'),
...     facet('author'),
...     facet('status'),
...     facet('paid')
... )
>>> request = mock_request()
>>> filters = FilterList(request, qs, filter_settings)
>>> isinstance(filters, FilterList)
True
>>> len(filters)
4
>>> filters.active
[]
>>> filters
[<RelationFilter "categories__slug": False>, <RelationFilter "author": False>, <AllValuesFilter "status": False>, <BooleanFilter "paid": False>]
>>> filters.object_list
[<Story: s1>, <Story: s2>, <Story: s3>]
>>> request = mock_request(author=a1.pk)
>>> filters = FilterList(request, qs, filter_settings)
>>> filters
[<RelationFilter "categories__slug": False>, <RelationFilter "author": True>, <AllValuesFilter "status": False>, <BooleanFilter "paid": False>]
>>> filters.active
[<RelationFilter "author": True>]
>>> filters.urlencode
'author=1'
>>> filters.object_list
[<Story: s1>, <Story: s3>]
>>> request = mock_request(author=a1.pk, status=Story.PUBLISHED)
>>> filters = FilterList(request, qs, filter_settings)
>>> filters.active
[<RelationFilter "author": True>, <AllValuesFilter "status": True>]
>>> filters.urlencode
'author=1&status=pub'
>>> filters = FilterList(request, qs, filter_settings)
>>> filters
[<RelationFilter "categories__slug": False>, <RelationFilter "author": True>, <AllValuesFilter "status": True>, <BooleanFilter "paid": False>]
>>> filters.object_list
[<Story: s1>]
>>> flt_author = filters[1]
>>> flt_author
<RelationFilter "author": True>
>>> flt_author.active
True
>>> flt_author.title
u'Written by'
>>> flt_author.urlencode
'author=1'
>>> flt_author.choices
[<Choice author="1">, <Choice author="2">]
>>> [c.title for c in flt_author.choices]
[u'John', u'Mary']
>>> [c for c in flt_author.get_active_choices()]
[<Choice author="1">]
>>> c_a1 = flt_author.get_first_active_choice()
>>> c_a1
<Choice author="1">
>>> c_a1.title
u'John'
>>> c_a1.urlencode
'author=1'
>>> c_a1.items_count
2
>>> for f in filters:
...     print u'%s:   [%s]' % (f.title, f.urlencode)
...     for c in f.choices:
...         print u'    - %s (%s) --> [%s]' % (c.title, c.items_count, c.urlencode)
Category:   [categories__slug=None]
    - News (2) --> [categories__slug=news]
    - Misc (2) --> [categories__slug=misc]
Written by:   [author=1]
    - John (2) --> [author=1]
    - Mary (1) --> [author=2]
Status:   [status=pub]
    - Published (2) --> [status=pub]
    - Draft (1) --> [status=draft]
Paid:   [paid=None]
    - yes (2) --> [paid=True]
    - no (1) --> [paid=False]
>>> qs_predefined = Story.objects.filter(status=Story.PUBLISHED)
>>> filters = FilterList(request, qs_predefined, filter_settings)
>>> for f in filters:
...     print u'%s:   [%s]' % (f.title, f.urlencode)
...     for c in f.choices:
...         print u'    - %s (%s) --> [%s]' % (c.title, c.items_count, c.urlencode)
Category:   [categories__slug=None]
    - News (2) --> [categories__slug=news]
    - Misc (1) --> [categories__slug=misc]
Written by:   [author=1]
    - John (1) --> [author=1]
    - Mary (1) --> [author=2]
Status:   [status=pub]
    - Published (2) --> [status=pub]
Paid:   [paid=None]
    - yes (1) --> [paid=True]
    - no (1) --> [paid=False]
>>> qs_predefined = Story.objects.filter(author__name__contains='J')
>>> filters = FilterList(mock_request(status=Story.PUBLISHED), qs_predefined, filter_settings)
>>> filters._qs            # predefined query
[<Story: s1>, <Story: s3>]
>>> filters.clean_query    # query made from scratch, no traces of predefined stuff
[<Story: s1>, <Story: s2>]
>>> filters.object_list    # intersection between the two
[<Story: s1>]
>>> request = mock_request(categories__slug='news')
>>> filters = FilterList(request, qs, filter_settings)
>>> filters
[<RelationFilter "categories__slug": True>, <RelationFilter "author": False>, <AllValuesFilter "status": False>, <BooleanFilter "paid": False>]
>>> filters.active
[<RelationFilter "categories__slug": True>]
>>> filters.object_list
[<Story: s1>, <Story: s2>]

# Test custom filters

>>> from view_shortcuts.filters import AlphabeticFilter
>>> filter_settings = (
...     facet('name', 'name', AlphabeticFilter),
... )
>>> request = mock_request()
>>> qs = Author.objects.all()
>>> filters = FilterList(request, qs, filter_settings)
>>> filters
[<AlphabeticFilter "name": False>]
>>> f = filters[0]
>>> f.choices
[<Choice name="j">, <Choice name="m">]
>>> for c in f.choices:
...     print "%s --> %s" % (c.title, c.urlencode)
J --> name=j
M --> name=m
>>> for value in 'j', 'm':
...     request = mock_request(name=value)
...     filters = FilterList(request, qs, filter_settings)
...     print "value:", value
...     for choice in filters[0].get_active_choices():
...         print '    title "%s", value "%s", %d items' % (choice.title, choice.value, choice.items_count)
value: j
    title "J", value "j", 2 items
value: m
    title "M", value "m", 1 items

"""

import urllib.request, urllib.parse, urllib.error
from django.test import Client
from django.core.handlers.wsgi import WSGIRequest
from django.core.urlresolvers import reverse
from django.db.models import BooleanField, CharField, ForeignKey, IntegerField, \
                             ManyToManyField, Model, SlugField, TextField
from django.utils.translation import ugettext_lazy as _


class Author(Model):
    name = CharField(max_length=255)

    __unicode__ = lambda s: s.name


class Category(Model):
    title = CharField(max_length=255)
    slug  = SlugField()

    __unicode__ = lambda s: s.title


class Story(Model):
    DRAFT, PUBLISHED = 'draft', 'pub'
    STORY_STATUS_CHOICES = (
        (DRAFT,     _('Draft')),
        (PUBLISHED, _('Published')),
    )
    title    = CharField(max_length=255)
    status   = CharField(_('Status'), max_length=255,
                         choices=STORY_STATUS_CHOICES, default=DRAFT)
    author   = ForeignKey(Author, related_name='stories', null=True,
                          verbose_name=_('Written by'))
    categories = ManyToManyField(Category, null=True, related_name='stories',
                               verbose_name=_('Category'))
    text     = TextField()
    paid     = BooleanField(_('Paid'))

    __unicode__ = lambda s: s.title
    get_url     = lambda s: reverse('example-story-detail',
                                    urlconf=None, args=None,
                                    kwargs=dict(object_id=s.pk))


class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.

    Usage:

    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})

    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client

    Once you have a request object you can pass it to any view function,
    just as if that view had been hooked up using a URLconf.

    Source: http://www.djangosnippets.org/snippets/963/
    """
    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)

def mock_request(**kw):
    return RequestFactory().request(QUERY_STRING=urllib.parse.urlencode(kw))
