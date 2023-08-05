## $Id: tests.py 11681 2014-06-06 12:01:03Z henrik $
##
## Copyright (C) 2012 Uli Fouquet & Henrik Bettermann
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
Tests for mandates.
"""
import tempfile
import shutil
import os
from zope.testbrowser.testing import Browser
from datetime import datetime, timedelta
from zope.interface.verify import verifyClass, verifyObject
from zope.component import createObject
from zope.component.hooks import setSite, clearSite
from waeup.kofa.app import University
from waeup.kofa.interfaces import IUserAccount
from waeup.kofa.mandates.interfaces import (
    IMandatesContainer, IMandate)
from waeup.kofa.mandates.container import MandatesContainer
from waeup.kofa.mandates.mandate import PasswordMandate
from waeup.kofa.testing import (FunctionalLayer, FunctionalTestCase)

class MandatesContainerTestCase(FunctionalTestCase):

    layer = FunctionalLayer

    def test_interfaces(self):
        # Make sure the correct interfaces are implemented.
        self.assertTrue(
            verifyClass(
                IMandatesContainer, MandatesContainer)
            )
        self.assertTrue(
            verifyObject(
                IMandatesContainer, MandatesContainer())
            )
        self.assertTrue(
            verifyClass(
                IMandate, PasswordMandate)
            )
        self.assertTrue(
            verifyObject(
                IMandate, PasswordMandate())
            )
        return

    def setUp(self):
        super(MandatesContainerTestCase, self).setUp()

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

        self.browser = Browser()
        self.browser.handleErrors = False

    def tearDown(self):
        super(MandatesContainerTestCase, self).tearDown()
        clearSite()
        shutil.rmtree(self.dc_root)

    def test_set_student_password(self):
        student = createObject('waeup.Student')
        # Add and execute a mandate with missing parameters.
        mandate = PasswordMandate()
        self.app['mandates'].addMandate(mandate)
        msg = mandate.execute()
        self.assertEqual(msg, u'Wrong mandate parameters.')
        # Add and execute an expired mandate.
        mandate = PasswordMandate(days=0)
        self.app['mandates'].addMandate(mandate)
        msg = mandate.execute()
        self.assertEqual(msg, u'Mandate expired.')
        # Add and execute a perfect mandate
        mandate = PasswordMandate()
        mandate.params['user'] = student
        mandate.params['password'] = 'mypwd1'
        self.app['mandates'].addMandate(mandate)
        msg = mandate.execute()
        # Password has been set.
        self.assertEqual(msg, 'Password has been successfully set. Login with your new password.')
        self.assertTrue(IUserAccount(student).checkPassword('mypwd1'))
        # All mandates have been removed.
        self.assertEqual(len(self.app['mandates'].keys()), 0)
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'main.log')
        logcontent = open(logfile).read()
        self.assertTrue('system - PasswordMandate used: K1000000' in logcontent)

    def test_set_officer_password(self):
        self.app['users'].addUser('bob', 'bobssecret')
        officer = self.app['users']['bob']
        mandate = PasswordMandate()
        mandate.params['user'] = officer
        mandate.params['password'] = 'mypwd1'
        self.app['mandates'].addMandate(mandate)
        msg = mandate.execute()
        # Password has been set.
        self.assertEqual(msg, 'Password has been successfully set. Login with your new password.')
        self.assertTrue(IUserAccount(officer).checkPassword('mypwd1'))
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'main.log')
        logcontent = open(logfile).read()
        self.assertTrue('system - PasswordMandate used: bob' in logcontent)

    def test_set_applicant_password(self):
        applicant = createObject('waeup.Applicant')
        applicant.applicant_id = u'abc'
        mandate = PasswordMandate()
        mandate.params['user'] = applicant
        mandate.params['password'] = 'mypwd1'
        self.app['mandates'].addMandate(mandate)
        msg = mandate.execute()
        # Password has been set.
        self.assertEqual(msg, 'Password has been successfully set. Login with your new password.')
        self.assertTrue(IUserAccount(applicant).checkPassword('mypwd1'))
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'main.log')
        logcontent = open(logfile).read()
        self.assertTrue('system - PasswordMandate used: abc' in logcontent)

    def test_remove_expired(self):
        # mandate1 is an old mandate which just expired.
        mandate1 = PasswordMandate(days=0)
        self.app['mandates'].addMandate(mandate1)
        # mandate2 is a new mandate with default time delta.
        mandate2 = PasswordMandate(mandate_id='23456')
        self.app['mandates'].addMandate(mandate2)
        self.assertEqual(len(self.app['mandates'].keys()), 2)
        num_deleted = self.app['mandates'].removeExpired()
        self.assertEqual(num_deleted, 1)
        # Only the new mandate remains in the container.
        self.assertEqual(len(self.app['mandates'].keys()), 1)
        self.assertEqual([i for i in self.app['mandates'].keys()], [u'23456'])

    def test_browser(self):
        student = createObject('waeup.Student')
        self.app['students'].addStudent(student)
        mandate = PasswordMandate()
        mandate.params['user'] = student
        mandate.params['password'] = 'mypwd1'
        self.app['mandates'].addMandate(mandate)
        self.browser.open('http://localhost/app/mandate?mandate_id=%s'
            % mandate.mandate_id)
        # Password has been set.
        self.assertTrue('Password has been successfully set. Login with your new password.'
            in self.browser.contents)
        self.assertTrue(IUserAccount(student).checkPassword('mypwd1'))
        # All mandates have been removed.
        self.assertEqual(len(self.app['mandates'].keys()), 0)
        # We redirect to login page not to the frontpage.
        self.assertEqual(self.browser.url, 'http://localhost/app/login')
