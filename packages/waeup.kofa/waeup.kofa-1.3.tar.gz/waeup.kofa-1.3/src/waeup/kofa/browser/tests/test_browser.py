## $Id: test_browser.py 11730 2014-07-04 07:46:16Z henrik $
## 
## Copyright (C) 2011-2013 Uli Fouquet & Henrik Bettermann
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
Extends the doctests in browser.txt and datacenter.txt.
"""
import shutil
import tempfile
import os
from zc.async.testing import wait_for_result
from zope.component import createObject, getUtility
from zope.component.hooks import setSite, clearSite
from zope.security.interfaces import Unauthorized
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.testbrowser.testing import Browser
from waeup.kofa.testing import FunctionalLayer, FunctionalTestCase
from waeup.kofa.app import University
from waeup.kofa.interfaces import IJobManager
from waeup.kofa.tests.test_async import FunctionalAsyncTestCase
from waeup.kofa.university.faculty import Faculty
from waeup.kofa.university.department import Department

SAMPLE_FILE = os.path.join(os.path.dirname(__file__), 'test_file.csv')
FORBIDDEN_FILE = os.path.join(os.path.dirname(__file__), 'forbidden_file.csv')

class UniversitySetup(FunctionalTestCase):
    # A test case that only contains a setup and teardown

    layer = FunctionalLayer

    def setUp(self):
        super(UniversitySetup, self).setUp()

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

        # Populate university
        self.certificate = createObject('waeup.Certificate')
        self.certificate.code = u'CERT1'
        self.certificate.application_category = 'basic'
        self.certificate.study_mode = 'ug_ft'
        self.certificate.start_level = 100
        self.certificate.end_level = 500
        self.certificate.school_fee_1 = 40000.0
        self.certificate.school_fee_2 = 20000.0
        self.app['faculties']['fac1'] = Faculty(code='fac1')
        self.app['faculties']['fac1']['dep1'] = Department(code=u'dep1')
        self.app['faculties']['fac1']['dep1'].certificates.addCertificate(
            self.certificate)
        self.course = createObject('waeup.Course')
        self.course.code = 'COURSE1'
        self.course.semester = 1
        self.course.credits = 10
        self.course.passmark = 40
        self.app['faculties']['fac1']['dep1'].courses.addCourse(
            self.course)
        self.app['faculties']['fac1']['dep1'].certificates['CERT1'].addCertCourse(
            self.course, level=100)

        # Configure university and hostels
        configuration = createObject('waeup.SessionConfiguration')
        configuration.academic_session = 2004
        configuration.clearance_fee = 3456.0
        configuration.booking_fee = 123.4
        self.app['configuration'].addSessionConfiguration(configuration)

        # Put the prepopulated site into test ZODB and prepare test
        # browser
        self.browser = Browser()
        self.browser.handleErrors = False

        self.datacenter_path = 'http://localhost/app/datacenter'

    def tearDown(self):
        super(UniversitySetup, self).tearDown()
        clearSite()
        shutil.rmtree(self.dc_root)

class DataCenterUITests(UniversitySetup):
    # Tests for DataCenter class views and pages

    layer = FunctionalLayer

    def test_anonymous_access(self):
        self.assertRaises(
            Unauthorized, self.browser.open, self.datacenter_path)
        return

    def test_file_download_delete(self):
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.datacenter_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertEqual(self.browser.url, self.datacenter_path)
        self.browser.getLink("Upload data").click()
        file = open(SAMPLE_FILE)
        ctrl = self.browser.getControl(name='uploadfile:file')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(file, filename='my_test_data.csv')
        self.browser.getControl('Upload').click()
        self.browser.open(self.datacenter_path)
        self.browser.getLink('my_test_data_zope.mgr.csv').click()
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertEqual(self.browser.headers['Content-Type'],
                         'text/csv; charset=UTF-8')
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'datacenter.log')
        logcontent = open(logfile).read()
        self.assertTrue('zope.mgr - browser.pages.FileDownloadView - '
                        'downloaded: my_test_data_zope.mgr.csv' in logcontent)
        self.browser.open(self.datacenter_path)
        ctrl = self.browser.getControl(name='val_id')
        ctrl.getControl(value='my_test_data_zope.mgr.csv').selected = True
        self.browser.getControl("Remove selected", index=0).click()
        self.assertTrue('Successfully deleted: my_test_data_zope.mgr.csv'
            in self.browser.contents)
        logcontent = open(logfile).read()
        self.assertTrue('zope.mgr - browser.pages.DatacenterPage - '
                        'deleted: my_test_data_zope.mgr.csv' in logcontent)
        return

    def test_forbidden_file_upload(self):
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.datacenter_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertEqual(self.browser.url, self.datacenter_path)
        self.browser.getLink("Upload data").click()
        file = open(FORBIDDEN_FILE)
        ctrl = self.browser.getControl(name='uploadfile:file')
        file_ctrl = ctrl.mech_control
        file_ctrl.add_file(file, filename='my_corrupted_file.csv')
        self.browser.getControl('Upload').click()
        self.assertTrue(
            'Your file contains forbidden characters or'
            in self.browser.contents)
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'datacenter.log')
        logcontent = open(logfile).read()
        self.assertTrue('zope.mgr - browser.pages.DatacenterUploadPage - '
            'invalid file uploaded:' in logcontent)
        return

class DataCenterUIExportTests(UniversitySetup, FunctionalAsyncTestCase):
    # Tests for DataCenter class views and pages

    layer = FunctionalLayer

    def wait_for_export_job_completed(self):
        # helper function waiting until the current export job is completed
        manager = getUtility(IJobManager)
        job_id = self.app['datacenter'].running_exports[0][0]
        job = manager.get(job_id)
        wait_for_result(job)
        return job_id

    def stored_in_datacenter(self, job_id):
        # tell whether job_id is stored in datacenter's running jobs list
        for entry in list(self.app['datacenter'].running_exports):
            if entry[0] == job_id:
                return True
        return False

    def trigger_export(self):
        # helper to start an export. Make sure to remove the result file
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.datacenter_path)
        self.browser.getLink("Export data").click()
        self.browser.getControl(name="exporter").value = ['faculties']
        self.browser.getControl("Create CSV file").click()
        return

    def cleanup_run_job(self):
        # helper to remove any result file of an export
        job_id = self.wait_for_export_job_completed()
        manager = getUtility(IJobManager)
        job = manager.get(job_id)
        if os.path.exists(job.result):
            shutil.rmtree(os.path.dirname(job.result))

    def test_export_start(self):
        # we can trigger export file creation
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.datacenter_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertEqual(self.browser.url, self.datacenter_path)
        self.browser.getLink("Export data").click()
        self.browser.getControl(name="exporter").value = ['faculties']
        self.browser.getControl("Create CSV file").click()
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.cleanup_run_job() # make sure to remove temp dirs
        return

    def test_export_download(self):
        # we can download a generated export result
        self.trigger_export()
        # while the export file is created, we get a reload button
        # (or a loading bar if javascript is enabled)...
        self.assertTrue('Reload' in self.browser.contents)
        # ...which is displayed as long as the job is not finished.
        # When the job is finished and we reload the page...
        job_id = self.wait_for_export_job_completed()
        self.browser.open(self.datacenter_path + '/export')
        self.assertFalse('Reload' in self.browser.contents)
        # ...we can download the result
        self.browser.getLink("Download").click()
        self.assertEqual(self.browser.headers['content-type'],
                         'text/csv; charset=UTF-8')
        self.assertEqual(self.browser.headers['content-disposition'],
            'attachment; filename="WAeUP.Kofa_faculties_%s.csv' % job_id)
        self.assertEqual(self.browser.contents,
            'code,title,title_prefix,users_with_local_roles\r\n'
            'fac1,Unnamed Faculty,faculty,[]\r\n')
        # Thew job can be discarded
        self.browser.open(self.datacenter_path + '/export')
        self.browser.getControl("Discard").click()
        self.assertEqual(len(self.app['datacenter'].running_exports), 0)

        # after download, the job and the result file are removed
        #manager = getUtility(IJobManager)
        #result = manager.get(job_id)
        #self.assertEqual(result, None)
        #self.assertEqual(self.stored_in_datacenter(job_id), False)
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'datacenter.log')
        logcontent = open(logfile).read()
        self.assertTrue('zope.mgr - browser.pages.ExportCSVPage - exported: '
                        'faculties, job_id=' in logcontent)
        self.assertTrue('zope.mgr - browser.pages.ExportCSVView - '
                        'downloaded: WAeUP.Kofa_faculties_%s.csv, job_id=%s'
                        % (job_id, job_id) in logcontent)
        return

    def test_export_accesscodes(self):
        # Create portal manager and an ExportManager
        self.app['users'].addUser('mrportal', 'mrportalsecret')
        self.app['users']['mrportal'].email = 'mrportal@foo.ng'
        self.app['users']['mrportal'].title = 'Carlo Pitter'
        # Assign PortalManager role
        prmlocal = IPrincipalRoleManager(self.app)
        prmlocal.assignRoleToPrincipal('waeup.PortalManager', 'mrportal')
        self.app['users'].addUser('mrexporter', 'mrexportersecret')
        self.app['users']['mrexporter'].email = 'mrexporter@foo.ng'
        self.app['users']['mrexporter'].title = 'Carlos Potter'
        # Assign ExportManager role
        prmlocal.assignRoleToPrincipal('waeup.ExportManager', 'mrexporter')

        # Login as portal manager
        self.browser.open('http://localhost/app/login')
        self.browser.getControl(name="form.login").value = 'mrportal'
        self.browser.getControl(name="form.password").value = 'mrportalsecret'
        self.browser.getControl("Login").click()

        self.browser.open(self.datacenter_path + '/export')
        self.assertTrue(
            '<option value="accesscodebatches">' in self.browser.contents)
        self.assertTrue('<option value="accesscodes">' in self.browser.contents)
        self.browser.getControl(name="exporter").value = ['accesscodes']
        self.browser.getControl("Create CSV file").click()
        job_id = self.wait_for_export_job_completed()
        self.browser.open(self.datacenter_path + '/@@export')
        self.browser.getLink("Download").click()
        self.assertEqual(self.browser.headers['content-type'],
                         'text/csv; charset=UTF-8')
        self.assertEqual(
            'batch_num,batch_prefix,batch_serial,cost,history,owner,'
            'random_num,representation,state\r\n',
            self.browser.contents)

        # Thew job can be discarded
        self.browser.open(self.datacenter_path + '/export')
        self.browser.getControl("Discard").click()
        self.assertEqual(len(self.app['datacenter'].running_exports), 0)

        # Login as officer who is not allowed to download accesscodes
        self.browser.open('http://localhost/app/login')
        self.browser.getControl(name="form.login").value = 'mrexporter'
        self.browser.getControl(name="form.password").value = 'mrexportersecret'
        self.browser.getControl("Login").click()

        self.browser.open(self.datacenter_path + '/export')
        # The Export Manager can see the accesscodebatches exporter ...
        self.assertTrue(
            '<option value="accesscodebatches">' in self.browser.contents)
        # ... but not the accesscodes exporter.
        self.assertFalse('<option value="accesscodes">'
                         in self.browser.contents)

    def test_export_students(self):
        # we can trigger export file creation
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.datacenter_path)
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertEqual(self.browser.url, self.datacenter_path)
        self.browser.getLink("Export data").click()
        self.browser.getLink("configuration page").click()
        self.browser.getControl(name="exporter").value = ['students']
        self.browser.getControl(name="session").value = ['all']
        self.browser.getControl(name="level").value = ['all']
        self.browser.getControl(name="mode").value = ['all']
        self.browser.getControl("Create CSV file").click()
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        job_id = self.wait_for_export_job_completed()
        self.browser.open(self.datacenter_path + '/export')
        self.browser.getLink("Download").click()
        self.assertEqual(self.browser.headers['content-type'],
          'text/csv; charset=UTF-8')
        self.assertEqual(self.browser.headers['content-disposition'],
          'attachment; filename="WAeUP.Kofa_students_%s.csv' % job_id)
        # No students yet
        self.assertEqual(self.browser.contents,
            'adm_code,clearance_locked,clr_code,date_of_birth,email,'
            'employer,firstname,lastname,matric_number,middlename,'
            'nationality,officer_comment,perm_address,personal_updated,'
            'phone,reg_number,sex,student_id,suspended,suspended_comment,'
            'transcript_comment,'
            'password,state,history,certcode,is_postgrad,current_level,'
            'current_session\r\n')
        self.cleanup_run_job()
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'datacenter.log')
        logcontent = open(logfile).read()
        self.assertTrue(
            'zope.mgr - students.browser.DatacenterExportJobContainerJobConfig '
            '- exported: students (None, None, None, None, None, None, None), '
            'job_id=%s'
            % job_id in logcontent)
        self.assertTrue(
            'zope.mgr - browser.pages.ExportCSVView '
            '- downloaded: WAeUP.Kofa_students_%s.csv, job_id=%s'
            % (job_id, job_id) in logcontent)
        return

    def test_export_discard(self):
        # we can discard a generated export result
        self.trigger_export()
        self.wait_for_export_job_completed()
        self.browser.open(self.datacenter_path + '/@@export')
        self.browser.getControl("Discard").click()
        self.assertTrue('Discarded export' in self.browser.contents)
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'datacenter.log')
        logcontent = open(logfile).read()
        self.assertTrue(
            'zope.mgr - browser.pages.ExportCSVPage - discarded: job_id='
            in logcontent)
        return

    def test_skeleton_download(self):
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open(self.datacenter_path)
        self.browser.getLink("Upload data").click()
        self.browser.getLink(url='skeleton?name=facultyprocessor').click()
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.assertEqual(self.browser.headers['Content-Type'],
                         'text/csv; charset=UTF-8')
        self.assertEqual(self.browser.contents,
            'code,local_roles,title,title_prefix\r\n')
        return

class SupplementaryBrowserTests(UniversitySetup):
    # These are additional tests to browser.txt

    def test_set_former_course(self):
        # A certificate course will be automatically removed when the
        # former_course attribute of the corresponding course is set.
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.assertTrue('COURSE1_100' in self.app[
            'faculties']['fac1']['dep1'].certificates['CERT1'])
        self.browser.open(
            'http://localhost/app/faculties/fac1/dep1/courses/COURSE1/manage')
        self.browser.getControl(name="form.former_course").value = ['selected']
        self.browser.getControl("Save").click()
        self.assertFalse('COURSE1_100' in self.app[
            'faculties']['fac1']['dep1'].certificates['CERT1'])
        return

    def test_remove_course(self):
        # We add a second certificate course which refers
        # to the same course but at a different level.
        self.app['faculties']['fac1']['dep1'].certificates['CERT1'].addCertCourse(
            self.course, level=210)
        # Both certificate courses will be automatically removed when
        # the corresponding course is removed.
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.assertTrue('COURSE1_100' in self.app[
            'faculties']['fac1']['dep1'].certificates['CERT1'])
        self.assertTrue('COURSE1_210' in self.app[
            'faculties']['fac1']['dep1'].certificates['CERT1'])
        self.browser.open('http://localhost/app/faculties/fac1/dep1/manage')
        ctrl = self.browser.getControl(name='val_id')
        ctrl.getControl(value='COURSE1').selected = True
        self.browser.getControl("Remove selected", index=0).click()
        self.assertFalse('COURSE1_100' in self.app[
            'faculties']['fac1']['dep1'].certificates['CERT1'])
        self.assertFalse('COURSE1_210' in self.app[
            'faculties']['fac1']['dep1'].certificates['CERT1'])
        return
