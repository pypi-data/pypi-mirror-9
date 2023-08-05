## $Id: export.py 12180 2014-12-09 05:21:31Z henrik $
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
"""Exporters for applicant-related stuff.
"""
import grok
from zope.catalog.interfaces import ICatalog
from zope.component import queryUtility
from waeup.kofa.applicants.interfaces import (
    IApplicantBaseData, IApplicantsContainer)
from waeup.kofa.interfaces import ICSVExporter
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.utils.batching import ExporterBase
from waeup.kofa.utils.helpers import iface_names

class ApplicantsContainerExporter(grok.GlobalUtility, ExporterBase):
    """Exporter for ApplicantsContainers.
    """
    grok.implements(ICSVExporter)
    grok.name('applicantscontainers')

    #: Fieldnames considered by this exporter
    fields = tuple(sorted(iface_names(IApplicantsContainer)))
    #: The title under which this exporter will be displayed
    title = _(u'Applicants Containers')

    def mangle_value(self, value, name, context=None):
        return super(
            ApplicantsContainerExporter, self).mangle_value(
            value, name, context=context)

    def export(self, containers, filepath=None):
        """Export `containers`, an iterable, as CSV file.

        If `filepath` is ``None``, a raw string with CSV data is returned.
        """
        writer, outfile = self.get_csv_writer(filepath)
        for container in containers:
            self.write_item(container, writer)
        return self.close_outfile(filepath, outfile)

    def export_all(self, site, filepath=None):
        """Export applicantscontainer into filepath as CSV data.

        If `filepath` is ``None``, a raw string with CSV data is returned.
        """
        writer, outfile = self.get_csv_writer(filepath)
        containers = site.get('applicants', {})
        return self.export(containers.values(), filepath)

class ApplicantExporter(grok.GlobalUtility, ExporterBase):
    """Exporter for Applicants.
    """
    grok.implements(ICSVExporter)
    grok.name('applicants')

    #: Fieldnames considered by this exporter
    fields = tuple(sorted(IApplicantBaseData.names())) + ('container_code',)

    #: The title under which this exporter will be displayed
    title = _(u'Applicants')

    def mangle_value(self, value, name, context=None):
        if name in (
            'course1', 'course2', 'course_admitted') and value is not None:
            value = value.code
        #elif name == 'school_grades':
        #    value = [eval(entry.to_string()) for entry in value]
        elif name == 'history':
            value = value.messages
        elif name == 'phone' and value is not None:
            # Append hash '#' to phone numbers to circumvent
            # unwanted excel automatic
            value = str('%s#' % value)
        return super(
            ApplicantExporter, self).mangle_value(
            value, name, context=context)

    def export(self, applicants, filepath=None):
        """Export `applicants`, an iterable, as CSV file.

        If `filepath` is ``None``, a raw string with CSV data is returned.
        """
        writer, outfile = self.get_csv_writer(filepath)
        for applicant in applicants:
            self.write_item(applicant, writer)
        return self.close_outfile(filepath, outfile)

    def export_all(self, site, filepath=None):
        """Export applicants into filepath as CSV data.

        If `filepath` is ``None``, a raw string with CSV data is returned.
        """
        catalog = queryUtility(
            ICatalog, context=site, name='applicants_catalog', default=None)
        if catalog is None:
            return self.export([], filepath)
        applicants = catalog.searchResults(
            # reg_num might not be set and then would not be found.
            # We therefore search for applicant_id.
            applicant_id=(None, None))
        return self.export(applicants, filepath)

    def export_filtered(self, site, filepath=None, **kw):
        """Export applicants in container.

        If `filepath` is ``None``, a raw string with CSV data should
        be returned.
        """
        container = grok.getSite()['applicants'][kw['container']]
        return self.export(container.values(), filepath=filepath)
