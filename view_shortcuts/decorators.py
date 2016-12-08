# -*- coding: utf-8 -*-
#
#  Copyright (c) 2008 Alexander Solovyov (parts)
#  Copyright (c) 2008--2009 Andy Mikhailenko and contributors
#
#  This file is part of Django View Shortcuts.
#
#  Django View Shortcuts is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#

from django.http import HttpRequest
from django.template import RequestContext
from django.shortcuts import render_to_response

def render_to(template=None):
    """
    Decorator for Django views that sends returned dict to render_to_response
    function with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

    :param template: template name to use

    Usage::

        >>> @render_to('foo.html')
        ... def view_foo(request):
        ...     return {'foo':'bar'}
        ...

    Template name can be omitted. The following code will render the output
    to template "foo_detail.html" -- its name is equal to the view function name::

        >>> @render_to()
        ... def foo_detail(request, pk):
        ...     obj = Foo.objects.get(pk=pk)
        ...     return {'object':obj}

    Source: <http://piranha.org.ua/blog/2008/03/22/render-to-improved/>

    Improved by Andy Mikhailenko, 2008--2009:
    + added support for class views (i.e. with "self" in args);
    + template name can be omitted if it's equal to function name + 'html' extension.
    """
    def renderer(func):
        def wrapper(*args, **kw):
            # ensure HttpRequest instance is passed properly
            request = None
            for arg in args:
                if isinstance(arg, HttpRequest):
                    request = arg
                    break
            if not request:
                raise ValueError('Request not found in arguments')

            # call the view function
            output = func(*args, **kw)

            # process results
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request))
            elif isinstance(output, dict):
                # if template not specified, use view function name instead
                if template:
                    tmpl = template
                else:
                    if func.__name__ == '<lambda>':
                        raise TypeError('Decorator render_to cannot be used ' \
                                         'with anonymous functions if template '\
                                         'name is not provided.')
                    tmpl = '%s.html' % func.__name__
                return render_to_response(tmpl, output, RequestContext(request))
            return output
        # preserve custom attributes of the view function
        wrapper.__dict__ = dict(func.__dict__)
        return wrapper
    return renderer

def cached_property(f):
    """A property which value is computed only once and then stored with
    the instance for quick repeated retrieval.
    """
    def _closure(self):
        cache_key = '_cache__%s' % f.__name__
        value = getattr(self, cache_key, None)
        if value == None:
            value = f(self)
            setattr(self, cache_key, value)
        return value
    return property(_closure)
