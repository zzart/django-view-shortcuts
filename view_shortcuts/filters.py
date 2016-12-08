# -*- coding: utf-8 -*-
#
#  Copyright (c) 2008--2009 Andy Mikhailenko and contributors
#
#  This file is part of Django View Shortcuts.
#
#  Django View Shortcuts is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#

" A set of typical QuerySet filters for ordinary views. "

import warnings
from urllib.parse import urlencode
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .decorators import cached_property


def filter_date(items, field_name, year, month=None, day=None):
    """
    Filters given queryset by date if any provided. Accepts three scopes: year, month and day.
    Similar to date_based generic view but for ordinary views.

    Instead of:

        def my_entry_list(request, year=None, month=None, day=None):
            entries = Entry.objects.all()
            if year and month and day:
                entries = entries.filter(pub_date__day=day)
            if year and month:
                entries = entries.filter(pub_date__month=month)
            if year:
                entries = entries.filter(pub_date__year=year)

    ...You can just write:

        def my_entry_list(request, year=None, month=None, day=None):
            entries = Entry.objects.all()
            entries = filter_date(entries, 'pub_date', year, month, day)
    """
    if year:
        items = items.filter(**{'%s__year'  % field_name : year})
        if month:
            items = items.filter(**{'%s__month' % field_name : month})
            if day:
                items = items.filter(**{'%s__day' % field_name : day})
    return items

def filter_date_range(items, start, end):
    """
    Filters given queryset by date range.

    Useful for queries with lookups (i.e. 'foo__bar') where nested date lookups
    are not possible (e.g. things like 'foo__somedate__year__gte' are not allowed).

    Usage:
    filter_date_range(queryset, start, end)
    where "start" and "end" are tuples of this form: (field_name, year, [month, [day])

    Example:

        def my_entry_list(request, from_year=None, to_year=None):
            people = Entry.objects.all()
            # show all entries of this year
            people = filter_date_range(people, ('joined', from_year), ('left', to_year))
    """

    def __make_qargs(mode, field_name, year, month, day):
        q_field = '%s__%s' % (field_name, mode)
        q_date  = '%s-%s-%s' % (year, month, day)
        return {q_field:q_date}

    def __make_qargs_till(field_name, year, month='12', day='31'):
        return __make_qargs('lte', field_name, year, month, day)

    def __make_qargs_from(field_name, year, month='01', day='01'):
        return __make_qargs('gte', field_name, year, month, day)

    qargs = dict(__make_qargs_from(*start), **__make_qargs_till(*end))
    items = items.filter(**qargs)
    return items

def filter_field(items, field_name, value):
    """
    Filters given queryset by given field.
    This filter does not significantly shorten your code but does make it a bit more readable.

    Instead of:

        def my_entry_list(request, foo=None, bar=None):
            entries = Entry.objects.all()
            if foo:
                entries = entries.filter(foo=foo)
            if bar:
                entries = entries.filter(bar=bar)

    ...You can write:

        def my_entry_list(request, foo=None, bar=None):
            entries = Entry.objects.all()
            entries = filter_field(entries, 'foo', foo)
            entries = filter_field(entries, 'bar', bar)
    """
    warnings.warn("filter_field() is deprecated, use FilterList() instead.",
                  DeprecationWarning, 2)
    if value:
        items = items.filter(**{field_name:value})
    return items


def filter_param(items, request, field_name, param_name=None):
    """
    Filters given queryset by given field with its value automatically taken from
    given Request parameter. If the param is not specified, it's assumed to be
    of the same name with the field.

    Instead of:

        def my_entry_list(request):
            entries = Entry.objects.all()
            if request.GET.get('foo'):
                entries = entries.filter(foo=request.GET.get('foo'))
            if request.GET.get('barbar'):
                entries = entries.filter(bar=request.GET.get('barbar'))

    You can write:

        def my_entry_list(request):
            entries = Entry.objects.all()
            entries = filter_param(entries, request, 'foo')
            entries = filter_param(entries, request, 'bar', 'barbar')
    """
    warnings.warn("filter_param() is deprecated, use FilterList() instead.",
                  DeprecationWarning, 2)
    param_name = param_name or field_name
    value = request.GET.get(param_name, None)
    if value:
        items = items.filter(**{field_name:value})
    return items


class facet(dict):
    """"A dictionary representing a facet filter settings.
    A Filter instance will be built using them.

    Example:

    >>> facets = (
    ...     facet('category'),
    ...     facet('author__pk', 'author', AlphabetRelationFilter),
    ... )
    >>> FilterList(qs, request, facets)
    """
    def __init__(self, lookup, param=None, kind=None):
        super(dict, self).__init__()
        if kind: assert issubclass(kind, Filter)
        self['lookup'] = lookup
        self['param']  = param or lookup
        self['kind']   = kind or Filter

class FilterList(list):
    """Filters given queryset by multiple fields with their values automatically
    taken from given HttpRequest parameters. If a parameter is not specified,
    it's assumed to be of the same name with the field.

    Instance of this class can be passed directly to template. It provides both
    the resulting queryset and the data to easily build a navigation block.
    (See Filter docstring and example application for details.)

    The keyword 'single' allows to filter by only one parameter even if multiple
    are provided in the request.

    Example One
    -----------

    Filter the entries by fields 'foo' and 'bar' using corresponding
    params from HttpRequest.

    views.py:

        @render_to('foo.html')
        def my_entry_list(request):
            qs = Entry.objects.all()
            filters = FilterList(qs, request, [facet('foo'), facet('bar')])
            return dict(filters=filters)

    templates/foo.html:

        <!-- show list of filters and available choices,
             each choice is clickable:
        -->
        <div id="filters">
            <dl>
            {% for filter in filters %}
                <dt>{{ filter.title }}</dt>
                {% for choice in filter.choices %}
                    {% if choice.active %}
                        <dd>{{ choice.title }}</dd>
                    {% else %}
                        {% if choice.items_count %}
                        <dd><a href="?{{ choice.urlencode }}">{{ choice.title }}</a> ({{ choice.items_count }})</dd>
                        {% endif %}
                    {% endif %}
                {% endfor %}
            {% endfor %}
            </dl>
            {% if filters.active %}
                <p><a href="?">Show all</a></p>
            {% endif %}
        </div>
        <!-- and now show the filtered list of objects -->
        <ul>
        {% for object in filters.object_list %}
            <li>{{ object }}</li>
        {% endfor %}
        </ul>

    Example Two
    -----------

    If param name does not match field name, use tuple instead of string.

    views.py:

        FILTER_MAP = (
            facet('author_id', 'author'),    # ORM lookup, CGI param
            facet('category__slug', 'cat'),
        )
        def my_entry_list(request):
            qs = Entry.objects.all()
            filters = FilterList(qs, request, FILTER_MAP)
            return dict(filters=filters)

    Example Three
    -------------

    FilterList expects and returns QuerySet objects. This means that you can
    easily pre-process and post-process the queries.

    Pre-processing (filter choices will be shown for published entries only):

        @render_to('foo.html')
        def my_entry_list(request):
            qs = Entry.objects.filter(published=True)
            filters = FilterList(qs, request, [facet('foo'), facet('bar')])
            return dict(filters=filters)

    Post-processing:

        @render_to('foo.html')
        def my_entry_list(request):
            qs = Entry.objects.all()
            filters = FilterList(qs, request, [facet('foo'), facet('bar')])
            object_list = filters.object_list
            for o in object_list:
                o.quux = 123
            return dict(filters=filters, object_list=object_list)
    """

    def __init__(self, request, qs, params, single=False, sort_by_usage=True):
        self._qs = qs
        self.single = single
        def _generate_filters(request, qs, params, single, sort_by_usage):
            single_triggered = False
            for p in params:
                klass = Filter
                if isinstance(p, facet):
                    lookup, param, klass = p['lookup'], p['param'], p['kind']
                elif isinstance(p, (tuple,list)):
                    warnings.warn("using tuple for lookup/param coupling is "\
                                  "deprecated, use filters.facet() instead.",
                                  DeprecationWarning, 2)
                    lookup, param = p
                else:
                    lookup = param = p
                active = False
                value = request.GET.get(param)
                if value and not single_triggered:
                    if single:
                        single_triggered = True
                    active = True
                f = klass.create(param, qs, lookup, value, active, sort_by_usage)
                yield f
        super(FilterList, self).__init__(
            _generate_filters(request, qs, params, single, sort_by_usage)
        )

    @cached_property
    def urlencode(self):
        """Encodes currently active filters so that they could be
        added to an URL as query string.
        """
        return urlencode([(f.param, f.value) for f in self.active])

    @cached_property
    def active(self):
        "Returns currently active filters. In single mode returns only the first one."
        if self.single:
            for f in self:
                if f.active:
                    return [f]
            return []
        else:
            return [f for f in self if f.active]

    @cached_property
    def object_list(self):
        """Applies currently active filters (known from the Request object)
        to the predefined QuerySet and returns the resulting QuerySet object.
        """
        return self._qs & self.clean_query

    @cached_property
    def clean_query(self):
        """Returns a QuerySet built from scratch with respect to active filter.
        Can be used to create arbitrary queries based on filters only.

        Real-life example: a set of shop items is filtered by region, then
        by facets. We want to generate statistics with a template tag (not in views)
        for *all* regions but with respect to current facets.
        The best way would be to simply remove the region facet from the queryset;
        unfortunately, it's technically impossible.
        Another way would be to pass two versions of the same queryset (with and
        without regional filter) into the template. However, regional facet *must*
        be applied before generating a FilterList because the list should display
        option count with respect to the region.
        The method ``clean_query`` allows to re-generate the queryset from scratch
        and only pass the FilterList instance to template.
        Of course custom query managers are also reset.
        """

        q = self._qs.model.objects.all()        # TODO use _default_manager?
        for f in self.active:
            q = f.filter(q)
        return q


class Filter(object):
    """ A facet filter. Objects of this class are instantiated by filter_params()
    and returned along with the queryset.
    Filter objects can then be passed to template and used to generate UI
    for tuning the queryset.

    By default the choices are sorted by usage (most referenced on top). To reset
    this behaviour, set sort_by_usage=False,

    Usage: see FilterList.

    Each filter subclass knows how to display a filter for a field that passes a
    certain test -- e.g. being a DateField or ForeignKey.
    """

    # TODO replace (qs, lookup, param) with (model, attribute) and let specify other stuff _if needed_.

    _cached_fields = {}
    _filter_specs = []
    def __init__(self, param, qs, lookup, value, active=False, sort_by_usage=False):
        self.param = param
        self.qs = qs
        self.lookup = lookup
        self.value = value
        self.active = active
        self.sort_by_usage = sort_by_usage
        self.field = self.resolve_field(qs, lookup)

    def __repr__(self):
        return '<%s "%s": %s>' % (self.__class__.__name__, self.param, self.active)

    @classmethod
    def register(cls, factory):
        """Registers Filter subclass so that it can be automatically chosen if
        no concrete class is explicitly specified. Note that classes are checked
        one by one in the order they are registered, and the first one which passes
        the test (i.e. which ``suitable_for()`` method returns True for given
        field) is chosen. The last one should be the universal AllValuesFilter.
        If your class is registered after it, it will *not* be used. If your
        class appears to be "all values" too, do not register it -- just specify
        it in your views in a facet.
        """
        cls._filter_specs.append(factory)

    @staticmethod
    def resolve_field(qs, lookup):
        f = None
        if lookup not in Filter._cached_fields:
            # we need the "author" part of "author__pk" lookup
            f = qs.model._meta.get_field(lookup.split('__')[0])
        return Filter._cached_fields.setdefault(lookup, f)

    @classmethod
    def create(cls, param, qs, lookup, value, active=False, sort_by_usage=True):
        # chosen by user
        if not cls == Filter:
            return cls(param, qs, lookup, value, active, sort_by_usage)
        # autoselect
        field = cls.resolve_field(qs,lookup)
        for factory in cls._filter_specs:
            if factory.suitable_for(field):
                return factory(param, qs, lookup, value, active, sort_by_usage)

    @classmethod
    def suitable_for(cls, field):
        return True

    @cached_property
    def urlencode(self):
        return urlencode({self.param: self.value})

    def extra_title(self):
        """Filter subclasses may overload this method to provide extra sources
        for filter title; they will only be used if no verbose name is specified
        in current model's field definition.
        """
        return None

    @cached_property
    def title(self):
        "Returns human-readable field name (if accessible)."
        return str(self.field.verbose_name or self.extra_title())

    def generate_choices(self):
        raise NotImplementedError

    @cached_property
    def choices(self):
        """Returns possible choices, each annotated with the number of linked
        objects. Multiple FKs from one model to another are supported as well as
        explicit choice lists and implicit ones (i.e. any possible values).

        Resulting list contains FilterChoice objects.

        An existing choice will be excluded from results if:

          a) it is not used by any object in current queryset;

          b) it is used but is not in the field's explicit list of choices
             (i.e. the "choices" keyword).
        """
        return list(self.generate_choices())

    def get_active_choices(self):
        "Returns list of currently selected options for this filter."
        for c in self.choices:
            if c.active:
                yield c

    def get_first_active_choice(self):
        "Returns one of currently selected options for this filter (usually enough)."
        for c in self.get_active_choices():
            return c

    def _annotate(self, choices, by='pk'):
        """Counts related objects for each choice in given queryset (i.e. discover
        how popular is each option). Returns annotated queryset.
        """
        #
        choices = choices.annotate(items_count=models.Count(by))
        if self.sort_by_usage:
            choices = choices.order_by('-items_count')
        return choices

    def filter(self, qs):
        return qs.filter(**{self.lookup: self.value})


class RelationFilter(Filter):
    @classmethod
    def suitable_for(cls, field):
        if field.rel:
            return True

    def extra_title(self):
        if isinstance(self.field, models.ManyToManyField):
            return self.field.rel.to._meta.verbose_name

    def generate_choices(self):
        # TODO: when multiple filters are active, count only intersections (? - can be heavy)

        related_name = getattr(self.field.rel, 'related_name', None) or \
                self.qs.model._meta.module_name
        # get all possible choices
        choices = self.field.rel.to.objects
        # apply constraints from field definition
        choices = choices.filter(**self.field.rel.limit_choices_to)
        # get intersection with current queryset
        choices = choices.filter(**{'%s__in' % related_name: self.qs })
        # count usage
        choices = self._annotate(choices, by=related_name)

        for c in choices:
            value = c.pk
            if '__' in self.lookup:
                try:
                    _, attr = self.lookup.split('__')
                except ValueError:
                    raise ValueError('Facet lookup must contain no more than '
                                     'two parts (got "%s")' % self.lookup)
                else:
                    value = getattr(c, attr)
            yield FilterChoice(self, str(c), value, c.items_count)
Filter.register(RelationFilter)


'''
@Filter.register
class DateFadeoutFilter(Filter):
    "Represents dates as single-level categories by remoteness from now."

    @staticmethod
    def suitable_for(field):
        return isinstance(f, models.DateField)

    # see django.contrib.admin.filterspecs.DateFieldFilterSpec
    pass


@Filter.register
class DateDrilldownFilter(Filter):
    "Represents dates as nested levels for year, month and day."

    @staticmethod
    def suitable_for(field):
        return isinstance(f, models.DateField)

    pass
'''


class BooleanFilter(Filter):
    @staticmethod
    def suitable_for(field):
        return isinstance(field, models.BooleanField)

    def generate_choices(self):
        # retrieve unique values and count how many times each is used
        choices = self.qs.values(self.lookup).distinct()
        choices = self._annotate(choices)

        bool_choices = (
            ('True',  _('yes')),
            ('False', _('no')),
        )
        for val,name in bool_choices:
            for c in choices:
                v = str(c.get(self.lookup))
                if v == val:
                    yield FilterChoice(self, name, val, c['items_count'])
Filter.register(BooleanFilter)


class AlphabeticFilter(Filter):
    def generate_choices(self):
        choices = self.qs.values(self.lookup).distinct()
        choices = self._annotate(choices)
        chars = {}
        # compress the list, combine counters
        for choice in choices:
            char = str(choice.get(self.lookup))[0].lower()
            chars[char] = chars.setdefault(char, 0) + 1
        for char in sorted(chars.keys()):
            yield FilterChoice(self, char.upper(), char, chars[char])

    def filter(self, qs):
        assert isinstance(self.value, str)
        lookup = '%s__startswith' % self.lookup
        q1 = models.Q(**{lookup: self.value.lower()})
        q2 = models.Q(**{lookup: self.value.upper()})
        return qs.filter(q1 | q2)


class AllValuesFilter(Filter):
    def generate_choices(self):
        # retrieve unique values and count how many times each is used
        choices = self.qs.values(self.lookup).distinct()
        choices = self._annotate(choices)

        # if list of choices is explicitly defined, exclude choices that
        # are not in this list (e.g. if the list was added post factum)
        if self.field.choices:
            explicit_values = [ c[0] for c in self.field.choices ]
            choices = choices.filter(**{'%s__in' % self.lookup: explicit_values})

        # choice title is its value unless the label is explicitly defined
        _value = lambda c: str(c.get(self.lookup))
        _title = lambda c: self.field.choices and \
                        dict(self.field.choices).get(c.get(self.lookup)) or _value(c)

        for c in choices:
            yield FilterChoice(self, _title(c), _value(c), c['items_count'])
Filter.register(AllValuesFilter)


class FilterChoice(object):
    def __init__(self, filter, title, value, items_count):
        # TODO accept model objects and parse them as late as possible using self.filter
        self.filter = filter
        self.title = title
        self.value = value
        self.items_count = items_count

    def __repr__(self):
        return '<Choice %s="%s">' % (self.filter.param, self.value)

    @cached_property
    def urlencode(self):
        value = self.value.encode('utf-8') if isinstance(self.value, str) else self.value
        return urlencode({self.filter.param: value})

    @cached_property
    def active(self):
        "Returns True if the choice value equals to the filter's current value."
        try:
            return self.value == type(self.value)(self.filter.value)
        except TypeError as ValueError:
            return False


def filter_params(qs, request, params, single=False):
    warnings.warn("filter_params() is deprecated, use FilterList() instead.",
                  DeprecationWarning, 2)
    filters = FilterList(request, qs, params, single)
    return filters.object_list, filters

def get_current_filter(request, qs, params):
    "Returns currently active single filter (if any)."
    filters = FilterList(request, qs, params, single=True)
    if filters.active:
        return filters.active[0]
