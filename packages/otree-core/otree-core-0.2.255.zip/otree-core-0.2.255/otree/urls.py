#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect

from django.conf import urls
from django.utils.importlib import import_module

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.conf import settings

import vanilla

from otree.common_internal import get_models_module


def url_patterns_from_module(module_name):
    """automatically generates URLs for all Views in the module,
    So that you don't need to enumerate them all in urlpatterns.
    URLs take the form "gamename/ViewName".
    See the method url_pattern() for more info

    So call this function in your urls.py and pass it the names of all
    Views modules as strings.

    """

    views_module = import_module(module_name)

    def isview(member):
        return (
            inspect.isclass(member) and
            issubclass(member, vanilla.View) and
            inspect.getmodule(member) == views_module
        )

    all_views = [
        ViewCls for _, ViewCls in inspect.getmembers(views_module, isview)
    ]

    view_urls = []

    for View in all_views:
        if hasattr(View, 'url_pattern'):
            the_url = urls.url(View.url_pattern(), View.as_view())
            view_urls.append(the_url)

    return urls.patterns('', *view_urls)


def augment_urlpatterns(urlpatterns):

    urlpatterns += urls.patterns(
        '',
        urls.url(r'^$', RedirectView.as_view(url='/demo')),
        urls.url(r'^admin/', urls.include(admin.site.urls)),
        urls.url(
            r'^export/(\w+)/$', 'otree.views.export.export',
            name='otree_views_export_export'
        ),
        urls.url(
            r'^export-list/$', 'otree.views.export.export_list',
            name='otree_views_export_export_list'
        ),
        urls.url(
            r'^export-docs/(\w+)/$', 'otree.views.export.export_docs',
            name='otree_views_export_export_docs'
        ),
    )

    urlpatterns += staticfiles_urlpatterns()

    used_names_in_url = set()
    for app_name in settings.INSTALLED_OTREE_APPS:
        models_module = get_models_module(app_name)
        name_in_url = models_module.Constants.name_in_url
        if name_in_url in used_names_in_url:
            msg = (
                "App {} has name_in_url='{}', "
                "which is already used by another app"
            ).format(app_name, name_in_url)
            raise ValueError(msg)

        used_names_in_url.add(name_in_url)
        views_module_name = '{}.views'.format(app_name)
        utilities_module_name = '{}._builtin'.format(app_name)
        urlpatterns += url_patterns_from_module(views_module_name)
        urlpatterns += url_patterns_from_module(utilities_module_name)

    urlpatterns += url_patterns_from_module('otree.views.concrete')
    urlpatterns += url_patterns_from_module('otree.views.demo')
    urlpatterns += url_patterns_from_module('otree.views.admin')
    urlpatterns += urls.patterns(
        'otree.views.ajax_change_list',
        urls.url(
            r'^ajax/otree-change-list-results/$',
            'ajax_otree_change_list_results',
            name='ajax_otree_change_list_results'
        ),
    )

    return urlpatterns
