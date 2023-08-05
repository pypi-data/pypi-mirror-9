## $Id: viewlets.py 11874 2014-10-23 07:24:39Z henrik $
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
import grok
from waeup.kofa.interfaces import IKofaObject
from waeup.kofa.students.viewlets import PrimaryStudentNavTab
from waeup.kofa.browser.viewlets import (
    ManageActionButton, PrimaryNavTab, AddActionButton)
from waeup.kofa.applicants.interfaces import (
    IApplicant, IApplicantsRoot, IApplicantsContainer,
    IApplicantOnlinePayment
    )
from waeup.kofa.applicants.browser import (
    ApplicantsRootPage, ApplicantsContainerPage, ApplicantManageFormPage,
    ApplicantDisplayFormPage, OnlinePaymentDisplayFormPage,
    ApplicantsContainerManageFormPage, ApplicantsStatisticsPage
    )

from waeup.kofa.interfaces import MessageFactory as _

grok.context(IKofaObject) # Make IKofaObject the default context
grok.templatedir('browser_templates')

class ApplicantsAuthTab(PrimaryNavTab):
    """Applicants tab in primary navigation.
    """
    grok.context(IKofaObject)
    grok.order(3)
    grok.require('waeup.viewApplicantsTab')
    pnav = 3
    tab_title = _(u'Applicants')

    @property
    def link_target(self):
        return self.view.application_url('applicants')

class ApplicantsAnonTab(ApplicantsAuthTab):
    """Applicants tab in primary navigation.

    Display tab only for anonymous. Authenticated users can call the
    form from the user navigation bar.
    """
    grok.require('waeup.Anonymous')
    tab_title = _(u'Application')

    # Also zope.manager has role Anonymous.
    # To avoid displaying this tab, we have to check the principal id too.
    @property
    def link_target(self):
        if self.request.principal.id == 'zope.anybody':
            return self.view.application_url('applicants')
        return

class MyApplicationDataTab(PrimaryStudentNavTab):
    """MyData-tab in primary navigation.
    """
    grok.order(3)
    grok.require('waeup.viewMyApplicationDataTab')
    pnav = 3
    tab_title = _(u'My Data')

    @property
    def link_target(self):
        try:
            container, application_number = self.request.principal.id.split('_')
        except ValueError:
            return
        rel_link = '/applicants/%s/%s' % (container, application_number)
        return self.view.application_url() + rel_link

class ApplicantsRootSearchActionButton(ManageActionButton):
    grok.order(1)
    grok.context(IApplicantsRoot)
    grok.view(ApplicantsRootPage)
    grok.require('waeup.viewApplication')
    text = _('Find applicants')
    icon = 'actionicon_search.png'
    target = '@@search'

class ApplicantsRootManageActionButton(ManageActionButton):
    grok.order(2)
    grok.context(IApplicantsRoot)
    grok.view(ApplicantsRootPage)
    grok.require('waeup.manageApplication')
    text = _('Manage application section')

class ApplicantRegisterActionButton(ManageActionButton):
    grok.order(1)
    grok.context(IApplicantsContainer)
    grok.view(ApplicantsContainerPage)
    grok.require('waeup.Anonymous')
    icon = 'actionicon_login.png'
    text = _('Register for application')
    target = 'register'

class ApplicantsContainerAddActionButton(AddActionButton):
    grok.order(1)
    grok.context(IApplicantsContainer)
    grok.view(ApplicantsContainerManageFormPage)
    grok.require('waeup.manageApplication')
    text = _('Add applicant')
    target = 'addapplicant'

class ApplicantsContainerStatisticsActionButton(ManageActionButton):
    grok.order(2)
    grok.context(IApplicantsContainer)
    grok.view(ApplicantsContainerManageFormPage)
    grok.require('waeup.viewApplicationStatistics')
    icon = 'actionicon_statistics.png'
    text = _('Container statistics')
    target = 'statistics'

class ApplicantsContainerStatisticsActionButton2(
        ApplicantsContainerStatisticsActionButton):
    grok.order(3)
    grok.view(ApplicantsContainerPage)

class ApplicantsContainerManageActionButton(ManageActionButton):
    grok.order(2)
    grok.context(IApplicantsContainer)
    grok.view(ApplicantsContainerPage)
    grok.require('waeup.manageApplication')
    text = _('Manage container')
    target = 'manage'

class ExportApplicantsActionButton(ManageActionButton):
    """ 'Export applicants' button for faculties.
    """
    grok.context(IApplicantsContainer)
    grok.view(ApplicantsContainerPage)
    grok.require('waeup.manageApplication')
    icon = 'actionicon_down.png'
    text = _('Export applicants')
    target = 'exports'
    grok.order(4)

class ApplicantsRootCreateStudentsActionButton(ManageActionButton):
    grok.order(3)
    grok.context(IApplicantsRoot)
    grok.view(ApplicantsRootPage)
    grok.require('waeup.managePortal')
    icon = 'actionicon_entrance.png'
    text = _('Create students')
    target ='createallstudents'

    @property
    def target_url(self):
        if self.target and self.request.principal.id == 'admin':
            return self.view.url(self.view.context, self.target)
        return

class ApplicantsContainerCreateStudentsActionButton(ManageActionButton):
    grok.order(1)
    grok.context(IApplicantsContainer)
    grok.view(ApplicantsStatisticsPage)
    grok.require('waeup.managePortal')
    icon = 'actionicon_entrance.png'
    text = _('Create students')
    target ='createallstudents'

    @property
    def target_url(self):
        if self.target and self.request.principal.id == 'admin':
            return self.view.url(self.view.context, self.target)
        return

class ApplicantViewActionButton(ManageActionButton):
    grok.context(IApplicant)
    grok.view(ApplicantManageFormPage)
    grok.require('waeup.viewApplication')
    icon = 'actionicon_view.png'
    text = _('View application record')
    target = 'index'

class ApplicantManageActionButton(ManageActionButton):
    grok.order(1)
    grok.context(IApplicant)
    grok.view(ApplicantDisplayFormPage)
    grok.require('waeup.manageApplication')
    text = _('Manage application record')
    target = 'manage'

class ApplicantEditActionButton(ManageActionButton):
    grok.order(2)
    grok.context(IApplicant)
    grok.view(ApplicantDisplayFormPage)
    grok.require('waeup.handleApplication')
    text = _('Edit application record')
    target ='edit'

    @property
    def target_url(self):
        """Get a URL to the target...
        """
        if self.context.locked or (
            self.context.__parent__.expired and
            self.context.__parent__.strict_deadline):
            return
        return self.view.url(self.view.context, self.target)

class PDFActionButton(ManageActionButton):
    grok.order(3)
    grok.context(IApplicant)
    grok.require('waeup.viewApplication')
    grok.name('pdfactionbutton')
    icon = 'actionicon_pdf.png'
    text = _('Download application slip')
    target = 'application_slip.pdf'

    @property
    def target_url(self):
        """Get a URL to the target...
        """
        if self.context.state in ('initialized', 'started', 'paid') \
            or self.context.special:
            return
        return self.view.url(self.view.context, self.target)

class StudentCreateActionButton(ManageActionButton):
    grok.order(4)
    grok.context(IApplicant)
    grok.require('waeup.manageApplication')
    icon = 'actionicon_entrance.png'
    text = _('Create student record')
    target ='createstudent'

    @property
    def target_url(self):
        """Get a URL to the target...
        """
        if self.context.state != 'admitted':
            return
        return self.view.url(self.view.context, self.target)

class PaymentReceiptActionButton(ManageActionButton):
    grok.order(9) # This button should always be the last one.
    grok.context(IApplicantOnlinePayment)
    grok.view(OnlinePaymentDisplayFormPage)
    grok.require('waeup.viewApplication')
    icon = 'actionicon_pdf.png'
    text = _('Download payment slip')
    target = 'payment_slip.pdf'

    @property
    def target_url(self):
        #if self.context.p_state != 'paid':
        #    return ''
        return self.view.url(self.view.context, self.target)

class ApprovePaymentActionButton(ManageActionButton):
    grok.order(8)
    grok.context(IApplicantOnlinePayment)
    grok.view(OnlinePaymentDisplayFormPage)
    grok.require('waeup.managePortal')
    icon = 'actionicon_accept.png'
    text = _('Approve payment')
    target = 'approve'

    @property
    def target_url(self):
        if self.context.p_state == 'paid':
            return ''
        return self.view.url(self.view.context, self.target)
