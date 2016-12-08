# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db.models import CharField, ForeignKey, IntegerField, \
                             ManyToManyField, Model, TextField
from django.utils.translation import ugettext_lazy as _


class Author(Model):
    name = CharField(max_length=255)
    
    __unicode__ = lambda s: s.name

class Category(Model):
    title = CharField(max_length=255)
    
    __unicode__ = lambda s: s.title


class Story(Model):
    DRAFT, PUBLISHED = 0, 1
    STORY_STATUS_CHOICES = (
        (DRAFT,     _('Draft')),
        (PUBLISHED, _('Published')),
    )
    title    = CharField(max_length=255)
    status   = IntegerField(_('Status'), choices=STORY_STATUS_CHOICES, default=DRAFT)
    author   = ForeignKey(Author, related_name='stories', null=True,
                          verbose_name=_('Written by'))
    category = ManyToManyField(Category, null=True, #related_name='category_set',
                               verbose_name=_('Category'))
    text     = TextField()
    
    __unicode__ = lambda s: s.title
    get_url     = lambda s: reverse('example-story-detail',
                                    urlconf=None, args=None,
                                    kwargs=dict(object_id=s.pk))
