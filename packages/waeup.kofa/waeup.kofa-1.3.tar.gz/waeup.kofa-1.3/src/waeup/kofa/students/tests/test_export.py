## $Id: test_export.py 12393 2015-01-04 16:00:38Z henrik $
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

import os
import grok
import datetime
from cStringIO import StringIO
from zope.component import queryUtility, getUtility
from zope.event import notify
from zope.interface.verify import verifyObject, verifyClass
from waeup.kofa.interfaces import (
    ICSVExporter, IExtFileStore, IFileStoreNameChooser)
from waeup.kofa.students.catalog import StudentsQuery
from waeup.kofa.students.export import (
    StudentExporter, StudentStudyCourseExporter, StudentStudyLevelExporter,
    CourseTicketExporter, StudentPaymentsExporter, BedTicketsExporter,
    StudentPaymentsOverviewExporter, StudentStudyLevelsOverviewExporter,
    ComboCardDataExporter, DataForBursaryExporter,
    get_students,)
from waeup.kofa.students.accommodation import BedTicket
from waeup.kofa.students.interfaces import ICSVStudentExporter
from waeup.kofa.students.payments import StudentOnlinePayment
from waeup.kofa.students.student import Student
from waeup.kofa.students.studycourse import StudentStudyCourse
from waeup.kofa.students.studylevel import StudentStudyLevel, CourseTicket
from waeup.kofa.students.tests.test_batching import StudentImportExportSetup
from waeup.kofa.testing import FunctionalLayer

curr_year = datetime.datetime.now().year
year_range = range(curr_year - 9, curr_year + 1)
year_range_str = ','.join([str(i) for i in year_range])

class ExportHelperTests(StudentImportExportSetup):
    layer = FunctionalLayer
    def setUp(self):
        super(ExportHelperTests, self).setUp()
        student = Student()
        self.app['students'].addStudent(student)
        student = self.setup_student(student)
        notify(grok.ObjectModifiedEvent(student))
        self.student = self.app['students'][student.student_id]
        return

    def test_get_students_plain(self):
        # without a filter we get all students
        result = get_students(self.app)
        self.assertEqual(len(list(result)), 1)
        return

    def test_get_students_by_session(self):
        # we can filter out students of a certain session
        my_filter1 = StudentsQuery(current_session=2012)
        result = get_students(self.app, stud_filter=my_filter1)
        self.assertEqual(len(list(result)), 1)

        my_filter2 = StudentsQuery(current_session=1964)
        result = get_students(self.app, stud_filter=my_filter2)
        self.assertEqual(len(list(result)), 0)
        return

    def test_get_students_by_level(self):
        # we can filter out students of a certain level
        my_filter1 = StudentsQuery(current_level=200)
        result = get_students(self.app, stud_filter=my_filter1)
        self.assertEqual(len(list(result)), 1)

        my_filter2 = StudentsQuery(current_level=300)
        result = get_students(self.app, stud_filter=my_filter2)
        self.assertEqual(len(list(result)), 0)
        return

    def test_get_students_by_deptcode(self):
        # we can filter out students of a certain dept.
        my_filter1 = StudentsQuery(depcode='NA')
        result = get_students(self.app, stud_filter=my_filter1)
        self.assertEqual(len(list(result)), 1)

        my_filter2 = StudentsQuery(depcode='NOTEXISTING')
        result = get_students(self.app, stud_filter=my_filter2)
        self.assertEqual(len(list(result)), 0)
        return

    def test_get_students_by_faccode(self):
        # we can filter out students of a certain faculty.
        my_filter1 = StudentsQuery(faccode='NA')
        result = get_students(self.app, stud_filter=my_filter1)
        self.assertEqual(len(list(result)), 1)

        my_filter2 = StudentsQuery(faccode='NOTEXISTING')
        result = get_students(self.app, stud_filter=my_filter2)
        self.assertEqual(len(list(result)), 0)
        return

    def test_get_students_by_current_mode(self):
        # we can filter out students in a certain mode.
        my_filter1 = StudentsQuery(current_mode='ug_ft')
        result = get_students(self.app, stud_filter=my_filter1)
        self.assertEqual(len(list(result)), 1)

        my_filter2 = StudentsQuery(current_mode='NOTEXISTING')
        result = get_students(self.app, stud_filter=my_filter2)
        self.assertEqual(len(list(result)), 0)
        return


class StudentExporterTest(StudentImportExportSetup):

    layer = FunctionalLayer

    std_csv_entry = (
        'my adm code,0,my clr code,1981-02-04#,anna@sample.com,,'
        'Anna,Tester,234,M.,NG,,"Studentroad 21\nLagos 123456\n",,'
        '+234-123-12345#,123,f,A111111,0,,,,created'
        )

    def setUp(self):
        super(StudentExporterTest, self).setUp()
        self.setup_for_export()
        return

    def test_ifaces(self):
        # make sure we fullfill interface contracts
        obj = StudentExporter()
        verifyObject(ICSVStudentExporter, obj)
        verifyClass(ICSVStudentExporter, StudentExporter)
        return

    def test_get_as_utility(self):
        # we can get an student exporter as utility
        result = queryUtility(ICSVExporter, name="students")
        self.assertTrue(result is not None)
        return

    def test_export(self):
        # we can really export students
        # set values we can expect in export file
        self.setup_student(self.student)
        exporter = StudentExporter()
        exporter.export([self.student], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertTrue(
            'adm_code,clearance_locked,clr_code,date_of_birth,email,'
            'employer,firstname,lastname,matric_number,middlename,'
            'nationality,officer_comment,perm_address,personal_updated,'
            'phone,reg_number,sex,student_id,suspended,suspended_comment,'
            'transcript_comment,password,state,history,certcode,is_postgrad,'
            'current_level,current_session\r\n'
            'my adm code,0,my clr code,'
            '1981-02-04#,anna@sample.com,,Anna,Tester,234,M.,NG,,'
            '"Studentroad 21\nLagos 123456\n",,+234-123-12345#,123,f,'
            'A111111,0,,,,created'
            in result
            )
        return

    def test_export_all(self):
        # we can really export students
        # set values we can expect in export file
        self.setup_student(self.student)
        exporter = StudentExporter()
        exporter.export_all(self.app, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertTrue(
            'adm_code,clearance_locked,clr_code,date_of_birth,email,'
            'employer,firstname,lastname,matric_number,middlename,'
            'nationality,officer_comment,perm_address,personal_updated,'
            'phone,reg_number,sex,student_id,suspended,suspended_comment,'
            'transcript_comment,password,state,history,certcode,'
            'is_postgrad,current_level,current_session\r\n'
            'my adm code,0,my clr code,1981-02-04#,anna@sample.com,,'
            'Anna,Tester,234,M.,NG,,"Studentroad 21\nLagos 123456\n"'
            ',,+234-123-12345#,123,f,A111111,0,,,,created'
            in result
            )
        return

    def test_export_student(self):
        # we can export a single student
        self.setup_student(self.student)
        exporter = StudentExporter()
        exporter.export_student(self.student, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertTrue(
            'adm_code,clearance_locked,clr_code,date_of_birth,email,'
            'employer,firstname,lastname,matric_number,middlename,'
            'nationality,officer_comment,perm_address,personal_updated,'
            'phone,reg_number,sex,student_id,suspended,suspended_comment,'
            'transcript_comment,password,state,history,certcode,'
            'is_postgrad,current_level,current_session\r\n'
            'my adm code,0,my clr code,1981-02-04#,anna@sample.com,,'
            'Anna,Tester,234,M.,NG,,"Studentroad 21\nLagos 123456\n"'
            ',,+234-123-12345#,123,f,A111111,0,,,,created'
            in result
            )
        return

    def test_export_filtered(self):
        # we can export a filtered set of students (filtered by session/level)
        self.setup_student(self.student)
        self.app['students'].addStudent(self.student)
        notify(grok.ObjectModifiedEvent(self.student))
        exporter = StudentExporter()

        exporter.export_filtered(
            self.app, self.outfile,
            current_session=None, current_level=None)
        result1 = open(self.outfile, 'rb').read()
        exporter.export_filtered(
            self.app, self.outfile,
            current_session=2012, current_level=None)
        result2 = open(self.outfile, 'rb').read()
        # current_level and current_session can be both a string ...
        exporter.export_filtered(
            self.app, self.outfile,
            current_session='2012', current_level=u'200')
        result3 = open(self.outfile, 'rb').read()
        exporter.export_filtered(
            self.app, self.outfile,
            current_session=2011, current_level=None)
        result4 = open(self.outfile, 'rb').read()
        # ... and an integer
        exporter.export_filtered(
            self.app, self.outfile,
            current_session=None, current_level=100)
        result5 = open(self.outfile, 'rb').read()
        # Also students at probating levels are being exported ...
        self.student['studycourse'].current_level = 210
        notify(grok.ObjectModifiedEvent(self.student))
        exporter.export_filtered(
            self.app, self.outfile,
            current_session=None, current_level=200)
        result6 = open(self.outfile, 'rb').read()
        # ... but not in the wrong level range.
        self.student['studycourse'].current_level = 310
        notify(grok.ObjectModifiedEvent(self.student))
        exporter.export_filtered(
            self.app, self.outfile,
            current_session=None, current_level=200)
        result7 = open(self.outfile, 'rb').read()
        self.assertTrue(self.std_csv_entry in result1)
        self.assertTrue(self.std_csv_entry in result2)
        self.assertTrue(self.std_csv_entry in result3)
        self.assertFalse(self.std_csv_entry in result4)
        self.assertFalse(self.std_csv_entry in result5)
        self.assertTrue(self.std_csv_entry in result6)
        self.assertFalse(self.std_csv_entry in result7)
        return

    def test_export_filtered_by_dept(self):
        # we can export a set of students filtered by department
        self.setup_student(self.student)
        self.app['students'].addStudent(self.student)
        notify(grok.ObjectModifiedEvent(self.student))
        exporter = StudentExporter()
        # current_session can be both a string ...
        exporter.export_filtered(
            self.app, self.outfile,
            current_session='2012', current_level=u'200', depcode='NA')
        result1 = open(self.outfile, 'rb').read()
        # ... and an integer
        exporter.export_filtered(
            self.app, self.outfile,
            current_session=2012, current_level=200, depcode='NODEPT')
        result2 = open(self.outfile, 'rb').read()
        self.assertTrue(self.std_csv_entry in result1)
        self.assertTrue(self.std_csv_entry not in result2)
        return

    def test_export_filtered_by_faculty(self):
        # we can export a set of students filtered by faculty
        self.setup_student(self.student)
        self.app['students'].addStudent(self.student)
        notify(grok.ObjectModifiedEvent(self.student))
        exporter = StudentExporter()

        exporter.export_filtered(
            self.app, self.outfile,
            current_session=2012, current_level='200', faccode='NA')
        result1 = open(self.outfile, 'rb').read()
        exporter.export_filtered(
            self.app, self.outfile,
            current_session=2012, current_level=200, faccode='NOFAC')
        result2 = open(self.outfile, 'rb').read()
        self.assertTrue(self.std_csv_entry in result1)
        self.assertTrue(self.std_csv_entry not in result2)
        return

class StudentStudyCourseExporterTest(StudentImportExportSetup):

    layer = FunctionalLayer

    def setUp(self):
        super(StudentStudyCourseExporterTest, self).setUp()
        self.setup_for_export()
        return

    def test_ifaces(self):
        # make sure we fullfill interface contracts
        obj = StudentStudyCourseExporter()
        verifyObject(ICSVStudentExporter, obj)
        verifyClass(ICSVStudentExporter, StudentStudyCourseExporter)
        return

    def test_get_as_utility(self):
        # we can get an student exporter as utility
        result = queryUtility(ICSVExporter, name="studentstudycourses")
        self.assertTrue(result is not None)
        return

    def test_export_empty(self):
        # we can export a nearly empty study course
        study_course = StudentStudyCourse()
        exporter = StudentStudyCourseExporter()
        exporter.export([study_course], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'certificate,current_level,current_session,current_verdict,'
            'entry_mode,entry_session,previous_verdict,student_id\r\n'

            ',,,0,,,0,\r\n'
            )
        return

    def test_export(self):
        # we can really export study courses.
        # set values we can expect in export file
        self.setup_student(self.student)
        study_course = self.student.get('studycourse')
        exporter = StudentStudyCourseExporter()
        exporter.export([study_course], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'certificate,current_level,current_session,current_verdict,'
            'entry_mode,entry_session,previous_verdict,student_id\r\n'

            'CERT1,200,2012,0,ug_ft,2010,0,A111111\r\n'
            )
        return

    def test_export_all(self):
        # we can really export students
        # set values we can expect in export file
        self.setup_student(self.student)
        exporter = StudentStudyCourseExporter()
        exporter.export_all(self.app, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'certificate,current_level,current_session,current_verdict,'
            'entry_mode,entry_session,previous_verdict,student_id\r\n'

            'CERT1,200,2012,0,ug_ft,2010,0,A111111\r\n'
            )
        return

    def test_export_student(self):
        # we can export studycourse of a certain student
        self.setup_student(self.student)
        exporter = StudentStudyCourseExporter()
        exporter.export_student(self.student, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'certificate,current_level,current_session,current_verdict,'
            'entry_mode,entry_session,previous_verdict,student_id\r\n'

            'CERT1,200,2012,0,ug_ft,2010,0,A111111\r\n'
            )
        return

    def test_export_filtered(self):
        # we can export studycourses of a filtered set of students
        self.setup_student(self.student)
        self.app['students'].addStudent(self.student)
        notify(grok.ObjectModifiedEvent(self.student))

        exporter = StudentStudyCourseExporter()
        exporter.export_filtered(
            self.student, self.outfile, current_session=2012)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'certificate,current_level,current_session,current_verdict,'
            'entry_mode,entry_session,previous_verdict,student_id\r\n'

            'CERT1,200,2012,0,ug_ft,2010,0,A111111\r\n'
            )
        return



class StudentStudyLevelExporterTest(StudentImportExportSetup):

    layer = FunctionalLayer

    def setUp(self):
        super(StudentStudyLevelExporterTest, self).setUp()
        self.setup_for_export()
        return

    def test_ifaces(self):
        # make sure we fullfill interface contracts
        obj = StudentStudyLevelExporter()
        verifyObject(ICSVStudentExporter, obj)
        verifyClass(ICSVStudentExporter, StudentStudyLevelExporter)
        return

    def test_get_as_utility(self):
        # we can get an student exporter as utility
        result = queryUtility(ICSVExporter, name="studentstudylevels")
        self.assertTrue(result is not None)
        return

    def test_export_empty(self):
        # we can export a nearly empty study level
        study_level = StudentStudyLevel()
        exporter = StudentStudyLevelExporter()
        exporter.export([study_level], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'gpa,level,level_session,level_verdict,total_credits,'
            'validated_by,validation_date,'
            'student_id,number_of_tickets,certcode\r\n'
            '0.0,,,0,0,,,,0,\r\n'
            )
        return

    def test_export(self):
        # we can really export study levels.
        # set values we can expect in export file
        self.setup_student(self.student)
        study_course = self.student.get('studycourse')
        study_level = study_course[study_course.keys()[0]]
        exporter = StudentStudyLevelExporter()
        exporter.export([study_level], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'gpa,level,level_session,level_verdict,total_credits,'
            'validated_by,validation_date,'
            'student_id,number_of_tickets,certcode\r\n'
            '0.0,100,2012,A,100,,,A111111,1,CERT1\r\n'
            )
        return

    def test_export_all(self):
        # we can really export study levels
        # set values we can expect in export file
        self.setup_student(self.student)
        exporter = StudentStudyLevelExporter()
        exporter.export_all(self.app, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'gpa,level,level_session,level_verdict,total_credits,'
            'validated_by,validation_date,'
            'student_id,number_of_tickets,certcode\r\n'
            '0.0,100,2012,A,100,,,A111111,1,CERT1\r\n'
            )
        return

    def test_export_student(self):
        # we can really export study levels of a certain student
        self.setup_student(self.student)
        exporter = StudentStudyLevelExporter()
        exporter.export_student(self.student, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'gpa,level,level_session,level_verdict,total_credits,'
            'validated_by,validation_date,'
            'student_id,number_of_tickets,certcode\r\n'
            '0.0,100,2012,A,100,,,A111111,1,CERT1\r\n'
            )
        return

    def test_export_filtered(self):
        # we can export studylevels of a filtered set of students
        self.setup_student(self.student)
        self.app['students'].addStudent(self.student)
        notify(grok.ObjectModifiedEvent(self.student))

        exporter = StudentStudyLevelExporter()
        exporter.export_filtered(
            self.student, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'gpa,level,level_session,level_verdict,total_credits,'
            'validated_by,validation_date,'
            'student_id,number_of_tickets,certcode\r\n'
            '0.0,100,2012,A,100,,,A111111,1,CERT1\r\n'
            )
        return

class CourseTicketExporterTest(StudentImportExportSetup):

    layer = FunctionalLayer

    def setUp(self):
        super(CourseTicketExporterTest, self).setUp()
        self.setup_for_export()
        return

    def test_ifaces(self):
        # make sure we fullfill interface contracts
        obj = CourseTicketExporter()
        verifyObject(ICSVStudentExporter, obj)
        verifyClass(ICSVStudentExporter, CourseTicketExporter)
        return

    def test_get_as_utility(self):
        # we can get an student exporter as utility
        result = queryUtility(ICSVExporter, name="coursetickets")
        self.assertTrue(result is not None)
        return

    def test_export_empty(self):
        # we can export a nearly empty course ticket
        ticket = CourseTicket()
        exporter = CourseTicketExporter()
        exporter.export([ticket], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'automatic,carry_over,code,credits,dcode,fcode,level,level_session,'
            'mandatory,passmark,score,semester,title,student_id,certcode,'
            'display_fullname\r\n'
            '0,0,,,,,,,0,,,,,,,\r\n'
            )
        return

    def test_export(self):
        # we can really export course tickets.
        # set values we can expect in export file
        self.setup_student(self.student)
        study_course = self.student.get('studycourse')
        study_level = study_course[study_course.keys()[0]]
        ticket = study_level['CRS1']
        exporter = CourseTicketExporter()
        exporter.export([ticket], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'automatic,carry_over,code,credits,dcode,fcode,level,level_session,'
            'mandatory,passmark,score,semester,title,student_id,certcode,'
            'display_fullname\r\n'
            '1,1,CRS1,100,DEP1,FAC1,100,2012,0,100,,2,Course 1,A111111,CERT1,'
            'Anna M. Tester\r\n'
            )
        return

    def test_export_all(self):
        # we can really export all course tickets
        # set values we can expect in export file
        self.setup_student(self.student)
        exporter = CourseTicketExporter()
        exporter.export_all(self.app, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'automatic,carry_over,code,credits,dcode,fcode,level,level_session,'
            'mandatory,passmark,score,semester,title,student_id,certcode,'
            'display_fullname\r\n'
            '1,1,CRS1,100,DEP1,FAC1,100,2012,0,100,,2,Course 1,A111111,CERT1,'
            'Anna M. Tester\r\n'
            )
        return

    def test_export_student(self):
        # we can really export all course tickets of a certain student
        self.setup_student(self.student)
        exporter = CourseTicketExporter()
        exporter.export_student(self.student, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'automatic,carry_over,code,credits,dcode,fcode,level,level_session,'
            'mandatory,passmark,score,semester,title,student_id,certcode,'
            'display_fullname\r\n'
            '1,1,CRS1,100,DEP1,FAC1,100,2012,0,100,,2,Course 1,A111111,CERT1,'
            'Anna M. Tester\r\n'
            )
        return

    def test_export_filtered(self):
        # we can export course tickets of a filtered set of students
        self.setup_student(self.student)
        self.app['students'].addStudent(self.student)
        notify(grok.ObjectModifiedEvent(self.student))

        exporter = CourseTicketExporter()
        exporter.export_filtered(
            self.student, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'automatic,carry_over,code,credits,dcode,fcode,level,level_session,'
            'mandatory,passmark,score,semester,title,student_id,certcode,'
            'display_fullname\r\n'
            '1,1,CRS1,100,DEP1,FAC1,100,2012,0,100,,2,Course 1,A111111,CERT1,'
            'Anna M. Tester\r\n'
            )
        # if the coursetickets catalog is used to filter students
        # and (course) code is not None
        # only course tickets which belong to this course are exported
        exporter.export_filtered(
            self.student, self.outfile, catalog='coursetickets', code='CRS1')
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'automatic,carry_over,code,credits,dcode,fcode,level,level_session,'
            'mandatory,passmark,score,semester,title,student_id,certcode,'
            'display_fullname\r\n'
            '1,1,CRS1,100,DEP1,FAC1,100,2012,0,100,,2,Course 1,A111111,CERT1,'
            'Anna M. Tester\r\n'
            )
        exporter.export_filtered(
            self.student, self.outfile, catalog='coursetickets', code='any code')
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'automatic,carry_over,code,credits,dcode,fcode,level,level_session,'
            'mandatory,passmark,score,semester,title,student_id,certcode,'
            'display_fullname\r\n'
            )
        # Also tickets in probating levels are exported. Therefore
        # we change the level attribute to fake a 110 level.
        self.student['studycourse']['100'].level = 110
        notify(grok.ObjectModifiedEvent(self.student['studycourse']['100']['CRS1']))
        exporter.export_filtered(
            self.student, self.outfile, catalog='coursetickets', code='CRS1', level='100')
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'automatic,carry_over,code,credits,dcode,fcode,level,level_session,'
            'mandatory,passmark,score,semester,title,student_id,certcode,'
            'display_fullname\r\n'
            '1,1,CRS1,100,DEP1,FAC1,110,2012,0,100,,2,Course 1,A111111,CERT1,'
            'Anna M. Tester\r\n'
            )
        return

class StudentPaymentsExporterTest(StudentImportExportSetup):

    layer = FunctionalLayer

    def setUp(self):
        super(StudentPaymentsExporterTest, self).setUp()
        self.setup_for_export()
        return

    def test_ifaces(self):
        # make sure we fullfill interface contracts
        obj = StudentPaymentsExporter()
        verifyObject(ICSVStudentExporter, obj)
        verifyClass(ICSVStudentExporter, StudentPaymentsExporter)
        return

    def test_get_as_utility(self):
        # we can get a payments exporter as utility
        result = queryUtility(ICSVExporter, name="studentpayments")
        self.assertTrue(result is not None)
        return

    def test_export_empty(self):
        # we can export a nearly empty payment
        payment = StudentOnlinePayment()
        payment.creation_date = datetime.datetime(2012, 4, 1, 13, 12, 1)
        exporter = StudentPaymentsExporter()
        exporter.export([payment], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'ac,amount_auth,creation_date,p_category,p_current,p_id,'
            'p_item,p_level,p_session,p_state,payment_date,r_amount_approved,'
            'r_code,r_desc,student_id,state,current_session\r\n'

            ',0.0,2012-04-01 13:12:01#,,1,,,,,unpaid,,0.0,,,,,\r\n'
            )
        return

    def test_export(self):
        # we can really export student payments.
        # set values we can expect in export file
        self.setup_student(self.student)
        payment = self.student['payments']['my-payment']
        exporter = StudentPaymentsExporter()
        exporter.export([payment], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'ac,amount_auth,creation_date,p_category,p_current,p_id,'
            'p_item,p_level,p_session,p_state,payment_date,r_amount_approved,'
            'r_code,r_desc,student_id,state,current_session\r\n'

            '666,12.12,2012-04-01 13:12:01#,schoolfee,1,my-id,'
            'p-item,100,2012,paid,2012-04-01 14:12:01#,12.12,'
            'r-code,,A111111,created,2012\r\n'
            )
        return

    def test_export_all(self):
        # we can really export all payments
        # set values we can expect in export file
        self.setup_student(self.student)
        exporter = StudentPaymentsExporter()
        exporter.export_all(self.app, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'ac,amount_auth,creation_date,p_category,p_current,p_id,'
            'p_item,p_level,p_session,p_state,payment_date,r_amount_approved,'
            'r_code,r_desc,student_id,state,current_session\r\n'

            '666,12.12,2012-04-01 13:12:01#,schoolfee,1,my-id,'
            'p-item,100,2012,paid,2012-04-01 14:12:01#,12.12,'
            'r-code,,A111111,created,2012\r\n'
            )
        return

    def test_export_student(self):
        # we can really export all payments of a certain student
        # set values we can expect in export file
        self.setup_student(self.student)
        exporter = StudentPaymentsExporter()
        exporter.export_student(self.student, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'ac,amount_auth,creation_date,p_category,p_current,p_id,'
            'p_item,p_level,p_session,p_state,payment_date,r_amount_approved,'
            'r_code,r_desc,student_id,state,current_session\r\n'

            '666,12.12,2012-04-01 13:12:01#,schoolfee,1,my-id,'
            'p-item,100,2012,paid,2012-04-01 14:12:01#,12.12,'
            'r-code,,A111111,created,2012\r\n'
            )
        return

    def test_export_filtered(self):
        # we can export payments of a filtered set of students
        self.setup_student(self.student)
        self.app['students'].addStudent(self.student)
        notify(grok.ObjectModifiedEvent(self.student))

        exporter = StudentPaymentsExporter()
        exporter.export_filtered(
            self.student, self.outfile, current_level=200)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'ac,amount_auth,creation_date,p_category,p_current,p_id,'
            'p_item,p_level,p_session,p_state,payment_date,r_amount_approved,'
            'r_code,r_desc,student_id,state,current_session\r\n'

            '666,12.12,2012-04-01 13:12:01#,schoolfee,1,my-id,'
            'p-item,100,2012,paid,2012-04-01 14:12:01#,12.12,'
            'r-code,,A111111,created,2012\r\n'
            )
        return

    def test_export_filtered_by_date(self):
        # payments_start and payments_end are being ignored
        self.setup_student(self.student)
        self.app['students'].addStudent(self.student)
        notify(grok.ObjectModifiedEvent(self.student))
        exporter = StudentPaymentsExporter()
        # A key xxx does not exist
        self.assertRaises(
            KeyError, exporter.export_filtered, self.app, self.outfile,
            current_session=None,
            current_level=None, xxx='nonsense')
        # payments_start and payments_end do exist but must match format '%Y-%m-%d'
        self.assertRaises(
            ValueError, exporter.export_filtered, self.app, self.outfile,
            current_session=None, current_level=None,
            payments_start='nonsense', payments_end='nonsense')
        # If they match the format they are ignored by get_filtered and the
        # exporter works properly
        exporter.export_filtered(
            self.app, self.outfile,
            current_session=None, current_level=None,
            payments_start='01/04/2012', payments_end='02/04/2012')
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'ac,amount_auth,creation_date,p_category,p_current,p_id,'
            'p_item,p_level,p_session,p_state,payment_date,r_amount_approved,'
            'r_code,r_desc,student_id,state,current_session\r\n'

            '666,12.12,2012-04-01 13:12:01#,schoolfee,1,my-id,'
            'p-item,100,2012,paid,2012-04-01 14:12:01#,12.12,'
            'r-code,,A111111,created,2012\r\n'
            )
        # no results if payment_date is outside the given period
        exporter.export_filtered(
            self.app, self.outfile,
            current_session=None, current_level=None,
            payments_start='31/03/2012', payments_end='01/04/2012')
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'ac,amount_auth,creation_date,p_category,p_current,p_id,'
            'p_item,p_level,p_session,p_state,payment_date,r_amount_approved,'
            'r_code,r_desc,student_id,state,current_session\r\n'
            )
        exporter.export_filtered(
            self.app, self.outfile,
            current_session=None, current_level=None,
            payments_start='02/04/2012', payments_end='03/04/2012')
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'ac,amount_auth,creation_date,p_category,p_current,p_id,'
            'p_item,p_level,p_session,p_state,payment_date,r_amount_approved,'
            'r_code,r_desc,student_id,state,current_session\r\n'
            )
        # no results if payment_date is not set
        self.payment.payment_date = None
        exporter.export_filtered(
            self.app, self.outfile,
            current_session=None, current_level=None,
            payments_start='01/04/2012', payments_end='02/04/2012')
        result = open(self.outfile, 'rb').read()
        
        return

class BursaryDataExporterTest(StudentImportExportSetup):

    layer = FunctionalLayer

    def setUp(self):
        super(BursaryDataExporterTest, self).setUp()
        self.setup_for_export()
        return

    def test_export_all(self):
        # we can really export all payments
        # set values we can expect in export file
        self.setup_student(self.student)
        exporter = DataForBursaryExporter()
        exporter.export_all(self.app, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            result,
            'ac,amount_auth,creation_date,p_category,p_current,p_id,p_item,'
            'p_level,p_session,p_state,payment_date,r_amount_approved,r_code,'
            'r_desc,student_id,matric_number,reg_number,firstname,middlename,lastname,'
            'state,current_session,entry_session,entry_mode,faccode,depcode,certcode\r\n'

            '666,12.12,2012-04-01 13:12:01#,schoolfee,1,my-id,p-item,100,2012,'
            'paid,2012-04-01 14:12:01#,12.12,r-code,,A111111,234,123,'
            'Anna,M.,Tester,created,2012,2010,ug_ft,NA,NA,CERT1\r\n'
            )
        return

class BedTicketsExporterTest(StudentImportExportSetup):

    layer = FunctionalLayer

    def setUp(self):
        super(BedTicketsExporterTest, self).setUp()
        self.setup_for_export()
        return

    def test_ifaces(self):
        # make sure we fullfill interface contracts
        obj = BedTicketsExporter()
        verifyObject(ICSVStudentExporter, obj)
        verifyClass(ICSVStudentExporter, BedTicketsExporter)
        return

    def test_get_as_utility(self):
        # we can get a bedtickets exporter as utility
        result = queryUtility(ICSVExporter, name="bedtickets")
        self.assertTrue(result is not None)
        return

    def test_export_empty(self):
        # we can export a nearly empty bedticket
        bedticket = BedTicket()
        bed = self.app['hostels']['hall-1']['hall-1_A_101_A']
        bedticket.bed = bed
        exporter = BedTicketsExporter()
        exporter.export([bedticket], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertMatches(
            result,
            'bed,bed_coordinates,bed_type,booking_code,booking_date,'
            'booking_session,student_id,actual_bed_type\r\n'
            'hall-1_A_101_A,,,,<YYYY-MM-DD hh:mm:ss>.<6-DIGITS>#,,,regular_male_fr\r\n'
            )
        return

    def test_export(self):
        # we can really export student bedtickets.
        # set values we can expect in export file
        self.setup_student(self.student)
        bedticket = self.student['accommodation']['2004']
        exporter = BedTicketsExporter()
        exporter.export([bedticket], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertMatches(
            result,
            'bed,bed_coordinates,bed_type,booking_code,booking_date,'
            'booking_session,student_id,actual_bed_type\r\n'
            'hall-1_A_101_A,,any bed type,,<YYYY-MM-DD hh:mm:ss>.<6-DIGITS>#,2004,'
            'A111111,regular_male_fr\r\n'
            )
        return

    def test_export_all(self):
        # we can really export all bedtickets
        # set values we can expect in export file
        self.setup_student(self.student)
        exporter = BedTicketsExporter()
        exporter.export_all(self.app, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertMatches(
            result,
            'bed,bed_coordinates,bed_type,booking_code,booking_date,'
            'booking_session,student_id,actual_bed_type\r\n'
            'hall-1_A_101_A,,any bed type,,<YYYY-MM-DD hh:mm:ss>.<6-DIGITS>#,2004,'
            'A111111,regular_male_fr\r\n'
            )
        return

    def test_export_student(self):
        # we can really export all bedtickets of a certain student
        # set values we can expect in export file
        self.setup_student(self.student)
        exporter = BedTicketsExporter()
        exporter.export_student(self.student, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertMatches(
            result,
            'bed,bed_coordinates,bed_type,booking_code,booking_date,'
            'booking_session,student_id,actual_bed_type\r\n'
            'hall-1_A_101_A,,any bed type,,<YYYY-MM-DD hh:mm:ss>.<6-DIGITS>#,2004,'
            'A111111,regular_male_fr\r\n'
            )
        return

    def test_export_filtered(self):
        # we can export payments of a filtered set of students
        self.setup_student(self.student)
        self.app['students'].addStudent(self.student)
        notify(grok.ObjectModifiedEvent(self.student))

        exporter = BedTicketsExporter()
        exporter.export_filtered(
            self.student, self.outfile, current_level=200)
        result = open(self.outfile, 'rb').read()
        self.assertMatches(
            result,
            'bed,bed_coordinates,bed_type,booking_code,booking_date,'
            'booking_session,student_id,actual_bed_type\r\n'
            'hall-1_A_101_A,,any bed type,,<YYYY-MM-DD hh:mm:ss>.<6-DIGITS>#,'
            '2004,A111111,regular_male_fr\r\n')
        return


class StudentPaymentsOverviewExporterTest(StudentImportExportSetup):

    layer = FunctionalLayer

    def setUp(self):
        super(StudentPaymentsOverviewExporterTest, self).setUp()
        self.setup_for_export()
        return

    def test_ifaces(self):
        # make sure we fullfill interface contracts
        obj = StudentPaymentsOverviewExporter()
        verifyObject(ICSVStudentExporter, obj)
        verifyClass(ICSVStudentExporter, StudentPaymentsOverviewExporter)
        return

    def test_get_as_utility(self):
        # we can get a payments exporter as utility
        result = queryUtility(ICSVExporter, name="paymentsoverview")
        self.assertTrue(result is not None)
        return

    def test_export(self):
        self.setup_student(self.student)
        exporter = StudentPaymentsOverviewExporter()
        exporter.export([self.student], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertTrue(
            'student_id,matric_number,display_fullname,state,certcode,'
            'faccode,depcode,is_postgrad,'
            'current_level,current_session,current_mode,'
            '%s\r\n'
            'A111111,234,Anna M. Tester,created,CERT1,NA,NA,0,200,2012,ug_ft,'
            % year_range_str in result
            )
        return

    def test_export_all(self):
        # we can really export students
        # set values we can expect in export file
        self.setup_student(self.student)
        # We add successful payments. 
        payment_2 = StudentOnlinePayment()
        payment_2.p_id = 'my-id'
        payment_2.p_session = curr_year - 5
        payment_2.amount_auth = 13.13
        payment_2.p_state = u'paid'
        payment_2.p_category = u'schoolfee'
        self.student['payments']['my-2ndpayment'] = payment_2
        # This one could be a balance payment.
        # The amount is being added.
        payment_3 = StudentOnlinePayment()
        payment_3.p_id = 'my-id_2'
        payment_3.p_session = curr_year - 5
        payment_3.amount_auth = 1.01
        payment_3.p_state = u'paid'
        payment_3.p_category = u'schoolfee'
        self.student['payments']['my-3rdpayment'] = payment_3
        exporter = StudentPaymentsOverviewExporter()
        exporter.export_all(self.app, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertTrue(
            'student_id,matric_number,display_fullname,state,'
            'certcode,faccode,depcode,is_postgrad,'
            'current_level,current_session,current_mode,'
            '%s\r\nA111111,234,Anna M. Tester,created,CERT1,NA,NA,0,'
            '200,2012,ug_ft,,,,,14.14,,12.12,,,\r\n'
            % year_range_str in result
            )
        return

class StudentStudyLevelsOverviewExporterTest(StudentImportExportSetup):

    layer = FunctionalLayer

    def setUp(self):
        super(StudentStudyLevelsOverviewExporterTest, self).setUp()
        self.setup_for_export()
        return

    def test_ifaces(self):
        obj = StudentStudyLevelsOverviewExporter()
        verifyObject(ICSVStudentExporter, obj)
        verifyClass(ICSVStudentExporter, StudentStudyLevelsOverviewExporter)
        return

    def test_get_as_utility(self):
        result = queryUtility(ICSVExporter, name="studylevelsoverview")
        self.assertTrue(result is not None)
        return

    def test_export(self):
        self.setup_student(self.student)
        exporter = StudentStudyLevelsOverviewExporter()
        exporter.export([self.student], self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
             'student_id,state,certcode,faccode,depcode,is_postgrad,'
             'entry_session,current_level,current_session,'
             '10,100,110,120,200,210,220,300,310,320,400,410,420,500,'
             '510,520,600,610,620,700,710,720,800,810,820,900,910,920,999\r\n'
             'A111111,created,CERT1,NA,NA,0,2010,200,2012,,2012'
             ',,,,,,,,,,,,,,,,,,,,,,,,,,,\r\n',
            result
            )
        return

    def test_export_all(self):
        self.setup_student(self.student)
        exporter = StudentStudyLevelsOverviewExporter()
        exporter.export_all(self.app, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertEqual(
            'student_id,state,certcode,faccode,depcode,is_postgrad,'
            'entry_session,current_level,current_session,'
            '10,100,110,120,200,210,220,300,310,320,400,410,420,500,'
            '510,520,600,610,620,700,710,720,800,810,820,900,910,920,999\r\n'
            'A111111,created,CERT1,NA,NA,0,2010,200,2012,,2012'
            ',,,,,,,,,,,,,,,,,,,,,,,,,,,\r\n',
            result
            )
        return

class ComboCardExporterTest(StudentImportExportSetup):

    layer = FunctionalLayer

    def setUp(self):
        super(ComboCardExporterTest, self).setUp()
        self.setup_for_export()
        return

    def create_passport_img(self, student):
        # create some passport file for `student`
        storage = getUtility(IExtFileStore)
        image_path = os.path.join(os.path.dirname(__file__), 'test_image.jpg')
        self.image_contents = open(image_path, 'rb').read()
        file_id = IFileStoreNameChooser(student).chooseName(
            attr='passport.jpg')
        storage.createFile(file_id, StringIO(self.image_contents))

    def test_export_all(self):
        self.setup_student(self.student)
        self.create_passport_img(self.student)
        exporter = ComboCardDataExporter()
        exporter.export_all(self.app, self.outfile)
        result = open(self.outfile, 'rb').read()
        self.assertTrue(
            'display_fullname,student_id,matric_number,certificate,faculty,'
            'department,passport_path\r\nAnna M. Tester,A111111,234,'
            'Unnamed Certificate,Faculty of Unnamed Faculty (NA),'
            'Department of Unnamed Department (NA),'
            'students/00110/A111111/passport_A111111.jpg\r\n'
            in result
            )
        return
