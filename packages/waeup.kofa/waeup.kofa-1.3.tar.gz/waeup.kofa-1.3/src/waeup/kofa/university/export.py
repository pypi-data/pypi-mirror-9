## $Id: export.py 10185 2013-05-22 06:45:17Z henrik $
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
"""Exporters for faculties, departments, and other academics components.
"""
import grok
from zope.securitypolicy.interfaces import IPrincipalRoleMap
from waeup.kofa.interfaces import ICSVExporter
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.utils.batching import ExporterBase

class FacultyExporter(grok.GlobalUtility, ExporterBase):
    """Exporter for faculties.
    """
    grok.implements(ICSVExporter)
    grok.name('faculties')

    #: Fieldnames considered by this exporter
    fields = ('code', 'title', 'title_prefix', 'users_with_local_roles')

    #: The title under which this exporter will be displayed
    title = _(u'Faculties')

    def mangle_value(self, value, name, context=None):
        """Hook for mangling values in derived classes
        """
        if name == 'users_with_local_roles':
            value = []
            role_map = IPrincipalRoleMap(context)
            for local_role, user_name, setting in role_map.getPrincipalsAndRoles():
                value.append({'user_name':user_name,'local_role':local_role})
        return super(FacultyExporter, self).mangle_value(
            value, name, context)

    def export(self, faculties, filepath=None):
        """Export `faculties`, an iterable, as CSV file.

        If `filepath` is ``None``, a raw string with CSV data is returned.
        """
        writer, outfile = self.get_csv_writer(filepath)
        for faculty in faculties:
            self.write_item(faculty, writer)
        return self.close_outfile(filepath, outfile)

    def export_all(self, site, filepath=None):
        """Export faculties in facultycontainer into filepath as CSV data.

        If `filepath` is ``None``, a raw string with CSV data is returned.
        """
        faculties = site.get('faculties', {})
        return self.export(faculties.values(), filepath)

class DepartmentExporter(FacultyExporter, grok.GlobalUtility):
    """Exporter for departments.
    """
    grok.implements(ICSVExporter)
    grok.name('departments')

    #: Fieldnames considered by this exporter
    fields = ('code', 'faculty_code', 'title', 'title_prefix',
        'users_with_local_roles')

    #: The title under which this exporter will be displayed
    title = _(u'Departments')

    def mangle_value(self, value, name, context=None):
        """Hook for mangling values in derived classes
        """
        if name == 'faculty_code':
            value = getattr(
                getattr(context, '__parent__', None),
                'code', None)
        return super(DepartmentExporter, self).mangle_value(
            value, name, context)

    def export_all(self, site, filepath=None):
        """Export departments in faculty into filepath as CSV data.

        If `filepath` is ``None``, a raw string with CSV data is returned.
        """
        writer, outfile = self.get_csv_writer(filepath)
        faculties = site.get('faculties', {})
        for faculty in faculties.values():
            for department in faculty.values():
                self.write_item(department, writer)
        return self.close_outfile(filepath, outfile)


class CourseExporter(FacultyExporter, grok.GlobalUtility):
    """Exporter for courses.
    """
    grok.implements(ICSVExporter)
    grok.name('courses')

    #: Fieldnames considered by this exporter
    fields = ('code', 'faculty_code', 'department_code', 'title', 'credits',
              'passmark', 'semester', 'users_with_local_roles', 'former_course')

    #: The title under which this exporter will be displayed
    title = _(u'Courses')

    def mangle_value(self, value, name, context=None):
        """Hook for mangling values in derived classes
        """
        if name == 'users_with_local_roles':
            value = []
            role_map = IPrincipalRoleMap(context)
            for local_role, user_name, setting in role_map.getPrincipalsAndRoles():
                value.append({'user_name':user_name,'local_role':local_role})
        elif name == 'faculty_code':
            try:
                value = context.__parent__.__parent__.__parent__.code
            except AttributeError:
                value = None
        elif name == 'department_code':
            try:
                value = context.__parent__.__parent__.code
            except AttributeError:
                value = None
        return super(CourseExporter, self).mangle_value(
            value, name, context)

    def export_all(self, site, filepath=None):
        """Export courses into filepath as CSV data.

        If `filepath` is ``None``, a raw string with CSV data is returned.
        """
        writer, outfile = self.get_csv_writer(filepath)
        faculties = site.get('faculties', {})
        for faculty in faculties.values():
            for department in faculty.values():
                for course in department.courses.values():
                    self.write_item(course, writer)
        return self.close_outfile(filepath, outfile)

class CertificateExporter(CourseExporter, grok.GlobalUtility):
    """Exporter for courses.
    """
    grok.implements(ICSVExporter)
    grok.name('certificates')

    #: Fieldnames considered by this exporter
    fields = ('code', 'faculty_code', 'department_code', 'title', 'study_mode',
              'start_level', 'end_level', 'application_category', 'ratio',
              'school_fee_1', 'school_fee_2', 'school_fee_3', 'school_fee_4',
              'custom_textline_1', 'custom_textline_2',
              'custom_float_1', 'custom_float_2',
              'users_with_local_roles')

    #: The title under which this exporter will be displayed
    title = _(u'Certificates')

    def export_all(self, site, filepath=None):
        """Export certificates into filepath as CSV data.

        If `filepath` is ``None``, a raw string with CSV data is returned.
        """
        writer, outfile = self.get_csv_writer(filepath)
        faculties = site.get('faculties', {})
        for faculty in faculties.values():
            for department in faculty.values():
                for cert in department.certificates.values():
                    self.write_item(cert, writer)
        return self.close_outfile(filepath, outfile)

class CertificateCourseExporter(CourseExporter, grok.GlobalUtility):
    """Exporter for courses.
    """
    grok.implements(ICSVExporter)
    grok.name('certificate_courses')

    #: Fieldnames considered by this exporter
    fields = ('course', 'faculty_code', 'department_code', 'certificate_code',
              'level', 'mandatory')

    #: The title under which this exporter will be displayed
    title = _(u'Courses in Certificates')

    def mangle_value(self, value, name, context=None):
        """Hook for mangling values in derived classes
        """
        if name == 'faculty_code':
            try:
                value = context.__parent__.__parent__.__parent__.__parent__.code
            except AttributeError:
                value = None
        elif name == 'department_code':
            try:
                value = context.__parent__.__parent__.__parent__.code
            except AttributeError:
                value = None
        elif name == 'certificate_code':
            value = getattr(context, '__parent__', None)
            value = getattr(value, 'code', None)
        if name == 'course':
            value = getattr(value, 'code', None)
        return super(CourseExporter, self).mangle_value(
            value, name, context)

    def export_all(self, site, filepath=None):
        """Export certificate courses into filepath as CSV data.

        If `filepath` is ``None``, a raw string with CSV data is returned.
        """
        writer, outfile = self.get_csv_writer(filepath)
        faculties = site.get('faculties', {})
        for faculty in faculties.values():
            for department in faculty.values():
                for cert in department.certificates.values():
                    for certref in cert.values():
                        self.write_item(certref, writer)
        return self.close_outfile(filepath, outfile)
