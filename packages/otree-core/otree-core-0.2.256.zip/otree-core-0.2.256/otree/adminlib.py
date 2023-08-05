#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict

from django.contrib import admin
from django.conf.urls import patterns
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
import django.db.models.options
import django.db.models.fields.related
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.staticfiles.templatetags.staticfiles import (
    static as static_template_tag
)

import otree.constants
import otree.models.session
from otree.models.session import ParticipantProxy
from otree.common_internal import add_params_to_url
from otree.common import Currency as c
from otree.common import Money
from otree.views.demo import render_to_start_links_page


def session_monitor_url(session):
    participants_table_url = reverse('admin:{}_{}_changelist'.format(
        ParticipantProxy._meta.app_label, ParticipantProxy._meta.module_name
    ))
    return add_params_to_url(participants_table_url, {'session': session.pk})


def new_tab_link(url, label):
    return '<a href="{}" target="_blank">{}</a>'.format(url, label)


def remove_duplicates(lst):
    return list(OrderedDict.fromkeys(lst))


def get_callables(Model,
                  fields_specific_to_this_subclass=None, for_export=False):

    fields_specific_to_this_subclass = fields_specific_to_this_subclass or []

    export_and_changelist = {
        'Player': [],
        'Group': [],
        'Subsession': [],
        'Session': [],
        'Participant': [],
    }[Model.__name__]

    changelist_but_not_export = {
        'Player': [],
        'Group': [],
        'Subsession': [],
        'Session': [
            'start_links_link',
            'participants_table_link',
            'raw_participant_urls_link',
            'payments_ready',
            'payments_link',
            'is_open',
        ],
        'Participant': [
            '_id_in_session_display',
            '_pages_completed',
            '_current_app_name',
            'status',
            'start_link',
        ],
    }[Model.__name__]

    export_but_not_changelist = {
        'Player': [],
        'Group': [],
        'Subsession': [],
        'Session': [],
        'Participant': [],
    }[Model.__name__]

    if for_export:
        callables = export_and_changelist + export_but_not_changelist
    else:
        callables = export_and_changelist + changelist_but_not_export

    return remove_duplicates(callables + fields_specific_to_this_subclass)


def get_readonly_fields(Model, fields_specific_to_this_subclass=None):
    callables = get_callables(Model, fields_specific_to_this_subclass)

    for_change_page_and_list = {
        'Player': [],
        'Group': [],
        'Subsession': [],
        'Session': [
            'code',
            'session_type_name',
            'time_started',
            '_players_assigned_to_groups',
            'special_category',
        ],
        'Participant': [],
    }[Model.__name__]

    return remove_duplicates(callables + for_change_page_and_list)


def get_all_fields_for_table(Model, callables,
                             first_fields=None, for_export=False):

    first_fields = {
        'Player':
            [
                'id',
                'name',
                'session',
                'subsession',
                'group',
                'id_in_group',
                'role',
            ],
        'Group':
            [
                'id',
                'session',
                'subsession',
            ],
        'Subsession':
            ['name',
             'session'],
        'Participant':
            [
                '_id_in_session_display',
                'code',
                'label',
                'start_link',
                '_pages_completed',
                '_current_app_name',
                '_round_number',
                '_current_page_name',
                'status',
                'last_request_succeeded',
            ],
        'Session':
            [
                'code',
                'session_type_name',
                'label',
                'hidden',
                'type',
            ],
    }[Model.__name__]

    last_fields = {
        'Player': [],
        'Group': [],
        'Subsession': [],
        'Participant': [
            'start_link',
            'exclude_from_data_analysis',
        ],
        'Session': [
        ],
    }[Model.__name__]

    fields_for_export_but_not_changelist = {
        'Player': {'id', 'label'},
        'Group': {'id'},
        'Subsession': {'id'},
        'Session': {
            'git_commit_timestamp',
            # 'fixed_pay',
        },
        'Participant': {
            # 'label',
            'ip_address',
            'time_started',
        },
    }[Model.__name__]

    fields_for_changelist_but_not_export = {
        'Player': {'group', 'subsession', 'session', 'participant'},
        'Group': {'subsession', 'session'},
        'Subsession': {'session'},
        'Session': {
            'players_assigned_to_groups',
            'hidden',
        },
        'Participant': {
            'name',
            'start_link',
            'session',
            'visited',
            # used to tell how long participant has been on a page
            '_last_page_timestamp',
            # the following fields are useful for telling if the participant
            # actually finished:
            #  '_pages_completed',
            #  '_current_app_name',
            #  '_current_page_name',
            'status',
            'last_request_succeeded',
        },
    }[Model.__name__]

    fields_to_exclude_from_export_and_changelist = {
        'Player': {
            '_index_in_game_pages',
            'participant',
        },
        'Group': set(),
        'Subsession': {
            'code',
            'label',
            'session_access_code',
            '_experimenter',
        },
        'Participant': {
            'id',
            'id_in_session',
            'session',  # because we already filter by session
            '_index_in_subsessions',
            'is_on_wait_page',
            'mturk_assignment_id',
            'mturk_worker_id',
            'vars',
            '_current_form_page_url',
            '_max_page_index',
            '_predetermined_arrival_order',
            '_index_in_pages',
            'visited',  # not necessary because 'status' column includes this
            '_waiting_for_ids',
            '_last_request_timestamp',
        },
        'Session': {
            'mturk_payment_was_sent',

            # can't be shown on change page, because pk not editable?
            'id',
            'session_experimenter',
            'subsession_names',
            'demo_already_used',
            'ready',
            'vars',
            '_pre_create_id',
            # don't hide the code, since it's useful as a checksum
            # (e.g. if you're on the payments page)
        }
    }[Model.__name__]

    if for_export:
        fields_to_exclude = fields_to_exclude_from_export_and_changelist.union(
            fields_for_changelist_but_not_export
        )
    else:
        fields_to_exclude = fields_to_exclude_from_export_and_changelist.union(
            fields_for_export_but_not_changelist
        )

    all_field_names = [field.name for field in Model._meta.fields
                       if field.name not in fields_to_exclude]
    all_member_names = set(callables + all_field_names)
    first_fields = [f for f in first_fields if f in all_member_names]
    last_fields = [f for f in last_fields if f in all_member_names]
    table_columns = first_fields + callables + all_field_names
    table_columns = (
        [f for f in table_columns if f not in last_fields] + last_fields
    )

    if for_export:
        return remove_duplicates(table_columns)
    else:
        return _add_links_for_foreign_keys(
            Model, remove_duplicates(table_columns)
        )


def get_all_fields_for_change_page(Model, readonly_fields):

    table_fields = get_all_fields_for_table(Model, readonly_fields)

    for_change_page_only = {
        'Player': [],
        'Group': [],
        'Subsession': [],
        'Session': [
            'time_scheduled',
            'comment',
        ],
        'Participant': [],
    }[Model.__name__]

    return remove_duplicates(table_fields + for_change_page_only)


def get_list_display(Model, readonly_fields, first_fields=None):
    return get_all_fields_for_table(Model, callables=readonly_fields,
                                    first_fields=first_fields,
                                    for_export=False)


class FieldLinkToForeignKey:
    def __init__(self, list_display_field):
        self.list_display_field = list_display_field

    @property
    def __name__(self):
        return self.list_display_field

    def __repr__(self):
        return self.list_display_field

    def __str__(self):
        return self.list_display_field

    def __call__(self, instance):
        object = getattr(instance, self.list_display_field)
        if object is None:
            return "(None)"
        else:
            pattern = 'admin:{}_{}_change'.format(
                object._meta.app_label,  object._meta.module_name
            )
            url = reverse(pattern, args=[object.id])
            return '<a href="{}">{}</a>'.format(url, object.__unicode__())

    @property
    def allow_tags(self):
        return True


def _add_links_for_foreign_keys(model, list_display_fields):

    result = []
    for list_display_field in list_display_fields:
        if hasattr(model, list_display_field):
            try:
                if isinstance(model._meta.get_field(list_display_field),
                              django.db.models.fields.related.ForeignKey):
                    result.append(FieldLinkToForeignKey(list_display_field))
                    continue
            except django.db.models.options.FieldDoesNotExist:
                pass
        result.append(list_display_field)
    return result


class NonHiddenSessionListFilter(admin.SimpleListFilter):
    title = "session"

    parameter_name = "session"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [(session.id, session.id) for session
                in otree.models.session.Session.objects.filter(hidden=False)]

    # is queryset method still necessary in 1.7?
    #
    #   def queryset(self, request, queryset):
    #       return self.get_queryset(request, queryset)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() is not None:
            return queryset.filter(session__pk=self.value())
        else:
            return queryset


class OTreeBaseModelAdmin(admin.ModelAdmin):
    """Allow leaving fields blank in the admin"""
    def get_form(self, request, obj=None, **kwargs):
        form = super(OTreeBaseModelAdmin, self).get_form(
            request, obj, **kwargs
        )
        for key in form.base_fields.keys():
            try:
                model_field, _, _, _ = self.model._meta.get_field_by_name(key)
                if model_field.null:
                    form.base_fields[key].required = False
            except django.db.models.options.FieldDoesNotExist:
                pass
        return form

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['extra_tools'] = getattr(self, "extra_tools", ())
        extra_context['table_title'] = getattr(self, "table_title", None)
        return super(OTreeBaseModelAdmin, self).changelist_view(
            request, extra_context=extra_context
        )


class PlayerAdmin(OTreeBaseModelAdmin):
    change_list_template = "admin/otree_change_list.html"

    list_filter = [NonHiddenSessionListFilter, 'subsession', 'group']
    list_per_page = 40

    def get_queryset(self, request):
        qs = super(PlayerAdmin, self).get_queryset(request)
        return qs.filter(session__hidden=False)


class GroupAdmin(OTreeBaseModelAdmin):
    change_list_template = "admin/otree_change_list.html"

    list_filter = [NonHiddenSessionListFilter, 'subsession']
    list_per_page = 40

    def get_queryset(self, request):
        qs = super(GroupAdmin, self).get_queryset(request)
        return qs.filter(session__hidden=False)


class SubsessionAdmin(OTreeBaseModelAdmin):

    change_list_template = "admin/otree_change_list.html"
    list_filter = [NonHiddenSessionListFilter]

    def get_queryset(self, request):
        qs = super(SubsessionAdmin, self).get_queryset(request)
        return qs.filter(session__hidden=False)


class GlobalSingletonAdmin(OTreeBaseModelAdmin):
    list_display = ['id', 'open_session',
                    'persistent_urls_link', 'mturk_snippet_link']
    list_editable = ['open_session']

    def get_urls(self):
        urls = super(GlobalSingletonAdmin, self).get_urls()
        my_urls = patterns(
            '',
            (
                r'^(?P<pk>\d+)/mturk_snippet/$',
                self.admin_site.admin_view(self.mturk_snippet)
            ),
            (
                r'^(?P<pk>\d+)/persistent_urls/$',
                self.admin_site.admin_view(self.persistent_urls)
            ),
        )
        return my_urls + urls

    def persistent_urls_link(self, instance):
        return new_tab_link('{}/persistent_urls/'.format(instance.pk), 'Link')
    persistent_urls_link.allow_tags = True
    persistent_urls_link.short_description = "Persistent URLs"

    def persistent_urls(self, request, pk):
        from otree.views.concrete import AssignVisitorToOpenSession
        open_session_base_url = request.build_absolute_uri(
            AssignVisitorToOpenSession.url()
        )
        open_session_example_urls = []
        for i in range(1, 31):
            open_session_example_urls.append(
                add_params_to_url(
                    open_session_base_url,
                    {otree.constants.participant_label: 'P{}'.format(i)}
                )
            )

        return TemplateResponse(
            request,
            'otree/admin/PersistentLabURLs.html',
            {
                'open_session_example_urls': open_session_example_urls,
                'access_code_for_open_session': (
                    otree.constants.access_code_for_open_session
                ),
                'participant_label': otree.constants.participant_label
            }
        )

    def mturk_snippet_link(self, instance):
        return new_tab_link('{}/mturk_snippet/'.format(instance.pk), 'Link')

    mturk_snippet_link.allow_tags = True
    mturk_snippet_link.short_description = "HTML snippet for MTurk HIT page"

    def mturk_snippet(self, request, pk):
        hit_page_js_url = request.build_absolute_uri(
            static_template_tag('otree/js/mturk_hit_page.js')
        )
        from otree.views.concrete import AssignVisitorToOpenSessionMTurk
        open_session_url = request.build_absolute_uri(
            AssignVisitorToOpenSessionMTurk.url()
        )
        context = {'hit_page_js_url': hit_page_js_url,
                   'open_session_url': open_session_url}
        return TemplateResponse(request, 'otree/admin/MTurkSnippet.html',
                                context, content_type='text/plain')


class ParticipantAdmin(OTreeBaseModelAdmin):
    change_list_template = "admin/otree_change_list.html"

    list_filter = [NonHiddenSessionListFilter]

    readonly_fields = get_callables(otree.models.session.Participant, [])
    list_display = get_all_fields_for_table(
        otree.models.session.Participant, readonly_fields
    )
    list_editable = ['exclude_from_data_analysis']

    list_display_links = None

    def start_link(self, instance):
        url = instance._start_url()
        return new_tab_link(url, 'Link')
    start_link.allow_tags = True

    def get_queryset(self, request):
        qs = super(ParticipantAdmin, self).get_queryset(request)
        return qs.filter(session__hidden=False)


class MonitorParticipantAdmin(ParticipantAdmin):

    list_filter = []

    def has_add_permission(self, request):
        """Hide add button"""
        return False

    def get_model_perms(self, request):
        """Return empty perms dict thus hiding the model from admin index."""
        return {}

    def changelist_view(self, request, extra_context=None):
        from otree.views.concrete import AdvanceSession

        self.session = otree.models.session.Session(pk=request.GET["session"])
        self.advance_session_url = request.build_absolute_uri(
            AdvanceSession.url(self.session)
        )
        return super(MonitorParticipantAdmin, self).changelist_view(
            request, extra_context
        )

    def extra_tools(self):
        return [("Advance slowest participant(s)", self.advance_session_url)]

    def table_title(self):
        title = u"{} of Session '{}'".format(
            self.model._meta.verbose_name, self.session.pk
        )
        return title


class SessionAdmin(OTreeBaseModelAdmin):
    change_list_template = "admin/otree_change_list.html"

    def get_urls(self):
        urls = super(SessionAdmin, self).get_urls()
        my_urls = patterns(
            '',
            (
                r'^(?P<pk>\d+)/payments/$',
                self.admin_site.admin_view(self.payments)
            ),
            (
                r'^(?P<pk>\d+)/raw_participant_urls/$',
                self.raw_participant_urls
            ),
            (r'^(?P<pk>\d+)/start_links/$', self.start_links),
        )
        return my_urls + urls

    def participants_table_link(self, instance):
        return new_tab_link(
            session_monitor_url(instance),
            'Link'
        )

    participants_table_link.allow_tags = True
    participants_table_link.short_description = 'Monitor participants'

    def participant_urls(self, request, session):
        participants = session.get_participants()
        return [request.build_absolute_uri(participant._start_url())
                for participant in participants]

    def start_links(self, request, pk):
        session = self.model.objects.get(pk=pk)
        return render_to_start_links_page(request, session)

    def start_links_link(self, instance):
        return new_tab_link(
            '/admin/session/session/{}/start_links/'.format(instance.pk),
            'Link'
        )

    start_links_link.short_description = 'Start links'
    start_links_link.allow_tags = True

    def raw_participant_urls(self, request, pk):
        session = self.model.objects.get(pk=pk)
        cond = (
            request.GET.get(otree.constants.session_user_code) !=
            session.session_experimenter.code
        )
        if cond:
            msg = '{} parameter missing or incorrect'.format(
                otree.constants.session_user_code
            )
            return HttpResponseBadRequest(msg)
        urls = self.participant_urls(request, session)
        return HttpResponse('\n'.join(urls), content_type="text/plain")

    def raw_participant_urls_link(self, instance):
        link = '/admin/session/session/{}/raw_participant_urls/?{}={}'.format(
            instance.pk, otree.constants.session_user_code,
            instance.session_experimenter.code
        )
        return new_tab_link(link, 'Link')

    raw_participant_urls_link.short_description = 'Participant URLs'
    raw_participant_urls_link.allow_tags = True

    def payments(self, request, pk):
        session = self.model.objects.get(pk=pk)
        participants = session.get_participants()
        total_payments = sum(
            participant.total_pay() or c(0) for participant in participants
        ).to_money(session)

        try:
            mean_payment = total_payments / len(participants)
        except ZeroDivisionError:
            mean_payment = Money(0)

        ctx = {
            'participants': participants,
            'total_payments': total_payments,
            'mean_payment': mean_payment,
            'session_code': session.code,
            'session_type': session.session_type_name,
            'fixed_pay': session.fixed_pay.to_money(session),
        }
        return TemplateResponse(request, 'otree/admin/Payments.html', ctx)

    def payments_link(self, instance):
        if instance.payments_ready():
            link_text = 'Ready'
        else:
            link_text = 'Incomplete'
        # FIXME: use proper URL
        link = '/admin/session/session/{}/payments/'.format(instance.pk)
        return new_tab_link(link, link_text)

    payments_link.short_description = "Payments page"
    payments_link.allow_tags = True

    readonly_fields = get_readonly_fields(otree.models.session.Session, [])
    list_display = get_all_fields_for_table(
        otree.models.session.Session, readonly_fields
    )

    fields = get_all_fields_for_change_page(
        otree.models.session.Session, readonly_fields
    )

    list_editable = ['hidden']


def autodiscover():
    """
    # django-1.7 -- will this still work?

    The purpose of this function is to look for an admin.py not in an app's
    root directory, but rather under a _builtin folder. This is because it's
    not common for an oTree programmer to customize the admin, so it's good to
    get admin.py out of the way so the programmer can focus on other things.
    in fact, it may be OK to get rid of admin.py entirely, and move to
    otree-core the code that registers the admin models.

    The below function is copied from django 1.6's
    django/contrib/admin/__init__.py I modified it to look instead for
    _builtin.admin.

    If we keep this in Django 1.7, we may want to instead use
    django.utils.module_loading.autodiscover_modules, which is better
    abstracted. But Django docs say this is now handled by AdminConfig rather
    than calling autodiscover()
    explicitly: http://goo.gl/YIQ3Gj. i don't have any knowledge of what
    AdminConfig is.

    """

    from django.contrib.admin.sites import site
    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        if app in settings.INSTALLED_OTREE_APPS:
            admin_module_dotted_path = '_builtin.admin'
        else:
            admin_module_dotted_path = 'admin'

        mod = import_module(app)
        # Attempt to import the app's admin module.
        try:
            before_import_registry = copy.copy(site._registry)
            import_module('{}.{}'.format(app, admin_module_dotted_path))
        except:
            # Reset the model registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            # (see #8245).
            site._registry = before_import_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have an admin module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, admin_module_dotted_path):
                raise
