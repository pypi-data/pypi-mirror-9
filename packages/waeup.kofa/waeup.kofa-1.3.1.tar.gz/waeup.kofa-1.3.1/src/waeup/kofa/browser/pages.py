## $Id: pages.py 12232 2014-12-14 21:41:02Z henrik $
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
""" Viewing components for Kofa objects.
"""
# XXX: All csv ops should move to a dedicated module soon
import unicodecsv as csv
import grok
import os
import re
import sys
from datetime import datetime, timedelta
from urllib import urlencode
from hurry.query import Eq, Text
from hurry.query.query import Query
from zope import schema
from zope.i18n import translate
from zope.authentication.interfaces import (
    IAuthentication, IUnauthenticatedPrincipal, ILogout)
from zope.catalog.interfaces import ICatalog
from zope.component import (
    getUtility, queryUtility, createObject, getAllUtilitiesRegisteredFor,
    getUtilitiesFor,
    )
from zope.event import notify
from zope.security import checkPermission
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.session.interfaces import ISession
from zope.password.interfaces import IPasswordManager
from waeup.kofa.utils.helpers import html2dict
from waeup.kofa.browser.layout import (
    KofaPage, KofaForm, KofaEditFormPage, KofaAddFormPage,
    KofaDisplayFormPage, NullValidator)
from waeup.kofa.browser.interfaces import (
    IUniversity, IFacultiesContainer, IFaculty,
    IDepartment, ICourse, ICertificate,
    ICertificateCourse,
    ICaptchaManager, IChangePassword)
from waeup.kofa.browser.layout import jsaction, action, UtilityView
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.interfaces import(
    IKofaObject, IUsersContainer, IUserAccount, IDataCenter,
    IKofaXMLImporter, IKofaXMLExporter, IBatchProcessor,
    ILocalRolesAssignable, DuplicationError, IConfigurationContainer,
    ISessionConfiguration, ISessionConfigurationAdd, IJobManager,
    IPasswordValidator, IContactForm, IKofaUtils, ICSVExporter,
    academic_sessions_vocab)
from waeup.kofa.permissions import (
    get_users_with_local_roles, get_all_roles, get_all_users,
    get_users_with_role)

from waeup.kofa.university.catalog import search
from waeup.kofa.university.vocabularies import course_levels
from waeup.kofa.authentication import LocalRoleSetEvent
from waeup.kofa.utils.helpers import get_user_account, check_csv_charset
from waeup.kofa.mandates.mandate import PasswordMandate
from waeup.kofa.datacenter import DataCenterFile

from waeup.kofa.students.catalog import StudentQueryResultItem
from waeup.kofa.students.interfaces import IStudentsUtils

FORBIDDEN_CHARACTERS = (160,)

grok.context(IKofaObject)
grok.templatedir('templates')

def add_local_role(view, tab, **data):
    localrole = view.request.form.get('local_role', None)
    user = view.request.form.get('user', None)
    if user is None or localrole is None:
        view.flash('No user selected.', type='danger')
        view.redirect(view.url(view.context, '@@manage')+'#tab%s' % tab)
        return
    role_manager = IPrincipalRoleManager(view.context)
    role_manager.assignRoleToPrincipal(localrole, user)
    notify(LocalRoleSetEvent(view.context, localrole, user, granted=True))
    ob_class = view.__implemented__.__name__.replace('waeup.kofa.','')
    grok.getSite().logger.info(
        '%s - added: %s|%s' % (ob_class, user, localrole))
    view.redirect(view.url(view.context, u'@@manage')+'#tab%s' % tab)
    return

def del_local_roles(view, tab, **data):
    child_ids = view.request.form.get('role_id', None)
    if child_ids is None:
        view.flash(_('No local role selected.'), type='danger')
        view.redirect(view.url(view.context, '@@manage')+'#tab%s' % tab)
        return
    if not isinstance(child_ids, list):
        child_ids = [child_ids]
    deleted = []
    role_manager = IPrincipalRoleManager(view.context)
    for child_id in child_ids:
        localrole = child_id.split('|')[1]
        user_name = child_id.split('|')[0]
        try:
            role_manager.unsetRoleForPrincipal(localrole, user_name)
            notify(LocalRoleSetEvent(
                    view.context, localrole, user_name, granted=False))
            deleted.append(child_id)
        except:
            view.flash('Could not remove %s: %s: %s' % (
                    child_id, sys.exc_info()[0], sys.exc_info()[1]),
                    type='danger')
    if len(deleted):
        view.flash(
            _('Local role successfully removed: ${a}',
            mapping = {'a':', '.join(deleted)}))
        ob_class = view.__implemented__.__name__.replace('waeup.kofa.','')
        grok.getSite().logger.info(
            '%s - removed: %s' % (ob_class, ', '.join(deleted)))
    view.redirect(view.url(view.context, u'@@manage')+'#tab%s' % tab)
    return

def delSubobjects(view, redirect, tab=None, subcontainer=None):
    form = view.request.form
    if 'val_id' in form:
        child_id = form['val_id']
    else:
        view.flash(_('No item selected.'), type='danger')
        if tab:
            view.redirect(view.url(view.context, redirect)+'#tab%s' % tab)
        else:
            view.redirect(view.url(view.context, redirect))
        return
    if not isinstance(child_id, list):
        child_id = [child_id]
    deleted = []
    for id in child_id:
        try:
            if subcontainer:
                container = getattr(view.context, subcontainer, None)
                del container[id]
            else:
                del view.context[id]
            deleted.append(id)
        except:
            view.flash('Could not delete %s: %s: %s' % (
                    id, sys.exc_info()[0], sys.exc_info()[1]), type='danger')
    if len(deleted):
        view.flash(_('Successfully removed: ${a}',
            mapping = {'a': ', '.join(deleted)}))
        ob_class = view.__implemented__.__name__.replace('waeup.kofa.','')
        grok.getSite().logger.info(
            '%s - removed: %s' % (ob_class, ', '.join(deleted)))
    if tab:
        view.redirect(view.url(view.context, redirect)+'#tab%s' % tab)
    else:
        view.redirect(view.url(view.context, redirect))
    return

def getPreviewTable(view, n):
    """Get transposed table with n sample record.

    The first column contains the headers.
    """
    if not view.reader:
        return
    header = view.getPreviewHeader()
    num = 0
    data = []
    for line in view.reader:
        if num > n-1:
            break
        num += 1
        data.append(line)
    result = []
    for name in header:
        result_line = []
        result_line.append(name)
        for d in data:
            result_line.append(d[name])
        result.append(result_line)
    return result

# Save function used for save methods in pages
def msave(view, **data):
    changed_fields = view.applyData(view.context, **data)
    # Turn list of lists into single list
    if changed_fields:
        changed_fields = reduce(lambda x,y: x+y, changed_fields.values())
    fields_string = ' + '.join(changed_fields)
    view.flash(_('Form has been saved.'))
    ob_class = view.__implemented__.__name__.replace('waeup.kofa.','')
    if fields_string:
        grok.getSite().logger.info('%s - %s - saved: %s' % (ob_class, view.context.__name__, fields_string))
    return

def doll_up(view, user=None):
    """Doll up export jobs for displaying in table.
    """
    job_entries = view.context.get_running_export_jobs(user)
    job_manager = getUtility(IJobManager)
    entries = []
    for job_id, exporter_name, user_id in job_entries:
        job = job_manager.get(job_id)
        exporter = getUtility(ICSVExporter, name=exporter_name)
        exporter_title = getattr(exporter, 'title', 'Unknown')
        args = ', '.join(['%s=%s' % (item[0], item[1])
            for item in job.kwargs.items()])
        status = job.finished and 'ready' or 'running'
        status = job.failed and 'FAILED' or status
        start_time = getattr(job, 'begin_after', None)
        time_delta = None
        if start_time:
            tz = getUtility(IKofaUtils).tzinfo
            time_delta = datetime.now(tz) - start_time
            start_time = start_time.astimezone(tz).strftime(
                "%Y-%m-%d %H:%M:%S %Z")
        download_url = view.url(view.context, 'download_export',
                                data=dict(job_id=job_id))
        show_download_button = job.finished and not \
                               job.failed and time_delta and \
                               time_delta.days < 1
        new_entry = dict(
            job=job_id,
            creator=user_id,
            args=args,
            exporter=exporter_title,
            status=status,
            start_time=start_time,
            download_url=download_url,
            show_download_button = show_download_button,
            show_refresh_button = not job.finished,
            show_discard_button = job.finished,)
        entries.append(new_entry)
    return entries

class LocalRoleAssignmentUtilityView(object):
    """A view mixin with useful methods for local role assignment.

    """

    def getLocalRoles(self):
        roles = ILocalRolesAssignable(self.context)
        return roles()

    def getUsers(self):
        return get_all_users()

    def getUsersWithLocalRoles(self):
        return get_users_with_local_roles(self.context)

#
# Login/logout and language switch pages...
#

class LoginPage(KofaPage):
    """A login page, available for all objects.
    """
    grok.name('login')
    grok.context(IKofaObject)
    grok.require('waeup.Public')
    label = _(u'Login')
    camefrom = None
    login_button = label

    def _comment(self, student):
        return getattr(student, 'suspended_comment', None)

    def update(self, SUBMIT=None, camefrom=None):
        self.camefrom = camefrom
        if SUBMIT is not None:
            if self.request.principal.id != 'zope.anybody':
                self.flash(_('You logged in.'))
                if self.request.principal.user_type == 'student':
                    student = grok.getSite()['students'][
                        self.request.principal.id]
                    rel_link = '/students/%s' % self.request.principal.id
                    if student.personal_data_expired:
                        rel_link = '/students/%s/edit_personal' % (
                            self.request.principal.id)
                        self.flash(
                          _('Your personal data record is outdated. Please update.'),
                          type='warning')
                    self.redirect(self.application_url() + rel_link)
                    return
                elif self.request.principal.user_type == 'applicant':
                    container, application_number = self.request.principal.id.split('_')
                    rel_link = '/applicants/%s/%s' % (
                        container, application_number)
                    self.redirect(self.application_url() + rel_link)
                    return
                if not self.camefrom:
                    self.redirect(self.application_url() + '/index')
                    return
                self.redirect(self.camefrom)
                return
            # Display appropriate flash message if credentials are correct
            # but student has been deactivated or a temporary password
            # has been set.
            login = self.request.form['form.login']
            if len(login) == 8 and login in grok.getSite()['students']:
                student = grok.getSite()['students'][login]
                password = self.request.form['form.password']
                passwordmanager = getUtility(IPasswordManager, 'SSHA')
                if student.password is not None and \
                    passwordmanager.checkPassword(student.password, password):
                    # The student entered valid credentials.
                    # First we check if a temporary password has been set.
                    delta = timedelta(minutes=10)
                    now = datetime.utcnow()
                    temp_password_dict = getattr(student, 'temp_password', None)
                    if temp_password_dict is not None and \
                        now < temp_password_dict.get('timestamp', now) + delta:
                        self.flash(
                            _('Your account has been temporarily deactivated.'),
                            type='warning')
                        return
                    # Now we know that the student is suspended.
                    comment = self._comment(student)
                    if comment:
                        self.flash(comment, type='warning')
                    else:
                        self.flash(_('Your account has been deactivated.'),
                                   type='warning')
                    return
            self.flash(_('You entered invalid credentials.'), type='danger')
            return


class LogoutPage(KofaPage):
    """A logout page. Calling this page will log the current user out.
    """
    grok.context(IKofaObject)
    grok.require('waeup.Public')
    grok.name('logout')

    def update(self):
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            auth = getUtility(IAuthentication)
            ILogout(auth).logout(self.request)
            self.flash(_("You have been logged out. Thanks for using WAeUP Kofa!"))
        self.redirect(self.application_url() + '/index')
        return


class LanguageChangePage(KofaPage):
    """ Language switch
    """
    grok.context(IKofaObject)
    grok.name('change_language')
    grok.require('waeup.Public')

    def update(self, lang='en', view_name='@@index'):
        self.response.setCookie('kofa.language', lang, path='/')
        self.redirect(self.url(self.context, view_name))
        return

    def render(self):
        return

#
# Contact form...
#

class ContactAdminForm(KofaForm):
    grok.name('contactadmin')
    #grok.context(IUniversity)
    grok.template('contactform')
    grok.require('waeup.Authenticated')
    pnav = 2
    form_fields = grok.AutoFields(IContactForm).select('body')

    def update(self):
        super(ContactAdminForm, self).update()
        self.form_fields.get('body').field.default = None
        return

    @property
    def config(self):
        return grok.getSite()['configuration']

    def label(self):
        return _(u'Contact ${a}', mapping = {'a': self.config.name_admin})

    @property
    def get_user_account(self):
        return get_user_account(self.request)

    @action(_('Send message now'), style='primary')
    def send(self, *args, **data):
        fullname = self.request.principal.title
        try:
            email = self.request.principal.email
        except AttributeError:
            email = self.config.email_admin
        username = self.request.principal.id
        usertype = getattr(self.request.principal,
                           'user_type', 'system').title()
        kofa_utils = getUtility(IKofaUtils)
        success = kofa_utils.sendContactForm(
                fullname,email,
                self.config.name_admin,self.config.email_admin,
                username,usertype,self.config.name,
                data['body'],self.config.email_subject)
        # Success is always True if sendContactForm didn't fail.
        # TODO: Catch exceptions.
        if success:
            self.flash(_('Your message has been sent.'))
        return

class EnquiriesForm(ContactAdminForm):
    """Captcha'd page to let anonymous send emails to the administrator.
    """
    grok.name('enquiries')
    grok.require('waeup.Public')
    pnav = 2
    form_fields = grok.AutoFields(IContactForm).select(
                          'fullname', 'email_from', 'body')

    def update(self):
        super(EnquiriesForm, self).update()
        # Handle captcha
        self.captcha = getUtility(ICaptchaManager).getCaptcha()
        self.captcha_result = self.captcha.verify(self.request)
        self.captcha_code = self.captcha.display(self.captcha_result.error_code)
        return

    @action(_('Send now'), style='primary')
    def send(self, *args, **data):
        if not self.captcha_result.is_valid:
            # Captcha will display error messages automatically.
            # No need to flash something.
            return
        kofa_utils = getUtility(IKofaUtils)
        success = kofa_utils.sendContactForm(
                data['fullname'],data['email_from'],
                self.config.name_admin,self.config.email_admin,
                u'None',u'Anonymous',self.config.name,
                data['body'],self.config.email_subject)
        if success:
            self.flash(_('Your message has been sent.'))
        else:
            self.flash(_('A smtp server error occurred.'), type='danger')
        return

#
# University related pages...
#

class UniversityPage(KofaDisplayFormPage):
    """ The main university page.
    """
    grok.require('waeup.Public')
    grok.name('index')
    grok.context(IUniversity)
    pnav = 0
    label = ''

    @property
    def frontpage(self):
        lang = self.request.cookies.get('kofa.language')
        html = self.context['configuration'].frontpage_dict.get(lang,'')
        if html =='':
            portal_language = getUtility(IKofaUtils).PORTAL_LANGUAGE
            html = self.context[
                'configuration'].frontpage_dict.get(portal_language,'')
        if html =='':
            return _(u'<h1>Welcome to WAeUP.Kofa</h1>')
        else:
            return html

class AdministrationPage(KofaPage):
    """ The administration overview page.
    """
    grok.name('administration')
    grok.context(IUniversity)
    grok.require('waeup.managePortal')
    label = _(u'Administration')
    pnav = 0

class RSS20Feed(grok.View):
    """An RSS 2.0 feed.
    """
    grok.name('feed.rss')
    grok.context(IUniversity)
    grok.require('waeup.Public')
    grok.template('universityrss20feed')

    name = 'General news feed'
    description = 'waeup.kofa now supports RSS 2.0 feeds :-)'
    language = None
    date = None
    buildDate = None
    editor = None
    webmaster = None

    @property
    def title(self):
        return getattr(grok.getSite(), 'name', u'Sample University')

    @property
    def contexttitle(self):
        return self.name

    @property
    def link(self):
        return self.url(grok.getSite())

    def update(self):
        self.response.setHeader('Content-Type', 'text/xml; charset=UTF-8')

    def entries(self):
        return ()

#
# User container pages...
#

class UsersContainerPage(KofaPage):
    """Overview page for all local users.
    """
    grok.require('waeup.manageUsers')
    grok.context(IUsersContainer)
    grok.name('index')
    label = _('Portal Users')
    manage_button = _(u'Manage')
    delete_button = _(u'Remove')

    def update(self, userid=None, adduser=None, manage=None, delete=None):
        if manage is not None and userid is not None:
            self.redirect(self.url(userid) + '/@@manage')
        if delete is not None and userid is not None:
            self.context.delUser(userid)
            self.flash(_('User account ${a} successfully deleted.',
                mapping = {'a':  userid}))
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            self.context.__parent__.logger.info(
                '%s - removed: %s' % (ob_class, userid))

    def getLocalRoles(self, account):
        local_roles = account.getLocalRoles()
        local_roles_string = ''
        site_url = self.url(grok.getSite())
        for local_role in local_roles.keys():
            role_title = getattr(
                dict(get_all_roles()).get(local_role, None), 'title', None)
            objects_string = ''
            for object in local_roles[local_role]:
                objects_string += '<a href="%s">%s</a>, ' %(self.url(object),
                    self.url(object).replace(site_url,''))
            local_roles_string += '%s: <br />%s <br />' %(role_title,
                objects_string.rstrip(', '))
        return local_roles_string

    def getSiteRoles(self, account):
        site_roles = account.roles
        site_roles_string = ''
        for site_role in site_roles:
            role_title = dict(get_all_roles())[site_role].title
            site_roles_string += '%s <br />' % role_title
        return site_roles_string

class AddUserFormPage(KofaAddFormPage):
    """Add a user account.
    """
    grok.require('waeup.manageUsers')
    grok.context(IUsersContainer)
    grok.name('add')
    grok.template('usereditformpage')
    form_fields = grok.AutoFields(IUserAccount)
    label = _('Add user')

    @action(_('Add user'), style='primary')
    def addUser(self, **data):
        name = data['name']
        title = data['title']
        email = data['email']
        phone = data['phone']
        description = data['description']
        #password = data['password']
        roles = data['roles']
        form = self.request.form
        password = form.get('password', None)
        password_ctl = form.get('control_password', None)
        if password:
            validator = getUtility(IPasswordValidator)
            errors = validator.validate_password(password, password_ctl)
            if errors:
                self.flash( ' '.join(errors), type='danger')
                return
        try:
            self.context.addUser(name, password, title=title, email=email,
                                 phone=phone, description=description,
                                 roles=roles)
            self.flash(_('User account ${a} successfully added.',
                mapping = {'a': name}))
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            self.context.__parent__.logger.info(
                '%s - added: %s' % (ob_class, name))
        except KeyError:
            self.status = self.flash('The userid chosen already exists '
                                  'in the database.', type='danger')
            return
        self.redirect(self.url(self.context))

class UserManageFormPage(KofaEditFormPage):
    """Manage a user account.
    """
    grok.context(IUserAccount)
    grok.name('manage')
    grok.template('usereditformpage')
    grok.require('waeup.manageUsers')
    form_fields = grok.AutoFields(IUserAccount).omit('name')

    def label(self):
        return _("Edit user ${a}", mapping = {'a':self.context.__name__})

    def setUpWidgets(self, ignore_request=False):
        super(UserManageFormPage,self).setUpWidgets(ignore_request)
        self.widgets['title'].displayWidth = 30
        self.widgets['description'].height = 3
        return

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
        changed_fields = self.applyData(self.context, **data)
        if changed_fields:
            changed_fields = reduce(lambda x,y: x+y, changed_fields.values())
        else:
            changed_fields = []
        if password:
            # Now we know that the form has no errors and can set password ...
            self.context.setPassword(password)
            changed_fields.append('password')
        fields_string = ' + '.join(changed_fields)
        if fields_string:
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            self.context.__parent__.logger.info(
                '%s - %s edited: %s' % (
                ob_class, self.context.name, fields_string))
        self.flash(_('User settings have been saved.'))
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context.__parent__))
        return

class ContactUserForm(ContactAdminForm):
    grok.name('contactuser')
    grok.context(IUserAccount)
    grok.template('contactform')
    grok.require('waeup.manageUsers')
    pnav = 0
    form_fields = grok.AutoFields(IContactForm).select('body')

    def label(self):
        return _(u'Send message to ${a}', mapping = {'a':self.context.title})

    @action(_('Send message now'), style='primary')
    def send(self, *args, **data):
        try:
            email = self.request.principal.email
        except AttributeError:
            email = self.config.email_admin
        usertype = getattr(self.request.principal,
                           'user_type', 'system').title()
        kofa_utils = getUtility(IKofaUtils)
        success = kofa_utils.sendContactForm(
                self.request.principal.title,email,
                self.context.title,self.context.email,
                self.request.principal.id,usertype,self.config.name,
                data['body'],self.config.email_subject)
        # Success is always True if sendContactForm didn't fail.
        # TODO: Catch exceptions.
        if success:
            self.flash(_('Your message has been sent.'))
        return

class UserEditFormPage(UserManageFormPage):
    """Edit a user account by user
    """
    grok.name('index')
    grok.require('waeup.editUser')
    form_fields = grok.AutoFields(IUserAccount).omit(
        'name', 'description', 'roles')
    label = _(u"My Preferences")

    def setUpWidgets(self, ignore_request=False):
        super(UserManageFormPage,self).setUpWidgets(ignore_request)
        self.widgets['title'].displayWidth = 30

class MyRolesPage(KofaPage):
    """Display site roles and local roles assigned to officers.
    """
    grok.name('my_roles')
    grok.require('waeup.editUser')
    grok.context(IUserAccount)
    grok.template('myrolespage')
    label = _(u"My Roles")

    @property
    def getLocalRoles(self):
        local_roles = get_user_account(self.request).getLocalRoles()
        local_roles_userfriendly = {}
        for local_role in local_roles:
            role_title = dict(get_all_roles())[local_role].title
            local_roles_userfriendly[role_title] = local_roles[local_role]
        return local_roles_userfriendly

    @property
    def getSiteRoles(self):
        site_roles = get_user_account(self.request).roles
        site_roles_userfriendly = []
        for site_role in site_roles:
            role_title = dict(get_all_roles())[site_role].title
            site_roles_userfriendly.append(role_title)
        return site_roles_userfriendly

#
# Search pages...
#

class SearchPage(KofaPage):
    """General search page for the academics section.
    """
    grok.context(IFacultiesContainer)
    grok.name('search')
    grok.template('searchpage')
    grok.require('waeup.viewAcademics')
    label = _(u"Search Academic Section")
    pnav = 1
    search_button = _(u'Search')

    def update(self, *args, **kw):
        form = self.request.form
        self.hitlist = []
        self.query = ''
        if not 'query' in form:
            return
        query = form['query']
        self.query = query
        self.hitlist = search(query=self.query, view=self)
        if not self.hitlist:
            self.flash(_('No object found.'), type="warning")
        return

#
# Configuration pages...
#

class ConfigurationContainerManageFormPage(KofaEditFormPage):
    """Manage page of the configuration container. We always use the
    manage page in the UI not the view page, thus we use the index name here.
    """
    grok.require('waeup.managePortalConfiguration')
    grok.name('index')
    grok.context(IConfigurationContainer)
    grok.template('configurationmanagepage')
    pnav = 0
    label = _(u'Edit portal configuration')
    taboneactions = [_('Save'), _('Update plugins')]
    tabtwoactions = [
        _('Add session configuration'),
        _('Remove selected')]
    form_fields = grok.AutoFields(IConfigurationContainer).omit(
        'frontpage_dict')

    @action(_('Save'), style='primary')
    def save(self, **data):
        msave(self, **data)
        frontpage = getattr(self.context, 'frontpage', None)
        portal_language = getUtility(IKofaUtils).PORTAL_LANGUAGE
        self.context.frontpage_dict = html2dict(frontpage, portal_language)
        return

    @action(_('Add session configuration'), validator=NullValidator,
            style='primary')
    def addSubunit(self, **data):
        self.redirect(self.url(self.context, '@@add'))
        return

    def getSessionConfigurations(self):
        """Get a list of all stored session configuration objects.
        """
        for key, val in self.context.items():
            url = self.url(val)
            session_string = val.getSessionString()
            title = _('Session ${a} Configuration',
                      mapping = {'a':session_string})
            yield(dict(url=url, name=key, title=title))

    @jsaction(_('Remove selected'))
    def delSessonConfigurations(self, **data):
        delSubobjects(self, redirect='@@index', tab='2')
        return

    @action(_('Update plugins'),
              tooltip=_('For experts only!'),
              warning=_('Plugins may only be updated after software upgrades. '
                        'Are you really sure?'),
              validator=NullValidator)
    def updatePlugins(self, **data):
        grok.getSite().updatePlugins()
        self.flash(_('Plugins were updated. See log file for details.'))
        return

class SessionConfigurationAddFormPage(KofaAddFormPage):
    """Add a session configuration object to configuration container.
    """
    grok.context(IConfigurationContainer)
    grok.name('add')
    grok.require('waeup.managePortalConfiguration')
    label = _('Add session configuration')
    form_fields = grok.AutoFields(ISessionConfigurationAdd)
    pnav = 0

    @action(_('Add Session Configuration'), style='primary')
    def addSessionConfiguration(self, **data):
        sessionconfiguration = createObject(u'waeup.SessionConfiguration')
        self.applyData(sessionconfiguration, **data)
        try:
            self.context.addSessionConfiguration(sessionconfiguration)
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            self.context.__parent__.logger.info(
                '%s - added: %s' % (
                ob_class, sessionconfiguration.academic_session))
        except KeyError:
            self.flash(_('The session chosen already exists.'), type='danger')
            return
        self.redirect(self.url(self.context, '@@index')+'#tab2')
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self):
        self.redirect(self.url(self.context, '@@index')+'#tab2')
        return

class SessionConfigurationManageFormPage(KofaEditFormPage):
    """Manage session configuration object.
    """
    grok.context(ISessionConfiguration)
    grok.name('index')
    grok.require('waeup.managePortalConfiguration')
    form_fields = grok.AutoFields(ISessionConfiguration)
    pnav = 0

    @property
    def label(self):
        session_string = self.context.getSessionString()
        return _('Edit academic session ${a} configuration',
            mapping = {'a':session_string})

    @action(_('Save'), style='primary')
    def save(self, **data):
        msave(self, **data)
        self.redirect(self.url(self.context.__parent__, '@@index')+'#tab2')
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self):
        self.redirect(self.url(self.context.__parent__, '@@index')+'#tab2')
        return

#
# Datacenter pages...
#

class DatacenterPage(KofaEditFormPage):
    grok.context(IDataCenter)
    grok.name('index')
    grok.require('waeup.manageDataCenter')
    label = _(u'Data Center')
    pnav = 0

    @jsaction(_('Remove selected'))
    def delFiles(self, **data):
        form = self.request.form
        if 'val_id' in form:
            child_id = form['val_id']
        else:
            self.flash(_('No item selected.'), type='danger')
            return
        if not isinstance(child_id, list):
            child_id = [child_id]
        deleted = []
        for id in child_id:
            fullpath = os.path.join(self.context.storage, id)
            try:
                os.remove(fullpath)
                deleted.append(id)
            except OSError:
                self.flash(_('OSError: The file could not be deleted.'),
                           type='danger')
                return
        if len(deleted):
            self.flash(_('Successfully deleted: ${a}',
                mapping = {'a': ', '.join(deleted)}))
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            self.context.logger.info(
                '%s - deleted: %s' % (ob_class, ', '.join(deleted)))
        return

class DatacenterFinishedPage(KofaEditFormPage):
    grok.context(IDataCenter)
    grok.name('processed')
    grok.require('waeup.manageDataCenter')
    label = _(u'Processed Files')
    pnav = 0
    cancel_button =_('Back to Data Center')

    def update(self, CANCEL=None):
        if CANCEL is not None:
            self.redirect(self.url(self.context))
            return
        return super(DatacenterFinishedPage, self).update()

class DatacenterUploadPage(KofaPage):
    grok.context(IDataCenter)
    grok.name('upload')
    grok.require('waeup.manageDataCenter')
    label = _(u'Upload portal data as CSV file')
    pnav = 0
    max_files = 20
    upload_button =_(u'Upload')
    cancel_button =_(u'Back to Data Center')

    def getPreviewHeader(self):
        """Get the header fields of uploaded CSV file.
        """
        reader = csv.reader(open(self.fullpath, 'rb'))
        return reader.next()

    def _notifyImportManagers(self, filename,
        normalized_filename, importer, import_mode):
        """Send email to Import Managers
        """
        # Get information about file
        self.fullpath = os.path.join(self.context.storage, normalized_filename)
        uploadfile = DataCenterFile(self.fullpath)
        self.reader = csv.DictReader(open(self.fullpath, 'rb'))
        table = getPreviewTable(self, 3)
        mail_table = ''
        for line in table:
            header = line[0]
            data = str(line[1:]).strip('[').strip(']')
            mail_table += '%s: %s ...\n' % (line[0], data)
        # Collect all recipient addresses
        kofa_utils = getUtility(IKofaUtils)
        import_managers = get_users_with_role(
            'waeup.ImportManager', grok.getSite())
        rcpt_addrs = ','.join(
            [user['user_email'] for user in import_managers if
                user['user_email'] is not None])
        if rcpt_addrs:
            config = grok.getSite()['configuration']
            fullname = self.request.principal.title
            try:
                email = self.request.principal.email
            except AttributeError:
                email = config.email_admin
            username = self.request.principal.id
            usertype = getattr(self.request.principal,
                               'user_type', 'system').title()
            rcpt_name = _('Import Manager')
            subject = translate(
                      _('${a}: ${b} uploaded',
                      mapping = {'a':config.acronym, 'b':filename}),
                      'waeup.kofa',
                      target_language=kofa_utils.PORTAL_LANGUAGE)
            text = _("""File: ${a}
Importer: ${b}
Import Mode: ${c}
Datasets: ${d}

${e}

Comment by Import Manager:""", mapping = {'a':normalized_filename,
                'b':importer,
                'c':import_mode,
                'd':uploadfile.lines - 1,
                'e':mail_table})
            success = kofa_utils.sendContactForm(
                    fullname,email,
                    rcpt_name,rcpt_addrs,
                    username,usertype,config.name,
                    text,subject)
            if success:
                self.flash(
                    _('All import managers have been notified by email.'))
            else:
                self.flash(_('An smtp server error occurred.'), type='danger')
            return

    def update(self, uploadfile=None, import_mode=None,
               importer=None, CANCEL=None, SUBMIT=None):
        number_of_pendings = len(self.context.getPendingFiles())
        if number_of_pendings > self.max_files:
            self.flash(
                _('Maximum number of files in the data center exceeded.'),
                  type='danger')
            self.redirect(self.url(self.context))
            return
        if CANCEL is not None:
            self.redirect(self.url(self.context))
            return
        if not uploadfile:
            return
        try:
            filename = uploadfile.filename
            #if 'pending' in filename:
            #    self.flash(_("You can't re-upload pending data files."), type='danger')
            #    return
            if not filename.endswith('.csv'):
                self.flash(_("Only csv files are allowed."), type='danger')
                return
            normalized_filename = self.getNormalizedFileName(filename)
            finished_file = os.path.join(
                self.context.storage, 'finished', normalized_filename)
            unfinished_file = os.path.join(
                self.context.storage, 'unfinished', normalized_filename)
            if os.path.exists(finished_file) or os.path.exists(unfinished_file):
                self.flash(_("File with same name was uploaded earlier."),
                           type='danger')
                return
            target = os.path.join(self.context.storage, normalized_filename)
            filecontent = uploadfile.read()
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            logger = self.context.logger

            # Forbid certain characters in import files.
            invalid_line = check_csv_charset(filecontent.splitlines())
            if invalid_line:
                self.flash(_(
                    "Your file contains forbidden characters or "
                    "has invalid CSV format. "
                    "First problematic line detected: line %s. "
                    "Please replace." % invalid_line), type='danger')
                logger.info('%s - invalid file uploaded: %s' %
                            (ob_class, target))
                return

            open(target, 'wb').write(filecontent)
            os.chmod(target, 0664)
            logger.info('%s - uploaded: %s' % (ob_class, target))
            self._notifyImportManagers(filename,
                normalized_filename, importer, import_mode)

        except IOError:
            self.flash('Error while uploading file. Please retry.', type='danger')
            self.flash('I/O error: %s' % sys.exc_info()[1], type='danger')
            return
        self.redirect(self.url(self.context))

    def getNormalizedFileName(self, filename):
        """Build sane filename.

        An uploaded file foo.csv will be stored as foo_USERNAME.csv
        where username is the principal id of the currently logged in
        user.

        Spaces in filename are replaced by underscore.
        Pending data filenames remain unchanged.
        """
        if filename.endswith('.pending.csv'):
            return filename
        username = self.request.principal.id
        filename = filename.replace(' ', '_')
        # Only accept typical filname chars...
        filtered_username = ''.join(re.findall('[a-zA-Z0-9_\.\-]', username))
        base, ext = os.path.splitext(filename)
        return '%s_%s%s' % (base, filtered_username, ext.lower())

    def getImporters(self):
        importers = getAllUtilitiesRegisteredFor(IBatchProcessor)
        importer_props = []
        for x in importers:
            iface_fields = schema.getFields(x.iface)
            available_fields = []
            for key in iface_fields.keys():
                iface_fields[key] = (iface_fields[key].__class__.__name__,
                    iface_fields[key].required)
            for value in x.available_fields:
                available_fields.append(
                    dict(f_name=value,
                         f_type=iface_fields.get(value, (None, False))[0],
                         f_required=iface_fields.get(value, (None, False))[1]
                         )
                    )
            available_fields = sorted(available_fields, key=lambda k: k['f_name'])
            importer_props.append(
                dict(title=x.name, name=x.util_name, fields=available_fields))
        return sorted(importer_props, key=lambda k: k['title'])

class FileDownloadView(UtilityView, grok.View):
    grok.context(IDataCenter)
    grok.name('download')
    grok.require('waeup.manageDataCenter')

    def update(self, filename=None):
        self.filename = self.request.form['filename']
        return

    def render(self):
        ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
        self.context.logger.info(
            '%s - downloaded: %s' % (ob_class, self.filename))
        self.response.setHeader(
            'Content-Type', 'text/csv; charset=UTF-8')
        self.response.setHeader(
            'Content-Disposition:', 'attachment; filename="%s' %
            self.filename.replace('finished/',''))
        fullpath = os.path.join(self.context.storage, self.filename)
        return open(fullpath, 'rb').read()

class SkeletonDownloadView(UtilityView, grok.View):
    grok.context(IDataCenter)
    grok.name('skeleton')
    grok.require('waeup.manageDataCenter')

    def update(self, processorname=None):
        self.processorname = self.request.form['name']
        self.filename = ('%s_000.csv' %
            self.processorname.replace('processor','import'))
        return

    def render(self):
        #ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
        #self.context.logger.info(
        #    '%s - skeleton downloaded: %s' % (ob_class, self.filename))
        self.response.setHeader(
            'Content-Type', 'text/csv; charset=UTF-8')
        self.response.setHeader(
            'Content-Disposition:', 'attachment; filename="%s' % self.filename)
        processor = getUtility(IBatchProcessor, name=self.processorname)
        csv_data = processor.get_csv_skeleton()
        return csv_data

class DatacenterImportStep1(KofaPage):
    """Manual import step 1: choose file
    """
    grok.context(IDataCenter)
    grok.name('import1')
    grok.template('datacenterimport1page')
    grok.require('waeup.manageDataCenter')
    label = _(u'Process CSV file')
    pnav = 0
    cancel_button =_(u'Back to Data Center')

    def getFiles(self):
        files = self.context.getPendingFiles(sort='date')
        for file in files:
            name = file.name
            if not name.endswith('.csv') and not name.endswith('.pending'):
                continue
            yield file

    def update(self, filename=None, select=None, cancel=None):
        if cancel is not None:
            self.redirect(self.url(self.context))
            return
        if select is not None:
            # A filename was selected
            session = ISession(self.request)['waeup.kofa']
            session['import_filename'] = select
            self.redirect(self.url(self.context, '@@import2'))

class DatacenterImportStep2(KofaPage):
    """Manual import step 2: choose processor
    """
    grok.context(IDataCenter)
    grok.name('import2')
    grok.template('datacenterimport2page')
    grok.require('waeup.manageDataCenter')
    label = _(u'Process CSV file')
    pnav = 0
    cancel_button =_(u'Cancel')
    back_button =_(u'Back to step 1')
    proceed_button =_(u'Proceed to step 3')

    filename = None
    mode = 'create'
    importer = None
    mode_locked = False

    def getPreviewHeader(self):
        """Get the header fields of attached CSV file.
        """
        reader = csv.reader(open(self.fullpath, 'rb'))
        return reader.next()

    def getPreviewTable(self):
        return getPreviewTable(self, 3)

    def getImporters(self):
        importers = getAllUtilitiesRegisteredFor(IBatchProcessor)
        importers = sorted(
            [dict(title=x.name, name=x.util_name) for x in importers])
        return importers

    def getModeFromFilename(self, filename):
        """Lookup filename or path and return included mode name or None.
        """
        if not filename.endswith('.pending.csv'):
            return None
        base = os.path.basename(filename)
        parts = base.rsplit('.', 3)
        if len(parts) != 4:
            return None
        if parts[1] not in ['create', 'update', 'remove']:
            return None
        return parts[1]

    def getWarnings(self):
        import sys
        result = []
        try:
            headerfields = self.getPreviewHeader()
            headerfields_clean = list(set(headerfields))
            if len(headerfields) > len(headerfields_clean):
                result.append(
                    _("Double headers: each column name may only appear once. "))
        except:
            fatal = '%s' % sys.exc_info()[1]
            result.append(fatal)
        if result:
            warnings = ""
            for line in result:
                warnings += line + '<br />'
            warnings += _('Replace imported file!')
            return warnings
        return False

    def update(self, mode=None, importer=None,
               back1=None, cancel=None, proceed=None):
        session = ISession(self.request)['waeup.kofa']
        self.filename = session.get('import_filename', None)

        if self.filename is None or back1 is not None:
            self.redirect(self.url(self.context, '@@import1'))
            return
        if cancel is not None:
            self.flash(_('Import aborted.'), type='warning')
            self.redirect(self.url(self.context))
            return
        self.mode = mode or session.get('import_mode', self.mode)
        filename_mode = self.getModeFromFilename(self.filename)
        if filename_mode is not None:
            self.mode = filename_mode
            self.mode_locked = True
        self.importer = importer or session.get('import_importer', None)
        session['import_importer'] = self.importer
        if self.importer and 'update' in self.importer:
            if self.mode != 'update':
                self.flash(_('Update mode only!'), type='warning')
                self.mode_locked = True
                self.mode = 'update'
                proceed = None
        session['import_mode'] = self.mode
        if proceed is not None:
            self.redirect(self.url(self.context, '@@import3'))
            return
        self.fullpath = os.path.join(self.context.storage, self.filename)
        warnings = self.getWarnings()
        if not warnings:
            self.reader = csv.DictReader(open(self.fullpath, 'rb'))
        else:
            self.reader = ()
            self.flash(warnings, type='warning')

class DatacenterImportStep3(KofaPage):
    """Manual import step 3: modify header
    """
    grok.context(IDataCenter)
    grok.name('import3')
    grok.template('datacenterimport3page')
    grok.require('waeup.manageDataCenter')
    label = _(u'Process CSV file')
    pnav = 0
    cancel_button =_(u'Cancel')
    reset_button =_(u'Reset')
    update_button =_(u'Set headerfields')
    back_button =_(u'Back to step 2')
    proceed_button =_(u'Perform import')

    filename = None
    mode = None
    importername = None

    @property
    def nextstep(self):
        return self.url(self.context, '@@import4')

    def getPreviewHeader(self):
        """Get the header fields of attached CSV file.
        """
        reader = csv.reader(open(self.fullpath, 'rb'))
        return reader.next()

    def getPreviewTable(self):
        """Get transposed table with 1 sample record.

        The first column contains the headers.
        """
        if not self.reader:
            return
        headers = self.getPreviewHeader()
        num = 0
        data = []
        for line in self.reader:
            if num > 0:
                break
            num += 1
            data.append(line)
        result = []
        field_num = 0
        for name in headers:
            result_line = []
            result_line.append(field_num)
            field_num += 1
            for d in data:
                result_line.append(d[name])
            result.append(result_line)
        return result

    def getPossibleHeaders(self):
        """Get the possible headers.

        The headers are described as dicts {value:internal_name,
        title:displayed_name}
        """
        result = [dict(title='<IGNORE COL>', value='--IGNORE--')]
        headers = self.importer.getHeaders()
        result.extend([dict(title=x, value=x) for x in headers])
        return result

    def getWarnings(self):
        import sys
        result = []
        try:
            self.importer.checkHeaders(self.headerfields, mode=self.mode)
        except:
            fatal = '%s' % sys.exc_info()[1]
            result.append(fatal)
        if result:
            warnings = ""
            for line in result:
                warnings += line + '<br />'
            warnings += _('Edit headers or replace imported file!')
            return warnings
        return False

    def update(self, headerfield=None, back2=None, cancel=None, proceed=None):
        session = ISession(self.request)['waeup.kofa']
        self.filename = session.get('import_filename', None)
        self.mode = session.get('import_mode', None)
        self.importername = session.get('import_importer', None)

        if None in (self.filename, self.mode, self.importername):
            self.redirect(self.url(self.context, '@@import2'))
            return
        if back2 is not None:
            self.redirect(self.url(self.context ,'@@import2'))
            return
        if cancel is not None:
            self.flash(_('Import aborted.'), type='warning')
            self.redirect(self.url(self.context))
            return

        self.fullpath = os.path.join(self.context.storage, self.filename)
        self.headerfields = headerfield or self.getPreviewHeader()
        session['import_headerfields'] = self.headerfields

        if proceed is not None:
            self.redirect(self.url(self.context, '@@import4'))
            return
        self.importer = getUtility(IBatchProcessor, name=self.importername)
        self.reader = csv.DictReader(open(self.fullpath, 'rb'))
        warnings = self.getWarnings()
        if warnings:
            self.flash(warnings, type='warning')

class DatacenterImportStep4(KofaPage):
    """Manual import step 4: do actual import
    """
    grok.context(IDataCenter)
    grok.name('import4')
    grok.template('datacenterimport4page')
    grok.require('waeup.importData')
    label = _(u'Process CSV file')
    pnav = 0
    back_button =_(u'Process next')

    filename = None
    mode = None
    importername = None
    headerfields = None
    warnnum = None

    def update(self, back=None, finish=None, showlog=None):
        if finish is not None:
            self.redirect(self.url(self.context, '@@import1'))
            return
        session = ISession(self.request)['waeup.kofa']
        self.filename = session.get('import_filename', None)
        self.mode = session.get('import_mode', None)
        self.importername = session.get('import_importer', None)
        # If the import file contains only one column
        # the import_headerfields attribute is a string.
        ihf = session.get('import_headerfields', None)
        if not isinstance(ihf, list):
            self.headerfields = ihf.split()
        else:
            self.headerfields = ihf

        if None in (self.filename, self.mode, self.importername,
                    self.headerfields):
            self.redirect(self.url(self.context, '@@import3'))
            return

        if showlog is not None:
            logfilename = "datacenter.log"
            session['logname'] = logfilename
            self.redirect(self.url(self.context, '@@show'))
            return

        self.fullpath = os.path.join(self.context.storage, self.filename)
        self.importer = getUtility(IBatchProcessor, name=self.importername)

        # Perform batch processing...
        # XXX: This might be better placed in datacenter module.
        (linenum, self.warn_num,
         fin_path, pending_path) = self.importer.doImport(
            self.fullpath, self.headerfields, self.mode,
            self.request.principal.id, logger=self.context.logger)
        # Put result files in desired locations...
        self.context.distProcessedFiles(
            self.warn_num == 0, self.fullpath, fin_path, pending_path,
            self.mode)

        if self.warn_num:
            self.flash(_('Processing of ${a} rows failed.',
                mapping = {'a':self.warn_num}), type='warning')
        self.flash(_('Successfully processed ${a} rows.',
            mapping = {'a':linenum - self.warn_num}))

class DatacenterLogsOverview(KofaPage):
    grok.context(IDataCenter)
    grok.name('logs')
    grok.template('datacenterlogspage')
    grok.require('waeup.manageDataCenter')
    label = _(u'Show logfiles')
    pnav = 0
    back_button = _(u'Back to Data Center')
    show_button = _(u'Show')

    def update(self, back=None):
        if back is not None:
            self.redirect(self.url(self.context))
            return
        self.files = self.context.getLogFiles()

class DatacenterLogsFileview(KofaPage):
    grok.context(IDataCenter)
    grok.name('show')
    grok.template('datacenterlogsshowfilepage')
    grok.require('waeup.manageDataCenter')
    title = _(u'Data Center')
    pnav = 0
    search_button = _('Search')
    back_button = _('Back to Data Center')
    placeholder = _('Enter a regular expression here...')

    def label(self):
        return "Logfile %s" % self.filename

    def update(self, back=None, query=None, logname=None):
        if os.name != 'posix':
            self.flash(
                _('Log files can only be searched ' +
                  'on Unix-based operating systems.'), type='danger')
            self.redirect(self.url(self.context, '@@logs'))
            return
        if back is not None or logname is None:
            self.redirect(self.url(self.context, '@@logs'))
            return
        self.filename = logname
        self.query = query
        if not query:
            return
        try:
            self.result = ''.join(
                self.context.queryLogfiles(logname, query))
        except ValueError:
            self.flash(_('Invalid search expression.'), type='danger')
            return
        if not self.result:
            self.flash(_('No search results found.'), type='warning')
        return

class DatacenterSettings(KofaPage):
    grok.context(IDataCenter)
    grok.name('manage')
    grok.template('datacentermanagepage')
    grok.require('waeup.managePortal')
    label = _('Edit data center settings')
    pnav = 0
    save_button =_(u'Save')
    reset_button =_(u'Reset')
    cancel_button =_(u'Back to Data Center')

    def update(self, newpath=None, move=False, overwrite=False,
               save=None, cancel=None):
        if move:
            move = True
        if overwrite:
            overwrite = True
        if newpath is None:
            return
        if cancel is not None:
            self.redirect(self.url(self.context))
            return
        try:
            not_copied = self.context.setStoragePath(newpath, move=move)
            for name in not_copied:
                self.flash(_('File already existed (not copied): ${a}',
                    mapping = {'a':name}), type='danger')
        except:
            self.flash(_('Given storage path cannot be used. ${a}',
                        mapping = {'a':sys.exc_info()[1]}), type='danger')
            return
        if newpath:
            self.flash(_('New storage path succefully set.'))
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            self.context.logger.info(
                '%s - storage path set: %s' % (ob_class, newpath))
            self.redirect(self.url(self.context))
        return

class ExportCSVPage(KofaPage):
    grok.context(IDataCenter)
    grok.name('export')
    grok.template('datacenterexportpage')
    grok.require('waeup.exportData')
    label = _('Download portal data as CSV file')
    pnav = 0
    export_button = _(u'Create CSV file')
    cancel_button =_(u'Back to Data Center')

    def getExporters(self):
        utils = getUtilitiesFor(ICSVExporter)
        STUDENT_EXPORTER_NAMES = getUtility(
            IStudentsUtils).STUDENT_EXPORTER_NAMES
        title_name_tuples = [
            (util.title, name) for name, util in utils
            if not name in STUDENT_EXPORTER_NAMES]
        # The exporter for access codes requires a special permission.
        if not checkPermission('waeup.manageACBatches', self.context):
            title_name_tuples.remove((u'Access Codes', u'accesscodes'))
        return sorted(title_name_tuples)

    def update(self, CREATE=None, DISCARD=None, exporter=None,
               job_id=None, CANCEL=None):
        if CANCEL is not None:
            self.redirect(self.url(self.context))
            return
        if CREATE:
            job_id = self.context.start_export_job(
                exporter, self.request.principal.id)
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            self.context.logger.info(
                '%s - exported: %s, job_id=%s' % (ob_class, exporter, job_id))
        if DISCARD and job_id:
            entry = self.context.entry_from_job_id(job_id)
            self.context.delete_export_entry(entry)
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            self.context.logger.info(
                '%s - discarded: job_id=%s' % (ob_class, job_id))
            self.flash(_('Discarded export') + ' %s' % job_id)
        self.entries = doll_up(self, user=None)
        return

class ExportCSVView(grok.View):
    grok.context(IDataCenter)
    grok.name('download_export')
    grok.require('waeup.exportData')

    def render(self, job_id=None):
        manager = getUtility(IJobManager)
        job = manager.get(job_id)
        if job is None:
            return
        if hasattr(job.result, 'traceback'):
            # XXX: Some error happened. Do something more approriate here...
            return
        path = job.result
        if not os.path.exists(path):
            # XXX: Do something more appropriate here...
            return
        result = open(path, 'rb').read()
        acronym = grok.getSite()['configuration'].acronym.replace(' ','')
        filename = "%s_%s" % (acronym, os.path.basename(path))
        filename = filename.replace('.csv', '_%s.csv' % job_id)
        self.response.setHeader(
            'Content-Type', 'text/csv; charset=UTF-8')
        self.response.setHeader(
            'Content-Disposition', 'attachment; filename="%s' % filename)
        # remove job and running_exports entry from context
        #self.context.delete_export_entry(
        #    self.context.entry_from_job_id(job_id))
        ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
        self.context.logger.info(
            '%s - downloaded: %s, job_id=%s' % (ob_class, filename, job_id))
        return result

class ExportXMLPage(grok.View):
    """Deliver an XML representation of the context.
    """
    grok.name('export.xml')
    grok.require('waeup.managePortal')

    def render(self):
        exporter = IKofaXMLExporter(self.context)
        xml = exporter.export().read()
        self.response.setHeader(
            'Content-Type', 'text/xml; charset=UTF-8')
        return xml

class ImportXMLPage(KofaPage):
    """Replace the context object by an object created from an XML
       representation.

       XXX: This does not work for ISite objects, i.e. for instance
            for complete University objects.
    """
    grok.name('importxml')
    grok.require('waeup.managePortal')

    def update(self, xmlfile=None, CANCEL=None, SUBMIT=None):
        if CANCEL is not None:
            self.redirect(self.url(self.context))
            return
        if not xmlfile:
            return
        importer = IKofaXMLImporter(self.context)
        obj = importer.doImport(xmlfile)
        if type(obj) != type(self.context):
            return
        parent = self.context.__parent__
        name = self.context.__name__
        self.context = obj
        if hasattr(parent, name):
            setattr(parent, name, obj)
        else:
            del parent[name]
            parent[name] = obj
            pass
        return


#
# FacultiesContainer pages...
#

class FacultiesContainerPage(KofaPage):
    """ Index page for faculty containers.
    """
    grok.context(IFacultiesContainer)
    grok.require('waeup.viewAcademics')
    grok.name('index')
    label = _('Academic Section')
    pnav = 1
    grok.template('facultypage')

class FacultiesContainerManageFormPage(KofaEditFormPage):
    """Manage the basic properties of a `Faculty` instance.
    """
    grok.context(IFacultiesContainer)
    grok.name('manage')
    grok.require('waeup.manageAcademics')
    grok.template('facultiescontainermanagepage')
    pnav = 1
    taboneactions = [_('Add faculty'), _('Remove selected'),_('Cancel')]
    subunits = _('Faculties')

    @property
    def label(self):
        return _('Manage academic section')

    @jsaction(_('Remove selected'))
    def delFaculties(self, **data):
        if not checkPermission('waeup.managePortal', self.context):
            self.flash(_('You are not allowed to remove entire faculties.'),
                       type='warning')
            return
        delSubobjects(self, redirect='@@manage', tab='1')
        return

    @action(_('Add faculty'), validator=NullValidator)
    def addFaculty(self, **data):
        self.redirect(self.url(self.context, '@@add'))
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context))
        return


class FacultyAddFormPage(KofaAddFormPage):
    """ Page form to add a new faculty to a faculty container.
    """
    grok.context(IFacultiesContainer)
    grok.require('waeup.manageAcademics')
    grok.name('add')
    label = _('Add faculty')
    form_fields = grok.AutoFields(IFaculty)
    pnav = 1

    @action(_('Add faculty'), style='primary')
    def addFaculty(self, **data):
        faculty = createObject(u'waeup.Faculty')
        self.applyData(faculty, **data)
        try:
            self.context.addFaculty(faculty)
        except KeyError:
            self.flash(_('The faculty code chosen already exists.'),
                       type='danger')
            return
        self.flash(
            _("Faculty ${a} added.", mapping = {'a':data['code']}))
        ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
        self.context.__parent__.logger.info(
            '%s - added: %s' % (ob_class, faculty.code))
        self.redirect(self.url(self.context, u'@@manage')+'#tab1')
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context))

#
# Faculty pages
#
class FacultyPage(KofaPage):
    """Index page of faculties.
    """
    grok.context(IFaculty)
    grok.require('waeup.viewAcademics')
    grok.name('index')
    pnav = 1

    @property
    def label(self):
        return _('Departments')

class FacultyManageFormPage(KofaEditFormPage,
                            LocalRoleAssignmentUtilityView):
    """Manage the basic properties of a `Faculty` instance.
    """
    grok.context(IFaculty)
    grok.name('manage')
    grok.require('waeup.manageAcademics')
    grok.template('facultymanagepage')
    pnav = 1
    subunits = _('Departments')
    taboneactions = [_('Save'),_('Cancel')]
    tabtwoactions = [_('Add department'), _('Remove selected'),_('Cancel')]
    tabthreeactions1 = [_('Remove selected local roles')]
    tabthreeactions2 = [_('Add local role')]

    form_fields = grok.AutoFields(IFaculty).omit('code')

    @property
    def label(self):
        return _('Manage faculty')

    @jsaction(_('Remove selected'))
    def delDepartments(self, **data):
        if not checkPermission('waeup.managePortal', self.context):
            self.flash(_('You are not allowed to remove entire departments.'),
                       type='danger')
            return
        delSubobjects(self, redirect='@@manage', tab='2')
        return

    @action(_('Save'), style='primary')
    def save(self, **data):
        return msave(self, **data)

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context))
        return

    @action(_('Add department'), validator=NullValidator)
    def addSubunit(self, **data):
        self.redirect(self.url(self.context, '@@add'))
        return

    @action(_('Add local role'), validator=NullValidator)
    def addLocalRole(self, **data):
        return add_local_role(self,3,**data)

    @action(_('Remove selected local roles'))
    def delLocalRoles(self, **data):
        return del_local_roles(self,3,**data)

class FindStudentsPage(KofaPage):
    """Search students in faculty.
    """
    grok.context(IFaculty)
    grok.name('find_students')
    grok.require('waeup.showStudents')
    grok.template('findstudentspage')
    search_button = _('Find student(s)')
    pnav = 1

    @property
    def label(self):
        return _('Find students in ') + ('%s' % self.context.longtitle)

    def _find_students(self,query=None, searchtype=None, view=None):
        hitlist = []
        if searchtype in ('fullname',):
            results = Query().searchResults(
                Text(('students_catalog', searchtype), query) &
                Eq(('students_catalog', 'faccode'), self.context.code)
                )
        else:
            results = Query().searchResults(
                Eq(('students_catalog', searchtype), query) &
                Eq(('students_catalog', 'faccode'), self.context.code)
                )
        for result in results:
            hitlist.append(StudentQueryResultItem(result, view=view))
        return hitlist

    def update(self, *args, **kw):
        form = self.request.form
        self.hitlist = []
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
        self.hitlist = self._find_students(query=self.searchterm,
            searchtype=self.searchtype, view=self)
        if not self.hitlist:
            self.flash(_('No student found.'), type='warning')
        return

class DepartmentAddFormPage(KofaAddFormPage):
    """Add a department to a faculty.
    """
    grok.context(IFaculty)
    grok.name('add')
    grok.require('waeup.manageAcademics')
    label = _('Add department')
    form_fields = grok.AutoFields(IDepartment)
    pnav = 1

    @action(_('Add department'), style='primary')
    def addDepartment(self, **data):
        department = createObject(u'waeup.Department')
        self.applyData(department, **data)
        try:
            self.context.addDepartment(department)
        except KeyError:
            self.flash(_('The code chosen already exists in this faculty.'),
                       type='danger')
            return
        self.flash(
            _("Department ${a} added.", mapping = {'a':data['code']}))
        ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
        self.context.__parent__.__parent__.logger.info(
            '%s - added: %s' % (ob_class, data['code']))
        self.redirect(self.url(self.context, u'@@manage')+'#tab2')
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context))
        return

#
# Department pages
#
class DepartmentPage(KofaPage):
    """Department index page.
    """
    grok.context(IDepartment)
    grok.require('waeup.viewAcademics')
    grok.name('index')
    pnav = 1
    label = _('Courses and Certificates')

    def update(self):
        super(DepartmentPage, self).update()
        return

    def getCourses(self):
        """Get a list of all stored courses.
        """
        for key, val in self.context.courses.items():
            url = self.url(val)
            yield(dict(url=url, name=key, container=val))

    def getCertificates(self):
        """Get a list of all stored certificates.
        """
        for key, val in self.context.certificates.items():
            url = self.url(val)
            yield(dict(url=url, name=key, container=val))

class DepartmentManageFormPage(KofaEditFormPage,
                               LocalRoleAssignmentUtilityView):
    """Manage the basic properties of a `Department` instance.
    """
    grok.context(IDepartment)
    grok.name('manage')
    grok.require('waeup.manageAcademics')
    pnav = 1
    grok.template('departmentmanagepage')
    taboneactions = [_('Save'),_('Cancel')]
    tabtwoactions = [_('Add course'), _('Remove selected courses'),_('Cancel')]
    tabthreeactions = [_('Add certificate'), _('Remove selected certificates'),
                       _('Cancel')]
    tabfouractions1 = [_('Remove selected local roles')]
    tabfouractions2 = [_('Add local role')]

    form_fields = grok.AutoFields(IDepartment).omit('code')

    @property
    def label(self):
        return _('Manage department')

    def getCourses(self):
        """Get a list of all stored courses.
        """
        for key, val in self.context.courses.items():
            url = self.url(val)
            yield(dict(url=url, name=key, container=val))

    def getCertificates(self):
        """Get a list of all stored certificates.
        """
        for key, val in self.context.certificates.items():
            url = self.url(val)
            yield(dict(url=url, name=key, container=val))

    @action(_('Save'), style='primary')
    def save(self, **data):
        return msave(self, **data)

    @jsaction(_('Remove selected courses'))
    def delCourses(self, **data):
        delSubobjects(
            self, redirect='@@manage', tab='2', subcontainer='courses')
        return

    @jsaction(_('Remove selected certificates'))
    def delCertificates(self, **data):
        if not checkPermission('waeup.managePortal', self.context):
            self.flash(_('You are not allowed to remove certificates.'),
                       type='warning')
            return
        delSubobjects(
            self, redirect='@@manage', tab='3', subcontainer='certificates')
        return

    @action(_('Add course'), validator=NullValidator)
    def addCourse(self, **data):
        self.redirect(self.url(self.context, 'addcourse'))
        return

    @action(_('Add certificate'), validator=NullValidator)
    def addCertificate(self, **data):
        self.redirect(self.url(self.context, 'addcertificate'))
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context))
        return

    @action(_('Add local role'), validator=NullValidator)
    def addLocalRole(self, **data):
        return add_local_role(self,4,**data)

    @action(_('Remove selected local roles'))
    def delLocalRoles(self, **data):
        return del_local_roles(self,4,**data)

class CourseAddFormPage(KofaAddFormPage):
    """Add-form to add course to a department.
    """
    grok.context(IDepartment)
    grok.name('addcourse')
    grok.require('waeup.manageAcademics')
    label = _(u'Add course')
    form_fields = grok.AutoFields(ICourse)
    pnav = 1

    @action(_('Add course'))
    def addCourse(self, **data):
        course = createObject(u'waeup.Course')
        self.applyData(course, **data)
        try:
            self.context.courses.addCourse(course)
        except DuplicationError, error:
            # signals duplication error
            entries = error.entries
            for entry in entries:
                # do not use error.msg but render a more detailed message instead
                # and show links to all certs with same code
                message = _('A course with same code already exists: ')
                message += '<a href="%s">%s</a>' % (
                    self.url(entry), getattr(entry, '__name__', u'Unnamed'))
                self.flash(message, type='warning')
            self.redirect(self.url(self.context, u'@@addcourse'))
            return
        message = _(u'Course ${a} successfully created.', mapping = {'a':course.code})
        self.flash(message)
        ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
        self.context.__parent__.__parent__.__parent__.logger.info(
            '%s - added: %s' % (ob_class, data['code']))
        self.redirect(self.url(self.context, u'@@manage')+'#tab2')
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context))
        return

class CertificateAddFormPage(KofaAddFormPage):
    """Add-form to add certificate to a department.
    """
    grok.context(IDepartment)
    grok.name('addcertificate')
    grok.require('waeup.manageAcademics')
    label = _(u'Add certificate')
    form_fields = grok.AutoFields(ICertificate)
    pnav = 1

    @action(_('Add certificate'))
    def addCertificate(self, **data):
        certificate = createObject(u'waeup.Certificate')
        self.applyData(certificate, **data)
        try:
            self.context.certificates.addCertificate(certificate)
        except DuplicationError, error:
            # signals duplication error
            entries = error.entries
            for entry in entries:
                # do not use error.msg but render a more detailed message instead
                # and show links to all certs with same code
                message = _('A certificate with same code already exists: ')
                message += '<a href="%s">%s</a>' % (
                    self.url(entry), getattr(entry, '__name__', u'Unnamed'))
                self.flash(message, type='warning')
            self.redirect(self.url(self.context, u'@@addcertificate'))
            return
        message = _(u'Certificate ${a} successfully created.', mapping = {'a':certificate.code})
        self.flash(message)
        ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
        self.context.__parent__.__parent__.__parent__.logger.info(
            '%s - added: %s' % (ob_class, data['code']))
        self.redirect(self.url(self.context, u'@@manage')+'#tab3')
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self): #, **data):
        self.redirect(self.url(self.context))
        return

#
# Courses pages
#
class CoursePage(KofaDisplayFormPage):
    """Course index page.
    """
    grok.context(ICourse)
    grok.name('index')
    grok.require('waeup.viewAcademics')
    pnav = 1
    form_fields = grok.AutoFields(ICourse)

    @property
    def label(self):
        return '%s (%s)' % (self.context.title, self.context.code)

class CourseManageFormPage(KofaEditFormPage,
                           LocalRoleAssignmentUtilityView):
    """Edit form page for courses.
    """
    grok.context(ICourse)
    grok.name('manage')
    grok.require('waeup.manageAcademics')
    grok.template('coursemanagepage')
    label = _(u'Edit course')
    pnav = 1
    taboneactions = [_('Save'),_('Cancel')]
    tabtwoactions1 = [_('Remove selected local roles')]
    tabtwoactions2 = [_('Add local role')]

    form_fields = grok.AutoFields(ICourse).omit('code')

    @action(_('Save'), style='primary')
    def save(self, **data):
        return msave(self, **data)

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context))
        return

    @action(_('Add local role'), validator=NullValidator)
    def addLocalRole(self, **data):
        return add_local_role(self,2,**data)

    @action(_('Remove selected local roles'))
    def delLocalRoles(self, **data):
        return del_local_roles(self,2,**data)

#
# Certificate pages
#
class CertificatePage(KofaDisplayFormPage):
    """Index page for certificates.
    """
    grok.context(ICertificate)
    grok.name('index')
    grok.require('waeup.viewAcademics')
    pnav = 1
    form_fields = grok.AutoFields(ICertificate)
    grok.template('certificatepage')

    @property
    def label(self):
        return "%s (%s)" % (self.context.title, self.context.code)

    def update(self):
        return super(CertificatePage, self).update()

class CertificateManageFormPage(KofaEditFormPage,
                                LocalRoleAssignmentUtilityView):
    """Manage the properties of a `Certificate` instance.
    """
    grok.context(ICertificate)
    grok.name('manage')
    grok.require('waeup.manageAcademics')
    pnav = 1
    label = _('Edit certificate')

    form_fields = grok.AutoFields(ICertificate).omit('code')

    pnav = 1
    grok.template('certificatemanagepage')
    taboneactions = [_('Save'),_('Cancel')]
    tabtwoactions = [_('Add certificate course'),
                     _('Remove selected certificate courses'),_('Cancel')]
    tabthreeactions1 = [_('Remove selected local roles')]
    tabthreeactions2 = [_('Add local role')]

    @property
    def label(self):
        return _('Manage certificate')

    @action(_('Save'), style='primary')
    def save(self, **data):
        return msave(self, **data)

    @jsaction(_('Remove selected certificate courses'))
    def delCertificateCourses(self, **data):
        delSubobjects(self, redirect='@@manage', tab='2')
        return

    @action(_('Add certificate course'), validator=NullValidator)
    def addCertificateCourse(self, **data):
        self.redirect(self.url(self.context, 'addcertificatecourse'))
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context))
        return

    @action(_('Add local role'), validator=NullValidator)
    def addLocalRole(self, **data):
        return add_local_role(self,3,**data)

    @action(_('Remove selected local roles'))
    def delLocalRoles(self, **data):
        return del_local_roles(self,3,**data)


class CertificateCourseAddFormPage(KofaAddFormPage):
    """Add-page to add a course ref to a certificate
    """
    grok.context(ICertificate)
    grok.name('addcertificatecourse')
    grok.require('waeup.manageAcademics')
    form_fields = grok.AutoFields(ICertificateCourse)
    pnav = 1
    label = _('Add certificate course')

    @action(_('Add certificate course'))
    def addCertcourse(self, **data):
        try:
            self.context.addCertCourse(**data)
        except KeyError:
            self.status = self.flash(_('The chosen certificate course is already '
                                  'part of this certificate.'), type='warning')
            return
        self.status = self.flash(
            _("certificate course ${a}_${b} added.",
            mapping = {'a': data['course'].code, 'b': data['level']}))
        code = "%s_%s" % (data['course'].code, data['level'])
        ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
        grok.getSite().logger.info('%s - added: %s' % (ob_class, code))
        self.redirect(self.url(self.context, u'@@manage')+'#tab2')
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context))
        return


#
# Certificate course pages...
#
class CertificateCoursePage(KofaPage):
    """CertificateCourse index page.
    """
    grok.context(ICertificateCourse)
    grok.name('index')
    grok.require('waeup.viewAcademics')
    pnav = 1
    #form_fields = grok.AutoFields(ICertificateCourse)

    @property
    def label(self):
        return '%s' % (self.context.longtitle)

    @property
    def leveltitle(self):
        return course_levels.getTerm(self.context.level).title

class CertificateCourseManageFormPage(KofaEditFormPage):
    """Manage the basic properties of a `CertificateCourse` instance.
    """
    grok.context(ICertificateCourse)
    grok.name('manage')
    grok.require('waeup.manageAcademics')
    form_fields = grok.AutoFields(ICertificateCourse).omit('code')
    label = _('Edit certificate course')
    pnav = 1

    @action(_('Save and return'), style='primary')
    def saveAndReturn(self, **data):
        parent = self.context.__parent__
        if self.context.level == data['level']:
            msave(self, **data)
        else:
            # The level changed. We have to create a new certcourse as
            # the key of the entry will change as well...
            old_level = self.context.level
            data['course'] = self.context.course
            parent.addCertCourse(**data)
            parent.delCertCourses(data['course'].code, level=old_level)
            self.flash(_('Form has been saved.'))
            old_code = "%s_%s" % (data['course'].code, old_level)
            new_code = "%s_%s" % (data['course'].code, data['level'])
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            grok.getSite().logger.info(
                '%s - renamed: %s to %s' % (ob_class, old_code, new_code))
        self.redirect(self.url(parent))
        return

    @action(_('Cancel'), validator=NullValidator)
    def cancel(self, **data):
        self.redirect(self.url(self.context))
        return

class ChangePasswordRequestPage(KofaForm):
    """Captcha'd page for all kind of users to request a password change.
    """
    grok.context(IUniversity)
    grok.name('changepw')
    grok.require('waeup.Anonymous')
    grok.template('changepw')
    label = _('Send me a new password')
    form_fields = grok.AutoFields(IChangePassword)

    def update(self):
        # Handle captcha
        self.captcha = getUtility(ICaptchaManager).getCaptcha()
        self.captcha_result = self.captcha.verify(self.request)
        self.captcha_code = self.captcha.display(self.captcha_result.error_code)
        return

    def _searchUser(self, identifier, email):
        # Search student
        cat = queryUtility(ICatalog, name='students_catalog')
        results = cat.searchResults(
            #reg_number=(identifier, identifier),
            email=(email,email))
        for result in results:
            if result.student_id == identifier or \
                result.reg_number == identifier or \
                result.matric_number == identifier:
                return result
        # Search applicant
        cat = queryUtility(ICatalog, name='applicants_catalog')
        if cat is not None:
            results = cat.searchResults(
                #reg_number=(identifier, identifier),
                email=(email,email))
            for result in results:
                if result.applicant_id == identifier or \
                    result.reg_number == identifier:
                    return result
        # Search portal user
        user = grok.getSite()['users'].get(identifier, None)
        if user is not None and user.email == email:
            return user
        return None

    @action(_('Send login credentials to email address'), style='primary')
    def request(self, **data):
        if not self.captcha_result.is_valid:
            # Captcha will display error messages automatically.
            # No need to flash something.
            return
        # Search student or applicant
        identifier = data['identifier']
        email = data['email']
        user = self._searchUser(identifier, email)
        if user is None:
            self.flash(_('No record found.'), type='warning')
            return
        # Change password
        kofa_utils = getUtility(IKofaUtils)
        password = kofa_utils.genPassword()
        mandate = PasswordMandate()
        mandate.params['password'] = password
        mandate.params['user'] = user
        site = grok.getSite()
        site['mandates'].addMandate(mandate)
        # Send email with credentials
        args = {'mandate_id':mandate.mandate_id}
        mandate_url = self.url(site) + '/mandate?%s' % urlencode(args)
        url_info = u'Confirmation link: %s' % mandate_url
        msg = _('You have successfully requested a password for the')
        success = kofa_utils.sendCredentials(
            IUserAccount(user),password,url_info,msg)
        if success:
            self.flash(_('An email with your user name and password ' +
                'has been sent to ${a}.', mapping = {'a':email}))
        else:
            self.flash(_('An smtp server error occurred.'), type='danger')
        ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
        self.context.logger.info(
            '%s - %s - %s' % (ob_class, data['identifier'], data['email']))
        return
