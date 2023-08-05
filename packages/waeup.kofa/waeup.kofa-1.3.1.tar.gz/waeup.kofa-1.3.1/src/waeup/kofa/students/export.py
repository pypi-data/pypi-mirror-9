## $Id: export.py 12104 2014-12-01 14:43:16Z henrik $
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
"""Exporters for student related stuff.
"""
import os
import grok
from datetime import datetime
from zope.component import getUtility
from waeup.kofa.interfaces import (
    IExtFileStore, IFileStoreNameChooser, IKofaUtils)
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.students.catalog import StudentsQuery, CourseTicketsQuery
from waeup.kofa.students.interfaces import (
    IStudent, IStudentStudyCourse, IStudentStudyLevel, ICourseTicket,
    IStudentOnlinePayment, ICSVStudentExporter, IBedTicket)
from waeup.kofa.students.vocabularies import study_levels
from waeup.kofa.utils.batching import ExporterBase
from waeup.kofa.utils.helpers import iface_names, to_timezone


def get_students(site, stud_filter=StudentsQuery()):
    """Get all students registered in catalog in `site`.
    """
    return stud_filter.query()

def get_studycourses(students):
    """Get studycourses of `students`.
    """
    return [x.get('studycourse', None) for x in students
            if x is not None]

def get_levels(students):
    """Get all studylevels of `students`.
    """
    levels = []
    for course in get_studycourses(students):
        for level in course.values():
            levels.append(level)
    return levels

def get_tickets(students, **kw):
    """Get course tickets of `students`.

    If code is passed through, filter course tickets
    which belong to this course code and meets level
    and level_session.
    """
    tickets = []
    code = kw.get('code', None)
    level = kw.get('level', None)
    level_session = kw.get('level_session', None)
    if code is None:
        for level_obj in get_levels(students):
            for ticket in level_obj.values():
                tickets.append(ticket)
    else:
        for level_obj in get_levels(students):
            for ticket in level_obj.values():
                if ticket.code != code:
                    continue
                if level is not None:
                    level = int(level)
                    if level_obj.level in (10, 999, None)  \
                        and int(level) != level_obj.level:
                        continue
                    if level_obj.level not in range(level, level+100, 10):
                        continue
                if level_session is not None and \
                    int(level_session) != level_obj.level_session:
                    continue
                tickets.append(ticket)
    return tickets

def get_payments(students, paid=False, **kw):
    """Get all payments of `students` within given payment_date period.

    """
    date_format = '%d/%m/%Y'
    payments = []
    payments_start = kw.get('payments_start')
    payments_end = kw.get('payments_end')
    if payments_start and payments_end:
        # Payment period given
        payments_start = datetime.strptime(payments_start, date_format)
        payments_end = datetime.strptime(payments_end, date_format)
        tz = getUtility(IKofaUtils).tzinfo
        payments_start = tz.localize(payments_start)
        payments_end = tz.localize(payments_end)
        if paid:
            # Only paid tickets in payment period are considered
            for student in students:
                for payment in student.get('payments', {}).values():
                    if payment.payment_date and payment.p_state == 'paid':
                        payment_date = to_timezone(payment.payment_date, tz)
                        if payment_date > payments_start and \
                            payment_date < payments_end:
                            payments.append(payment)
        else:
            # All tickets in payment period are considered
            for student in students:
                for payment in student.get('payments', {}).values():
                    if payment.payment_date:
                        payment_date = to_timezone(payment.payment_date, tz)
                        if payment_date > payments_start and \
                            payment_date < payments_end:
                            payments.append(payment)
    else:
        # Payment period not given
        if paid:
            # Only paid tickets are considered
            for student in students:
                for payment in student.get('payments', {}).values():
                    if payment.p_state == 'paid':
                        payments.append(payment)
        else:
            # All tickets are considered
            for student in students:
                for payment in student.get('payments', {}).values():
                    payments.append(payment)
    return payments

def get_bedtickets(students):
    """Get all bedtickets of `students`.
    """
    tickets = []
    for student in students:
        for ticket in student.get('accommodation', {}).values():
            tickets.append(ticket)
    return tickets

class StudentExporterBase(ExporterBase):
    """Exporter for students or related objects.

    This is a baseclass.
    """
    grok.baseclass()
    grok.implements(ICSVStudentExporter)
    grok.provides(ICSVStudentExporter)

    def filter_func(self, x, **kw):
        return x

    def get_filtered(self, site, **kw):
        """Get students from a catalog filtered by keywords.

        students_catalog is the default catalog. The keys must be valid
        catalog index names.
        Returns a simple empty list, a list with `Student`
        objects or a catalog result set with `Student`
        objects.

        .. seealso:: `waeup.kofa.students.catalog.StudentsCatalog`

        """
        # Pass only given keywords to create FilteredCatalogQuery objects.
        # This way we avoid
        # trouble with `None` value ambivalences and queries are also
        # faster (normally less indexes to ask). Drawback is, that
        # developers must look into catalog to see what keywords are
        # valid.
        if kw.get('catalog', None) == 'coursetickets':
            coursetickets = CourseTicketsQuery(**kw).query()
            students = []
            for ticket in coursetickets:
                students.append(ticket.student)
            return list(set(students))
        # Payments can be filtered by payment_date. The period boundaries
        # are not keys of the catalog and must thus be removed from kw.
        try:
            del kw['payments_start']
            del kw['payments_end']
        except KeyError:
            pass
        query = StudentsQuery(**kw)
        return query.query()

    def export(self, values, filepath=None):
        """Export `values`, an iterable, as CSV file.

        If `filepath` is ``None``, a raw string with CSV data is returned.
        """
        writer, outfile = self.get_csv_writer(filepath)
        for value in values:
            self.write_item(value, writer)
        return self.close_outfile(filepath, outfile)

    def export_all(self, site, filepath=None):
        """Export students into filepath as CSV data.

        If `filepath` is ``None``, a raw string with CSV data is returned.
        """
        return self.export(self.filter_func(get_students(site)), filepath)

    def export_student(self, student, filepath=None):
        return self.export(self.filter_func([student]), filepath=filepath)

    def export_filtered(self, site, filepath=None, **kw):
        """Export items denoted by `kw`.

        If `filepath` is ``None``, a raw string with CSV data should
        be returned.
        """
        data = self.get_filtered(site, **kw)
        return self.export(self.filter_func(data, **kw), filepath=filepath)


class StudentExporter(grok.GlobalUtility, StudentExporterBase):
    """Exporter for Students.
    """
    grok.name('students')

    #: Fieldnames considered by this exporter
    fields = tuple(sorted(iface_names(IStudent))) + (
        'password', 'state', 'history', 'certcode', 'is_postgrad',
        'current_level', 'current_session')

    #: The title under which this exporter will be displayed
    title = _(u'Students')

    def mangle_value(self, value, name, context=None):
        if name == 'history':
            value = value.messages
        if name == 'phone' and value is not None:
            # Append hash '#' to phone numbers to circumvent
            # unwanted excel automatic
            value = str('%s#' % value)
        return super(
            StudentExporter, self).mangle_value(
            value, name, context=context)


class StudentStudyCourseExporter(grok.GlobalUtility, StudentExporterBase):
    """Exporter for StudentStudyCourses.
    """
    grok.name('studentstudycourses')

    #: Fieldnames considered by this exporter
    fields = tuple(sorted(iface_names(IStudentStudyCourse))) + ('student_id',)

    #: The title under which this exporter will be displayed
    title = _(u'Student Study Courses')

    def filter_func(self, x, **kw):
        return get_studycourses(x)

    def mangle_value(self, value, name, context=None):
        """Treat location values special.
        """
        if name == 'certificate' and value is not None:
            # XXX: hopefully cert codes are unique site-wide
            value = value.code
        if name == 'student_id' and context is not None:
            student = context.student
            value = getattr(student, name, None)
        return super(
            StudentStudyCourseExporter, self).mangle_value(
            value, name, context=context)


class StudentStudyLevelExporter(grok.GlobalUtility, StudentExporterBase):
    """Exporter for StudentStudyLevels.
    """
    grok.name('studentstudylevels')

    #: Fieldnames considered by this exporter
    fields = tuple(sorted(iface_names(
        IStudentStudyLevel) + ['level'])) + (
        'student_id', 'number_of_tickets','certcode')

    #: The title under which this exporter will be displayed
    title = _(u'Student Study Levels')

    def filter_func(self, x, **kw):
        return get_levels(x)

    def mangle_value(self, value, name, context=None):
        """Treat location values special.
        """
        if name == 'student_id' and context is not None:
            student = context.student
            value = getattr(student, name, None)
        return super(
            StudentStudyLevelExporter, self).mangle_value(
            value, name, context=context)

class CourseTicketExporter(grok.GlobalUtility, StudentExporterBase):
    """Exporter for CourseTickets.
    """
    grok.name('coursetickets')

    #: Fieldnames considered by this exporter
    fields = tuple(sorted(iface_names(ICourseTicket) +
        ['level', 'code', 'level_session'])) + ('student_id',
        'certcode', 'display_fullname')

    #: The title under which this exporter will be displayed
    title = _(u'Course Tickets')

    def filter_func(self, x, **kw):
        return get_tickets(x, **kw)

    def mangle_value(self, value, name, context=None):
        """Treat location values special.
        """
        if context is not None:
            student = context.student
            if name in ('student_id', 'display_fullname') and student is not None:
                value = getattr(student, name, None)
            #if name == 'level':
            #    value = getattr(context, 'level', lambda: None)
            #if name == 'level_session':
            #    value = getattr(context, 'level_session', lambda: None)
        return super(
            CourseTicketExporter, self).mangle_value(
            value, name, context=context)


class StudentPaymentsExporter(grok.GlobalUtility, StudentExporterBase):
    """Exporter for OnlinePayment instances.
    """
    grok.name('studentpayments')

    #: Fieldnames considered by this exporter
    fields = tuple(
        sorted(iface_names(
            IStudentOnlinePayment, exclude_attribs=False,
            omit=['display_item']))) + (
            'student_id','state','current_session')

    #: The title under which this exporter will be displayed
    title = _(u'Student Payments')

    def filter_func(self, x, **kw):
        return get_payments(x, **kw)

    def mangle_value(self, value, name, context=None):
        """Treat location values special.
        """
        if context is not None:
            student = context.student
            if name in ['student_id','state',
                        'current_session'] and student is not None:
                value = getattr(student, name, None)
        return super(
            StudentPaymentsExporter, self).mangle_value(
            value, name, context=context)

class DataForBursaryExporter(StudentPaymentsExporter):
    """Exporter for OnlinePayment instances.
    """
    grok.name('bursary')

    def filter_func(self, x, **kw):
        return get_payments(x, paid=True, **kw)

    #: Fieldnames considered by this exporter
    fields = tuple(
        sorted(iface_names(
            IStudentOnlinePayment, exclude_attribs=False,
            omit=['display_item']))) + (
            'student_id','matric_number','reg_number',
            'firstname', 'middlename', 'lastname',
            'state','current_session',
            'entry_session', 'entry_mode',
            'faccode', 'depcode','certcode')

    #: The title under which this exporter will be displayed
    title = _(u'Payment Data for Bursary')

    def mangle_value(self, value, name, context=None):
        """Treat location values special.
        """
        if context is not None:
            student = context.student
            if name in [
                'student_id','matric_number', 'reg_number',
                'firstname', 'middlename', 'lastname',
                'state', 'current_session',
                'entry_session', 'entry_mode',
                'faccode', 'depcode', 'certcode'] and student is not None:
                value = getattr(student, name, None)
        return super(
            StudentPaymentsExporter, self).mangle_value(
            value, name, context=context)

class BedTicketsExporter(grok.GlobalUtility, StudentExporterBase):
    """Exporter for BedTicket instances.
    """
    grok.name('bedtickets')

    #: Fieldnames considered by this exporter
    fields = tuple(
        sorted(iface_names(
            IBedTicket, exclude_attribs=False,
            omit=['display_coordinates']))) + (
            'student_id', 'actual_bed_type')

    #: The title under which this exporter will be displayed
    title = _(u'Bed Tickets')

    def filter_func(self, x, **kw):
        return get_bedtickets(x)

    def mangle_value(self, value, name, context=None):
        """Treat location values and others special.
        """
        if context is not None:
            student = context.student
            if name in ['student_id'] and student is not None:
                value = getattr(student, name, None)
        if name == 'bed' and value is not None:
            value = getattr(value, 'bed_id', None)
        if name == 'actual_bed_type':
            value = getattr(getattr(context, 'bed', None), 'bed_type')
        return super(
            BedTicketsExporter, self).mangle_value(
            value, name, context=context)

class StudentPaymentsOverviewExporter(StudentExporter):
    """Exporter for students with payment overview.
    """
    grok.name('paymentsoverview')

    curr_year = datetime.now().year
    year_range = range(curr_year - 9, curr_year + 1)
    year_range_tuple = tuple([str(year) for year in year_range])

    #: Fieldnames considered by this exporter
    fields = ('student_id', 'matric_number', 'display_fullname',
        'state', 'certcode', 'faccode', 'depcode', 'is_postgrad',
        'current_level', 'current_session', 'current_mode',
        ) + year_range_tuple

    #: The title under which this exporter will be displayed
    title = _(u'Student Payments Overview')

    def mangle_value(self, value, name, context=None):
        if name in self.year_range_tuple and context is not None:
            value = 0
            for ticket in context['payments'].values():
                if ticket.p_state == 'paid' and \
                    ticket.p_category == 'schoolfee' and \
                    ticket.p_session == int(name):
                    try:
                        value += ticket.amount_auth
                    except TypeError:
                        pass
            if value == 0:
                value = ''
        return super(
            StudentExporter, self).mangle_value(
            value, name, context=context)

class StudentStudyLevelsOverviewExporter(StudentExporter):
    """Exporter for students with study level overview.
    """
    grok.name('studylevelsoverview')

    avail_levels = tuple([str(x) for x in study_levels(None)])

    #: Fieldnames considered by this exporter
    fields = ('student_id', ) + (
        'state', 'certcode', 'faccode', 'depcode', 'is_postgrad',
        'entry_session', 'current_level', 'current_session',
        ) + avail_levels

    #: The title under which this exporter will be displayed
    title = _(u'Student Study Levels Overview')

    def mangle_value(self, value, name, context=None):
        if name in self.avail_levels and context is not None:
            value = ''
            for level in context['studycourse'].values():
                if level.level == int(name):
                    #value = '%s|%s|%s|%s' % (
                    #    level.level_session,
                    #    len(level),
                    #    level.validated_by,
                    #    level.level_verdict)
                    value = '%s' % level.level_session
                    break
        return super(
            StudentExporter, self).mangle_value(
            value, name, context=context)

class ComboCardDataExporter(grok.GlobalUtility, StudentExporterBase):
    """Exporter for Interswitch Combo Card Data.
    """
    grok.name('combocard')

    #: Fieldnames considered by this exporter
    fields = ('display_fullname',
              'student_id','matric_number',
              'certificate', 'faculty', 'department', 'passport_path')

    #: The title under which this exporter will be displayed
    title = _(u'Combo Card Data')

    def mangle_value(self, value, name, context=None):
        certificate = context['studycourse'].certificate
        if name == 'certificate' and certificate is not None:
            value = certificate.title
        if name == 'department' and certificate is not None:
            value = certificate.__parent__.__parent__.longtitle
        if name == 'faculty' and certificate is not None:
            value = certificate.__parent__.__parent__.__parent__.longtitle
        if name == 'passport_path' and certificate is not None:
            file_id = IFileStoreNameChooser(context).chooseName(attr='passport.jpg')
            os_path = getUtility(IExtFileStore)._pathFromFileID(file_id)
            if not os.path.exists(os_path):
                value = None
            else:
                value = '/'.join(os_path.split('/')[-4:])
        return super(
            ComboCardDataExporter, self).mangle_value(
            value, name, context=context)