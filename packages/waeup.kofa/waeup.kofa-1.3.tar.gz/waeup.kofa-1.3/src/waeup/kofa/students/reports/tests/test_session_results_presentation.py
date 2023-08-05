import os
from zc.async.testing import wait_for_result
from zope.event import notify
from zope.interface.verify import verifyClass, verifyObject
from zope.component import getUtility
from waeup.kofa.interfaces import IJobManager
from waeup.kofa.students.reports.session_results_presentation import (
    get_students, SessionResultsPresentation, ISessionResultsPresentation)
from waeup.kofa.students.tests.test_catalog import CatalogTestSetup
from waeup.kofa.students.tests.test_browser import StudentsFullSetup
from waeup.kofa.testing import FunctionalLayer
from waeup.kofa.tests.test_async import FunctionalAsyncTestCase
from waeup.kofa.browser.tests.test_pdf import samples_dir
from waeup.kofa.students.studylevel import StudentStudyLevel

class SessionResultsPresentationTests(CatalogTestSetup):

    layer = FunctionalLayer

    def test_iface(self):
        # ensure we fullfill interface contracts
        obj = SessionResultsPresentation('fac1', 'dep1', 2010, 100)
        verifyClass(ISessionResultsPresentation, SessionResultsPresentation)
        verifyObject(ISessionResultsPresentation, obj)
        return

    def test_get_students(self):
        result = get_students('fac1', 'dep1', 2010, 100)
        self.assertEqual(result,
            [[], [], [], [], [], [(u'K1000000', u'1234', u'Bob Tester')], []])
        return

    def test_get_students_at_all_levels(self):
        result = get_students('fac1', 'dep1', 2010)
        self.assertEqual(result,
            [[], [], [], [], [], [(u'K1000000', u'1234', u'Bob Tester')], []])
        return

    def test_get_students_with_two_levels_in_session(self):
        # Register second level in the same session (which shouldn't be!)
        studylevel = StudentStudyLevel()
        studylevel.level = 200
        studylevel.level_session = 2010
        self.student['studycourse']['200'] = studylevel
        result = get_students('fac1', 'dep1', 2010)
        self.assertEqual(result,
            [[], [], [], [], [], [], [(u'K1000000', u'1234', u'Bob Tester')]])
        return

    def test_get_students_without_scores(self):
        self.student['studycourse']['100']['Course1'].score = None
        result = get_students('fac1', 'dep1', 2010)
        self.assertEqual(result,
            [[], [], [], [], [], [], [(u'K1000000', u'1234', u'Bob Tester')]])

    def test_get_students_without_level_in_session(self):
        self.student['studycourse']['100'].level_session = 2011
        result = get_students('fac1', 'dep1', 2010)
        self.assertEqual(result,
            [[], [], [], [], [], [], []])
        return

    def test_create_pdf(self):
        report = SessionResultsPresentation('fac1', 'dep1', 2010, 100)
        result = report.create_pdf()
        self.assertTrue(result.startswith('%PDF-'))
        path = os.path.join(samples_dir(), 'session_results_presentation.pdf')
        open(path, 'wb').write(result)
        print "Sample session_results_presentation.pdf written to %s" % path
        return

    def test_create_pdf_with_two_levels_in_session(self):
        # Register second level in the same session (which shouldn't be!)
        # Check the pdf file if the student record has really been classified
        # as erroneous.
        studylevel = StudentStudyLevel()
        studylevel.level = 200
        studylevel.level_session = 2010
        self.student['studycourse']['200'] = studylevel
        report = SessionResultsPresentation('fac1', 'dep1', 2010, None)
        result = report.create_pdf()
        self.assertTrue(result.startswith('%PDF-'))
        path = os.path.join(samples_dir(), 'session_results_presentation_erroneous.pdf')
        open(path, 'wb').write(result)
        print "Sample session_results_presentation_erroneous.pdf written to %s" % path
        return

class SessionResultsPresentationUITests(StudentsFullSetup, FunctionalAsyncTestCase):

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

    def trigger_report_creation(self, level='100'):
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.open('http://localhost/app/reports')
        self.assertEqual(self.browser.headers['Status'], '200 Ok')
        self.browser.getLink("Create new report").click()
        self.browser.getControl(name="generator").value = ['session_results_presentation']
        self.browser.getControl("Configure").click()
        self.browser.getControl(name="level").value = [level]
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
            'filename="SessionResultsPresentation_fac1_dep1_2010_100_' in
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
            'INFO - zope.mgr - students.reports.session_results_presentation.SessionResultsPresentationGeneratorPage - '
            'report %s created: Session Results Presentation (faculty=fac1, department=dep1, session=2010, level=100)'
            % job_id in logcontent
            )
        self.assertTrue(
            'INFO - zope.mgr - students.reports.session_results_presentation.SessionResultsPresentationPDFView - '
            'report %s downloaded: SessionResultsPresentation_fac1_dep1_2010_100_'
            % job_id in logcontent
            )
        self.assertTrue(
            'INFO - zope.mgr - browser.reports.ReportsContainerPage - '
            'report %s discarded' % job_id in logcontent
            )

        return

    def test_report_download_all_levels(self):
        # We can download a generated report for all levels
        self.trigger_report_creation(level='all')
        # When the job is finished and we reload the page...
        job_id = self.wait_for_report_job_completed()
        self.browser.open('http://localhost/app/reports')
        # ... the pdf file can be downloaded ...
        self.browser.getControl("Download").click()
        self.assertEqual(self.browser.headers['content-type'],
                         'application/pdf')
        self.assertTrue(
            'filename="SessionResultsPresentation_fac1_dep1_2010_None_' in
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
            'INFO - zope.mgr - students.reports.session_results_presentation.SessionResultsPresentationGeneratorPage - '
            'report %s created: Session Results Presentation (faculty=fac1, department=dep1, session=2010, level=None)'
            % job_id in logcontent
            )
        self.assertTrue(
            'INFO - zope.mgr - students.reports.session_results_presentation.SessionResultsPresentationPDFView - '
            'report %s downloaded: SessionResultsPresentation_fac1_dep1_2010_None_'
            % job_id in logcontent
            )
        self.assertTrue(
            'INFO - zope.mgr - browser.reports.ReportsContainerPage - '
            'report %s discarded' % job_id in logcontent
            )

        return