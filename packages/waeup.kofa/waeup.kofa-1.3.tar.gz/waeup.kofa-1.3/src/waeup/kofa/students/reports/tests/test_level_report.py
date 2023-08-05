import os
from zc.async.testing import wait_for_result
from zope.interface.verify import verifyClass, verifyObject
from zope.component import getUtility
from waeup.kofa.interfaces import IJobManager
from waeup.kofa.students.reports.level_report import (
    get_students, LevelReport, ILevelReport)
from waeup.kofa.students.tests.test_catalog import CatalogTestSetup
from waeup.kofa.students.tests.test_browser import StudentsFullSetup
from waeup.kofa.testing import FunctionalLayer
from waeup.kofa.tests.test_async import FunctionalAsyncTestCase
from waeup.kofa.browser.tests.test_pdf import samples_dir

class LevelReportTests(CatalogTestSetup):

    layer = FunctionalLayer

    def test_iface(self):
        # ensure we fullfill interface contracts
        obj = LevelReport('fac1', 'dep1', 2010, 100)
        verifyClass(ILevelReport, LevelReport)
        verifyObject(ILevelReport, obj)
        return

    def test_get_students(self):
        # we can get a table with one student
        result = get_students('fac1', 'dep1', 2010, 100)
        self.assertEqual(result,
            [(u'1234', u'Bob Tester', 30, 30, 5.0, [], 30, 30, 5.0)])
        return

    def test_create_pdf(self):
        report = LevelReport('fac1', 'dep1', 2010, 100)
        result = report.create_pdf()
        self.assertTrue(result.startswith('%PDF-'))
        path = os.path.join(samples_dir(), 'level_report.pdf')
        open(path, 'wb').write(result)
        print "Sample level_report.pdf written to %s" % path
        return

class LevelReportUITests(StudentsFullSetup, FunctionalAsyncTestCase):

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
        self.browser.getControl(name="generator").value = ['level_report']
        self.browser.getControl("Configure").click()
        self.browser.getControl(name="level").value = ['100']
        self.browser.getControl(name="session").value = ['2010']
        self.browser.getControl(name="faccode_depcode").value = ['fac1_dep1']
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
            'filename="LevelReport_fac1_dep1_2010_100_' in
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
            'INFO - zope.mgr - students.reports.level_report.LevelReportGeneratorPage - '
            'report %s created: Level Report (faculty=fac1, department=dep1, session=2010, level=100)'
            % job_id in logcontent
            )
        self.assertTrue(
            'INFO - zope.mgr - students.reports.level_report.LevelReportPDFView - '
            'report %s downloaded: LevelReport_fac1_dep1_2010_100_'
            % job_id in logcontent
            )
        self.assertTrue(
            'INFO - zope.mgr - browser.reports.ReportsContainerPage - '
            'report %s discarded' % job_id in logcontent
            )
        return