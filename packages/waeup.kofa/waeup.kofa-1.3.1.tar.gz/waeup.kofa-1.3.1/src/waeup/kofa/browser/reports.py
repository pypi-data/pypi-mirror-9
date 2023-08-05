## $Id: reports.py 9680 2012-11-18 16:58:48Z henrik $
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
"""Browser components for report generation.
"""
import grok
from zope.component import getUtility, queryUtility
from zope.location.location import located
from waeup.kofa.interfaces import IJobManager, IKofaUtils
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.browser.layout import KofaPage
from waeup.kofa.reports import IReportsContainer, IReportGenerator
from waeup.kofa.reports import get_generators

grok.templatedir('templates')

class ReportsContainerPage(KofaPage):
    """A view on a reports container.
    """
    grok.name('index')
    grok.context(IReportsContainer)
    grok.require('waeup.manageReports')
    label = _('Reports')

    def _report_url(self, job_id):
        """Get the PDF download URL of a report.
        """
        return self.url(self.context, '%s/pdf' % job_id)

    def update(self, job_id=None, DISCARD=None, DOWNLOAD=None):
        self.entries = []
        if job_id and DISCARD:
            entry = self.context.report_entry_from_job_id(job_id)
            self.context.delete_report_entry(entry)
            self.flash('Report discarded: %s' % job_id)
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            grok.getSite().logger.info(
                '%s - report %s discarded' % (ob_class, job_id))
        self.entries = self._generate_entries(user_id=None)
        if job_id and DOWNLOAD:
            self.redirect(self._report_url(job_id))
            return
        return

    def _generate_entries(self, user_id=None):
        entries = []
        for entry in self.context.get_running_report_jobs(user_id=user_id):
            job_id, gen_name, user = entry
            job = getUtility(IJobManager).get(job_id)
            generator = queryUtility(IReportGenerator, name=gen_name)
            gen_title = getattr(generator, 'title', 'Unknown')
            args = ', '.join([str(x) for x in job.kwargs['kw'].values()])
            descr = '%s (%s)' % (gen_title, args)
            status = job.finished and 'ready' or 'running'
            status = job.failed and 'FAILED' or status
            starttime = getattr(job, 'begin_after', None)
            if starttime:
                starttime = starttime.astimezone(
                    getUtility(
                        IKofaUtils).tzinfo).strftime("%Y-%m-%d %H:%M:%S %Z")
            new_entry = (job_id, descr, status, job.finished, job.finished \
                and not job.failed, not job.finished, starttime, user)
            entries.append(new_entry)
        return entries


class ReportsContainerTraverser(grok.Traverser):
    """A traverser for reports containers.
    """
    grok.context(IReportsContainer)
    def traverse(self, name):
        """Return a report generator or report if one is registered under
        `name`.

        Generators are registered by their utility names while reports
        are looked up by their job id. So, `name` must be a report
        generator name or a valid job_id of a report job.
        """
        generators = dict(list(get_generators()))
        result = generators.get(name, None)
        if result:
            # give generator a location in URLs (make url() work)
            return located(result, self.context, name)
        result = self.context.report_entry_from_job_id(name)
        if result:
            manager = getUtility(IJobManager)
            job = manager.get(name)
            report = job.result
            return located(report, self.context, name)
        return None

class ReportsContainerCreate(KofaPage):
    """Create a new report.
    """
    grok.name('create')
    grok.context(IReportsContainer)
    grok.require('waeup.manageReports')
    label = _('Create report')

    def update(self, START_GENERATOR=None, generator=None):
        self.creators = self.get_creators()
        self.generator_names = [x[1] for x in self.creators]
        if START_GENERATOR and generator and generator in self.generator_names:
            self.redirect(self.url(self.context, generator))
        pass

    def get_creators(self):
        """Get all registered report generator names.

        Returns a list of tuples (<TITLE>, <NAME>) with ``<TITLE>``
        being a human readable description of the respective generator
        and ``<NAME>`` being the registration name with the ZCA.
        """
        result = [(gen.title, name) for name, gen in get_generators()]
        return result
