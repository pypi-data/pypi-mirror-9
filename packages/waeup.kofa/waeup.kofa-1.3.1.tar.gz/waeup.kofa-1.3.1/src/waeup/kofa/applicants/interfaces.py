## $Id: interfaces.py 11869 2014-10-22 06:26:31Z henrik $
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
"""Interfaces of the university application package.
"""
from datetime import datetime
from grokcore.content.interfaces import IContainer
from zc.sourcefactory.contextual import BasicContextualSourceFactory
from zope import schema
from zope.component import queryUtility, getUtility
from zope.catalog.interfaces import ICatalog
from zope.interface import Interface, Attribute, implements, directlyProvides
from zope.schema.interfaces import (
    ValidationError, ISource, IContextSourceBinder)
from waeup.kofa.browser.interfaces import IApplicantBase
from waeup.kofa.schema import TextLineChoice, FormattedDate
from waeup.kofa.interfaces import (
    IKofaObject, validate_email,
    SimpleKofaVocabulary)
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.payments.interfaces import IOnlinePayment
from waeup.kofa.schema import PhoneNumber
from waeup.kofa.students.vocabularies import GenderSource, RegNumberSource
from waeup.kofa.university.vocabularies import (
    AppCatSource, CertificateSource, SpecialApplicationSource)

#: Maximum upload size for applicant passport photographs (in bytes)
MAX_UPLOAD_SIZE = 1024 * 20

_marker = object() # a marker different from None

def year_range():
    curr_year = datetime.now().year
    return range(curr_year - 2, curr_year + 5)

class RegNumInSource(ValidationError):
    """Registration number exists already
    """
    # The docstring of ValidationErrors is used as error description
    # by zope.formlib.
    pass

class ApplicantRegNumberSource(RegNumberSource):
    """A source that accepts any reg number if not used already by a
    different applicant.
    """
    cat_name = 'applicants_catalog'
    field_name = 'reg_number'
    validation_error = RegNumInSource
    comp_field = 'applicant_id'

def contextual_reg_num_source(context):
    source = ApplicantRegNumberSource(context)
    return source
directlyProvides(contextual_reg_num_source, IContextSourceBinder)


class AppCatCertificateSource(CertificateSource):
    """An application certificate source delivers all certificates
    which belong to a certain application_category.

    This source is meant to be used with Applicants.

    The application category must match the application category of
    the context parent, normally an applicants container.
    """
    def contains(self, context, value):
        context_appcat = getattr(getattr(
            context, '__parent__', None), 'application_category', _marker)
        if context_appcat is _marker:
            # If the context (applicant) has no application category,
            # then it might be not part of a container (yet), for
            # instance during imports. We consider this correct.
            return True
        if value.application_category == context_appcat:
            return True
        return False

    def getValues(self, context):
        appcat = getattr(getattr(context, '__parent__', None),
                         'application_category', None)
        catalog = getUtility(ICatalog, name='certificates_catalog')
        result = catalog.searchResults(
            application_category=(appcat,appcat))
        resultlist = getUtility(
            IApplicantsUtils).filterCertificates(context, result)
        return resultlist

    def getTitle(self, context, value):
        return getUtility(
            IApplicantsUtils).getCertTitle(context, value)

class ApplicationTypeSource(BasicContextualSourceFactory):
    """An application type source delivers screening types defined in the
    portal.
    """
    def getValues(self, context):
        appcats_dict = getUtility(
            IApplicantsUtils).APP_TYPES_DICT
        return sorted(appcats_dict.keys())

    def getToken(self, context, value):
        return value

    def getTitle(self, context, value):
        appcats_dict = getUtility(
            IApplicantsUtils).APP_TYPES_DICT
        return appcats_dict[value][0]

# Maybe FUTMinna still needs this ...
#class ApplicationPinSource(BasicContextualSourceFactory):
#    """An application pin source delivers PIN prefixes for application
#    defined in the portal.
#    """
#    def getValues(self, context):
#        apppins_dict = getUtility(
#            IApplicantsUtils).APP_TYPES_DICT
#        return sorted(appcats_dict.keys())
#
#    def getToken(self, context, value):
#        return value
#
#    def getTitle(self, context, value):
#        apppins_dict = getUtility(
#            IApplicantsUtils).APP_TYPES_DICT
#        return u"%s (%s)" % (
#            apppins_dict[value][1],self.apppins_dict[value][0])

application_modes_vocab = SimpleKofaVocabulary(
    (_('Create Application Records'), 'create'),
    (_('Update Application Records'), 'update'),
    )

class IApplicantsUtils(Interface):
    """A collection of methods which are subject to customization.
    """

    APP_TYPES_DICT = Attribute('dict of application types')

    def setPaymentDetails(container, payment):
        """Set the payment data of an applicant.
        """

    def getApplicantsStatistics(container):
        """Count applicants in containers.
        """

    def filterCertificates(context, resultset):
        """Filter and sort certificates for AppCatCertificateSource.
        """

    def getCertTitle(context, value):
        """Compose the titles in AppCatCertificateSource.
        """

class IApplicantsRoot(IKofaObject, IContainer):
    """A container for university applicants containers.
    """

    description = schema.Text(
        title = _(u'Human readable description in HTML format'),
        required = False,
        default = u'''This text can been seen by anonymous users.
Here we put multi-lingual general information about the application procedure.
>>de<<
Dieser Text kann von anonymen Benutzern gelesen werden.
Hier koennen mehrsprachige Informationen fuer Antragsteller hinterlegt werden.'''
        )

    description_dict = Attribute(
        """Content as language dictionary with values in HTML format.""")

class IApplicantsContainer(IKofaObject):
    """An applicants container contains university applicants.

    """

    code = schema.TextLine(
        title = _(u'Code'),
        required = True,
        readonly = True,
        )

    title = schema.TextLine(
        title = _(u'Title'),
        required = True,
        readonly = False,
        )

    prefix = schema.Choice(
        title = _(u'Application Target'),
        required = True,
        source = ApplicationTypeSource(),
        readonly = True,
        )

    year = schema.Choice(
        title = _(u'Year of Entrance'),
        required = True,
        values = year_range(),
        readonly = True,
        )

    mode = schema.Choice(
        title = _(u'Application Mode'),
        vocabulary = application_modes_vocab,
        required = True,
        )

    # Maybe FUTMinna still needs this ...
    #ac_prefix = schema.Choice(
    #    title = u'Activation code prefix',
    #    required = True,
    #    default = None,
    #    source = ApplicationPinSource(),
    #    )

    application_category = schema.Choice(
        title = _(u'Category for the grouping of certificates'),
        required = True,
        source = AppCatSource(),
        )

    description = schema.Text(
        title = _(u'Human readable description in HTML format'),
        required = False,
        default = u'''This text can been seen by anonymous users.
Here we put multi-lingual information about the study courses provided, the application procedure and deadlines.
>>de<<
Dieser Text kann von anonymen Benutzern gelesen werden.
Hier koennen mehrsprachige Informationen fuer Antragsteller hinterlegt werden.'''
        )

    description_dict = Attribute(
        """Content as language dictionary with values in HTML format.""")

    startdate = schema.Datetime(
        title = _(u'Application Start Date'),
        required = False,
        description = _('Example:') + u'2011-12-01 18:30:00+01:00',
        )

    enddate = schema.Datetime(
        title = _(u'Application Closing Date'),
        required = False,
        description = _('Example:') + u'2011-12-31 23:59:59+01:00',
        )

    strict_deadline = schema.Bool(
        title = _(u'Forbid additions after deadline (enddate)'),
        required = False,
        default = True,
        )

    application_fee = schema.Float(
        title = _(u'Application Fee'),
        default = 0.0,
        required = False,
        )

    application_slip_notice = schema.Text(
        title = _(u'Human readable notice on application slip in HTML format'),
        required = False,
        )


    hidden= schema.Bool(
        title = _(u'Hide container'),
        required = False,
        default = False,
        )

    def archive(id=None):
        """Create on-dist archive of applicants stored in this term.

        If id is `None`, all applicants are archived.

        If id contains a single id string, only the respective
        applicants are archived.

        If id contains a list of id strings all of the respective
        applicants types are saved to disk.
        """

    def clear(id=None, archive=True):
        """Remove applicants of type given by 'id'.

        Optionally archive the applicants.

        If id is `None`, all applicants are archived.

        If id contains a single id string, only the respective
        applicants are archived.

        If id contains a list of id strings all of the respective
        applicant types are saved to disk.

        If `archive` is ``False`` none of the archive-handling is done
        and respective applicants are simply removed from the
        database.
        """

    def writeLogMessage(view, comment):
        """Adds an INFO message to the log file
        """

class IApplicantsContainerAdd(IApplicantsContainer):
    """An applicants container contains university applicants.
    """
    prefix = schema.Choice(
        title = _(u'Application Target'),
        required = True,
        source = ApplicationTypeSource(),
        readonly = False,
        )

    year = schema.Choice(
        title = _(u'Year of Entrance'),
        required = True,
        values = year_range(),
        readonly = False,
        )

IApplicantsContainerAdd[
    'prefix'].order =  IApplicantsContainer['prefix'].order
IApplicantsContainerAdd[
    'year'].order =  IApplicantsContainer['year'].order

class IApplicantBaseData(IApplicantBase):
    """The data for an applicant.

    This is a base interface with no field
    required. For use with processors, forms, etc., please use one of
    the derived interfaces below, which set more fields to required
    state, depending on use-case.
    """

    history = Attribute('Object history, a list of messages')
    state = Attribute('The application state of an applicant')
    display_fullname = Attribute('The fullname of an applicant')
    application_date = Attribute('UTC datetime of submission, used for export only')
    password = Attribute('Encrypted password of a applicant')
    application_number = Attribute('The key under which the record is stored')

    suspended = schema.Bool(
        title = _(u'Account suspended'),
        default = False,
        required = False,
        )

    applicant_id = schema.TextLine(
        title = _(u'Applicant Id'),
        required = False,
        readonly = False,
        )
    reg_number = TextLineChoice(
        title = _(u'Registration Number'),
        readonly = False,
        required = True,
        source = contextual_reg_num_source,
        )
    #access_code = schema.TextLine(
    #    title = u'Activation Code',
    #    required = False,
    #    readonly = True,
    #    )
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
    date_of_birth = FormattedDate(
        title = _(u'Date of Birth'),
        required = False,
        #date_format = u'%d/%m/%Y', # Use grok-instance-wide default
        show_year = True,
        )
    sex = schema.Choice(
        title = _(u'Sex'),
        source = GenderSource(),
        required = True,
        )
    email = schema.ASCIILine(
        title = _(u'Email Address'),
        required = False,
        constraint=validate_email,
        )
    phone = PhoneNumber(
        title = _(u'Phone'),
        description = u'',
        required = False,
        )
    course1 = schema.Choice(
        title = _(u'1st Choice Course of Study'),
        source = AppCatCertificateSource(),
        required = True,
        )
    course2 = schema.Choice(
        title = _(u'2nd Choice Course of Study'),
        source = AppCatCertificateSource(),
        required = False,
        )
    #school_grades = schema.List(
    #    title = _(u'School Grades'),
    #    value_type = ResultEntryField(),
    #    required = False,
    #    default = [],
    #    )

    notice = schema.Text(
        title = _(u'Notice'),
        required = False,
        )
    student_id = schema.TextLine(
        title = _(u'Student Id'),
        required = False,
        readonly = False,
        )
    course_admitted = schema.Choice(
        title = _(u'Admitted Course of Study'),
        source = CertificateSource(),
        required = False,
        )
    locked = schema.Bool(
        title = _(u'Form locked'),
        default = False,
        required = False,
        )

    special_application = schema.Choice(
        title = _(u'Special Application'),
        source = SpecialApplicationSource(),
        required = False,
        )

class IApplicant(IApplicantBaseData):
    """An applicant.

    This is basically the applicant base data. Here we repeat the
    fields from base data if we have to set the `required` attribute
    to True (which is the default).
    """

    def writeLogMessage(view, comment):
        """Adds an INFO message to the log file
        """

    def createStudent():
        """Create a student object from applicatnt data
        and copy applicant object.
        """

class ISpecialApplicant(IApplicantBase):
    """A special applicant.

    This reduced interface is for former students or students who are not
    users of the portal but have to pay supplementary fees.

    This interface is used in browser components only. Thus we can't add
    fields here to the regular IApplicant interface here. We can
    only 'customize' fields.
    """

    history = Attribute('Object history, a list of messages')
    state = Attribute('The application state of an applicant')
    display_fullname = Attribute('The fullname of an applicant')
    application_date = Attribute('UTC datetime of submission, used for export only')
    password = Attribute('Encrypted password of a applicant')
    application_number = Attribute('The key under which the record is stored')

    suspended = schema.Bool(
        title = _(u'Account suspended'),
        default = False,
        required = False,
        )

    locked = schema.Bool(
        title = _(u'Form locked'),
        default = False,
        required = False,
        )

    applicant_id = schema.TextLine(
        title = _(u'Applicant Id'),
        required = False,
        readonly = False,
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

    reg_number = TextLineChoice(
        title = _(u'Identification Number'),
        description = u'Enter either registration or matriculation number.',
        readonly = False,
        required = True,
        source = contextual_reg_num_source,
        )

    date_of_birth = FormattedDate(
        title = _(u'Date of Birth'),
        required = False,
        #date_format = u'%d/%m/%Y', # Use grok-instance-wide default
        show_year = True,
        )

    email = schema.ASCIILine(
        title = _(u'Email Address'),
        required = True,
        constraint=validate_email,
        )

    phone = PhoneNumber(
        title = _(u'Phone'),
        description = u'',
        required = False,
        )

    special_application = schema.Choice(
        title = _(u'Special Application'),
        source = SpecialApplicationSource(),
        required = True,
        )

class IApplicantEdit(IApplicant):
    """An applicant interface for editing.

    Here we can repeat the fields from base data and set the
    `required` and `readonly` attributes to True to further restrict
    the data access. Or we can allow only certain certificates to be
    selected by choosing the appropriate source.

    We cannot omit fields here. This has to be done in the
    respective form page.
    """

    email = schema.ASCIILine(
        title = _(u'Email Address'),
        required = True,
        constraint=validate_email,
        )
    course1 = schema.Choice(
        title = _(u'1st Choice Course of Study'),
        source = AppCatCertificateSource(),
        required = True,
        )
    course2 = schema.Choice(
        title = _(u'2nd Choice Course of Study'),
        source = AppCatCertificateSource(),
        required = False,
        )
    course_admitted = schema.Choice(
        title = _(u'Admitted Course of Study'),
        source = CertificateSource(),
        required = False,
        readonly = True,
        )
    notice = schema.Text(
        title = _(u'Notice'),
        required = False,
        readonly = True,
        )

IApplicantEdit['email'].order = IApplicantEdit[
    'sex'].order

class IApplicantUpdateByRegNo(IApplicant):
    """Representation of an applicant.

    Skip regular reg_number validation if reg_number is used for finding
    the applicant object.
    """
    reg_number = schema.TextLine(
        title = u'Registration Number',
        required = False,
        )

class IApplicantRegisterUpdate(IApplicant):
    """Representation of an applicant for first-time registration.

    This interface is used when applicants use the registration page to
    update their records.
    """
    reg_number = schema.TextLine(
        title = u'Registration Number',
        required = True,
        )

    #firstname = schema.TextLine(
    #    title = _(u'First Name'),
    #    required = True,
    #    )

    lastname = schema.TextLine(
        title = _(u'Last Name (Surname)'),
        required = True,
        )

    email = schema.ASCIILine(
        title = _(u'Email Address'),
        required = True,
        constraint=validate_email,
        )

class IApplicantOnlinePayment(IOnlinePayment):
    """An applicant payment via payment gateways.

    """

    def doAfterApplicantPayment():
        """Process applicant after payment was made.

        """

    def doAfterApplicantPaymentApproval():
        """Process applicant after payment was approved.

        """

    def approveApplicantPayment():
        """Approve payment and process applicant.

        """
