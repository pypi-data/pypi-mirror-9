"""Workflow for students.
"""
import grok
from datetime import datetime
from zope.component import getUtility
from hurry.workflow.workflow import Transition, WorkflowState, NullCondition
from hurry.workflow.interfaces import IWorkflowState, IWorkflowTransitionEvent
from waeup.kofa.interfaces import (
    IObjectHistory, IKofaWorkflowInfo, IKofaUtils,
    CREATED, ADMITTED, CLEARANCE, REQUESTED, CLEARED, PAID, RETURNING,
    REGISTERED, VALIDATED, GRADUATED, TRANSCRIPT)
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.workflow import KofaWorkflow, KofaWorkflowInfo
from waeup.kofa.students.interfaces import IStudent, IStudentsUtils
from waeup.kofa.utils.helpers import get_current_principal


IMPORTABLE_STATES = (ADMITTED, CLEARANCE, REQUESTED, CLEARED, PAID, RETURNING,
    REGISTERED, VALIDATED, GRADUATED)

FORBIDDEN_POSTGRAD_STATES = (RETURNING, REGISTERED, VALIDATED)

REGISTRATION_TRANSITIONS = (
    Transition(
        transition_id = 'create',
        title = _('Create student'),
        source = None,
        condition = NullCondition,
        msg = _('Record created'),
        destination = CREATED),

    Transition(
        transition_id = 'admit',
        title = _('Admit student'),
        msg = _('Admitted'),
        source = CREATED,
        destination = ADMITTED),

    Transition(
        transition_id = 'reset1',
        title = _('Reset student'),
        msg = _('Reset to initial state'),
        source = ADMITTED,
        destination = CREATED),

    Transition(
        transition_id = 'start_clearance',
        title = _('Start clearance'),
        msg = _('Clearance started'),
        source = ADMITTED,
        destination = CLEARANCE),

    Transition(
        transition_id = 'reset2',
        title = _('Reset to admitted'),
        msg = _("Reset to 'admitted'"),
        source = CLEARANCE,
        destination = ADMITTED),

    Transition(
        transition_id = 'request_clearance',
        title = _('Request clearance'),
        msg = _('Clearance requested'),
        source = CLEARANCE,
        destination = REQUESTED),

    Transition(
        transition_id = 'reset3',
        title = _('Reset to clearance started'),
        msg = _("Reset to 'clearance started'"),
        source = REQUESTED,
        destination = CLEARANCE),

    Transition(
        transition_id = 'clear',
        title = _('Clear student'),
        msg = _('Cleared'),
        source = REQUESTED,
        destination = CLEARED),

    Transition(
        transition_id = 'reset4',
        title = _('Reset to clearance started'),
        msg = _("Reset to 'clearance started'"),
        source = CLEARED,
        destination = CLEARANCE),

    Transition(
        transition_id = 'pay_first_school_fee',
        title = _('Pay school fee'),
        msg = _('First school fee payment made'),
        source = CLEARED,
        destination = PAID),

    Transition(
        transition_id = 'approve_first_school_fee',
        title = _('Approve payment'),
        msg = _('First school fee payment approved'),
        source = CLEARED,
        destination = PAID),

    Transition(
        transition_id = 'reset5',
        title = _('Reset to cleared'),
        msg = _("Reset to 'cleared'"),
        source = PAID,
        destination = CLEARED),

    Transition(
        transition_id = 'pay_school_fee',
        title = _('Pay school fee'),
        msg = _('School fee payment made'),
        source = RETURNING,
        destination = PAID),

    Transition(
        transition_id = 'pay_pg_fee',
        title = _('Pay PG school fee'),
        msg = _('PG school fee payment made'),
        source = PAID,
        destination = PAID),

    Transition(
        transition_id = 'approve_school_fee',
        title = _('Approve school fee payment'),
        msg = _('School fee payment approved'),
        source = RETURNING,
        destination = PAID),

    Transition(
        transition_id = 'approve_pg_fee',
        title = _('Approve PG school fee payment'),
        msg = _('PG school fee payment approved'),
        source = PAID,
        destination = PAID),

    Transition(
        transition_id = 'reset6',
        title = _('Reset to returning'),
        msg = _("Reset to 'returning'"),
        source = PAID,
        destination = RETURNING),

    Transition(
        transition_id = 'register_courses',
        title = _('Register courses'),
        msg = _('Courses registered'),
        source = PAID,
        destination = REGISTERED),

    Transition(
        transition_id = 'reset7',
        title = _('Reset to school fee paid'),
        msg = _("Reset to 'school fee paid'"),
        source = REGISTERED,
        destination = PAID),

    Transition(
        transition_id = 'validate_courses',
        title = _('Validate courses'),
        msg = _('Courses validated'),
        source = REGISTERED,
        destination = VALIDATED),

    Transition(
        transition_id = 'bypass_validation',
        title = _('Return and bypass validation'),
        msg = _("Course validation bypassed"),
        source = REGISTERED,
        destination = RETURNING),

    Transition(
        transition_id = 'reset8',
        title = _('Reset to school fee paid'),
        msg = _("Reset to 'school fee paid'"),
        source = VALIDATED,
        destination = PAID),

    Transition(
        transition_id = 'return',
        title = _('Return'),
        msg = _("Returned"),
        source = VALIDATED,
        destination = RETURNING),

    Transition(
        transition_id = 'reset9',
        title = _('Reset to courses validated'),
        msg = _("Reset to 'courses validated'"),
        source = RETURNING,
        destination = VALIDATED),

    # There is no transition to graduated.

    Transition(
        transition_id = 'request_transcript',
        title = _('Request transript'),
        msg = _("Transcript requested"),
        source = GRADUATED,
        destination = TRANSCRIPT),

    Transition(
        transition_id = 'process_transcript',
        title = _('Transcript processed'),
        msg = _("Transcript processed"),
        source = TRANSCRIPT,
        destination = GRADUATED),
    )


IMPORTABLE_TRANSITIONS = [i.transition_id for i in REGISTRATION_TRANSITIONS]

FORBIDDEN_POSTGRAD_TRANS = ['reset6', 'register_courses']
LOCK_CLEARANCE_TRANS = ('reset2', 'request_clearance')
UNLOCK_CLEARANCE_TRANS = ('reset3', 'reset4', 'start_clearance')

registration_workflow = KofaWorkflow(REGISTRATION_TRANSITIONS)

class RegistrationWorkflowState(WorkflowState, grok.Adapter):
    """An adapter to adapt Student objects to workflow states.
    """
    grok.context(IStudent)
    grok.provides(IWorkflowState)

    state_key = 'wf.registration.state'
    state_id = 'wf.registration.id'

class RegistrationWorkflowInfo(KofaWorkflowInfo, grok.Adapter):
    """Adapter to adapt Student objects to workflow info objects.
    """
    grok.context(IStudent)
    grok.provides(IKofaWorkflowInfo)

    def __init__(self, context):
        self.context = context
        self.wf = registration_workflow

@grok.subscribe(IStudent, IWorkflowTransitionEvent)
def handle_student_transition_event(obj, event):
    """Append message to student history and log file when transition happened.

    Lock and unlock clearance form.
    Trigger actions after school fee payment.
    """

    msg = event.transition.user_data['msg']
    history = IObjectHistory(obj)
    history.addMessage(msg)
    if event.transition.transition_id in LOCK_CLEARANCE_TRANS:
        obj.clearance_locked = True
    if event.transition.transition_id in UNLOCK_CLEARANCE_TRANS:
        obj.clearance_locked = False
    # School fee payment of returning students triggers the change of
    # current session, current level, and current verdict
    if event.transition.transition_id in (
        'pay_school_fee', 'approve_school_fee'):
        getUtility(IStudentsUtils).setReturningData(obj)
    elif event.transition.transition_id in (
        'pay_pg_fee', 'approve_pg_fee'):
        new_session = obj['studycourse'].current_session + 1
        obj['studycourse'].current_session = new_session
    elif event.transition.transition_id == 'validate_courses':
        current_level = obj['studycourse'].current_level
        level_object = obj['studycourse'].get(str(current_level), None)
        if level_object is not None:
            user = get_current_principal()
            if user is None:
                usertitle = 'system'
            else:
                usertitle = getattr(user, 'public_name', None)
                if not usertitle:
                    usertitle = user.title
            level_object.validated_by = usertitle
            level_object.validation_date = datetime.utcnow()
    elif event.transition.transition_id == 'clear':
        obj.officer_comment = None
    elif event.transition.transition_id == 'reset8':
        current_level = obj['studycourse'].current_level
        level_object = obj['studycourse'].get(str(current_level), None)
        if level_object is not None:
            level_object.validated_by = None
            level_object.validation_date = None
    # In some tests we don't have a students container
    try:
        students_container = grok.getSite()['students']
        students_container.logger.info('%s - %s' % (obj.student_id,msg))
    except (TypeError, AttributeError):
        pass
    return
