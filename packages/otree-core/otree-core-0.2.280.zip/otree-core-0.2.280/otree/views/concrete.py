#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# IMPORTS
# =============================================================================

import time
import vanilla

import django.utils.timezone
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.contrib import messages
from django.http import (
    HttpResponse, HttpResponseRedirect, HttpResponseNotFound
)

import otree.constants as constants
import otree.models.session
from otree.models.session import Participant
from otree.models.session import lock_on_this_code_path
import otree.views.admin
import otree.common_internal
from otree.views.abstract import (
    NonSequenceUrlMixin, OTreeMixin, AssignVisitorToOpenSessionBase,
    GenericWaitPageMixin, FormPageOrWaitPageMixin, PlayerMixin
)
from otree.models_concrete import GroupSize


class OutOfRangeNotification(NonSequenceUrlMixin, OTreeMixin, vanilla.View):
    name_in_url = 'shared'

    def dispatch(self, request, *args, **kwargs):
        user_type = kwargs.pop(constants.user_type)
        if user_type == constants.user_type_experimenter:
            return TemplateResponse(
                request, 'otree/OutOfRangeNotificationExperimenter.html'
            )
        else:
            return TemplateResponse(
                request, 'otree/OutOfRangeNotification.html'
            )


class WaitUntilAssignedToGroup(FormPageOrWaitPageMixin, PlayerMixin,
                               GenericWaitPageMixin, vanilla.View):
    """This is visited after Initialize, to make sure the player has a group
    the player can be assigned at any time, but this is a safeguard,
    and therefore should be at the beginning of each subsession.
    Should it instead be called after InitializeParticipant?
    Someday, we might want to shuffle players dynamically,
    e.g. based on the results of the past game.
    """
    name_in_url = 'shared'

    def _is_ready(self):
        if bool(self.group):
            return True
        elif self.session.session_type['group_by_arrival_time']:
            with lock_on_this_code_path():
                if self.subsession.round_number == 1:
                    open_group = self.subsession._get_open_group()
                    group_players = open_group.get_players()
                    group_players.append(self.player)
                    open_group.set_players(group_players)
                    group_size_obj = GroupSize.objects.filter(
                        app_label=self.subsession._meta.app_label,
                        subsession_pk=self.subsession.pk,
                    ).order_by('group_index')[0]
                    group_quota = group_size_obj.group_size
                    if len(group_players) == group_quota:
                        open_group._is_missing_players = False
                        group_size_obj.delete()
                    open_group.save()
                else:
                    self.subsession._create_groups()
            return True
        return False

    def body_text(self):
        return (
            'Waiting until other participants and/or '
            'the study supervisor are ready.'
        )

    def _response_when_ready(self):
        self._increment_index_in_pages()
        # so it can be shown in the admin
        self._session_user._round_number = self.subsession.round_number
        return self._redirect_to_page_the_user_should_be_on()

    def get_debug_values(self):
        pass


class SessionExperimenterWaitUntilPlayersAreAssigned(NonSequenceUrlMixin,
                                                     GenericWaitPageMixin,
                                                     vanilla.View):

    def title_text(self):
        return 'Please wait'

    def body_text(self):
        return 'Assigning players to groups.'

    def _is_ready(self):
        return self.session._ready_to_play

    @classmethod
    def get_name_in_url(cls):
        return 'shared'

    def dispatch(self, request, *args, **kwargs):
        session_user_code = kwargs[constants.session_user_code]
        self.request.session[session_user_code] = {}

        self._session_user = get_object_or_404(
            otree.models.session.SessionExperimenter,
            code=kwargs[constants.session_user_code]
        )

        self.session = self._session_user.session

        if self.request_is_from_wait_page():
            return self._response_to_wait_page()
        else:
            # if the player shouldn't see this view, skip to the next
            if self._is_ready():
                # FIXME 2014-12-4: what should this do instead of directing
                # to the start url?
                return HttpResponse(
                    'not yet implemented: redirect to experimenter page'
                )
            return self._get_wait_page()


class InitializeParticipant(vanilla.UpdateView):
    """just collects data and sets properties. not essential to functionality.
    the only exception is if the participant needs to be assigned to groups on
    the fly, which is done here.

    2014-11-16: also, this sets _last_page_timestamp. what if that is not set?
    will it still work?

    """

    @classmethod
    def url_pattern(cls):
        return r'^InitializeParticipant/(?P<{}>[a-z]+)/$'.format(
            constants.session_user_code
        )

    def get(self, *args, **kwargs):

        session_user = get_object_or_404(
            otree.models.session.Participant,
            code=kwargs[constants.session_user_code]
        )

        session_user.visited = True

        # session_user.label might already have been set by AssignToOpenSession
        session_user.label = session_user.label or self.request.GET.get(
            constants.participant_label
        )
        session_user.ip_address = self.request.META['REMOTE_ADDR']

        now = django.utils.timezone.now()
        session_user.time_started = now
        session_user._last_page_timestamp = time.time()
        session_user.save()
        first_url = session_user._url_i_should_be_on()
        return HttpResponseRedirect(first_url)


class MTurkLandingPage(vanilla.TemplateView):

    def get_template_names(self):
        hit_settings = self.session.session_type['mturk_hit_settings']
        return hit_settings['preview_template']

    @classmethod
    def url_pattern(cls):
        return r"^MTurkLandingPage/(?P<session_code>[a-z]+)/$"

    @classmethod
    def url_name(cls):
        return 'mturk_landing_page'

    def dispatch(self, request, *args, **kwargs):
        session_code = kwargs['session_code']
        self.session = get_object_or_404(
            otree.models.Session, code=session_code
        )
        return super(MTurkLandingPage, self).dispatch(
            request, *args, **kwargs
        )

    def get(self, request, *args, **kwargs):
        assignment_id = (
            self.request.GET['assignmentId']
            if 'assignmentId' in self.request.GET else
            ''
        )
        if assignment_id and assignment_id != 'ASSIGNMENT_ID_NOT_AVAILABLE':
            url_start = reverse('mturk_start', args=(self.session.code,))
            url_start = otree.common_internal.add_params_to_url(url_start, {
                'assignmentId': self.request.GET['assignmentId'],
                'workerId': self.request.GET['workerId']})
            return HttpResponseRedirect(url_start)
        else:
            context = super(MTurkLandingPage, self).get_context_data(**kwargs)
            return self.render_to_response(context)


class MTurkStart(vanilla.View):

    @classmethod
    def url_pattern(cls):
        return r"^MTurkStart/(?P<session_code>[a-z]+)/$"

    @classmethod
    def url_name(cls):
        return 'mturk_start'

    def dispatch(self, request, *args, **kwargs):
        session_code = kwargs['session_code']
        self.session = get_object_or_404(
            otree.models.Session, code=session_code
        )
        return super(MTurkStart, self).dispatch(
            request, *args, **kwargs
        )

    def get(self, *args, **kwargs):
        assignment_id = self.request.GET['assignmentId']
        worker_id = self.request.GET['workerId']
        try:
            participant = Participant.objects.get(
                session=self.session,
                mturk_worker_id=worker_id,
                mturk_assignment_id=assignment_id)
        except Participant.DoesNotExist:
            with lock_on_this_code_path():
                try:
                    participant = (
                        Participant.objects.select_for_update().filter(
                            session=self.session,
                            visited=False
                        )
                    )[0]
                except IndexError:
                    return HttpResponseNotFound(
                        "No Player objects left in the database "
                        "to assign to new visitor."
                    )

            # 2014-10-17: needs to be here even if it's also set in
            # the next view to prevent race conditions
            participant.visited = True
            participant.mturk_worker_id = worker_id
            participant.mturk_assignment_id = assignment_id
            participant.save()
        return HttpResponseRedirect(participant._start_url())


class AssignVisitorToOpenSessionMTurk(AssignVisitorToOpenSessionBase):

    def incorrect_parameters_in_url_message(self):
        # A visitor to this experiment was turned away because they did not
        # have the MTurk parameters in their URL.
        # This URL only works if clicked from a MTurk job posting with the
        # JavaScript snippet embedded
        return (
            "To participate, you need to first accept this Mechanical Turk "
            "HIT and then re-click the link "
            "(refreshing this page will not work)."
        )

    @classmethod
    def url(cls):
        code = otree.constants.access_code_for_default_session
        default_session_code = settings.ACCESS_CODE_FOR_DEFAULT_SESSION
        return otree.common_internal.add_params_to_url(
            '/{}'.format(cls.__name__), {code: default_session_code}
        )

    @classmethod
    def url_pattern(cls):
        return r'^{}/$'.format(cls.__name__)

    required_params = {
        'mturk_worker_id': otree.constants.mturk_worker_id,
        'mturk_assignment_id': otree.constants.mturk_assignment_id,
    }

    def url_has_correct_parameters(self):
        correct_params = super(
            AssignVisitorToOpenSessionMTurk, self
        ).url_has_correct_parameters()
        same_id = (
            self.request.GET[constants.mturk_assignment_id] !=
            'ASSIGNMENT_ID_NOT_AVAILABLE'
        )
        return correct_params and same_id


class AssignVisitorToOpenSession(AssignVisitorToOpenSessionBase):

    def incorrect_parameters_in_url_message(self):
        return 'Missing parameter(s) in URL: {}'.format(
            self.required_params.values()
        )

    @classmethod
    def url(cls):
        return otree.common_internal.add_params_to_url(
            '/{}'.format(cls.__name__), {
                otree.constants.access_code_for_default_session:
                    settings.ACCESS_CODE_FOR_DEFAULT_SESSION
            }
        )

    @classmethod
    def url_pattern(cls):
        return r'^{}/$'.format(cls.__name__)

    required_params = {
        'label': otree.constants.participant_label,
    }


class AdvanceSession(vanilla.View):

    @classmethod
    def url_pattern(cls):
        return r'^AdvanceSession/(?P<{}>[0-9]+)/$'.format('session_pk')

    @classmethod
    def url_name(cls):
        return 'session_advance'

    @classmethod
    def url(cls, session):
        return '/AdvanceSession/{}/'.format(session.pk)

    def dispatch(self, request, *args, **kwargs):
        self.session = get_object_or_404(
            otree.models.session.Session, pk=kwargs['session_pk']
        )
        return super(AdvanceSession, self).dispatch(
            request, *args, **kwargs
        )

    def get(self, request, *args, **kwargs):
        self.session.advance_last_place_participants()
        redirect_url = reverse('session_monitor', args=(self.session.pk,))
        return HttpResponseRedirect(redirect_url)


class SetDefaultSession(vanilla.View):
    '''
        This view sets the default ("landing") session
        for persistent urls and amt urls.
        Globally we can have only one default_session.
    '''

    @classmethod
    def url_pattern(cls):
        return r'^SetDefaultSession/(?P<{}>[0-9]+)/$'.format('session_pk')

    @classmethod
    def url_name(cls):
        return 'set_default_session'

    @classmethod
    def url(cls, session):
        return '/SetDefaultSession/{}/'.format(session.pk)

    def dispatch(self, request, *args, **kwargs):
        self.session = get_object_or_404(
            otree.models.session.Session, pk=kwargs['session_pk']
        )
        return super(SetDefaultSession, self).dispatch(
            request, *args, **kwargs
        )

    def get(self, request, *args, **kwargs):
        global_singleton = otree.models.session.GlobalSingleton.objects.get()
        global_singleton.default_session = self.session
        global_singleton.save()

        msg = (
            'You have set the default session to <a href="{}">{}</a>. '
            'All participants are going to be routed to this session.'
        ).format(
            reverse('session_description', args=(self.session.pk,)),
            self.session.code
        )
        messages.success(request, msg, extra_tags='safe')
        return HttpResponseRedirect(reverse('admin_home'))


class UnsetDefaultSession(vanilla.View):
    '''
        This view unsets the default ("landing") session
        for persistent urls and amt urls.
        This is the opposite action to SetDefaultSession
    '''

    @classmethod
    def url_pattern(cls):
        return r'^UnsetDefaultSession/'

    @classmethod
    def url_name(cls):
        return 'unset_default_session'

    @classmethod
    def url(cls, session):
        return '/UnsetDefaultSession/'

    def dispatch(self, request, *args, **kwargs):
        return super(UnsetDefaultSession, self).dispatch(
            request, *args, **kwargs
        )

    def get(self, request, *args, **kwargs):
        global_singleton = otree.models.session.GlobalSingleton.objects.get()
        global_singleton.default_session = None
        global_singleton.save()
        messages.success(
            request, "You have successfully reset the default session"
        )
        return HttpResponseRedirect(reverse('admin_home'))


class ToggleArchivedSessions(vanilla.View):

    @classmethod
    def url_pattern(cls):
        return r'^ToggleArchivedSessions/'

    @classmethod
    def url_name(cls):
        return 'toggle_archived_sessions'

    def post(self, request, *args, **kwargs):
        for pk in request.POST.getlist('item-action'):
            session = get_object_or_404(
                otree.models.session.Session, pk=pk
            )
            if session.archived:
                session.archived = False
            else:
                session.archived = True
            session.save()
        return HttpResponseRedirect(request.POST['origin_url'])


class DeleteSessions(vanilla.View):

    @classmethod
    def url_pattern(cls):
        return r'^DeleteSessions/'

    @classmethod
    def url_name(cls):
        return 'delete_sessions'

    def post(self, request, *args, **kwargs):
        for pk in request.POST.getlist('item-action'):
            session = get_object_or_404(
                otree.models.session.Session, pk=pk
            )
            session.delete()
        return HttpResponseRedirect(reverse('admin_home'))
