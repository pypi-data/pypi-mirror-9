# -*- coding: utf-8 -*-
from collections import namedtuple
import inspect
import six
from functools import update_wrapper
from django.conf.urls import patterns, url
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect


def labelize(label):
    return label.replace('_', ' ').strip().title()


class ExtraUrlConfigException(RuntimeError):
    pass


opts = namedtuple('UrlOptions', 'path,label,icon,perm,order,css_class,visible')


def link(path=None, label=None, icon='', permission=None,
         css_class="btn btn-success", order=999, visible=True):
    """
    decorator to mark ModelAdmin method as 'url' links.

    Each decorated method will be added to the ModelAdmin.urls and
    appear as button close to the 'Add <model>'.

    :param path url path for the action
    :param label button label
    :param icon button icon
    :param required permission to run the action

    """

    def link_decorator(func):
        def _inner(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)
            if not isinstance(ret, HttpResponse):
                url = reverse(admin_urlname(self.model._meta, 'changelist'))
                return HttpResponseRedirect(url)
            return ret

        _inner.link = opts(path or func.__name__,
                           label or labelize(func.__name__),
                           icon,
                           permission,
                           order,
                           css_class,
                           visible)

        return _inner

    return link_decorator


def action(path=None, label=None, icon='', permission=None,
           css_class="btn btn-success", order=999, visible=True):
    """
    decorator to mark ModelAdmin method as 'url' action.

    Each decorated method will be added to the ModelAdmin.urls and
    appear as button close to the 'Add <model>'.

    :param path url path for the action
    :param label button label
    :param icon button icon
    :param required permission to run the action

    """

    def action_decorator(func):
        def _inner(self, request, pk):
            try:
                ret = func(self, request, pk)
            except TypeError:
                raise ExtraUrlConfigException("'%s()' must accept 3 arguments. "
                                              "Did you missed 'request' and 'pk' ?" % func.__name__)
            if not isinstance(ret, HttpResponse):
                url = reverse(admin_urlname(self.model._meta, 'change'),
                              args=[pk])
                return HttpResponseRedirect(url)
            return ret

        _inner.action = opts(path or func.__name__,
                             label or labelize(func.__name__),
                             icon,
                             permission,
                             order,
                             css_class,
                             visible)

        return _inner

    return action_decorator


class ExtraUrlMixin(object):
    """
    Allow to add new 'url' to the standard ModelAdmin
    """
    change_list_template = 'admin_extra_urls/change_list.html'
    change_form_template = 'admin_extra_urls/change_form.html'

    def __init__(self, model, admin_site):
        self.extra_buttons = []
        self.extra_detail_buttons = []
        super(ExtraUrlMixin, self).__init__(model, admin_site)

    def get_urls(self):
        self.extra_buttons = []
        self.extra_detail_buttons = []
        extra_urls = {}
        for c in inspect.getmro(self.__class__):
            for method_name, method in six.iteritems(c.__dict__):
                if hasattr(method, 'link'):
                    extra_urls[method_name] = (False, method_name,
                                               getattr(method, 'link'))
                elif hasattr(method, 'action'):
                    extra_urls[method_name] = (True, method_name,
                                               getattr(method, 'action'))

        original = super(ExtraUrlMixin, self).get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        info = [self.model._meta.app_label, self.model._meta.model_name, '']
        extras = []

        for __, entry in extra_urls.items():
            isdetail, method_name, options = entry
            info[2] = method_name
            if isdetail:
                self.extra_detail_buttons.append([method_name, options])
                uri = r'^%s/(?P<pk>.*)/$' % options.path
            else:
                uri = r'^%s/$' % options.path
                self.extra_buttons.append([method_name, options])

            extras.append(url(uri,
                              wrap(getattr(self, method_name)),
                              name='{}_{}_{}'.format(*info)))
        self.extra_buttons = sorted(self.extra_buttons, key=lambda d: d[-1])
        self.extra_detail_buttons = sorted(self.extra_detail_buttons, key=lambda d: d[-1])

        return patterns('', *extras) + original
