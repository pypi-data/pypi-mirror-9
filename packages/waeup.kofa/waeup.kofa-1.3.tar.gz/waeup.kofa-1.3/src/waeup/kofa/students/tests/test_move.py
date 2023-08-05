## $Id: test_move.py 10634 2013-09-21 08:27:47Z henrik $
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
Tests for moving objects in faculties.
"""
import os
from zope.catalog.interfaces import ICatalog
from zope.component import queryUtility
from waeup.kofa.university.department import Department
from waeup.kofa.students.tests.test_browser import StudentsFullSetup

class MoveObjectsInFaculties(StudentsFullSetup):

    def test_move_certificate(self):
        self.assertEqual(
            self.app['faculties']['fac1']['dep1'].certificates['CERT1'],
            self.certificate)
        self.app['faculties']['fac1']['dep2'] = Department(code=u'dep2')
        self.certificate.moveCertificate('fac1', 'dep2')
        self.assertEqual(
            self.app['faculties']['fac1']['dep2'].certificates['CERT1'],
            self.certificate)
        self.assertEqual(
            [key for key in self.app['faculties']['fac1'][
                'dep2'].certificates['CERT1'].keys()],
            [u'COURSE1_100'])
        self.assertEqual(
            self.student['studycourse'].certificate,
            self.certificate)

        # We can still find the certificate in the catalog
        cat = queryUtility(ICatalog, name='certificates_catalog')
        results = cat.searchResults(code=('CERT1','CERT1'))
        results = [x for x in results] # Turn results generator into list
        assert len(results) == 1
        assert results[0] is self.certificate

        # We can find the student studying in the new department
        cat = queryUtility(ICatalog, name='students_catalog')
        results = cat.searchResults(depcode=('dep2','dep2'))
        results = [x for x in results] # Turn results generator into list
        assert len(results) == 1
        assert results[0] is self.app['students'][self.student_id]
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'students.log')
        logcontent = open(logfile).read()
        self.assertTrue('INFO - system - K1000000 - Certificate moved'
            in logcontent)

