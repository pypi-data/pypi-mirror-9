## $Id: interfaces.py 11589 2014-04-22 07:13:16Z henrik $
##
## Copyright (C) 2011 Uli Fouquet & Henrik Bettermann
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
#from datetime import datetime
from zope.component import getUtility
from zope.interface import Attribute, Interface
from zope import schema
from zc.sourcefactory.contextual import BasicContextualSourceFactory
from waeup.kofa.browser.interfaces import IStudentNavigationBase
from waeup.kofa.interfaces import (
    IKofaObject, academic_sessions_vocab, validate_email, ICSVExporter,
    ContextualDictSourceFactoryBase)
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.schema import TextLineChoice, FormattedDate, PhoneNumber
from waeup.kofa.students.vocabularies import (
    StudyLevelSource, contextual_reg_num_source, contextual_mat_num_source,
    GenderSource, nats_vocab
    )
from waeup.kofa.payments.interfaces import (
    IPaymentsContainer, IOnlinePayment)
from waeup.kofa.university.vocabularies import (
    CourseSource, StudyModeSource, CertificateSource, SemesterSource,
    )

class PreviousPaymentCategorySource(ContextualDictSourceFactoryBase):
    """A source that delivers all selectable categories of previous session
    payments.
    """
    #: name of dict to deliver from kofa utils.
    DICT_NAME = 'PREVIOUS_PAYMENT_CATEGORIES'

class BalancePaymentCategorySource(ContextualDictSourceFactoryBase):
    """A source that delivers all selectable items of balance payments.
    """
    #: name of dict to deliver from kofa utils.
    DICT_NAME = 'BALANCE_PAYMENT_CATEGORIES'

# VerdictSource can't be placed into the vocabularies module because it
# requires importing IStudentsUtils which then leads to circular imports.
class VerdictSource(BasicContextualSourceFactory):
    """A verdicts source delivers all verdicts provided
    in the portal.
    """
    def getValues(self, context):
        verdicts_dict = getUtility(IStudentsUtils).VERDICTS_DICT
        return sorted(verdicts_dict.keys())

    def getToken(self, context, value):
        return value

    def getTitle(self, context, value):
        verdicts_dict = getUtility(IStudentsUtils).VERDICTS_DICT
        if value != '0':
            return verdicts_dict[value] + ' (%s)' % value
        return verdicts_dict[value]


class IStudentsUtils(Interface):
    """A collection of methods which are subject to customization.

    """
    def setReturningData(student):
        """ This method defines what happens after school fee payment
        depending on the student's senate verdict.

        In the base configuration current level is always increased
        by 100 no matter which verdict has been assigned.
        """

    def setPaymentDetails(category, student, previous_session=None,
            previous_level=None,):
        """Create Payment object and set the payment data of a student for
        the payment category specified.

        """

    def setMatricNumber(student):
        """Set matriculation number of student.

        If the student's matric number is unset a new matric number is
        constructed using the next_matric_integer attribute of
        the site configuration container and according to the
        matriculation number construction rules defined in the
        _constructMatricNumber method. The new matric number is set,
        the students catalog updated and next_matric_integer
        increased by one.

        This method is tested but not used in the base package. It can
        be used in custom packages by adding respective views
        and by customizing _composeMatricNumber according to the
        university's matriculation number construction rules.

        The method can be disabled by setting next_matric_integer to zero.
        """

    def getAccommodation_details(student):
        """Determine the accommodation dates of a student.

        """

    def selectBed(available_beds):
        """Select a bed from a list of available beds.

        In the standard configuration we select the first bed found,
        but can also randomize the selection if we like.
        """

    def getPDFCreator(context):
        """Get some IPDFCreator instance suitable for use with `context`.
        """

    def renderPDF(view, subject='', filename='slip.pdf',):
        """Render pdf slips for various pages.

        """

class IStudentsContainer(IKofaObject):
    """A students container contains university students.

    """
    def addStudent(student):
        """Add an IStudent object and subcontainers.

        """

    def archive(id=None):
        """Create on-dist archive of students.

        If id is `None`, all students are archived.

        If id contains a single id string, only the respective
        students are archived.

        If id contains a list of id strings all of the respective
        students types are saved to disk.
        """

    def clear(id=None, archive=True):
        """Remove students of type given by 'id'.

        Optionally archive the students.

        If id is `None`, all students are archived.

        If id contains a single id string, only the respective
        students are archived.

        If id contains a list of id strings all of the respective
        student types are saved to disk.

        If `archive` is ``False`` none of the archive-handling is done
        and respective students are simply removed from the
        database.
        """

    unique_student_id = Attribute("""A unique student id.""")

class IStudentNavigation(IStudentNavigationBase):
    """Interface needed for student navigation, logging, etc.

    """
    student = Attribute('Student object of context.')

    def writeLogMessage(view, message):
        """Write a view specific log message into students.log.

        """

class IStudentBase(IKofaObject):
    """Representation of student base data.

    """
    history = Attribute('Object history, a list of messages')
    state = Attribute('Returns the registration state of a student')
    password = Attribute('Encrypted password of a student')
    temp_password = Attribute(
        'Dictionary with user name, timestamp and encrypted password')
    certcode = Attribute('The certificate code of any chosen study course')
    depcode = Attribute('The department code of any chosen study course')
    faccode = Attribute('The faculty code of any chosen study course')
    entry_session = Attribute('The entry session of the student')
    current_session = Attribute('The current session of the student')
    current_level = Attribute('The current level of the student')
    current_mode = Attribute('The current mode of the student')
    current_verdict = Attribute('The current verdict of the student')
    fullname = Attribute('All name parts separated by hyphens')
    display_fullname = Attribute('The fullname of an applicant')
    is_postgrad = Attribute('True if postgraduate student')

    suspended = schema.Bool(
        title = _(u'Account suspended'),
        default = False,
        required = False,
        )

    suspended_comment = schema.Text(
        title = _(u"Reasons for Deactivation"),
        required = False,
        description = _(
            u'This message will be shown if and only if deactivated '
            'students try to login.'),
        )

    student_id = schema.TextLine(
        title = _(u'Student Id'),
        required = False,
        )

    firstname = schema.TextLine(
        title = _(u'First Name'),
        required = True,
        )

    middlename = schema.TextLine(
        title = _(u'Middle Name'),
        required = False,
        )

    lastname = schema.TextLine(
        title = _(u'Last Name (Surname)'),
        required = True,
        )

    sex = schema.Choice(
        title = _(u'Sex'),
        source = GenderSource(),
        required = True,
        )

    reg_number = TextLineChoice(
        title = _(u'Registration Number'),
        required = True,
        readonly = False,
        source = contextual_reg_num_source,
        )

    matric_number = TextLineChoice(
        title = _(u'Matriculation Number'),
        required = False,
        readonly = False,
        source = contextual_mat_num_source,
        )

    adm_code = schema.TextLine(
        title = _(u'PWD Activation Code'),
        required = False,
        readonly = False,
        )

    email = schema.ASCIILine(
        title = _(u'Email'),
        required = False,
        constraint=validate_email,
        )
    phone = PhoneNumber(
        title = _(u'Phone'),
        description = u'',
        required = False,
        )

    def setTempPassword(user, password):
        """Set a temporary password (LDAP-compatible) SSHA encoded for
        officers.

        """

    def getTempPassword():
        """Check if a temporary password has been set and if it
        is not expired.

        Return the temporary password if valid,
        None otherwise. Unset the temporary password if expired.
        """

    def transfer(certificate, current_session,
        current_level, current_verdict):
        """ Creates a new studycourse and backups the old one.

        """

class IUGStudentClearance(IKofaObject):
    """Representation of undergraduate student clearance data.

    """
    officer_comment = schema.Text(
        title = _(u"Officer's Comment"),
        required = False,
        )

    clearance_locked = schema.Bool(
        title = _(u'Clearance form locked'),
        default = False,
        required = False,
        )

    clr_code = schema.TextLine(
        title = _(u'CLR Activation Code'),
        required = False,
        readonly = False,
        )

    date_of_birth = FormattedDate(
        title = _(u'Date of Birth'),
        required = True,
        show_year = True,
        )

    nationality = schema.Choice(
        vocabulary = nats_vocab,
        title = _(u'Nationality'),
        required = False,
        )

class IPGStudentClearance(IUGStudentClearance):
    """Representation of postgraduate student clearance data.

    """
    employer = schema.TextLine(
        title = _(u'Employer'),
        required = False,
        readonly = False,
        )

class IStudentPersonal(IKofaObject):
    """Representation of student personal data.

    """
    personal_updated = schema.Datetime(
        title = _(u'Updated'),
        required = False,
        readonly = False,
        )

    perm_address = schema.Text(
        title = _(u'Permanent Address'),
        required = False,
        )

class IStudentTranscript(IKofaObject):
    """Representation of student transcript data.

    """

    transcript_comment = schema.Text(
        title = _(u'Comment'),
        required = False,
        )


class IStudent(IStudentBase,IUGStudentClearance,IPGStudentClearance,
    IStudentPersonal, IStudentTranscript):
    """Representation of a student.

    """

class IStudentPersonalEdit(IStudentPersonal):
    """Interface for editing personal data by students.

    Here we can repeat the fields from IStudentPersonal and set the
    `required` if necessary.
    """

    perm_address = schema.Text(
        title = _(u'Permanent Address'),
        required = True,
        )

class IStudentUpdateByRegNo(IStudent):
    """Representation of a student. Skip regular reg_number validation.

    """
    reg_number = schema.TextLine(
        title = _(u'Registration Number'),
        required = False,
        )

class IStudentUpdateByMatricNo(IStudent):
    """Representation of a student. Skip regular matric_number validation.

    """
    matric_number = schema.TextLine(
        title = _(u'Matriculation Number'),
        required = False,
        )

class IStudentRequestPW(IStudent):
    """Representation of an student for first-time password request.

    This interface is used when students use the requestpw page to
    login for the the first time.
    """
    number = schema.TextLine(
        title = _(u'Registr. or Matric. Number'),
        required = True,
        )

    firstname = schema.TextLine(
        title = _(u'First Name'),
        required = True,
        )

    email = schema.ASCIILine(
        title = _(u'Email Address'),
        required = True,
        constraint=validate_email,
        )

class IStudentStudyCourse(IKofaObject):
    """A container for student study levels.

    """
    certificate = schema.Choice(
        title = _(u'Certificate'),
        source = CertificateSource(),
        required = False,
        )

    entry_mode = schema.Choice(
        title = _(u'Entry Mode'),
        source = StudyModeSource(),
        required = True,
        readonly = False,
        )

    entry_session = schema.Choice(
        title = _(u'Entry Session'),
        source = academic_sessions_vocab,
        #default = datetime.now().year,
        required = True,
        readonly = False,
        )

    current_session = schema.Choice(
        title = _(u'Current Session'),
        source = academic_sessions_vocab,
        required = True,
        readonly = False,
        )

    current_level = schema.Choice(
        title = _(u'Current Level'),
        source = StudyLevelSource(),
        required = False,
        readonly = False,
        )

    current_verdict = schema.Choice(
        title = _(u'Current Verdict'),
        source = VerdictSource(),
        default = '0',
        required = False,
        )

    previous_verdict = schema.Choice(
        title = _(u'Previous Verdict'),
        source = VerdictSource(),
        default = '0',
        required = False,
        )

class IStudentStudyCourseTransfer(IStudentStudyCourse):
    """An student transfers.

    """

    certificate = schema.Choice(
        title = _(u'Certificate'),
        source = CertificateSource(),
        required = True,
        )

    current_level = schema.Choice(
        title = _(u'Current Level'),
        source = StudyLevelSource(),
        required = True,
        readonly = False,
        )

    entry_session = schema.Choice(
        title = _(u'Entry Session'),
        source = academic_sessions_vocab,
        #default = datetime.now().year,
        required = False,
        readonly = False,
        )


IStudentStudyCourseTransfer['certificate'].order = IStudentStudyCourse[
    'certificate'].order
IStudentStudyCourseTransfer['current_level'].order = IStudentStudyCourse[
    'current_level'].order

class IStudentStudyCourseTranscript(IKofaObject):
    """An interface for student transcripts.

    """

    entry_mode = schema.Choice(
        title = _(u'Entry Mode'),
        source = StudyModeSource(),
        required = True,
        readonly = False,
        )

    entry_session = schema.Choice(
        title = _(u'Entry Session'),
        source = academic_sessions_vocab,
        #default = datetime.now().year,
        required = True,
        readonly = False,
        )

class IStudentVerdictUpdate(IKofaObject):
    """A interface for verdict imports.

    """

    current_verdict = schema.Choice(
        title = _(u'Current Verdict'),
        source = VerdictSource(),
        required = True,
        )

    current_session = schema.Choice(
        title = _(u'Current Session'),
        source = academic_sessions_vocab,
        required = True,
        )

    current_level = schema.Choice(
        title = _(u'Current Level'),
        source = StudyLevelSource(),
        required = True,
        )

    bypass_validation = schema.Bool(
        title = _(u'Bypass validation'),
        required = False,
        )

    validated_by = schema.TextLine(
        title = _(u'Validated by'),
        required = False,
        )

class IStudentStudyLevel(IKofaObject):
    """A container for course tickets.

    """
    level = Attribute('The level code')
    number_of_tickets = Attribute('Number of tickets contained in this level')
    certcode = Attribute('The certificate code of the study course')
    is_current_level = Attribute('Is this level the current level of the student?')
    passed_params = Attribute('Information about passed and failed courses')

    level_session = schema.Choice(
        title = _(u'Session'),
        source = academic_sessions_vocab,
        required = True,
        )

    level_verdict = schema.Choice(
        title = _(u'Verdict'),
        source = VerdictSource(),
        default = '0',
        required = False,
        )

    validated_by = schema.TextLine(
        title = _(u'Validated by'),
        default = None,
        required = False,
        )

    validation_date = schema.Datetime(
        title = _(u'Validation Date'),
        required = False,
        readonly = False,
        )

    total_credits = schema.Int(
        title = _(u'Total Credits'),
        required = False,
        readonly = True,
        )

    gpa = schema.Int(
        title = _(u'Unrectified GPA'),
        required = False,
        readonly = True,
        )

    def addCourseTicket(ticket, course):
        """Add a course ticket object.
        """

    def addCertCourseTickets(cert):
        """Collect all certificate courses and create course
        tickets automatically.
        """

class ICourseTicket(IKofaObject):
    """An interface for course tickets.

    """
    code = Attribute('code of the original course')
    certcode = Attribute('certificate code of the study course')
    grade = Attribute('grade calculated from score')
    weight = Attribute('weight calculated from score')
    removable_by_student = Attribute('Is student allowed to remove the ticket?')
    level_session = Attribute('session of the level the ticket has been added to')
    level = Attribute('id of the level the ticket has been added to')

    title = schema.TextLine(
        title = _(u'Title'),
        required = False,
        )

    fcode = schema.TextLine(
        title = _(u'Faculty Code'),
        required = False,
        )

    dcode = schema.TextLine(
        title = _(u'Department Code'),
        required = False,
        )

    semester = schema.Choice(
        title = _(u'Semester/Term'),
        source = SemesterSource(),
        required = False,
        )

    passmark = schema.Int(
        title = _(u'Passmark'),
        required = False,
        )

    credits = schema.Int(
        title = _(u'Credits'),
        required = False,
        )

    mandatory = schema.Bool(
        title = _(u'Required'),
        default = False,
        required = False,
        )

    score = schema.Int(
        title = _(u'Score'),
        default = None,
        required = False,
        missing_value = None,
        )

    carry_over = schema.Bool(
        title = _(u'Carry-over Course'),
        default = False,
        required = False,
        )

    automatic = schema.Bool(
        title = _(u'Automatical Creation'),
        default = False,
        required = False,
        )


class ICourseTicketAdd(IKofaObject):
    """An interface for adding course tickets.

    """
    course = schema.Choice(
        title = _(u'Course'),
        source = CourseSource(),
        readonly = False,
        )

class ICourseTicketImport(ICourseTicket):
    """An interface for importing course results and nothing more.

    """
    score = schema.Int(
        title = _(u'Score'),
        required = False,
        readonly = False,
        )

    level_session = schema.Choice(
        title = _(u'Level Session'),
        source = academic_sessions_vocab,
        required = False,
        readonly = False,
        )

class IStudentAccommodation(IKofaObject):
    """A container for student accommodation objects.

    """

    def addBedTicket(bedticket):
        """Add a bed ticket object.
        """


class IBedTicket(IKofaObject):
    """A ticket for accommodation booking.

    """
    bed = Attribute('The bed object.')

    bed_coordinates = schema.TextLine(
        title = u'',
        required = True,
        readonly = False,
        )

    display_coordinates = schema.TextLine(
        title = _(u'Allocated Bed'),
        required = False,
        readonly = True,
        )

    bed_type = schema.TextLine(
        title = _(u'Requested Bed Type'),
        required = True,
        readonly = False,
        )

    booking_session = schema.Choice(
        title = _(u'Session'),
        source = academic_sessions_vocab,
        required = True,
        readonly = True,
        )

    booking_date = schema.Datetime(
        title = _(u'Booking Date'),
        required = False,
        readonly = True,
        )

    booking_code = schema.TextLine(
        title = _(u'Booking Activation Code'),
        required = False,
        readonly = True,
        )

    def getSessionString():
        """Returns the title of academic_sessions_vocab term.

        """

class IStudentPaymentsContainer(IPaymentsContainer):
    """A container for student payment objects.

    """

class IStudentOnlinePayment(IOnlinePayment):
    """A student payment via payment gateways.

    """

    p_current = schema.Bool(
        title = _(u'Current Session Payment'),
        default = True,
        required = False,
        )

    p_level = schema.Int(
        title = _(u'Payment Level'),
        required = False,
        )

    def doAfterStudentPayment():
        """Process student after payment was made.

        """

    def doAfterStudentPaymentApproval():
        """Process student after payment was approved.

        """

    def approveStudentPayment():
        """Approve payment and process student.

        """

IStudentOnlinePayment['p_level'].order = IStudentOnlinePayment[
    'p_session'].order

class IStudentPreviousPayment(IKofaObject):
    """An interface for adding previous session payments.

    """

    p_category = schema.Choice(
        title = _(u'Payment Category'),
        default = u'schoolfee',
        source = PreviousPaymentCategorySource(),
        required = True,
        )

    p_session = schema.Choice(
        title = _(u'Payment Session'),
        source = academic_sessions_vocab,
        required = True,
        )

    p_level = schema.Choice(
        title = _(u'Payment Level'),
        source = StudyLevelSource(),
        required = True,
        )

class IStudentBalancePayment(IKofaObject):
    """An interface for adding balances.

    """

    p_category = schema.Choice(
        title = _(u'Payment Category'),
        default = u'schoolfee',
        required = True,
        source = BalancePaymentCategorySource(),
        )

    balance_session = schema.Choice(
        title = _(u'Payment Session'),
        source = academic_sessions_vocab,
        required = True,
        )

    balance_level = schema.Choice(
        title = _(u'Payment Level'),
        source = StudyLevelSource(),
        required = True,
        )

    balance_amount = schema.Float(
        title = _(u'Balance Amount'),
        default = None,
        required = True,
        readonly = False,
        description = _(
            u'Balance in Naira '),
        )

class ICSVStudentExporter(ICSVExporter):
    """A regular ICSVExporter that additionally supports exporting
      data from a given student object.
    """
    def get_filtered(site, **kw):
        """Get a filtered set of students.
        """

    def export_student(student, filepath=None):
        """Export data for a given student.
        """

    def export_filtered(site, filepath=None, **kw):
        """Export filtered set of students.
        """
