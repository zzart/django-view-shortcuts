# -*- coding: utf-8 -*-

# django
from django.shortcuts import get_object_or_404
# site
from view_shortcuts.decorators import render_to
from view_shortcuts.filters import FilterList
# app
from models import Story

facets = (
    facet('category'),
    facet('author__pk', 'author', AlphabetRelationFilter),
    facet('status'),
)

@render_to()
def story_list(request):
    items = Story.objects.all() #filter(status=Story.PUBLISHED)
    filters = FilterList(request, items, params=FILTER_MAP)
    # another_query = filters.object_list.filter(foo='bar')
    return dict(filters=filters)

@render_to()
def story_detail(request, object_id):
    obj = get_object_or_404(Story, pk=object_id)
    return dict(object=obj)
