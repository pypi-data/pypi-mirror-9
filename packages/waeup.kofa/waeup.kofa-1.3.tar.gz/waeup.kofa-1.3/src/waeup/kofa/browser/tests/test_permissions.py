## $Id: test_permissions.py 8920 2012-07-05 14:48:51Z henrik $
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
Permission tests.

Check accessibility of views, pages, viewlets.

:test-layer: python

"""
import shutil
import tempfile
from zope.app.testing.functional import HTTPCaller as http
from zope.component import createObject
from zope.component.hooks import setSite, clearSite
from zope.security.interfaces import Unauthorized
from zope.testbrowser.testing import Browser
from waeup.kofa.app import University
from waeup.kofa.testing import (
    FunctionalLayer, FunctionalTestCase, get_all_loggers, remove_new_loggers,
    remove_logger)

manager_pages = [
    # The pages that should only be accessible by manager...
    '/@@manage', '/@@administration', '/faculties/@@search',
    '/users/@@index', '/users/@@add', '/users/alice/@@manage',
    '/datacenter/@@index', '/datacenter/@@upload', '/datacenter/@@import1',
    '/datacenter/@@import2', '/datacenter/@@import3', '/datacenter/@@import4',
    '/datacenter/@@logs', '/datacenter/@@show', '/datacenter/@@manage',
    '/faculties/@@index', '/faculties/@@add', '/faculties/@@manage',
    '/faculties/fac1/@@index', '/faculties/fac1/@@manage',
    '/faculties/fac1/@@add',
    '/faculties/fac1/dept1/@@index',
    '/faculties/fac1/dept1/@@manage',
    '/faculties/fac1/dept1/@@addcourse',
    '/faculties/fac1/dept1/@@addcertificate',
    '/faculties/fac1/dept1/courses/crs1/@@index',
    '/faculties/fac1/dept1/courses/crs1/@@manage',
    '/faculties/fac1/dept1/certificates/cert1/@@index',
    '/faculties/fac1/dept1/certificates/cert1/@@manage',
    '/faculties/fac1/dept1/certificates/cert1/@@addcertificatecourse',
    '/faculties/fac1/dept1/certificates/cert1/crs1_100/@@index',
    '/faculties/fac1/dept1/certificates/cert1/crs1_100/@@manage',
    ]
public_pages = [
    # Pages accessible also by the public...
    '/@@index', '/@@login', '/@@logout',
    ]

class PermissionTest(FunctionalTestCase):
    """Here we try to request all pages and check, whether they are
    accessible.
    """

    layer = FunctionalLayer

    def setUp(self):
        super(PermissionTest, self).setUp()
        # Set up a complete university to have every page available...
        app = University()
        self.getRootFolder()['app'] = app
        setSite(self.getRootFolder()['app'])
        self.dc_root = tempfile.mkdtemp()
        app['datacenter'].setStoragePath(self.dc_root)
        app['users'].addUser('alice', 'alice')
        fac1 = createObject('waeup.Faculty')
        fac1.code = "fac1"
        app['faculties'].addFaculty(fac1)
        dept = createObject('waeup.Department')
        dept.code = 'dept1'
        fac1.addDepartment(dept)
        course = createObject('waeup.Course')
        course.code = 'crs1'
        dept.courses.addCourse(course)
        cert = createObject('waeup.Certificate')
        cert.code = 'cert1'
        dept.certificates.addCertificate(cert)
        cert.addCertCourse(course)

        self.browser = Browser()
        self.browser.handleErrors = False
        pass

    def tearDown(self):
        super(PermissionTest, self).tearDown()
        clearSite()
        shutil.rmtree(self.dc_root)
        return

    def isAccessible(self, path):
        path = 'http://localhost/app%s' % path
        try:
            self.browser.open(path)
            return True
        except Unauthorized:
            return False
        return

    def testUnauthenticatedUser(self):
        for path in manager_pages:
            if not self.isAccessible(path):
                continue
            self.fail('Path %s can be accessed by anonymous.' % path)
        for path in public_pages:
            if self.isAccessible(path):
                continue
            self.fail('Path %s cannot be accessed by anonymous.' % path)
        return
