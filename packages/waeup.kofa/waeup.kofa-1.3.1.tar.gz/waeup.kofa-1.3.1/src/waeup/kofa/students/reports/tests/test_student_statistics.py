# Tests for student related reports
import os
from zc.async.testing import wait_for_result
from zope.interface.verify import verifyClass, verifyObject
from zope.component import getUtility
from waeup.kofa.interfaces import IJobManager
from waeup.kofa.students.reports.student_statistics import (
    get_student_stats, StudentStatisticsReport, IStudentStatisticsReport)
from waeup.kofa.students.tests.test_catalog import CatalogTestSetup
from waeup.kofa.students.tests.test_browser import StudentsFullSetup
from waeup.kofa.testing import FunctionalLayer
from waeup.kofa.tests.test_async import FunctionalAsyncTestCase
from waeup.kofa.browser.tests.test_pdf import samples_dir

class StudentStatisticsReportTests(CatalogTestSetup):

    layer = FunctionalLayer

    states = ('created', 'admitted', 'clearance started',
              'clearance requested', 'cleared', 'school fee paid',
              'courses registered', 'courses validated', 'returning',
              'graduated', 'transcript requested', 'Total')

    def test_iface(self):
        # ensure we fullfill interface contracts
        obj = StudentStatisticsReport(2010, 'Undergraduate Full-Time')
        verifyClass(IStudentStatisticsReport, StudentStatisticsReport)
        verifyObject(IStudentStatisticsReport, obj)
        return

    def test_get_student_stats_session_simple(self):
        # we can get a table with one student
        result1 = get_student_stats(2010, 'Undergraduate Full-Time')
        result2 = get_student_stats(2009, 'Undergraduate Full-Time')
        self.assertEqual(
            result1,
            ((u'fac1', u'Total',),
             self.states,
             ((1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
              (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),)))
        self.assertEqual(
            result2,
            ((u'fac1', u'Total'),
             self.states,
             ((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
              (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),)))
        return

    def test_get_student_stats_session_multiple(self):
        # we can get a table with several students
        self.create_cert(u'fac2', u'dept2', u'CERT2')
        result1 = get_student_stats(2010, 'Undergraduate Full-Time')
        result2 = get_student_stats(2009, 'Undergraduate Full-Time')
        self.assertEqual(
            result1,
            ((u'fac1', u'fac2', u'Total'),
             self.states,
             ((1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
              (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
              (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),)))
        self.assertEqual(
            result2,
            ((u'fac1', u'fac2', u'Total'),
             self.states,
             ((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
              (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
              (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),)))
        return

    def test_create_pdf(self):
        self.create_cert(u'FAC2', u'dept2', u'CERT2')
        report = StudentStatisticsReport(2010, 'Undergraduate Full-Time')
        result = report.create_pdf()
        self.assertTrue(result.startswith('%PDF-'))
        path = os.path.join(samples_dir(), 'student_statistics.pdf')
        open(path, 'wb').write(result)
        print "Sample PDF student_statistics.pdf written to %s" % path
        return

class StudentStatisticsReportUITests(StudentsFullSetup, FunctionalAsyncTestCase):

    layer = FunctionalLayer

    def wait_for_report_job_completed(self):
        # helper function waiting until the current export job is completed
        manager = getUtility(IJobManager)
        job_id = self.app['reports'].running_report_jobs[0][0]
        job = manager.get(job_id)
        wait_for_result(job)
        return job_id

    def stored_in_reports(self, job_id):
        # tell whether job_id is stored in reports's running jobs list
        for entry in list(self.app['reports'].running_report_jobs):
            if entry[0] == job_id:
                return True
        return False

    def trigger_report_creation(self):
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open('http://localhost/app/reports')
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.browser.getLink("Create new report").click()
        self.browser.getControl(name="generator").value = ['student_stats']
        self.browser.getControl("Configure").click()
        self.browser.getControl(name="mode").value = ['All']
        self.browser.getControl(name="session").value = ['2004']
        self.browser.getControl("Create").click()
        return

    def test_report_download(self):
        # We can download a generated report
        self.trigger_report_creation()
        # When the job is finished and we reload the page...
        job_id = self.wait_for_report_job_completed()
        self.browser.open('http://localhost/app/reports')
        # ... the pdf file can be downloaded ...
        self.browser.getControl("Download").click()
        self.assertEqual(self.browser.headers['content-type'],
                         'application/pdf')
        self.assertTrue(
            'filename="StudentStatisticsReport_2004_2005_All_' in
            self.browser.headers['content-disposition'])
        self.assertEqual(len(self.app['reports'].running_report_jobs), 1)
        job_id = self.app['reports'].running_report_jobs[0][0]
        # ... and discarded
        self.browser.open('http://localhost/app/reports')
        self.browser.getControl("Discard").click()
        self.assertEqual(len(self.app['reports'].running_report_jobs), 0)
        # Creation, downloading and discarding is logged
        logfile = os.path.join(
            self.app['datacenter'].storage, 'logs', 'main.log')
        logcontent = open(logfile).read()
        self.assertTrue(
            'INFO - zope.mgr - students.reports.student_statistics.StudentStatisticsReportGeneratorPage - '
            'report %s created: Student Statistics (session=2004, mode=All)'
            % job_id in logcontent
            )
        self.assertTrue(
            'INFO - zope.mgr - students.reports.student_statistics.StudentStatisticsReportPDFView - '
            'report %s downloaded: StudentStatisticsReport_2004_2005_All_'
            % job_id in logcontent
            )
        self.assertTrue(
            'INFO - zope.mgr - browser.reports.ReportsContainerPage - '
            'report %s discarded' % job_id in logcontent
            )
        return
