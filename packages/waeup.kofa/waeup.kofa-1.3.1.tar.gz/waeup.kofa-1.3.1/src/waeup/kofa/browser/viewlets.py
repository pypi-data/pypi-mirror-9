## $Id: viewlets.py 11862 2014-10-21 07:07:04Z henrik $
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
from urllib import urlencode
from zope.i18n import translate
from zope.component import getMultiAdapter, queryAdapter, getUtility
from zope.interface import Interface
from zope.location.interfaces import ISite
from zope.traversing.browser import absoluteURL
from waeup.kofa.browser.pages import (
    UniversityPage, FacultiesContainerPage, DatacenterPage, FacultyPage,
    DepartmentPage, CoursePage, CertificatePage, CertificateCoursePage,
    UsersContainerPage, UserManageFormPage)
from waeup.kofa.browser.interfaces import (
    IFacultiesContainer, IFaculty, IDepartment, ICourse, ICertificate,
    ICertificateCourse, IBreadcrumbContainer, IUniversity, IUsersContainer)
from waeup.kofa.interfaces import (
    IKofaUtils, IKofaObject, IKofaXMLExporter,
    IKofaXMLImporter, IDataCenter, IUserAccount)
from waeup.kofa.browser.layout import KofaPage, default_primary_nav_template
from waeup.kofa.utils.helpers import get_user_account

from waeup.kofa.interfaces import MessageFactory as _

grok.templatedir('templates')
grok.context(IKofaObject) # Make IKofaObject the default context

class ManageSidebar(grok.ViewletManager):
    grok.name('left_manage')

class BreadCrumbManager(grok.ViewletManager):
    grok.name('breadcrumbs')

class LanguageManager(grok.ViewletManager):
    grok.name('languages')

class ActionBar(grok.ViewletManager):
    grok.name('actionbar')

class AdministrationTasks(grok.ViewletManager):
    grok.name('admintasks')

class WidgetsSlot(grok.ViewletManager):
    grok.name('widgets')


#
# Baseclasses that give some defaults for really used viewlets.
#
class ActionButton(grok.Viewlet):
    """A base for action buttons.

    An action button provides an icon, some text, links to a
    target and optionally an onclick event handler.
    If you want to set a different text, icon or target name
    for some active button below, just override the approriate
    attribute in the concerned viewlet.

    Action buttons provide by default dynamic attributes

     * ``alt``
          An alternative text for the icon. By default the same as
          the text.

     * ``icon_url``
          The URL of the icon.

     * ``target_url``
          The URL of the link target.

     * ``onclick``
          An onclick Javascript event handler.

    """
    grok.baseclass()
    grok.context(IKofaObject)
    grok.viewletmanager(ActionBar)
    icon = 'actionicon_modify.png' # File must exist in static/
    target = '@@manage' # link to this viewname.
    text = _('Edit') # Text to display on the button

    # We set the template file explicitly (instead of using
    # ``grok.template('actionbutton')``) to stick with this template
    # also in derived classes in other packages. If we didn't, those
    # derived ActionButton viewlets had to provide an own template,
    # which would not be updated automatically, when the local
    # template ``templates/actionbutton.pt`` changes.
    #
    # Inheriting viewlets that wish to use their own template anyway
    # can do so by setting their local ``grok.template(<mytemplate>)``
    # and setting ``template`` to ``None`` for the class::
    #
    # class DerivedActionButton(ActionButton):
    #   ...
    #   grok.template('overriding_template')
    #   template = None
    #   ...
    #
    template = grok.PageTemplateFile('templates/actionbutton.pt')

    @property
    def alt(self):
        """Alternative text for icon.
        """
        return self.text

    @property
    def icon_url(self):
        """Get the icon URL.
        """
        return '/static/img/%s' % self.icon

    @property
    def target_url(self):
        """Get a URL to the target...
        """
        if self.target:
            return self.view.url(self.view.context, self.target)
        return

    @property
    def onclick(self):
        """Onclick event...
        """
        return

class PlainActionButton(ActionButton):
    """A base for action buttons without image
    """
    grok.baseclass()
    template = grok.PageTemplateFile('templates/plainactionbutton.pt')

    
class ManageActionButton(ActionButton):
    """A base for 'edit' buttons
    """
    grok.baseclass()
    grok.order(2)
    grok.require('waeup.manageAcademics')
    icon = 'actionicon_modify.png'
    target = '@@manage'
    text = _('Edit')

class AddActionButton(ActionButton):
    """A base for 'add' buttons.
    """
    grok.baseclass()
    grok.order(4)
    grok.require('waeup.manageAcademics')
    icon = 'actionicon_add.png'
    target = 'add'
    text = _('Add')
    
class RemoveActionButton(ActionButton):
    """A base for 'remove' buttons.
    """
    grok.baseclass()
    grok.order(4)
    grok.require('waeup.manageAcademics')
    icon = 'actionicon_delete.png'
    target = 'remove'
    text = _('Remove')

class SearchActionButton(ActionButton):
    """A base for 'search' buttons.
    """
    grok.baseclass()
    grok.order(5)
    grok.require('waeup.manageAcademics')
    icon = 'actionicon_search.png'
    target = 'search'
    text = _('Search')


#
# General viewlets (for more than one page/context)
#

class BreadCrumbs(grok.Viewlet):
    grok.context(IKofaObject)
    grok.viewletmanager(BreadCrumbManager)
    grok.order(1)

    def getEntries(self):
        result = []
        site = grok.getSite()
        context = self.context
        breadcrumbs = IBreadcrumbContainer(self.view)
        for breadcrumb in breadcrumbs:
            if breadcrumb.target is None:
                yield dict(
                    title = breadcrumb.title,
                    url = self.view.url(breadcrumb.context)
                    )
            elif breadcrumb.target:
                yield dict(
                    title = breadcrumb.title,
                    url = self.view.url(breadcrumb.context, breadcrumb.target)
                    )

class LanguagesLink(grok.Viewlet):
    """ The language selector itself.
    """
    grok.viewletmanager(LanguageManager)
    grok.context(IKofaObject)
    grok.require('waeup.Public')
    title = u'Languages'

    def render(self):
        preferred_languages = getUtility(IKofaUtils).PREFERRED_LANGUAGES_DICT
        html = u''
        for key, value in sorted(
            preferred_languages.items(), key=lambda lang: lang[1][0]):
            args = {'lang':key, 'view_name':self.view.__name__}
            url = self.view.url(
                self.context) + '/@@change_language?%s' % urlencode(args)
            html += u'| <a href="%s" title="%s">%s</a> ' % (url, value[1], key)
        return html

# Problem with circular references. Disabled for now...
# class ExportXMLAction(grok.Viewlet):
#    grok.viewletmanager(ActionBar)
#     #grok.view(Index)
#     grok.order(98)
#     grok.require('waeup.managePortal')

#class ImportXMLAction(grok.Viewlet):
#    grok.viewletmanager(ActionBar)
#    #grok.view(Index)
#    grok.order(99)
#    grok.require('waeup.managePortal')
#
#    def update(self):
#        # We cannot simply replace local sites.
#        self.can_import = not ISite.providedBy(self.context)


class WidgetsTableRows(grok.Viewlet):
    """The only viewlet for the WidgetsSlot viewlet manager.
    """
    template = grok.PageTemplateFile('templates/widgets.pt')
    grok.viewletmanager(WidgetsSlot)


class Login(grok.Viewlet):
    """This viewlet allows to login in the sidebar.
    """
    grok.viewletmanager(ManageSidebar)
    grok.context(IKofaObject)
    grok.view(Interface)
    grok.order(2)
    grok.require('waeup.Anonymous')
    text = _('Login')
    link = 'login'

    def render(self):
        if self.request.principal.id != 'zope.anybody':
            return ''
        url = self.view.url(grok.getSite(), self.link)
        return u'<li"><a href="%s">%s</a></li>' % (
                url, self.text)


class ManageLink(grok.Viewlet):
    """A link displayed in the upper left box.

    This viewlet renders a link to the application object's settings
    form (the 'manage' view).

    In derived classes you can create different links by setting a
    different link and text attribute. The `link` parameter is
    understood relative to the respective application object, so that
    ``@@manage`` will create a link to
    ``localhost:8080/app/@@manage``.

    Links defined by descendants from this viewlet are displayed on
    every page the user is allowed to go to, if the user has also the
    permissions set by `grok.require()`. By default only users with
    ``waeup.managePortal`` permission will see links defined by
    this or derivated classes.
    """
    grok.baseclass()
    grok.viewletmanager(ManageSidebar)
    grok.context(IKofaObject)
    grok.view(Interface)
    grok.order(1)
    # This link is only displayed, if the user is
    # allowed to use it!
    grok.require('waeup.managePortal')

    link = 'relative_link'
    text = _(u'Any link text')
    
    def render(self):
        url = self.view.url(grok.getSite(), self.link)
        text = translate(self.text, context=self.request)
        return u'<li><a href="%s">%s</a></li>' % (
                url, text)

class ManagePortalConfiguration(ManageLink):
    """A link to portal configuration.
    """
    grok.order(1)
    grok.require('waeup.managePortalConfiguration')

    link = 'configuration'
    text = _(u'Portal Configuration')

class ManageUsersLink(ManageLink):
    """A link to users management, placed in upper left box.
    """
    grok.order(2)
    grok.require('waeup.manageUsers')

    link = u'users'
    text = _(u'Portal Users')

class ManageDataCenter(ManageLink):
    """A link to datacenter, placed in upper left box.
    """
    grok.order(3)
    grok.require('waeup.manageDataCenter')

    link = u'datacenter'
    text = _(u'Data Center')

class ManageReports(ManageLink):
    """A link to reports, placed in upper left box.
    """
    grok.order(4)
    grok.require('waeup.manageReports')

    link = u'reports'
    text = _(u'Reports')

class MyPreferences(ManageLink):
    """A link to personal preferences, placed in upper left box.
    """
    grok.order(6)
    grok.require('waeup.Public')
    text = _(u'My Preferences')

    def render(self):
        account_object = get_user_account(self.request)
        if account_object:
            url = self.view.url(account_object)
            text = translate(self.text, context=self.request)
            return u'<li><a href="%s">%s</a></li>' % (
                    url, text)
        return ''

class MyRoles(ManageLink):
    """A link to display site and local roles.
    """
    grok.order(7)
    grok.require('waeup.Public')
    text = _(u'My Roles')

    def render(self):
        account_object = get_user_account(self.request)
        if account_object:
            url = self.view.url(account_object) + '/my_roles'
            text = translate(self.text, context=self.request)
            return u'<li><a href="%s">%s</a></li>' % (
                    url, text)
        return ''

class ContactActionButton(ManageActionButton):
    grok.order(4)
    grok.context(IUserAccount)
    grok.view(UserManageFormPage)
    grok.require('waeup.manageUsers')
    icon = 'actionicon_mail.png'
    text = _('Send email')
    target = 'contactuser'

class ManageDataCenterActionButton(ManageActionButton):
    """ 'Edit settings' button for datacenter.
    """
    grok.context(IDataCenter)
    grok.view(DatacenterPage)
    grok.require('waeup.managePortal')
    text = _('Edit settings')
    grok.order(1)

class ManageFacultiesContainerActionButton(ManageActionButton):
    """ 'Manage settings' button for faculties.
    """
    grok.context(IFacultiesContainer)
    grok.view(FacultiesContainerPage)
    text = _('Manage academic section')

class ExportFacultiesStudentsActionButton(ManageActionButton):
    """ 'Export student data' button for faculties.
    """
    grok.context(IFacultiesContainer)
    grok.view(FacultiesContainerPage)
    grok.name('exportfacultystudents')
    grok.require('waeup.showStudents')
    icon = 'actionicon_down.png'
    text = _('Export student data')
    target = 'exports'
    grok.order(3)

class SearchFacultiesContainerActionButton(ManageActionButton):
    """ 'Manage settings' button for faculties.
    """
    grok.context(IFacultiesContainer)
    grok.view(FacultiesContainerPage)
    text = _('Search academic section')
    icon = 'actionicon_search.png'
    target = '@@search'
    
class ManageFacultyActionButton(ManageActionButton):
    """ 'Manage settings' button for faculties.
    """
    grok.context(IFaculty)
    grok.view(FacultyPage)
    text = _('Manage faculty')

class StudentSearchActionButton(ManageActionButton):
    grok.order(2)
    grok.context(IFaculty)
    grok.view(FacultyPage)
    grok.name('findstudents')
    grok.require('waeup.showStudents')
    text = _('Find students')
    icon = 'actionicon_search.png'
    target = 'find_students'

class ManageDepartmentActionButton(ManageActionButton):
    """ 'Manage settings' button for departments.
    """
    grok.context(IDepartment)
    grok.view(DepartmentPage)
    text = _('Manage department')
    grok.order(1)

class ShowDepartmentStudentsActionButton(ManageActionButton):
    """ 'Show students' button for departments.
    """
    grok.context(IDepartment)
    grok.view(DepartmentPage)
    grok.name('showdepartmentstudents')
    grok.require('waeup.showStudents')
    icon = 'actionicon_student.png'
    text = _('Show students')
    target = 'students'
    grok.order(2)

class ExportDepartmentStudentsActionButton(ManageActionButton):
    """ 'Export student data' button for departments.
    """
    grok.context(IDepartment)
    grok.view(DepartmentPage)
    grok.name('exportdepartmentstudents')
    grok.require('waeup.showStudents')
    icon = 'actionicon_down.png'
    text = _('Export student data')
    target = 'exports'
    grok.order(3)

class ClearDepartmentStudentsActionButton(ManageActionButton):
    """ 'Clear all students' button for departments.
    """
    grok.context(IDepartment)
    grok.view(DepartmentPage)
    grok.name('cleardepartmentstudents')
    grok.require('waeup.clearAllStudents')
    icon = 'actionicon_accept.png'
    text = _('Clear all students')
    target = 'clearallstudents'
    grok.order(4)

    @property
    def onclick(self):
        return "return window.confirm(%s);" % _(
            "'All students, who requested clearance in this department, will be cleared. Are you sure?'")

class ManageCourseActionButton(ManageActionButton):
    """ 'Edit settings' button for courses.
    """
    grok.context(ICourse)
    grok.view(CoursePage)
    text = _('Edit course')
    grok.order(1)
    
class ShowCourseStudentsActionButton(ManageActionButton):
    """ 'Show students' button in course.
    """
    grok.context(ICourse)
    grok.view(CoursePage)
    grok.name('showcoursestudents')
    grok.require('waeup.showStudents')
    icon = 'actionicon_student.png'
    text = _('Show students')
    target = 'students'
    grok.order(2)

class ExportCourseStudentsActionButton(ManageActionButton):
    """ 'Export student data' button for courses.
    """
    grok.context(ICourse)
    grok.view(CoursePage)
    grok.name('exportcoursestudents')
    grok.require('waeup.showStudents')
    icon = 'actionicon_down.png'
    text = _('Export student data')
    target = 'exports'
    grok.order(3)

class UpdateScoresActionButton(ManageActionButton):
    """ 'Update scores' button in course.
    """
    grok.context(ICourse)
    grok.view(CoursePage)
    grok.name('updatescores')
    grok.require('waeup.editScores')
    icon = 'actionicon_scores.png'
    text = _('Update scores')
    target = 'edit_scores'
    grok.order(4)

class ManageCertificateActionButton(ManageActionButton):
    """ 'Manage settings' button for certificates.
    """
    grok.context(ICertificate)
    grok.view(CertificatePage)
    text = _('Manage certificate')
    grok.order(1)

class ShowCertificateStudentsActionButton(ManageActionButton):
    """ 'Show students' button for certificates.
    """
    grok.context(ICertificate)
    grok.view(CertificatePage)
    grok.name('showcertificatestudents')
    grok.require('waeup.showStudents')
    icon = 'actionicon_student.png'
    text = _('Show students')
    target = 'students'
    grok.order(2)

class ExportCertificateStudentsActionButton(ManageActionButton):
    """ 'Export student data' button for certificates.
    """
    grok.context(ICertificate)
    grok.view(CertificatePage)
    grok.name('exportcertificatestudents')
    grok.require('waeup.showStudents')
    icon = 'actionicon_down.png'
    text = _('Export student data')
    target = 'exports'
    grok.order(3)

class ManageCertificateCourseActionButton(ManageActionButton):
    """ 'Manage settings' button for certificate courses.
    """
    grok.context(ICertificateCourse)
    grok.view(CertificateCoursePage)
    text = _('Edit certificate course')

class AddUserActionButton(AddActionButton):
    grok.require('waeup.manageUsers')
    grok.context(IUsersContainer)
    grok.view(UsersContainerPage)
    text = _('Add user')

class BrowseDatacenterLogs(ActionButton):
    grok.context(IDataCenter)
    grok.require('waeup.manageDataCenter')
    grok.view(DatacenterPage)
    grok.order(2)
    icon = 'actionicon_info.png'
    target = '@@logs'
    text = _('Show logs')

class UploadCSVButton(ActionButton):
    grok.context(IDataCenter)
    grok.view(DatacenterPage)
    grok.require('waeup.manageDataCenter')
    grok.order(3)
    icon = 'actionicon_up.png'
    target = '@@upload'
    text = _('Upload data')

class BatchOpButton(ActionButton):
    grok.context(IDataCenter)
    grok.view(DatacenterPage)
    grok.require('waeup.manageDataCenter')
    grok.order(4)
    icon = 'actionicon_gear.png'
    target = '@@import1'
    text = _('Process data')

class ExportCSVButton(ActionButton):
    grok.context(IDataCenter)
    grok.view(DatacenterPage)
    grok.require('waeup.exportData')
    grok.order(5)
    icon = 'actionicon_down.png'
    target = '@@export'
    text = _('Export data')

class BrowseFinishedFiles(ActionButton):
    grok.context(IDataCenter)
    grok.require('waeup.manageDataCenter')
    grok.view(DatacenterPage)
    grok.order(6)
    icon = 'actionicon_finished.png'
    target = '@@processed'
    text = _('View processed files')

#
# Primary navigation tabs (in upper left navigation bar)...
#
class PrimaryNavManager(grok.ViewletManager):
    """Viewlet manager for the primary navigation tab.
    """
    grok.name('primary_nav')

class PrimaryNavTab(grok.Viewlet):
    """Base for primary nav tabs.
    """
    grok.baseclass()
    grok.viewletmanager(PrimaryNavManager)
    grok.order(1)
    grok.require('waeup.Public')
    template = default_primary_nav_template

    pnav = 0 # This is a kind of id of a tab. If some page provides
             # also a 'pnav' attribute with the same value (here: 0),
             # then the tab will be rendered as 'active' when the page
             # gets rendered.
             #
             # This way you can assign certain pages to certain
             # primary nav tabs. Each primary tab should therefore set
             # the 'pnav' attribute to a different value (or several
             # tabs might be rendered as active simultanously when the
             # page gets rendered.
    tab_title = u'Some Text'
    
    @property
    def link_target(self):
        return self.view.application_url()

    @property
    def active(self):
        view_pnav = getattr(self.view, 'pnav', 0)
        if view_pnav == self.pnav:
            return 'active'
        return ''

#class HomeTab(PrimaryNavTab):
#    """Home-tab in primary navigation.
#    """
#    grok.order(1)
#    grok.require('waeup.Public')

#    pnav = 0
#    tab_title = u'Home'

class FacultiesTab(PrimaryNavTab):
    """Faculties-tab in primary navigation.
    """
    grok.order(2)
    grok.require('waeup.viewAcademics')

    pnav = 1
    tab_title = _(u'Academics')

    @property
    def link_target(self):
        return self.view.application_url('faculties')

    
class EnquiriesTab(PrimaryNavTab):
    """Contact tab in primary navigation.

    Display tab only for anonymous. Authenticated users can call a
    contact form from the user navigation bar.
    """
    grok.order(6)
    grok.require('waeup.Anonymous')
    tab_title = _(u'Enquiries')
    pnav = 2

    # Also zope.manager has role Anonymous.
    # To avoid displaying this tab, we have to check the principal id too.
    @property
    def link_target(self):
        if self.request.principal.id == 'zope.anybody':
            return self.view.application_url('enquiries')
        return

#
# Administration tasks
#
class AdminTask(grok.Viewlet):
    """The base for task entries on administration page.
    """
    grok.baseclass()
    grok.order(1)
    grok.viewletmanager(AdministrationTasks)
    grok.require('waeup.managePortal')
    grok.template('admintask')

    link_title = 'Manage users' # How the link to the target will be titled.
    target_viewname = 'users'   # The name of the target view.
    
    @property
    def link_target(self):
        return self.view.url(self.context[self.target_viewname])

class AdminTaskPortalConfiguration(AdminTask):
    """Entry on administration page that link to portal settings.
    """
    grok.order(1)
    grok.require('waeup.managePortalConfiguration')

    link_title = _('Portal Configuration')
    def link_target(self):
        return self.view.url(self.view.context, 'configuration')

class AdminTaskUsers(AdminTask):
    """Entry on administration page that link to user folder.
    """
    grok.order(2)
    grok.require('waeup.manageUsers')

    link_title = _('Portal Users')
    target_viewname = 'users'
    
class AdminTaskDatacenter(AdminTask):
    """Entry on administration page that link to datacenter.
    """
    grok.order(3)
    grok.require('waeup.manageDataCenter')

    link_title = _('Data Center')
    target_viewname = 'datacenter'

class AdminTaskReports(AdminTask):
    """Entry on administration page that link to datacenter.
    """
    grok.order(3)
    grok.require('waeup.manageReports')

    link_title = _('Reports')
    target_viewname = 'reports'

# The SubobjectLister and its viewlets below are not used in Kofa.

class SubobjectLister(grok.ViewletManager):
    """Very special viewlet manager that displays lists of subobjects.
    """
    grok.name('subobjectlist')
    grok.template('subobjectlist')

    def update(self):
        # The default implementation of update() sets self.viewlets to
        # a list of viewlets for the current context
        # (self.context). We make use of that fact by retrieving all
        # viewlets for all items in our context container by simply
        # setting these items as context while we call the default
        # update() method. So we get a list of lists of viewlets for
        # each item in a 'row' (where a single item is a row).
        rows = []
        orig_context = self.context
        for name, value in self.context.items():
            # Retrieve all viewlets for the current item (not the context)
            self.context = value
            super(SubobjectLister, self).update() # sets self.viewlets
            rows.append(self.viewlets)
            self.context = orig_context
        self.rows = rows
        # Finally, set the viewlets we would retrieve normally...
        super(SubobjectLister, self).update()
        return


class FacultiesContainerListHead(grok.Viewlet):
    """The header line of faculty container subobject lists.
    """
    grok.order(1)
    grok.viewletmanager(SubobjectLister)
    grok.context(IFacultiesContainer)
    grok.require('waeup.viewAcademics')

    def render(self):
        return u'<th>Code</th><th>Title</th><th></th>'

class FacultyListName(grok.Viewlet):
    """Display a the title of a faculty as link in a list.
    """
    grok.order(1)
    grok.viewletmanager(SubobjectLister)
    grok.context(IFaculty)
    grok.require('waeup.viewAcademics')

    def render(self):
        return u'<a href="%s">%s</a>' % (
            self.view.url(self.context), self.context.__name__)

class FacultyListTitle(grok.Viewlet):
    """Display the title of a faculty in a list.
    """
    grok.order(2)
    grok.viewletmanager(SubobjectLister)
    grok.context(IFaculty)
    grok.require('waeup.viewAcademics')

    def render(self):
        return self.context.title

class FacultyRemoveButton(grok.Viewlet):
    """Render a remove button for faculty lists.
    """
    grok.order(3)
    grok.viewletmanager(SubobjectLister)
    grok.context(IFaculty)
    grok.require('waeup.manageAcademics')

    def render(self):
        return u'<div class="text-right"><form method="POST">' + \
            '<input class="text-right" type="submit" value="remove" />' + \
            '</form></div>'
