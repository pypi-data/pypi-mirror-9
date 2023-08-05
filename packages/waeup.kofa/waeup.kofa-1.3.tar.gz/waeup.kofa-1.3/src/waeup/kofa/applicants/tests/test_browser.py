## $Id: test_browser.py 12395 2015-01-04 17:19:06Z henrik $
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
"""
Test the applicant-related UI components.
"""
import os
import pytz
import shutil
import tempfile
import grok
from datetime import datetime
from StringIO import StringIO
from datetime import datetime, date, timedelta
from mechanize import LinkNotFoundError
from zc.async.testing import wait_for_result
from zope.event import notify
from zope.catalog.interfaces import ICatalog
from zope.component import createObject, getUtility
from zope.component.hooks import setSite, clearSite
from zope.security.interfaces import Unauthorized
from zope.testbrowser.testing import Browser
from hurry.workflow.interfaces import IWorkflowInfo, IWorkflowState
from waeup.kofa.testing import FunctionalLayer, FunctionalTestCase
from waeup.kofa.app import University
from waeup.kofa.payments.interfaces import IPayer
from waeup.kofa.configuration import SessionConfiguration
from waeup.kofa.applicants.container import ApplicantsContainer
from waeup.kofa.applicants.applicant import Applicant
from waeup.kofa.interfaces import (
    IExtFileStore, IFileStoreNameChooser, IUserAccount, IJobManager)
from waeup.kofa.university.faculty import Faculty
from waeup.kofa.university.department import Department
from waeup.kofa.tests.test_async import FunctionalAsyncTestCase

PH_LEN = 15911  # Length of placeholder file

session_1 = datetime.now().year - 2
container_name_1 = u'app%s' % session_1
session_2 = datetime.now().year - 1
container_name_2 = u'app%s' % session_2

SAMPLE_IMAGE = os.path.join(os.path.dirname(__file__), 'test_image.jpg')

class ApplicantsFullSetup(FunctionalTestCase):
    # A test case that only contains a setup and teardown
    #
    # Complete setup for applicants handlings is rather complex and
    # requires lots of things created before we can start. This is a
    # setup that does all this, creates a university, creates PINs,
    # etc.  so that we do not have to bother with that in different
    # test cases.

    layer = FunctionalLayer

    def setUp(self):
        super(ApplicantsFullSetup, self).setUp()

        # Setup a sample site for each test
        app = University()
        self.dc_root = tempfile.mkdtemp()
        app['datacenter'].setStoragePath(self.dc_root)

        # Prepopulate the ZODB...
        self.getRootFolder()['app'] = app
        # we add the site immediately after creation to the
        # ZODB. Catalogs and other local utilities are not setup
        # before that step.
        self.app = self.getRootFolder()['app']
        # Set site here. Some of the following setup code might need
        # to access grok.getSite() and should get our new app then
        setSite(app)

        self.login_path = 'http://localhost/app/login'
        self.root_path = 'http://localhost/app/applicants'
        self.search_path = 'http://localhost/app/applicants/search'
        self.manage_root_path = self.root_path + '/@@manage'
        self.add_container_path = self.root_path + '/@@add'
        self.container_path = 'http://localhost/app/applicants/%s' % container_name_1
        self.manage_container_path = self.container_path + '/@@manage'

        # Add an applicants container
        applicantscontainer = ApplicantsContainer()
        applicantscontainer.code = container_name_1
        applicantscontainer.prefix = 'app'
        applicantscontainer.year = session_1
        applicantscontainer.title = u'This is the %s container' % container_name_1
        applicantscontainer.application_category = 'basic'
        applicantscontainer.mode = 'create'
        applicantscontainer.strict_deadline = True
        delta = timedelta(days=10)
        applicantscontainer.startdate = datetime.now(pytz.utc) - delta
        applicantscontainer.enddate = datetime.now(pytz.utc) + delta
        self.app['applicants'][container_name_1] = applicantscontainer
        self.applicantscontainer = self.app['applicants'][container_name_1]

        # Populate university
        certificate = createObject('waeup.Certificate')
        certificate.code = 'CERT1'
        certificate.application_category = 'basic'
        certificate.start_level = 100
        certificate.end_level = 500
        certificate.study_mode = u'ug_ft'
        self.certificate = certificate
        self.app['faculties']['fac1'] = Faculty()
        # The code has explicitely to be set, otherwise we don't
        # find created students in their department
        self.app['faculties']['fac1']['dep1'] = Department(code=u'dep1')
        self.department = self.app['faculties']['fac1']['dep1']
        self.app['faculties']['fac1']['dep1'].certificates.addCertificate(
            certificate)

        # Put the prepopulated site into test ZODB and prepare test
        # browser
        self.browser = Browser()
        self.browser.handleErrors = False

        # Create 5 access codes with prefix'FOO' and cost 9.99 each
        pin_container = self.app['accesscodes']
        pin_container.createBatch(
            datetime.now(), 'some_userid', 'APP', 9.99, 5)
        pins = pin_container[pin_container.keys()[0]].values()
        self.pins = [x.representation for x in pins]
        self.existing_pin = self.pins[0]
        parts = self.existing_pin.split('-')[1:]
        self.existing_series, self.existing_number = parts

        # Add an applicant
        self.applicant = createObject('waeup.Applicant')
        # reg_number is the only field which has to be preset here
        # because managers are allowed to edit this required field
        self.applicant.reg_number = u'1234'
        self.applicant.course1 = certificate
        app['applicants'][container_name_1].addApplicant(self.applicant)
        IUserAccount(
            self.app['applicants'][container_name_1][
            self.applicant.application_number]).setPassword('apwd')
        self.manage_path = 'http://localhost/app/applicants/%s/%s/%s' % (
            container_name_1, self.applicant.application_number, 'manage')
        self.edit_path = 'http://localhost/app/applicants/%s/%s/%s' % (
            container_name_1, self.applicant.application_number, 'edit')
        self.view_path = 'http://localhost/app/applicants/%s/%s' % (
            container_name_1, self.applicant.application_number)

    def login(self):
        # Perform an applicant login. This creates an applicant record.
        #
        # This helper also sets `self.applicant`, which is the
        # applicant object created.
        self.browser.open(self.login_path)
        self.browser.getControl(
            name="form.login").value = self.applicant.applicant_id
        self.browser.getControl(name="form.password").value = 'apwd'
        self.browser.getControl("Login").click()

    def fill_correct_values(self):
        # Fill the edit form with suitable values
        self.browser.getControl(name="form.firstname").value = 'John'
        self.browser.getControl(name="form.middlename").value = 'Anthony'
        self.browser.getControl(name="form.lastname").value = 'Tester'
        self.browser.getControl(name="form.course1").value = ['CERT1']
        self.browser.getControl(name="form.date_of_birth").value = '09/09/1988'
        self.browser.getControl(name="form.sex").value = ['m']
        self.browser.getControl(name="form.email").value = 'xx@yy.zz'

    def tearDown(self):
        super(ApplicantsFullSetup, self).tearDown()
        clearSite()
        shutil.rmtree(self.dc_root)

class ApplicantsRootUITests(ApplicantsFullSetup):
    # Tests for ApplicantsRoot class

    layer = FunctionalLayer

    def test_anonymous_access(self):
        # Anonymous users can access applicants root
        self.browser.open(self.root_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertFalse(
            'Manage ' in self.browser.contents)
        return

    def test_anonymous_no_actions(self):
        # Make sure anonymous users cannot access actions
        self.browser.open(self.root_path)
        self.assertRaises(
            LookupError, self.browser.getControl, "Add local role")
        # Manage screen neither linked nor accessible for anonymous
        self.assertRaises(
            LinkNotFoundError,
            self.browser.getLink, 'Manage application section')
        self.assertRaises(
            Unauthorized, self.browser.open, self.manage_root_path)
        # Add container screen not accessible for anonymous
        self.assertRaises(
            Unauthorized, self.browser.open, self.add_container_path)
        return

    def test_manage_access(self):
        # Managers can access the manage pages of applicants root
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.root_path)
        self.assertTrue('Manage application section' in self.browser.contents)
        # There is a manage link
        link = self.browser.getLink('Manage application section')
        link.click()
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertEqual(self.browser.url, self.manage_root_path)
        return

    def test_hide_container(self):
        self.browser.open(self.root_path)
        self.assertTrue(
            '<a href="http://localhost/app/applicants/%s">'
            'This is the %s container</a>' % (container_name_1, container_name_1)
            in self.browser.contents)
        self.app['applicants'][container_name_1].hidden = True
        self.browser.open(self.root_path)
        # Anonymous users can't see hidden containers
        self.assertFalse(
            '<a href="http://localhost/app/applicants/%s">'
            'This is the %s container</a>' % (container_name_1, container_name_1)
            in self.browser.contents)
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.root_path)
        self.assertTrue(
            '<a href="http://localhost/app/applicants/%s">'
            'This is the %s container</a>' % (container_name_1, container_name_1)
            in self.browser.contents)
        return

    def test_search(self):
        # Managers can access the manage pages of applicants root
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.manage_path)
        self.fill_correct_values()
        self.browser.getControl("Save").click()
        self.browser.open(self.root_path)
        self.assertTrue('Manage application section' in self.browser.contents)
        # There is a search link
        link = self.browser.getLink('Find applicants')
        link.click()
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        # We can find an applicant ...
        # ... via his name
        self.browser.getControl(name="searchtype").value = ['fullname']
        self.browser.getControl(name="searchterm").value = 'John'
        self.browser.getControl("Find applicant").click()
        self.assertTrue('John Anthony Tester' in self.browser.contents)
        self.browser.getControl(name="searchtype").value = ['fullname']
        self.browser.getControl(name="searchterm").value = 'Tester'
        self.browser.getControl("Find applicant").click()
        self.assertTrue('John Anthony Tester' in self.browser.contents)
        self.browser.open(self.search_path)
        # ... and via his reg_number ...
        self.browser.getControl(name="searchtype").value = ['reg_number']
        self.browser.getControl(name="searchterm").value = '2345'
        self.browser.getControl("Find applicant").click()
        self.assertFalse('John Anthony Tester' in self.browser.contents)
        self.browser.getControl(name="searchtype").value = ['reg_number']
        self.browser.getControl(name="searchterm").value = '1234'
        self.browser.getControl("Find applicant").click()
        self.assertTrue('John Anthony Tester' in self.browser.contents)
        # ... and not via his application_number ...
        self.browser.getControl(name="searchtype").value = ['applicant_id']
        self.browser.getControl(
            name="searchterm").value = self.applicant.application_number
        self.browser.getControl("Find applicant").click()
        self.assertFalse('John Anthony Tester' in self.browser.contents)
        # ... but ia his applicant_id ...
        self.browser.getControl(name="searchtype").value = ['applicant_id']
        self.browser.getControl(
            name="searchterm").value = self.applicant.applicant_id
        self.browser.getControl("Find applicant").click()
        self.assertTrue('John Anthony Tester' in self.browser.contents)
        # ... and via his email
        self.browser.getControl(name="searchtype").value = ['email']
        self.browser.getControl(name="searchterm").value = 'xx@yy.zz'
        self.browser.getControl("Find applicant").click()
        self.assertTrue('John Anthony Tester' in self.browser.contents)
        return

    def test_manage_actions_access(self):
        # Managers can access the action on manage screen
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.manage_root_path)
        self.browser.getControl("Add local role").click()
        self.assertTrue('No user selected' in self.browser.contents)
        return

    def test_local_roles_add_delete(self):
        # Managers can assign and delete local roles of applicants root
        myusers = self.app['users']
        myusers.addUser('bob', 'bobssecret')
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open('http://localhost/app/faculties/fac1/dep1/manage')
        self.browser.getControl(name="user").value = ['bob']
        self.browser.getControl(name="local_role").value = [
            'waeup.local.ApplicationsManager']
        self.browser.getControl("Add local role").click()
        self.assertTrue('<td>bob</td>' in self.browser.contents)
        # Remove the role assigned
        ctrl = self.browser.getControl(name='role_id')
        ctrl.getControl(
            value='bob|waeup.local.ApplicationsManager').selected = True
        self.browser.getControl("Remove selected local roles").click()
        self.assertTrue(
            'Local role successfully removed: bob|waeup.local.ApplicationsManager'
            in self.browser.contents)
        self.assertFalse('<td>bob</td>' in self.browser.contents)
        return

    def test_add_delete_container(self):
        # Managers can add and delete applicants containers
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.manage_root_path)
        self.browser.getControl("Add applicants container").click()
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertEqual(self.browser.url, self.add_container_path)
        self.browser.getControl(name="form.prefix").value = ['app']
        self.browser.getControl("Add applicants container").click()
        self.assertTrue(
            'There were errors' in self.browser.contents)
        self.browser.getControl(name="form.prefix").value = ['app']
        self.browser.getControl(name="form.year").value = [str(session_2)]
        self.browser.getControl(name="form.mode").value = ['create']
        self.browser.getControl(
            name="form.application_category").value = ['basic']
        self.browser.getControl("Add applicants container").click()
        self.assertTrue('Added:' in self.browser.contents)
        self.browser.getLink(container_name_1).click()
        self.assertTrue('Manage applicants container'
            in self.browser.contents)
        self.browser.open(self.add_container_path)
        self.browser.getControl("Cancel").click()
        self.assertEqual(self.browser.url, self.manage_root_path)
        self.browser.open(self.add_container_path)
        self.browser.getControl(name="form.prefix").value = ['app']
        self.browser.getControl(name="form.year").value = [str(session_2)]
        self.browser.getControl(name="form.mode").value = ['create']
        self.browser.getControl(
            name="form.application_category").value = ['basic']
        self.browser.getControl("Add applicants container").click()
        self.assertTrue('exists already in the database'
                        in self.browser.contents)
        self.browser.open(self.manage_root_path)
        ctrl = self.browser.getControl(name='val_id')
        ctrl.getControl(value=container_name_2).selected = True
        self.browser.getControl("Remove selected", index=0).click()
        self.assertTrue('Successfully removed:' in self.browser.contents)
        self.browser.open(self.add_container_path)
        self.browser.getControl(name="form.prefix").value = ['app']
        self.browser.getControl(name="form.year").value = [str(session_2)]
        self.browser.getControl(name="form.mode").value = ['create']
        #self.browser.getControl(name="form.ac_prefix").value = ['APP']
        self.browser.getControl(
            name="form.application_category").value = ['basic']
        self.browser.getControl("Add applicants container").click()
        del self.app['applicants'][container_name_2]
        ctrl = self.browser.getControl(name='val_id')
        ctrl.getControl(value=container_name_2).selected = True
        self.browser.getControl("Remove selected", index=0).click()
        self.assertMatches('...Could not delete...', self.browser.contents)
        return

class ApplicantsContainerUITests(ApplicantsFullSetup):
    # Tests for ApplicantsContainer class views and pages

    layer = FunctionalLayer

    def test_anonymous_access(self):
        # Anonymous users can access applicants containers
        self.browser.open(self.container_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertFalse(
            'Manage ' in self.browser.contents)
        return

    def test_manage_access(self):
        # Managers can access the manage pages of applicants
        # containers and can perform actions
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.manage_container_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertEqual(self.browser.url, self.manage_container_path)
        self.browser.getControl(name="form.application_fee").value = '200'
        self.browser.getControl("Save").click()
        self.assertTrue('Form has been saved' in self.browser.contents)
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'applicants.log')
        logcontent = open(logfile).read()
        self.assertTrue(
            'zope.mgr - applicants.browser.ApplicantsContainerManageFormPage - '
            '%s - saved: application_fee\n' % container_name_1 in logcontent)
        self.browser.getControl("Remove selected", index=0).click()
        self.assertTrue('No applicant selected' in self.browser.contents)
        self.browser.getControl("Add local role").click()
        self.assertTrue('No user selected' in self.browser.contents)
        self.browser.getControl("Cancel", index=0).click()
        self.assertEqual(self.browser.url, self.container_path)
        return

    def test_statistics(self):
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.container_path)
        self.browser.getLink("Container statistics").click()
        self.assertTrue('<td>initialized</td>' in self.browser.contents)
        self.assertTrue('<td>1</td>' in self.browser.contents)
        self.assertEqual(self.applicantscontainer.statistics[0],
            {'not admitted': 0, 'started': 0, 'created': 0,
            'admitted': 0, 'submitted': 0, 'initialized': 1, 'paid': 0})
        #self.assertEqual(self.applicantscontainer.statistics[1],
        #    {u'fac1': 0})
        IWorkflowState(self.applicant).setState('submitted')
        notify(grok.ObjectModifiedEvent(self.applicant))
        self.assertEqual(self.applicantscontainer.statistics[0],
            {'not admitted': 0, 'started': 0, 'created': 0,
            'admitted': 0, 'submitted': 1, 'initialized': 0, 'paid': 0})
        #self.assertEqual(self.applicantscontainer.statistics[1],
        #    {u'fac1': 1})
        return

    def test_add_delete_applicants(self):
        # Managers can add and delete applicants
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.add_applicant_path = self.container_path + '/addapplicant'
        self.container_manage_path = self.container_path + '/@@manage'
        self.browser.open(self.container_manage_path)
        self.browser.getLink("Add applicant").click()
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertEqual(self.browser.url, self.add_applicant_path)
        self.browser.getControl(name="form.firstname").value = 'Alois'
        self.browser.getControl(name="form.middlename").value = 'Kofi'
        self.browser.getControl(name="form.lastname").value = 'Bettermann'
        self.browser.getControl(name="form.email").value = 'xx@yy.zz'
        self.browser.getControl("Create application record").click()
        self.assertTrue('Application initialized' in self.browser.contents)
        self.browser.open(self.container_manage_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        ctrl = self.browser.getControl(name='val_id')
        value = ctrl.options[0]
        ctrl.getControl(value=value).selected = True
        self.browser.getControl("Remove selected", index=0).click()
        self.assertTrue('Successfully removed:' in self.browser.contents)
        self.browser.open(self.add_applicant_path)
        self.browser.getControl(name="form.firstname").value = 'Albert'
        self.browser.getControl(name="form.lastname").value = 'Einstein'
        self.browser.getControl(name="form.email").value = 'xx@yy.zz'
        self.browser.getControl("Create application record").click()
        self.assertTrue('Application initialized' in self.browser.contents)
        return

class ApplicantUITests(ApplicantsFullSetup):
    # Tests for uploading/browsing the passport image of appplicants

    layer = FunctionalLayer

    def test_manage_and_view_applicant(self):
        # Managers can manage applicants
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.slip_path = self.view_path + '/application_slip.pdf'
        self.browser.open(self.manage_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.fill_correct_values()
        # Fire transition
        self.browser.getControl(name="transition").value = ['start']
        self.browser.getControl("Save").click()
        # Be sure that the empty phone field does not show wrong error message
        self.assertFalse('Required input is missing' in self.browser.contents)
        self.assertMatches('...Form has been saved...', self.browser.contents)
        self.assertMatches('...Application started by Manager...',
                           self.browser.contents)
        self.browser.open(self.view_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        # Change course_admitted
        self.browser.open(self.manage_path)
        self.browser.getControl(name="form.course_admitted").value = ['CERT1']
        self.browser.getControl("Save").click()
        self.assertMatches('...Form has been saved...', self.browser.contents)
        # Change password
        self.browser.getControl(name="password").value = 'secret'
        self.browser.getControl(name="control_password").value = 'secre'
        self.browser.getControl("Save").click()
        self.assertMatches('...Passwords do not match...',
                           self.browser.contents)
        self.browser.getControl(name="password").value = 'secret'
        self.browser.getControl(name="control_password").value = 'secret'
        self.browser.getControl("Save").click()
        self.assertMatches('...Form has been saved...', self.browser.contents)
        # Pdf slip can't be opened and download button is not available
        self.assertFalse('Download application slip' in self.browser.contents)
        self.browser.open(self.slip_path)
        self.assertTrue(
            'Please pay and submit before trying to download the application slip.'
            in self.browser.contents)
        # If applicant is in correct state the pdf slip can be opened.
        IWorkflowState(self.applicant).setState('submitted')
        self.browser.open(self.manage_path)
        self.browser.getLink("Download application slip").click()
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertEqual(self.browser.headers['Content-Type'],
                         'application/pdf')
        # Managers can view applicants even if certificate has been removed
        del self.app['faculties']['fac1']['dep1'].certificates['CERT1']
        self.browser.open(self.view_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.browser.open(self.slip_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        return

    def test_passport_edit_view(self):
        # We get a default image after login
        self.browser.open(self.login_path)
        self.login()
        self.browser.open(self.browser.url + '/passport.jpg')
        self.assertEqual(self.browser.headers['status'], '200 Ok')
        self.assertEqual(self.browser.headers['content-type'], 'image/jpeg')
        self.assertTrue('JFIF' in self.browser.contents)
        self.assertEqual(
            self.browser.headers['content-length'], str(PH_LEN))

    def test_applicant_login(self):
        self.applicant.suspended = True
        self.login()
        self.assertTrue(
            'You entered invalid credentials.' in self.browser.contents)
        self.applicant.suspended = False
        self.browser.getControl("Login").click()
        self.assertTrue(
            'You logged in.' in self.browser.contents)

    def test_applicant_access(self):
        # Applicants can edit their record
        self.browser.open(self.login_path)
        self.login()
        self.assertTrue(
            'You logged in.' in self.browser.contents)
        self.browser.open(self.edit_path)
        self.assertTrue(self.browser.url != self.login_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.fill_correct_values()
        self.assertTrue(IUserAccount(self.applicant).checkPassword('apwd'))
        self.browser.getControl("Save").click()
        self.assertMatches('...Form has been saved...', self.browser.contents)
        # Applicants don't see manage and search links ...
        self.browser.open(self.root_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertFalse('Search' in self.browser.contents)
        self.assertFalse('Manage application section' in self.browser.contents)
        # ... and can't access the manage page
        self.assertRaises(
            Unauthorized, self.browser.open, self.manage_path)
        return

    def test_message_for_created(self):
        IWorkflowState(self.applicant).setState('created')
        self.applicant.student_id = u'my id'
        self.browser.open(self.login_path)
        self.login()
        self.assertTrue(
            'You logged in.' in self.browser.contents)
        self.assertTrue(
            '<strong>Congratulations!</strong> You have been offered provisional'
            ' admission into the %s/%s Academic Session of'
            ' Sample University. Your student record has been created for you.'
            % (session_1, session_1 + 1) in self.browser.contents)
        self.assertTrue(
            'Then enter your new student credentials: user name= my id,'
            ' password = %s.' % self.applicant.application_number
            in self.browser.contents)
        return

    def image_url(self, filename):
        return self.edit_path.replace('edit', filename)

    def test_after_login_default_browsable(self):
        # After login we see the placeholder image in the edit view
        self.login()
        self.assertEqual(self.browser.url, self.view_path)
        self.browser.open(self.edit_path)
        # There is a correct <img> link included
        self.assertTrue(
              '<img src="passport.jpg" height="180px" />' in self.browser.contents)
        # Browsing the link shows a real image
        self.browser.open(self.image_url('passport.jpg'))
        self.assertEqual(
            self.browser.headers['content-type'], 'image/jpeg')
        self.assertEqual(len(self.browser.contents), PH_LEN)

    def test_after_submit_default_browsable(self):
        # After submitting an applicant form the default image is
        # still visible
        self.login()
        self.browser.open(self.edit_path)
        self.browser.getControl("Save").click() # submit form
        # There is a correct <img> link included
        self.assertTrue(
            '<img src="passport.jpg" height="180px" />' in self.browser.contents)
        # Browsing the link shows a real image
        self.browser.open(self.image_url('passport.jpg'))
        self.assertEqual(
            self.browser.headers['content-type'], 'image/jpeg')
        self.assertEqual(len(self.browser.contents), PH_LEN)

    def test_uploaded_image_respects_file_size_restriction(self):
        # When we upload an image that is too big ( > 10 KB) we will
        # get an error message
        self.login()
        self.browser.open(self.edit_path)
        # Create a pseudo image file and select it to be uploaded in form
        photo_content = 'A' * 1024 * 21  # A string of 21 KB size
        pseudo_image = StringIO(photo_content)
        ctrl = self.browser.getControl(name='form.passport')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(pseudo_image, filename='myphoto.jpg')
        self.browser.getControl("Save").click() # submit form
        # There is a correct <img> link included
        self.assertTrue(
            '<img src="passport.jpg" height="180px" />' in self.browser.contents)
        # We get a warning message
        self.assertTrue(
            'Uploaded image is too big' in self.browser.contents)
        # Browsing the image gives us the default image, not the
        # uploaded one.
        self.browser.open(self.image_url('passport.jpg'))
        self.assertEqual(
            self.browser.headers['content-type'], 'image/jpeg')
        self.assertEqual(len(self.browser.contents), PH_LEN)
        # There is really no file stored for the applicant
        img = getUtility(IExtFileStore).getFile(
            IFileStoreNameChooser(self.applicant).chooseName())
        self.assertTrue(img is None)

    def test_uploaded_image_browsable_w_errors(self):
        # We can upload a different image and browse it after submit,
        # even if there are still errors in the form
        self.login()
        self.browser.open(self.edit_path)
        # Create a pseudo image file and select it to be uploaded in form
        photo_content = 'I pretend to be a graphics file'
        pseudo_image = StringIO(photo_content)
        ctrl = self.browser.getControl(name='form.passport')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(pseudo_image, filename='myphoto.jpg')
        self.browser.getControl("Save").click() # submit form
        # There is a correct <img> link included
        self.assertTrue(
            '<img src="passport.jpg" height="180px" />' in self.browser.contents)
        # Browsing the link shows a real image
        self.browser.open(self.image_url('passport.jpg'))
        self.assertEqual(
            self.browser.headers['content-type'], 'image/jpeg')
        self.assertEqual(self.browser.contents, photo_content)

    def test_uploaded_image_stored_in_imagestorage_w_errors(self):
        # After uploading a new passport pic the file is correctly
        # stored in an imagestorage
        self.login()
        self.browser.open(self.edit_path)
        # Create a pseudo image file and select it to be uploaded in form
        pseudo_image = StringIO('I pretend to be a graphics file')
        ctrl = self.browser.getControl(name='form.passport')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(pseudo_image, filename='myphoto.jpg')
        self.browser.getControl("Save").click() # submit form
        storage = getUtility(IExtFileStore)
        file_id = IFileStoreNameChooser(self.applicant).chooseName()
        pseudo_image.seek(0) # reset our file data source
        self.assertEqual(
            storage.getFile(file_id).read(), pseudo_image.read())
        return

    def test_uploaded_image_browsable_wo_errors(self):
        # We can upload a different image and browse it after submit,
        # if there are no errors in form
        self.login()
        self.browser.open(self.edit_path)
        self.fill_correct_values() # fill other fields with correct values
        # Create a pseudo image file and select it to be uploaded in form
        pseudo_image = StringIO('I pretend to be a graphics file')
        ctrl = self.browser.getControl(name='form.passport')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(pseudo_image, filename='myphoto.jpg')
        self.browser.getControl("Save").click() # submit form
        # There is a correct <img> link included
        self.assertTrue(
            '<img src="passport.jpg" height="180px" />' in self.browser.contents)
        # Browsing the link shows a real image
        self.browser.open(self.image_url('passport.jpg'))
        self.assertEqual(
            self.browser.headers['content-type'], 'image/jpeg')
        self.assertEqual(len(self.browser.contents), 31)

    def test_uploaded_image_stored_in_imagestorage_wo_errors(self):
        # After uploading a new passport pic the file is correctly
        # stored in an imagestorage if form contains no errors
        self.login()
        self.browser.open(self.edit_path)
        self.fill_correct_values() # fill other fields with correct values
        # Create a pseudo image file and select it to be uploaded in form
        pseudo_image = StringIO('I pretend to be a graphics file')
        ctrl = self.browser.getControl(name='form.passport')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(pseudo_image, filename='myphoto.jpg')
        self.browser.getControl("Save").click() # submit form
        storage = getUtility(IExtFileStore)
        file_id = IFileStoreNameChooser(self.applicant).chooseName()
        # The stored image can be fetched
        fd = storage.getFile(file_id)
        file_len = len(fd.read())
        self.assertEqual(file_len, 31)
        # When an applicant is removed, also the image is gone.
        del self.app['applicants'][container_name_1][self.applicant.application_number]
        fd = storage.getFile(file_id)
        self.assertTrue(fd is None)

    def test_uploaded_images_equal(self):
        # Make sure uploaded images do really differ if we eject a
        # change notfication (and do not if we don't)
        self.login()
        self.browser.open(self.edit_path)
        self.fill_correct_values() # fill other fields with correct values
        self.browser.getControl("Save").click() # submit form
        # Now go on as an officer
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.manage_path)

        # Create a pseudo image file and select it to be uploaded in form
        pseudo_image = StringIO('I pretend to be a graphics file')
        ctrl = self.browser.getControl(name='form.passport')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(pseudo_image, filename='myphoto.jpg')
        file_id = IFileStoreNameChooser(self.applicant).chooseName()
        setSite(self.app)
        passport0 = getUtility(IExtFileStore).getFile(file_id)
        self.browser.getControl("Save").click() # submit form with changed pic
        passport1 = getUtility(IExtFileStore).getFile(file_id).read()
        self.browser.getControl("Save").click() # submit form w/o changes
        passport2 = getUtility(IExtFileStore).getFile(file_id).read()
        self.assertTrue(passport0 is None)
        self.assertTrue(passport0 != passport1)
        self.assertTrue(passport1 == passport2)
        return

    def test_upload_image_by_manager_with_logging(self):
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.manage_path)
        # Create a pseudo image file and select it to be uploaded in form
        photo_content = 'A' * 1024 * 5  # A string of 5 KB size
        pseudo_image = StringIO(photo_content)
        ctrl = self.browser.getControl(name='form.passport')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(pseudo_image, filename='myphoto.jpg')
        self.browser.getControl("Save").click() # submit form
        # Even though the form could not be saved ...
        self.assertTrue(
            'Required input is missing' in self.browser.contents)
        # ... the file has been successfully uploaded
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'applicants.log')
        logcontent = open(logfile).read()
        self.assertTrue(
            'zope.mgr - applicants.browser.ApplicantManageFormPage - '
            '%s - saved: passport'
            % (self.applicant.applicant_id)
            in logcontent)

    def test_application_slip_with_non_jpg_image(self):
        IWorkflowState(self.applicant).setState('submitted')
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.manage_path)
        # Create a pseudo image file and select it to be uploaded in form
        photo_content = 'A' * 1024 * 5  # A string of 5 KB size
        pseudo_image = StringIO(photo_content)
        ctrl = self.browser.getControl(name='form.passport')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(pseudo_image, filename='myphoto.jpg')
        self.browser.getControl("Save").click() # submit form
        self.browser.open(self.manage_path)
        self.browser.getLink("Download application slip").click()
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertMatches(
            '...Your image file is corrupted. Please replace...',
            self.browser.contents)

    def test_pay_portal_application_fee(self):
        self.login()
        self.browser.open(self.edit_path)
        # Payment tickets can't be created before the form has been validated
        self.browser.getControl("Add online payment ticket").click()
        self.assertTrue('Required input is missing' in self.browser.contents)
        self.fill_correct_values()
        # We have to save the form otherwise the filled fields will be cleared
        # after adding an online payment, because adding an online payment
        # requires a filled form but does not save it
        self.browser.getControl("Save").click()
        self.browser.getControl("Add online payment ticket").click()
        # Session object missing
        self.assertTrue(
            'Session configuration object is not available'
            in self.browser.contents)
        configuration = SessionConfiguration()
        configuration.academic_session = session_1
        configuration.application_fee = 200.0
        self.app['configuration'].addSessionConfiguration(configuration)
        self.browser.open(self.edit_path)
        self.browser.getControl("Add online payment ticket").click()
        self.assertMatches('...Payment ticket created...',
                           self.browser.contents)
        self.assertMatches('...Activation Code...',
                           self.browser.contents)
        # Payment ticket can be removed if they haven't received a
        # valid callback
        self.browser.open(self.edit_path)
        ctrl = self.browser.getControl(name='val_id')
        value = ctrl.options[0]
        ctrl.getControl(value=value).selected = True
        self.browser.getControl("Remove selected", index=0).click()
        self.assertMatches('...Successfully removed...', self.browser.contents)
        # We will try the callback request view
        self.browser.getControl("Add online payment ticket").click()
        self.browser.open(self.edit_path)
        ctrl = self.browser.getControl(name='val_id')
        value = ctrl.options[0]
        self.browser.getLink(value).click()
        self.assertMatches('...Amount Authorized...',
                           self.browser.contents)
        payment_url = self.browser.url
        payment_id = self.applicant.keys()[0]
        payment = self.applicant[payment_id]
        self.assertEqual(payment.p_item,'This is the %s container' % container_name_1)
        self.assertEqual(payment.p_session, session_1)
        self.assertEqual(payment.p_category,'application')
        self.assertEqual(payment.amount_auth,200.0)
        # Applicant is payer of the payment ticket.
        self.assertEqual(
            IPayer(payment).display_fullname, 'John Anthony Tester')
        self.assertEqual(
            IPayer(payment).id, self.applicant.applicant_id)
        self.assertEqual(IPayer(payment).faculty, 'N/A')
        self.assertEqual(IPayer(payment).department, 'N/A')
        # The pdf payment slip can't yet be opened
        #self.browser.open(payment_url + '/payment_receipt.pdf')
        #self.assertMatches('...Ticket not yet paid...',
        #                   self.browser.contents)
        # Approve payment
        # Applicants can't approve payments
        self.assertRaises(
            Unauthorized, self.browser.open, payment_url + '/approve')
        # We approve the payment by bypassing the view
        payment.approve()
        # Applicant is is not yet in state 'paid' because it was only
        # the payment which we set to paid
        self.browser.open(self.view_path)
        self.assertMatches('...started...',
                           self.browser.contents)
        self.assertTrue(self.applicant.state == 'started')
        # Let's logout and approve the payment as manager
        self.browser.getLink("Logout").click()
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        # First we reset the payment
        payment.r_amount_approved = 0.0
        payment.r_code = u''
        payment.p_state = 'unpaid'
        payment.r_desc = u''
        payment.payment_date = None
        self.browser.open(payment_url)
        self.browser.getLink("Approve payment").click()
        self.assertEqual(payment.p_state, 'paid')
        self.assertEqual(payment.r_amount_approved, 200.0)
        self.assertEqual(payment.r_code, 'AP')
        self.assertTrue(self.applicant.state == 'paid')
        # Approval is logged in students.log ...
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'applicants.log')
        logcontent = open(logfile).read()
        self.assertTrue(
            'zope.mgr - applicants.browser.OnlinePaymentApprovePage - '
            '%s - payment approved' % self.applicant.applicant_id
            in logcontent)
        # ... and in payments.log
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'payments.log')
        logcontent = open(logfile).read()
        self.assertTrue(
            '"zope.mgr",%s,%s,application,200.0,AP,,,,,,\n'
            % (self.applicant.applicant_id, payment.p_id)
            in logcontent)
        # Payment slips can't be downloaded ...
        payment_id = self.applicant.keys()[0]
        self.browser.open(self.view_path + '/' + payment_id)
        self.browser.getLink("Download payment slip").click()
        self.assertTrue(
            'Please submit the application form before trying to download payment slips.'
            in self.browser.contents)
        # ... unless form is submitted.
        self.browser.open(self.view_path + '/edit')
        image = open(SAMPLE_IMAGE, 'rb')
        ctrl = self.browser.getControl(name='form.passport')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(image, filename='myphoto.jpg')
        self.browser.getControl(name="confirm_passport").value = True
        self.browser.getControl("Final Submit").click()
        self.browser.open(self.view_path + '/' + payment_id)
        self.browser.getLink("Download payment slip").click()
        self.assertEqual(self.browser.headers['Content-Type'],
                 'application/pdf')
        return

    def test_pay_container_application_fee(self):
        self.login()
        self.browser.open(self.edit_path)
        self.fill_correct_values()
        self.browser.getControl("Save").click()
        configuration = SessionConfiguration()
        configuration.academic_session = session_1
        self.applicantscontainer.application_fee = 120.0
        configuration.application_fee = 9999.9
        self.app['configuration'].addSessionConfiguration(configuration)
        self.browser.open(self.edit_path)
        self.browser.getControl("Add online payment ticket").click()
        self.assertMatches('...Payment ticket created...',
                           self.browser.contents)
        self.assertMatches('...Payment ticket created...',
                           self.browser.contents)
        self.assertFalse(
            '<span>9999.9</span>' in self.browser.contents)
        self.assertTrue(
            '<span>120.0</span>' in self.browser.contents)
        self.assertTrue(
            '<span>Application Fee</span>' in self.browser.contents)
        return

    def prepare_special_container(self):
        # Add special application container
        container_name = u'special%s' % session_1
        applicantscontainer = ApplicantsContainer()
        applicantscontainer.code = container_name
        applicantscontainer.prefix = 'special'
        applicantscontainer.year = session_1
        applicantscontainer.title = u'This is a special app container'
        applicantscontainer.application_category = 'no'
        applicantscontainer.mode = 'create'
        applicantscontainer.strict_deadline = True
        delta = timedelta(days=10)
        applicantscontainer.startdate = datetime.now(pytz.utc) - delta
        applicantscontainer.enddate = datetime.now(pytz.utc) + delta
        self.app['applicants'][container_name] = applicantscontainer
        # Add an applicant
        applicant = createObject('waeup.Applicant')
        # reg_number is the only field which has to be preset here
        # because managers are allowed to edit this required field
        applicant.reg_number = u'12345'
        self.special_applicant = applicant
        self.app['applicants'][container_name].addApplicant(applicant)
        IUserAccount(
            self.app['applicants'][container_name][
            applicant.application_number]).setPassword('apwd')
        # Add session configuration object
        configuration = SessionConfiguration()
        configuration.academic_session = session_1
        configuration.transcript_fee = 200.0
        configuration.clearance_fee = 300.0
        self.app['configuration'].addSessionConfiguration(configuration)


    def test_pay_special_fee(self):
        self.prepare_special_container()
        # Login
        self.browser.open(self.login_path)
        self.browser.getControl(
            name="form.login").value = self.special_applicant.applicant_id
        self.browser.getControl(name="form.password").value = 'apwd'
        self.browser.getControl("Login").click()
        applicant_path = self.browser.url
        self.browser.getLink("Edit application record").click()
        self.browser.getControl(name="form.firstname").value = 'John'
        self.browser.getControl(name="form.middlename").value = 'Anthony'
        self.browser.getControl(name="form.lastname").value = 'Tester'
        self.browser.getControl(name="form.special_application").value = [
            'transcript']
        self.browser.getControl(name="form.date_of_birth").value = '09/09/1988'
        #self.browser.getControl(name="form.sex").value = ['m']
        self.browser.getControl(name="form.email").value = 'xx@yy.zz'
        self.browser.getControl("Save").click()
        self.browser.getControl("Add online payment ticket").click()
        self.assertMatches('...Payment ticket created...',
                           self.browser.contents)
        self.assertTrue(
            '<span>Transcript Fee</span>' in self.browser.contents)
        self.assertTrue(
            'This is a special app container' in self.browser.contents)
        self.assertTrue(
            '<span>200.0</span>' in self.browser.contents)
        self.assertEqual(len(self.special_applicant.keys()), 1)
        # The applicant's workflow state is paid ...
        self.special_applicant.values()[0].approveApplicantPayment()
        self.assertEqual(self.special_applicant.state, 'paid')
        self.browser.open(applicant_path + '/edit')
        # ... but he can create further tickets.
        self.browser.getControl(name="form.special_application").value = [
            'clearance']
        self.browser.getControl("Save").click()
        self.browser.getControl("Add online payment ticket").click()
        self.assertMatches('...Payment ticket created...',
                           self.browser.contents)
        self.browser.open(applicant_path)
        self.assertTrue(
            '<td>Acceptance Fee</td>' in self.browser.contents)
        self.assertEqual(len(self.special_applicant.keys()), 2)
        # Second payment can also be approved wthout error message
        flashtype, msg, log = self.special_applicant.values()[1].approveApplicantPayment()
        self.assertEqual(flashtype, 'success')
        self.assertEqual(msg, 'Payment approved')
        # Payment slips can't be downloaded ...
        payment_id = self.special_applicant.keys()[0]
        self.browser.open(applicant_path + '/' + payment_id)
        self.browser.getLink("Download payment slip").click()
        self.assertTrue(
            'Please submit the application form before trying to download payment slips.'
            in self.browser.contents)
        # ... unless form is submitted.
        self.browser.open(applicant_path + '/edit')
        image = open(SAMPLE_IMAGE, 'rb')
        ctrl = self.browser.getControl(name='form.passport')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(image, filename='myphoto.jpg')
        self.browser.getControl(name="confirm_passport").value = True
        self.browser.getControl("Final Submit").click()
        self.browser.open(applicant_path + '/' + payment_id)
        self.browser.getLink("Download payment slip").click()
        self.assertEqual(self.browser.headers['Content-Type'],
                 'application/pdf')
        return

    def test_duplicate_choice(self):
        # Make sure that that 1st and 2nd choice are different
        self.login()
        self.browser.open(self.edit_path)
        self.fill_correct_values() # fill other fields with correct values
        self.browser.getControl(name="form.course2").value = ['CERT1']
        self.browser.getControl("Save").click()
        self.assertTrue(
            '1st and 2nd choice must be different' in self.browser.contents)
        self.browser.getControl(name="form.course2").value = []
        self.browser.getControl("Save").click()
        self.assertTrue('Form has been saved' in self.browser.contents)
        return

    def test_final_submit(self):
        # Make sure that a correctly filled form with passport picture
        # can be submitted (only) after payment
        self.login()
        self.browser.getLink("Edit application record").click()
        self.assertFalse('Final Submit' in self.browser.contents)
        IWorkflowInfo(self.applicant).fireTransition('pay')
        self.browser.open(self.edit_path)
        self.assertTrue('Final Submit' in self.browser.contents)
        self.fill_correct_values() # fill other fields with correct values
        self.browser.getControl("Save").click()
        self.browser.getControl("Final Submit").click()
        # We forgot to upload a passport picture
        self.assertTrue(
            'No passport picture uploaded' in self.browser.contents)
        # Use a real image file and select it to be uploaded in form
        image = open(SAMPLE_IMAGE, 'rb')
        ctrl = self.browser.getControl(name='form.passport')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(image, filename='myphoto.jpg')
        self.browser.getControl("Final Submit").click() # (finally) submit form
        # The picture has been uploaded but the form cannot be submitted
        # since the passport confirmation box was not ticked
        self.assertTrue(
            'Passport picture confirmation box not ticked'
            in self.browser.contents)
        self.browser.getControl(name="confirm_passport").value = True
        # If application period has expired and strict-deadline is set
        # applicants do notsee edit button and can't open
        # the edit form.
        self.applicantscontainer.enddate = datetime.now(pytz.utc)
        self.browser.open(self.view_path)
        self.assertFalse(
            'Edit application record' in self.browser.contents)
        self.browser.open(self.edit_path)
        self.assertTrue(
            'form is locked' in self.browser.contents)
        # We can either postpone the enddate ...
        self.applicantscontainer.enddate = datetime.now(
            pytz.utc) + timedelta(days=10)
        self.browser.open(self.edit_path)
        self.browser.getControl(name="confirm_passport").value = True
        self.browser.getControl("Final Submit").click()
        self.assertTrue(
            'Application submitted' in self.browser.contents)
        # ... or allow submission after deadline.
        IWorkflowState(self.applicant).setState('paid')
        self.applicant.locked = False
        self.applicantscontainer.strict_deadline = False
        self.browser.open(self.edit_path)
        self.browser.getControl(name="confirm_passport").value = True
        self.browser.getControl("Final Submit").click()
        self.assertTrue(
            'Application submitted' in self.browser.contents)
        self.browser.goBack(count=1)
        self.browser.getControl("Save").click()
        # The form is locked.
        self.assertTrue(self.applicant.locked)
        self.assertTrue(
            'The requested form is locked' in self.browser.contents)
        self.browser.goBack(count=1)
        self.browser.getControl("Final Submit").click()
        self.assertTrue(
            'The requested form is locked' in self.browser.contents)
        return

    def test_locking(self):
        # Make sure that locked forms can't be submitted
        self.login()
        self.browser.open(self.edit_path)
        self.fill_correct_values() # fill other fields with correct values
        # Create a pseudo image file and select it to be uploaded in form
        pseudo_image = StringIO('I pretend to be a graphics file')
        ctrl = self.browser.getControl(name='form.passport')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(pseudo_image, filename='myphoto.jpg')
        self.browser.getControl("Save").click()
        # Now we lock the form
        self.applicant.locked = True
        self.browser.open(self.edit_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertTrue(
            'The requested form is locked' in self.browser.contents)
        return

    def test_certificate_removed(self):
        self.login()
        self.browser.open(self.edit_path)
        self.fill_correct_values()
        self.browser.getControl("Save").click()
        self.browser.open(self.view_path)
        self.assertTrue(
            'Unnamed Certificate' in self.browser.contents)
        self.browser.open(self.edit_path)
        self.assertTrue(
            '<option selected="selected" value="CERT1">' in self.browser.contents)
        # Now we remove the certificate
        del self.app['faculties']['fac1']['dep1'].certificates['CERT1']
        # The certificate is still shown in display mode
        self.browser.open(self.view_path)
        self.assertTrue(
            'Unnamed Certificate' in self.browser.contents)
        # The certificate is still selectable in edit mode so that it won't
        # be automatically replaced by another (arbitrary) certificate
        self.browser.open(self.edit_path)
        self.assertTrue(
            '<option selected="selected" value="CERT1">' in self.browser.contents)
        # Consequently, the certificate is still shown after saving the form
        self.browser.getControl("Save").click()
        self.browser.open(self.view_path)
        self.assertTrue(
            'Unnamed Certificate' in self.browser.contents)
        # Even if we add a new certificate the previous (removed)
        # certificate is shown
        certificate = createObject('waeup.Certificate')
        certificate.code = 'CERT2'
        certificate.title = 'New Certificate'
        certificate.application_category = 'basic'
        self.app['faculties']['fac1']['dep1'].certificates.addCertificate(
            certificate)
        self.browser.open(self.edit_path)
        self.assertTrue(
            '<option selected="selected" value="CERT1">'
            in self.browser.contents)

class ApplicantRegisterTests(ApplicantsFullSetup):
    # Tests for applicant registration

    layer = FunctionalLayer

    def test_register_applicant_create(self):
        # An applicant can register himself.
        self.browser.open(self.container_path)
        self.browser.getLink("Register for application").click()
        # Fill the edit form with suitable values
        self.browser.getControl(name="form.firstname").value = 'Anna'
        self.browser.getControl(name="form.lastname").value = 'Kurios'
        self.browser.getControl(name="form.email").value = 'xx@yy.zz'
        self.browser.getControl(name="form.phone.country").value = ['+234']
        self.browser.getControl(name="form.phone.area").value = '555'
        self.browser.getControl(name="form.phone.ext").value = '6666666'
        self.browser.getControl("Send login credentials").click()
        self.assertEqual(self.browser.url,
            self.container_path + '/registration_complete?email=xx%40yy.zz')
        # The new applicant can be found in the catalog via the email address
        cat = getUtility(ICatalog, name='applicants_catalog')
        results = list(
            cat.searchResults(email=('xx@yy.zz', 'xx@yy.zz')))
        applicant = results[0]
        self.assertEqual(applicant.lastname,'Kurios')
        # The application_id has been copied to the reg_number
        self.assertEqual(applicant.applicant_id, applicant.reg_number)
        # The applicant can be found in the catalog via the reg_number
        results = list(
            cat.searchResults(
            reg_number=(applicant.reg_number, applicant.reg_number)))
        self.assertEqual(applicant,results[0])
        return

    def test_register_applicant_update(self):
        # We change the application mode and check if applicants
        # can find and update imported records instead of creating new records.
        # First we check what happens if record does not exist.
        self.applicantscontainer.mode = 'update'
        self.browser.open(self.container_path + '/register')
        self.browser.getControl(name="form.lastname").value = 'Better'
        self.browser.getControl(name="form.reg_number").value = 'anynumber'
        self.browser.getControl(name="form.email").value = 'xx@yy.zz'
        self.browser.getControl("Send login credentials").click()
        self.assertTrue('No application record found.'
            in self.browser.contents)
        # Even with the correct reg_number we can't register
        # because lastname attribute is not set.
        self.applicantscontainer.mode = 'update'
        self.browser.open(self.container_path + '/register')
        self.browser.getControl(name="form.lastname").value = 'Better'
        self.browser.getControl(name="form.reg_number").value = '1234'
        self.browser.getControl(name="form.email").value = 'xx@yy.zz'
        self.browser.getControl("Send login credentials").click()
        self.assertTrue('An error occurred.' in self.browser.contents)
        # Let's set this attribute manually
        # and try to register with a wrong name.
        self.applicant.lastname = u'Better'
        self.browser.open(self.container_path + '/register')
        self.browser.getControl(name="form.lastname").value = 'Worse'
        self.browser.getControl(name="form.reg_number").value = '1234'
        self.browser.getControl(name="form.email").value = 'xx@yy.zz'
        self.browser.getControl("Send login credentials").click()
        # Anonymous is not informed that lastname verification failed.
        # It seems that the record doesn't exist.
        self.assertTrue('No application record found.'
            in self.browser.contents)
        # Even with the correct lastname we can't register if a
        # password has been set and used.
        IWorkflowState(self.applicant).setState('started')
        self.browser.getControl(name="form.lastname").value = 'Better'
        self.browser.getControl(name="form.reg_number").value = '1234'
        self.browser.getControl("Send login credentials").click()
        self.assertTrue('Your password has already been set and used.'
            in self.browser.contents)
        #IUserAccount(
        #    self.app['applicants'][container_name_1][
        #    self.applicant.application_number]).context.password = None
        # Even without unsetting the password we can re-register if state
        # is 'initialized'
        IWorkflowState(self.applicant).setState('initialized')
        self.browser.open(self.container_path + '/register')
        # The lastname field, used for verification, is not case-sensitive.
        self.browser.getControl(name="form.lastname").value = 'bEtter'
        self.browser.getControl(name="form.reg_number").value = '1234'
        self.browser.getControl(name="form.email").value = 'new@yy.zz'
        self.browser.getControl("Send login credentials").click()
        # Yeah, we succeded ...
        self.assertTrue('Your registration was successful.'
            in self.browser.contents)
        # ... and  applicant can be found in the catalog via the email address
        cat = getUtility(ICatalog, name='applicants_catalog')
        results = list(
            cat.searchResults(
            email=('new@yy.zz', 'new@yy.zz')))
        self.assertEqual(self.applicant,results[0])
        return

    def test_change_password_request(self):
        self.browser.open('http://localhost/app/changepw')
        self.browser.getControl(name="form.identifier").value = '1234'
        self.browser.getControl(name="form.email").value = 'aa@aa.ng'
        self.browser.getControl("Send login credentials").click()
        self.assertTrue('No record found' in self.browser.contents)
        self.applicant.email = 'aa@aa.ng'
        # Update the catalog
        notify(grok.ObjectModifiedEvent(self.applicant))
        self.browser.open('http://localhost/app/changepw')
        self.browser.getControl(name="form.identifier").value = '1234'
        self.browser.getControl(name="form.email").value = 'aa@aa.ng'
        self.browser.getControl("Send login credentials").click()
        self.assertTrue(
            'An email with your user name and password has been sent'
            in self.browser.contents)

class ApplicantsExportTests(ApplicantsFullSetup, FunctionalAsyncTestCase):
    # Tests for StudentsContainer class views and pages

    layer = FunctionalLayer

    def wait_for_export_job_completed(self):
        # helper function waiting until the current export job is completed
        manager = getUtility(IJobManager)
        job_id = self.app['datacenter'].running_exports[0][0]
        job = manager.get(job_id)
        wait_for_result(job)
        return job_id

    def test_applicants_in_container_export(self):
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        container_path = 'http://localhost/app/applicants/%s' % container_name_1
        self.browser.open(container_path)
        self.browser.getLink("Export applicants").click()
        self.browser.getControl("Start new export").click()

        # When the job is finished and we reload the page...
        job_id = self.wait_for_export_job_completed()
        self.browser.open(container_path + '/exports')
        # ... the csv file can be downloaded ...
        self.browser.getLink("Download").click()
        self.assertEqual(self.browser.headers['content-type'],
            'text/csv; charset=UTF-8')
        self.assertTrue(
            'filename="WAeUP.Kofa_applicants_%s.csv' % job_id in
            self.browser.headers['content-disposition'])
        self.assertEqual(len(self.app['datacenter'].running_exports), 1)
        job_id = self.app['datacenter'].running_exports[0][0]
        # ... and discarded
        self.browser.open(container_path + '/exports')
        self.browser.getControl("Discard").click()
        self.assertEqual(len(self.app['datacenter'].running_exports), 0)
        # Creation, downloading and discarding is logged
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'datacenter.log')
        logcontent = open(logfile).read()
        self.assertTrue(
            'zope.mgr - applicants.browser.ExportJobContainerJobStart - '
            'exported: applicants (%s), job_id=%s'
            % (container_name_1, job_id) in logcontent
            )
        self.assertTrue(
            'zope.mgr - applicants.browser.ExportJobContainerDownload '
            '- downloaded: WAeUP.Kofa_applicants_%s.csv, job_id=%s'
            % (job_id, job_id) in logcontent
            )
        self.assertTrue(
            'zope.mgr - applicants.browser.ExportJobContainerOverview '
            '- discarded: job_id=%s' % job_id in logcontent
            )
