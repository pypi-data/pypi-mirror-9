## $Id: browser.py 12395 2015-01-04 17:19:06Z henrik $
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
"""UI components for basic applicants and related components.
"""
import os
import sys
import grok
from datetime import datetime, date
from zope.event import notify
from zope.component import getUtility, createObject, getAdapter
from zope.catalog.interfaces import ICatalog
from zope.i18n import translate
from hurry.workflow.interfaces import (
    IWorkflowInfo, IWorkflowState, InvalidTransitionError)
from waeup.kofa.applicants.interfaces import (
    IApplicant, IApplicantEdit, IApplicantsRoot,
    IApplicantsContainer, IApplicantsContainerAdd,
    MAX_UPLOAD_SIZE, IApplicantOnlinePayment, IApplicantsUtils,
    IApplicantRegisterUpdate, ISpecialApplicant
    )
from waeup.kofa.utils.helpers import html2dict
from waeup.kofa.applicants.container import (
    ApplicantsContainer, VirtualApplicantsExportJobContainer)
from waeup.kofa.applicants.applicant import search
from waeup.kofa.applicants.workflow import (
    INITIALIZED, STARTED, PAID, SUBMITTED, ADMITTED)
from waeup.kofa.browser import (
#    KofaPage, KofaEditFormPage, KofaAddFormPage, KofaDisplayFormPage,
    DEFAULT_PASSPORT_IMAGE_PATH)
from waeup.kofa.browser.layout import (
    KofaPage, KofaEditFormPage, KofaAddFormPage, KofaDisplayFormPage)
from waeup.kofa.browser.interfaces import ICaptchaManager
from waeup.kofa.browser.breadcrumbs import Breadcrumb
from waeup.kofa.browser.layout import (
    NullValidator, jsaction, action, UtilityView)
from waeup.kofa.browser.pages import (
    add_local_role, del_local_roles, doll_up, ExportCSVView)
from waeup.kofa.interfaces import (
    IKofaObject, ILocalRolesAssignable, IExtFileStore, IPDF,
    IFileStoreNameChooser, IPasswordValidator, IUserAccount, IKofaUtils)
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.permissions import get_users_with_local_roles
from waeup.kofa.students.interfaces import IStudentsUtils
from waeup.kofa.utils.helpers import string_from_bytes, file_size, now
from waeup.kofa.widgets.datewidget import (
    FriendlyDateDisplayWidget,
    FriendlyDatetimeDisplayWidget)

grok.context(IKofaObject) # Make IKofaObject the default context

WARNING = _('You can not edit your application records after final submission.'
            ' You really want to submit?')

class ApplicantsRootPage(KofaDisplayFormPage):
    grok.context(IApplicantsRoot)
    grok.name('index')
    grok.require('waeup.Public')
    form_fields = grok.AutoFields(IApplicantsRoot)
    label = _('Application Section')
    pnav = 3

    def update(self):
        super(ApplicantsRootPage, self).update()
        return

    @property
    def introduction(self):
        # Here we know that the cookie has been set
        lang = self.request.cookies.get('kofa.language')
        html = self.context.description_dict.get(lang,'')
        if html == '':
            portal_language = getUtility(IKofaUtils).PORTAL_LANGUAGE
            html = self.context.description_dict.get(portal_language,'')
        return html

    @property
    def containers(self):
        if self.layout.isAuthenticated():
            return self.context.values()
        return [value for value in self.context.values() if not value.hidden]

class ApplicantsSearchPage(KofaPage):
    grok.context(IApplicantsRoot)
    grok.name('search')
    grok.require('waeup.viewApplication')
    label = _('Find applicants')
    search_button = _('Find applicant')
    pnav = 3

    def update(self, *args, **kw):
        form = self.request.form
        self.results = []
        if 'searchterm' in form and form['searchterm']:
            self.searchterm = form['searchterm']
            self.searchtype = form['searchtype']
        elif 'old_searchterm' in form:
            self.searchterm = form['old_searchterm']
            self.searchtype = form['old_searchtype']
        else:
            if 'search' in form:
                self.flash(_('Empty search string'), type='warning')
            return
        self.results = search(query=self.searchterm,
            searchtype=self.searchtype, view=self)
        if not self.results:
            self.flash(_('No applicant found.'), type='warning')
        return

class ApplicantsRootManageFormPage(KofaEditFormPage):
    grok.context(IApplicantsRoot)
    grok.name('manage')
    grok.template('applicantsrootmanagepage')
    form_fields = grok.AutoFields(IApplicantsRoot)
    label = _('Manage application section')
    pnav = 3
    grok.require('waeup.manageApplication')
    taboneactions = [_('Save')]
    tabtwoactions = [_('Add applicants container'), _('Remove selected')]
    tabthreeactions1 = [_('Remove selected local roles')]
    tabthreeactions2 = [_('Add local role')]
    subunits = _('Applicants Containers')

    def getLocalRoles(self):
        roles = ILocalRolesAssignable(self.context)
        return roles()

    def getUsers(self):
        """Get a list of all users.
        """
        for key, val in grok.getSite()['users'].items():
            url = self.url(val)
            yield(dict(url=url, name=key, val=val))

    def getUsersWithLocalRoles(self):
        return get_users_with_local_roles(self.context)

    @jsaction(_('Remove selected'))
    def delApplicantsContainers(self, **data):
        form = self.request.form
        if 'val_id' in form:
            child_id = form['val_id']
        else:
            self.flash(_('No container selected!'), type='warning')
            self.redirect(self.url(self.context, '@@manage')+'#tab2')
            return
        if not isinstance(child_id, list):
            child_id = [child_id]
        deleted = []
        for id in child_id:
            try:
                del self.context[id]
                deleted.append(id)
            except:
                self.flash(_('Could not delete:') + ' %s: %s: %s' % (
                    id, sys.exc_info()[0], sys.exc_info()[1]), type='danger')
        if len(deleted):
            self.flash(_('Successfully removed: ${a}',
                mapping = {'a':', '.join(deleted)}))
        self.redirect(self.url(self.context, '@@manage')+'#tab2')
        return

    @action(_('Add applicants container'), validator=NullValidator)
    def addApplicantsContainer(self, **data):
        self.redirect(self.url(self.context, '@@add'))
        return

    @action(_('Add local role'), validator=NullValidator)
    def addLocalRole(self, **data):
        return add_local_role(self,3, **data)

    @action(_('Remove selected local roles'))
    def delLocalRoles(self, **data):
        return del_local_roles(self,3,**data)

    @action(_('Save'), style='primary')
    def save(self, **data):
        self.applyData(self.context, **data)
        description = getattr(self.context, 'description', None)
        portal_language = getUtility(IKofaUtils).PORTAL_LANGUAGE
        self.context.description_dict = html2dict(description, portal_language)
        self.flash(_('Form has been saved.'))
        return

class ApplicantsContainerAddFormPage(KofaAddFormPage):
    grok.context(IApplicantsRoot)
    grok.require('waeup.manageApplication')
    grok.name('add')
    grok.template('applicantscontaineraddpage')
    label = _('Add applicants container')
    pnav = 3

    form_fields = grok.AutoFields(
        IApplicantsContainerAdd).omit('code').omit('title')

    @action(_('Add applicants container'))
    def addApplicantsContainer(self, **data):
        year = data['year']
        code = u'%s%s' % (data['prefix'], year)
        apptypes_dict = getUtility(IApplicantsUtils).APP_TYPES_DICT
        title = apptypes_dict[data['prefix']][0]
        title = u'%s %s/%s' % (title, year, year + 1)
        if code in self.context.keys():
            self.flash(
              _('An applicants container for the same application '
                'type and entrance year exists already in the database.'),
                type='warning')
            return
        # Add new applicants container...
        container = createObject(u'waeup.ApplicantsContainer')
        self.applyData(container, **data)
        container.code = code
        container.title = title
        self.context[code] = container
        self.flash(_('Added:') + ' "%s".' % code)
        self.redirect(self.url(self.context, u'@@manage'))
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context, '@@manage'))

class ApplicantsRootBreadcrumb(Breadcrumb):
    """A breadcrumb for applicantsroot.
    """
    grok.context(IApplicantsRoot)
    title = _(u'Applicants')

class ApplicantsContainerBreadcrumb(Breadcrumb):
    """A breadcrumb for applicantscontainers.
    """
    grok.context(IApplicantsContainer)


class ApplicantsExportsBreadcrumb(Breadcrumb):
    """A breadcrumb for exports.
    """
    grok.context(VirtualApplicantsExportJobContainer)
    title = _(u'Applicant Data Exports')
    target = None

class ApplicantBreadcrumb(Breadcrumb):
    """A breadcrumb for applicants.
    """
    grok.context(IApplicant)

    @property
    def title(self):
        """Get a title for a context.
        """
        return self.context.application_number

class OnlinePaymentBreadcrumb(Breadcrumb):
    """A breadcrumb for payments.
    """
    grok.context(IApplicantOnlinePayment)

    @property
    def title(self):
        return self.context.p_id

class ApplicantsStatisticsPage(KofaDisplayFormPage):
    """Some statistics about applicants in a container.
    """
    grok.context(IApplicantsContainer)
    grok.name('statistics')
    grok.require('waeup.viewApplicationStatistics')
    grok.template('applicantcontainerstatistics')

    @property
    def label(self):
        return "%s" % self.context.title

class ApplicantsContainerPage(KofaDisplayFormPage):
    """The standard view for regular applicant containers.
    """
    grok.context(IApplicantsContainer)
    grok.name('index')
    grok.require('waeup.Public')
    grok.template('applicantscontainerpage')
    pnav = 3

    @property
    def form_fields(self):
        form_fields = grok.AutoFields(IApplicantsContainer).omit(
            'title', 'description')
        form_fields[
            'startdate'].custom_widget = FriendlyDatetimeDisplayWidget('le')
        form_fields[
            'enddate'].custom_widget = FriendlyDatetimeDisplayWidget('le')
        if self.request.principal.id == 'zope.anybody':
            form_fields = form_fields.omit(
                'code', 'prefix', 'year', 'mode', 'hidden',
                'strict_deadline', 'application_category',
                'application_slip_notice')
        return form_fields

    @property
    def introduction(self):
        # Here we know that the cookie has been set
        lang = self.request.cookies.get('kofa.language')
        html = self.context.description_dict.get(lang,'')
        if html == '':
            portal_language = getUtility(IKofaUtils).PORTAL_LANGUAGE
            html = self.context.description_dict.get(portal_language,'')
        return html

    @property
    def label(self):
        return "%s" % self.context.title

class ApplicantsContainerManageFormPage(KofaEditFormPage):
    grok.context(IApplicantsContainer)
    grok.name('manage')
    grok.template('applicantscontainermanagepage')
    form_fields = grok.AutoFields(IApplicantsContainer)
    taboneactions = [_('Save'),_('Cancel')]
    tabtwoactions = [_('Remove selected'),_('Cancel'),
        _('Create students from selected')]
    tabthreeactions1 = [_('Remove selected local roles')]
    tabthreeactions2 = [_('Add local role')]
    # Use friendlier date widget...
    grok.require('waeup.manageApplication')

    @property
    def label(self):
        return _('Manage applicants container')

    pnav = 3

    @property
    def showApplicants(self):
        if len(self.context) < 5000:
            return True
        return False

    def getLocalRoles(self):
        roles = ILocalRolesAssignable(self.context)
        return roles()

    def getUsers(self):
        """Get a list of all users.
        """
        for key, val in grok.getSite()['users'].items():
            url = self.url(val)
            yield(dict(url=url, name=key, val=val))

    def getUsersWithLocalRoles(self):
        return get_users_with_local_roles(self.context)

    @action(_('Save'), style='primary')
    def save(self, **data):
        changed_fields = self.applyData(self.context, **data)
        if changed_fields:
            changed_fields = reduce(lambda x,y: x+y, changed_fields.values())
        else:
            changed_fields = []
        description = getattr(self.context, 'description', None)
        portal_language = getUtility(IKofaUtils).PORTAL_LANGUAGE
        self.context.description_dict = html2dict(description, portal_language)
        # Always refresh title. So we can change titles
        # if APP_TYPES_DICT has been edited.
        apptypes_dict = getUtility(IApplicantsUtils).APP_TYPES_DICT
        title = apptypes_dict[self.context.prefix][0]
        #self.context.title = u'%s %s/%s' % (
        #    title, self.context.year, self.context.year + 1)
        self.flash(_('Form has been saved.'))
        fields_string = ' + '.join(changed_fields)
        self.context.writeLogMessage(self, 'saved: % s' % fields_string)
        return

    @jsaction(_('Remove selected'))
    def delApplicant(self, **data):
        form = self.request.form
        if 'val_id' in form:
            child_id = form['val_id']
        else:
            self.flash(_('No applicant selected!'), type='warning')
            self.redirect(self.url(self.context, '@@manage')+'#tab2')
            return
        if not isinstance(child_id, list):
            child_id = [child_id]
        deleted = []
        for id in child_id:
            try:
                del self.context[id]
                deleted.append(id)
            except:
                self.flash(_('Could not delete:') + ' %s: %s: %s' % (
                    id, sys.exc_info()[0], sys.exc_info()[1]), type='danger')
        if len(deleted):
            self.flash(_('Successfully removed: ${a}',
                mapping = {'a':', '.join(deleted)}))
        self.redirect(self.url(self.context, u'@@manage')+'#tab2')
        return

    @action(_('Create students from selected'))
    def createStudents(self, **data):
        form = self.request.form
        if 'val_id' in form:
            child_id = form['val_id']
        else:
            self.flash(_('No applicant selected!'), type='warning')
            self.redirect(self.url(self.context, '@@manage')+'#tab2')
            return
        if not isinstance(child_id, list):
            child_id = [child_id]
        created = []
        for id in child_id:
            success, msg = self.context[id].createStudent(view=self)
            if success:
                created.append(id)
        if len(created):
            self.flash(_('${a} students successfully created.',
                mapping = {'a': len(created)}))
        else:
            self.flash(_('No student could be created.'), type='warning')
        self.redirect(self.url(self.context, u'@@manage')+'#tab2')
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context))
        return

    @action(_('Add local role'), validator=NullValidator)
    def addLocalRole(self, **data):
        return add_local_role(self,3, **data)

    @action(_('Remove selected local roles'))
    def delLocalRoles(self, **data):
        return del_local_roles(self,3,**data)

class ApplicantAddFormPage(KofaAddFormPage):
    """Add-form to add an applicant.
    """
    grok.context(IApplicantsContainer)
    grok.require('waeup.manageApplication')
    grok.name('addapplicant')
    #grok.template('applicantaddpage')
    form_fields = grok.AutoFields(IApplicant).select(
        'firstname', 'middlename', 'lastname',
        'email', 'phone')
    label = _('Add applicant')
    pnav = 3

    @action(_('Create application record'))
    def addApplicant(self, **data):
        applicant = createObject(u'waeup.Applicant')
        self.applyData(applicant, **data)
        self.context.addApplicant(applicant)
        self.flash(_('Applicant record created.'))
        self.redirect(
            self.url(self.context[applicant.application_number], 'index'))
        return

class ApplicantDisplayFormPage(KofaDisplayFormPage):
    """A display view for applicant data.
    """
    grok.context(IApplicant)
    grok.name('index')
    grok.require('waeup.viewApplication')
    grok.template('applicantdisplaypage')
    label = _('Applicant')
    pnav = 3
    hide_hint = False

    @property
    def form_fields(self):
        if self.context.special:
            form_fields = grok.AutoFields(ISpecialApplicant).omit('locked')
        else:
            form_fields = grok.AutoFields(IApplicant).omit(
                'locked', 'course_admitted', 'password', 'suspended')
        return form_fields

    @property
    def target(self):
        return getattr(self.context.__parent__, 'prefix', None)

    @property
    def separators(self):
        return getUtility(IApplicantsUtils).SEPARATORS_DICT

    def update(self):
        self.passport_url = self.url(self.context, 'passport.jpg')
        # Mark application as started if applicant logs in for the first time
        usertype = getattr(self.request.principal, 'user_type', None)
        if usertype == 'applicant' and \
            IWorkflowState(self.context).getState() == INITIALIZED:
            IWorkflowInfo(self.context).fireTransition('start')
        if usertype == 'applicant' and self.context.state == 'created':
            session = '%s/%s' % (self.context.__parent__.year,
                                 self.context.__parent__.year+1)
            title = getattr(grok.getSite()['configuration'], 'name', u'Sample University')
            msg = _(
                '\n <strong>Congratulations!</strong>' +
                ' You have been offered provisional admission into the' +
                ' ${c} Academic Session of ${d}.'
                ' Your student record has been created for you.' +
                ' Please, logout again and proceed to the' +
                ' login page of the portal.'
                ' Then enter your new student credentials:' +
                ' user name= ${a}, password = ${b}.' +
                ' Change your password when you have logged in.',
                mapping = {
                    'a':self.context.student_id,
                    'b':self.context.application_number,
                    'c':session,
                    'd':title}
                )
            self.flash(msg)
        return

    @property
    def hasPassword(self):
        if self.context.password:
            return _('set')
        return _('unset')

    @property
    def label(self):
        container_title = self.context.__parent__.title
        return _('${a} <br /> Application Record ${b}', mapping = {
            'a':container_title, 'b':self.context.application_number})

    def getCourseAdmitted(self):
        """Return link, title and code in html format to the certificate
           admitted.
        """
        course_admitted = self.context.course_admitted
        if getattr(course_admitted, '__parent__',None):
            url = self.url(course_admitted)
            title = course_admitted.title
            code = course_admitted.code
            return '<a href="%s">%s - %s</a>' %(url,code,title)
        return ''

class ApplicantBaseDisplayFormPage(ApplicantDisplayFormPage):
    grok.context(IApplicant)
    grok.name('base')
    form_fields = grok.AutoFields(IApplicant).select(
        'applicant_id','email', 'course1')

class CreateStudentPage(UtilityView, grok.View):
    """Create a student object from applicant data.
    """
    grok.context(IApplicant)
    grok.name('createstudent')
    grok.require('waeup.manageStudent')

    def update(self):
        msg = self.context.createStudent(view=self)[1]
        self.flash(msg, type='warning')
        self.redirect(self.url(self.context))
        return

    def render(self):
        return

class CreateAllStudentsPage(UtilityView, grok.View):
    """Create all student objects from applicant data
    in the root container or in a specific  applicants container only.

    Only PortalManagers can do this.
    """
    #grok.context(IApplicantsContainer)
    grok.name('createallstudents')
    grok.require('waeup.managePortal')

    def update(self):
        cat = getUtility(ICatalog, name='applicants_catalog')
        results = list(cat.searchResults(state=(ADMITTED, ADMITTED)))
        created = []
        container_only = False
        applicants_root = grok.getSite()['applicants']
        if isinstance(self.context, ApplicantsContainer):
            container_only = True
        for result in results:
            if container_only and result.__parent__ is not self.context:
                continue
            success, msg = result.createStudent(view=self)
            if success:
                created.append(result.applicant_id)
            else:
                ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
                applicants_root.logger.info(
                    '%s - %s - %s' % (ob_class, result.applicant_id, msg))
        if len(created):
            self.flash(_('${a} students successfully created.',
                mapping = {'a': len(created)}))
        else:
            self.flash(_('No student could be created.'), type='warning')
        self.redirect(self.url(self.context))
        return

    def render(self):
        return

class ApplicationFeePaymentAddPage(UtilityView, grok.View):
    """ Page to add an online payment ticket
    """
    grok.context(IApplicant)
    grok.name('addafp')
    grok.require('waeup.payApplicant')
    factory = u'waeup.ApplicantOnlinePayment'

    @property
    def custom_requirements(self):
        return ''

    def update(self):
        # Additional requirements in custom packages.
        if self.custom_requirements:
            self.flash(
                self.custom_requirements,
                type='danger')
            self.redirect(self.url(self.context))
            return
        if not self.context.special:
            for key in self.context.keys():
                ticket = self.context[key]
                if ticket.p_state == 'paid':
                      self.flash(
                          _('This type of payment has already been made.'),
                          type='warning')
                      self.redirect(self.url(self.context))
                      return
        applicants_utils = getUtility(IApplicantsUtils)
        container = self.context.__parent__
        payment = createObject(self.factory)
        failure = applicants_utils.setPaymentDetails(
            container, payment, self.context)
        if failure is not None:
            self.flash(failure[0], type='danger')
            self.redirect(self.url(self.context))
            return
        self.context[payment.p_id] = payment
        self.flash(_('Payment ticket created.'))
        self.redirect(self.url(payment))
        return

    def render(self):
        return


class OnlinePaymentDisplayFormPage(KofaDisplayFormPage):
    """ Page to view an online payment ticket
    """
    grok.context(IApplicantOnlinePayment)
    grok.name('index')
    grok.require('waeup.viewApplication')
    form_fields = grok.AutoFields(IApplicantOnlinePayment).omit('p_item')
    form_fields[
        'creation_date'].custom_widget = FriendlyDatetimeDisplayWidget('le')
    form_fields[
        'payment_date'].custom_widget = FriendlyDatetimeDisplayWidget('le')
    pnav = 3

    @property
    def label(self):
        return _('${a}: Online Payment Ticket ${b}', mapping = {
            'a':self.context.__parent__.display_fullname,
            'b':self.context.p_id})

class OnlinePaymentApprovePage(UtilityView, grok.View):
    """ Approval view
    """
    grok.context(IApplicantOnlinePayment)
    grok.name('approve')
    grok.require('waeup.managePortal')

    def update(self):
        flashtype, msg, log = self.context.approveApplicantPayment()
        if log is not None:
            applicant = self.context.__parent__
            # Add log message to applicants.log
            applicant.writeLogMessage(self, log)
            # Add log message to payments.log
            self.context.logger.info(
                '%s,%s,%s,%s,%s,,,,,,' % (
                applicant.applicant_id,
                self.context.p_id, self.context.p_category,
                self.context.amount_auth, self.context.r_code))
        self.flash(msg, type=flashtype)
        return

    def render(self):
        self.redirect(self.url(self.context, '@@index'))
        return

class ExportPDFPaymentSlipPage(UtilityView, grok.View):
    """Deliver a PDF slip of the context.
    """
    grok.context(IApplicantOnlinePayment)
    grok.name('payment_slip.pdf')
    grok.require('waeup.viewApplication')
    form_fields = grok.AutoFields(IApplicantOnlinePayment).omit('p_item')
    form_fields['creation_date'].custom_widget = FriendlyDatetimeDisplayWidget('le')
    form_fields['payment_date'].custom_widget = FriendlyDatetimeDisplayWidget('le')
    prefix = 'form'
    note = None

    @property
    def title(self):
        portal_language = getUtility(IKofaUtils).PORTAL_LANGUAGE
        return translate(_('Payment Data'), 'waeup.kofa',
            target_language=portal_language)

    @property
    def label(self):
        portal_language = getUtility(IKofaUtils).PORTAL_LANGUAGE
        return translate(_('Online Payment Slip'),
            'waeup.kofa', target_language=portal_language) \
            + ' %s' % self.context.p_id

    @property
    def payment_slip_download_warning(self):
        if self.context.__parent__.state != SUBMITTED:
            return _('Please submit the application form before '
                     'trying to download payment slips.')
        return ''

    def render(self):
        if self.payment_slip_download_warning:
            self.flash(self.payment_slip_download_warning, type='danger')
            self.redirect(self.url(self.context))
            return
        applicantview = ApplicantBaseDisplayFormPage(self.context.__parent__,
            self.request)
        students_utils = getUtility(IStudentsUtils)
        return students_utils.renderPDF(self,'payment_slip.pdf',
            self.context.__parent__, applicantview, note=self.note)

class ExportPDFPageApplicationSlip(UtilityView, grok.View):
    """Deliver a PDF slip of the context.
    """
    grok.context(IApplicant)
    grok.name('application_slip.pdf')
    grok.require('waeup.viewApplication')
    prefix = 'form'

    def update(self):
        if self.context.state in ('initialized', 'started', 'paid'):
            self.flash(
                _('Please pay and submit before trying to download '
                  'the application slip.'), type='warning')
            return self.redirect(self.url(self.context))
        return

    def render(self):
        try:
            pdfstream = getAdapter(self.context, IPDF, name='application_slip')(
                view=self)
        except IOError:
            self.flash(
                _('Your image file is corrupted. '
                  'Please replace.'), type='danger')
            return self.redirect(self.url(self.context))
        self.response.setHeader(
            'Content-Type', 'application/pdf')
        return pdfstream

def handle_img_upload(upload, context, view):
    """Handle upload of applicant image.

    Returns `True` in case of success or `False`.

    Please note that file pointer passed in (`upload`) most probably
    points to end of file when leaving this function.
    """
    size = file_size(upload)
    if size > MAX_UPLOAD_SIZE:
        view.flash(_('Uploaded image is too big!'), type='danger')
        return False
    dummy, ext = os.path.splitext(upload.filename)
    ext.lower()
    if ext != '.jpg':
        view.flash(_('jpg file extension expected.'), type='danger')
        return False
    upload.seek(0) # file pointer moved when determining size
    store = getUtility(IExtFileStore)
    file_id = IFileStoreNameChooser(context).chooseName()
    store.createFile(file_id, upload)
    return True

class ApplicantManageFormPage(KofaEditFormPage):
    """A full edit view for applicant data.
    """
    grok.context(IApplicant)
    grok.name('manage')
    grok.require('waeup.manageApplication')
    grok.template('applicanteditpage')
    manage_applications = True
    pnav = 3
    display_actions = [[_('Save'), _('Final Submit')],
        [_('Add online payment ticket'),_('Remove selected tickets')]]

    @property
    def form_fields(self):
        if self.context.special:
            form_fields = grok.AutoFields(ISpecialApplicant)
            form_fields['applicant_id'].for_display = True
        else:
            form_fields = grok.AutoFields(IApplicant)
            form_fields['student_id'].for_display = True
            form_fields['applicant_id'].for_display = True
        return form_fields

    @property
    def target(self):
        return getattr(self.context.__parent__, 'prefix', None)

    @property
    def separators(self):
        return getUtility(IApplicantsUtils).SEPARATORS_DICT

    @property
    def custom_upload_requirements(self):
        return ''

    def update(self):
        super(ApplicantManageFormPage, self).update()
        self.wf_info = IWorkflowInfo(self.context)
        self.max_upload_size = string_from_bytes(MAX_UPLOAD_SIZE)
        self.upload_success = None
        upload = self.request.form.get('form.passport', None)
        if upload:
            if self.custom_upload_requirements:
                self.flash(
                    self.custom_upload_requirements,
                    type='danger')
                self.redirect(self.url(self.context))
                return
            # We got a fresh upload, upload_success is
            # either True or False
            self.upload_success = handle_img_upload(
                upload, self.context, self)
            if self.upload_success:
                self.context.writeLogMessage(self, 'saved: passport')
        return

    @property
    def label(self):
        container_title = self.context.__parent__.title
        return _('${a} <br /> Application Form ${b}', mapping = {
            'a':container_title, 'b':self.context.application_number})

    def getTransitions(self):
        """Return a list of dicts of allowed transition ids and titles.

        Each list entry provides keys ``name`` and ``title`` for
        internal name and (human readable) title of a single
        transition.
        """
        allowed_transitions = [t for t in self.wf_info.getManualTransitions()
            if not t[0] in ('pay', 'create')]
        return [dict(name='', title=_('No transition'))] +[
            dict(name=x, title=y) for x, y in allowed_transitions]

    @action(_('Save'), style='primary')
    def save(self, **data):
        form = self.request.form
        password = form.get('password', None)
        password_ctl = form.get('control_password', None)
        if password:
            validator = getUtility(IPasswordValidator)
            errors = validator.validate_password(password, password_ctl)
            if errors:
                self.flash( ' '.join(errors), type='danger')
                return
        if self.upload_success is False:  # False is not None!
            # Error during image upload. Ignore other values.
            return 
        changed_fields = self.applyData(self.context, **data)
        # Turn list of lists into single list
        if changed_fields:
            changed_fields = reduce(lambda x,y: x+y, changed_fields.values())
        else:
            changed_fields = []
        if password:
            # Now we know that the form has no errors and can set password ...
            IUserAccount(self.context).setPassword(password)
            changed_fields.append('password')
        fields_string = ' + '.join(changed_fields)
        trans_id = form.get('transition', None)
        if trans_id:
            self.wf_info.fireTransition(trans_id)
        self.flash(_('Form has been saved.'))
        if fields_string:
            self.context.writeLogMessage(self, 'saved: % s' % fields_string)
        return

    def unremovable(self, ticket):
        return False

    # This method is also used by the ApplicantEditFormPage
    def delPaymentTickets(self, **data):
        form = self.request.form
        if 'val_id' in form:
            child_id = form['val_id']
        else:
            self.flash(_('No payment selected.'), type='warning')
            self.redirect(self.url(self.context))
            return
        if not isinstance(child_id, list):
            child_id = [child_id]
        deleted = []
        for id in child_id:
            # Applicants are not allowed to remove used payment tickets
            if not self.unremovable(self.context[id]):
                try:
                    del self.context[id]
                    deleted.append(id)
                except:
                    self.flash(_('Could not delete:') + ' %s: %s: %s' % (
                      id, sys.exc_info()[0], sys.exc_info()[1]), type='danger')
        if len(deleted):
            self.flash(_('Successfully removed: ${a}',
                mapping = {'a':', '.join(deleted)}))
            self.context.writeLogMessage(
                self, 'removed: % s' % ', '.join(deleted))
        return

    # We explicitely want the forms to be validated before payment tickets
    # can be created. If no validation is requested, use
    # 'validator=NullValidator' in the action directive
    @action(_('Add online payment ticket'), style='primary')
    def addPaymentTicket(self, **data):
        self.redirect(self.url(self.context, '@@addafp'))
        return

    @jsaction(_('Remove selected tickets'))
    def removePaymentTickets(self, **data):
        self.delPaymentTickets(**data)
        self.redirect(self.url(self.context) + '/@@manage')
        return

    # Not used in base package
    def file_exists(self, attr):
        file = getUtility(IExtFileStore).getFileByContext(
            self.context, attr=attr)
        if file:
            return True
        else:
            return False

class ApplicantEditFormPage(ApplicantManageFormPage):
    """An applicant-centered edit view for applicant data.
    """
    grok.context(IApplicantEdit)
    grok.name('edit')
    grok.require('waeup.handleApplication')
    grok.template('applicanteditpage')
    manage_applications = False
    submit_state = PAID

    @property
    def form_fields(self):
        if self.context.special:
            form_fields = grok.AutoFields(ISpecialApplicant).omit(
                'locked', 'suspended')
            form_fields['applicant_id'].for_display = True
        else:
            form_fields = grok.AutoFields(IApplicantEdit).omit(
                'locked', 'course_admitted', 'student_id',
                'suspended'
                )
            form_fields['applicant_id'].for_display = True
            form_fields['reg_number'].for_display = True
        return form_fields

    @property
    def display_actions(self):
        state = IWorkflowState(self.context).getState()
        actions = [[],[]]
        if state == STARTED:
            actions = [[_('Save')],
                [_('Add online payment ticket'),_('Remove selected tickets')]]
        elif self.context.special and state == PAID:
            actions = [[_('Save'), _('Final Submit')],
                [_('Add online payment ticket'),_('Remove selected tickets')]]
        elif state == PAID:
            actions = [[_('Save'), _('Final Submit')],
                [_('Remove selected tickets')]]
        return actions

    def unremovable(self, ticket):
        state = IWorkflowState(self.context).getState()
        return ticket.r_code or state in (INITIALIZED, SUBMITTED)

    def emit_lock_message(self):
        self.flash(_('The requested form is locked (read-only).'),
                   type='warning')
        self.redirect(self.url(self.context))
        return

    def update(self):
        if self.context.locked or (
            self.context.__parent__.expired and
            self.context.__parent__.strict_deadline):
            self.emit_lock_message()
            return
        super(ApplicantEditFormPage, self).update()
        return

    def dataNotComplete(self):
        store = getUtility(IExtFileStore)
        if not store.getFileByContext(self.context, attr=u'passport.jpg'):
            return _('No passport picture uploaded.')
        if not self.request.form.get('confirm_passport', False):
            return _('Passport picture confirmation box not ticked.')
        return False

    # We explicitely want the forms to be validated before payment tickets
    # can be created. If no validation is requested, use
    # 'validator=NullValidator' in the action directive
    @action(_('Add online payment ticket'), style='primary')
    def addPaymentTicket(self, **data):
        self.redirect(self.url(self.context, '@@addafp'))
        return

    @jsaction(_('Remove selected tickets'))
    def removePaymentTickets(self, **data):
        self.delPaymentTickets(**data)
        self.redirect(self.url(self.context) + '/@@edit')
        return

    @action(_('Save'), style='primary')
    def save(self, **data):
        if self.upload_success is False:  # False is not None!
            # Error during image upload. Ignore other values.
            return
        if data.get('course1', 1) == data.get('course2', 2):
            self.flash(_('1st and 2nd choice must be different.'),
                       type='warning')
            return
        self.applyData(self.context, **data)
        self.flash(_('Form has been saved.'))
        return

    @action(_('Final Submit'), warning=WARNING)
    def finalsubmit(self, **data):
        if self.upload_success is False:  # False is not None!
            return # error during image upload. Ignore other values
        if self.dataNotComplete():
            self.flash(self.dataNotComplete(), type='danger')
            return
        self.applyData(self.context, **data)
        state = IWorkflowState(self.context).getState()
        # This shouldn't happen, but the application officer
        # might have forgotten to lock the form after changing the state
        if state != self.submit_state:
            self.flash(_('The form cannot be submitted. Wrong state!'),
                       type='danger')
            return
        IWorkflowInfo(self.context).fireTransition('submit')
        # application_date is used in export files for sorting.
        # We can thus store utc.
        self.context.application_date = datetime.utcnow()
        self.flash(_('Form has been submitted.'))
        self.redirect(self.url(self.context))
        return

class PassportImage(grok.View):
    """Renders the passport image for applicants.
    """
    grok.name('passport.jpg')
    grok.context(IApplicant)
    grok.require('waeup.viewApplication')

    def render(self):
        # A filename chooser turns a context into a filename suitable
        # for file storage.
        image = getUtility(IExtFileStore).getFileByContext(self.context)
        self.response.setHeader(
            'Content-Type', 'image/jpeg')
        if image is None:
            # show placeholder image
            return open(DEFAULT_PASSPORT_IMAGE_PATH, 'rb').read()
        return image

class ApplicantRegistrationPage(KofaAddFormPage):
    """Captcha'd registration page for applicants.
    """
    grok.context(IApplicantsContainer)
    grok.name('register')
    grok.require('waeup.Anonymous')
    grok.template('applicantregister')

    @property
    def form_fields(self):
        form_fields = None
        if self.context.mode == 'update':
            form_fields = grok.AutoFields(IApplicantRegisterUpdate).select(
                'lastname','reg_number','email')
        else: #if self.context.mode == 'create':
            form_fields = grok.AutoFields(IApplicantEdit).select(
                'firstname', 'middlename', 'lastname', 'email', 'phone')
        return form_fields

    @property
    def label(self):
        return _('Apply for ${a}',
            mapping = {'a':self.context.title})

    def update(self):
        if self.context.expired:
            self.flash(_('Outside application period.'), type='warning')
            self.redirect(self.url(self.context))
            return
        # Handle captcha
        self.captcha = getUtility(ICaptchaManager).getCaptcha()
        self.captcha_result = self.captcha.verify(self.request)
        self.captcha_code = self.captcha.display(self.captcha_result.error_code)
        return

    def _redirect(self, email, password, applicant_id):
        # Forward only email to landing page in base package.
        self.redirect(self.url(self.context, 'registration_complete',
            data = dict(email=email)))
        return

    @action(_('Send login credentials to email address'), style='primary')
    def register(self, **data):
        if not self.captcha_result.is_valid:
            # Captcha will display error messages automatically.
            # No need to flash something.
            return
        if self.context.mode == 'create':
            # Add applicant
            applicant = createObject(u'waeup.Applicant')
            self.applyData(applicant, **data)
            self.context.addApplicant(applicant)
            applicant.reg_number = applicant.applicant_id
            notify(grok.ObjectModifiedEvent(applicant))
        elif self.context.mode == 'update':
            # Update applicant
            reg_number = data.get('reg_number','')
            lastname = data.get('lastname','')
            cat = getUtility(ICatalog, name='applicants_catalog')
            results = list(
                cat.searchResults(reg_number=(reg_number, reg_number)))
            if results:
                applicant = results[0]
                if getattr(applicant,'lastname',None) is None:
                    self.flash(_('An error occurred.'), type='danger')
                    return
                elif applicant.lastname.lower() != lastname.lower():
                    # Don't tell the truth here. Anonymous must not
                    # know that a record was found and only the lastname
                    # verification failed.
                    self.flash(_('No application record found.'), type='warning')
                    return
                elif applicant.password is not None and \
                    applicant.state != INITIALIZED:
                    self.flash(_('Your password has already been set and used. '
                                 'Please proceed to the login page.'),
                               type='warning')
                    return
                # Store email address but nothing else.
                applicant.email = data['email']
                notify(grok.ObjectModifiedEvent(applicant))
            else:
                # No record found, this is the truth.
                self.flash(_('No application record found.'), type='warning')
                return
        else:
            # Does not happen but anyway ...
            return
        kofa_utils = getUtility(IKofaUtils)
        password = kofa_utils.genPassword()
        IUserAccount(applicant).setPassword(password)
        # Send email with credentials
        login_url = self.url(grok.getSite(), 'login')
        url_info = u'Login: %s' % login_url
        msg = _('You have successfully been registered for the')
        if kofa_utils.sendCredentials(IUserAccount(applicant),
            password, url_info, msg):
            email_sent = applicant.email
        else:
            email_sent = None
        self._redirect(email=email_sent, password=password,
            applicant_id=applicant.applicant_id)
        return

class ApplicantRegistrationEmailSent(KofaPage):
    """Landing page after successful registration.

    """
    grok.name('registration_complete')
    grok.require('waeup.Public')
    grok.template('applicantregemailsent')
    label = _('Your registration was successful.')

    def update(self, email=None, applicant_id=None, password=None):
        self.email = email
        self.password = password
        self.applicant_id = applicant_id
        return

class ExportJobContainerOverview(KofaPage):
    """Page that lists active applicant data export jobs and provides links
    to discard or download CSV files.

    """
    grok.context(VirtualApplicantsExportJobContainer)
    grok.require('waeup.manageApplication')
    grok.name('index.html')
    grok.template('exportjobsindex')
    label = _('Data Exports')
    pnav = 3

    def update(self, CREATE=None, DISCARD=None, job_id=None):
        if CREATE:
            self.redirect(self.url('@@start_export'))
            return
        if DISCARD and job_id:
            entry = self.context.entry_from_job_id(job_id)
            self.context.delete_export_entry(entry)
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            self.context.logger.info(
                '%s - discarded: job_id=%s' % (ob_class, job_id))
            self.flash(_('Discarded export') + ' %s' % job_id)
        self.entries = doll_up(self, user=self.request.principal.id)
        return

class ExportJobContainerJobStart(KofaPage):
    """Page that starts an applicants export job.

    """
    grok.context(VirtualApplicantsExportJobContainer)
    grok.require('waeup.manageApplication')
    grok.name('start_export')

    def update(self):
        exporter = 'applicants'
        container_code = self.context.__parent__.code
        job_id = self.context.start_export_job(exporter,
                                      self.request.principal.id,
                                      container=container_code)

        ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
        self.context.logger.info(
            '%s - exported: %s (%s), job_id=%s'
            % (ob_class, exporter, container_code, job_id))
        self.flash(_('Export started.'))
        self.redirect(self.url(self.context))
        return

    def render(self):
        return

class ExportJobContainerDownload(ExportCSVView):
    """Page that downloads a students export csv file.

    """
    grok.context(VirtualApplicantsExportJobContainer)
    grok.require('waeup.manageApplication')
