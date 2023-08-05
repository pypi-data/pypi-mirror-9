## $Id: permissions.py 10465 2013-08-07 11:18:43Z henrik $
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
Permissions for the student section.
"""
import grok

# Student section permissions

class HandleStudent(grok.Permission):
    grok.name('waeup.handleStudent')

class ViewStudent(grok.Permission):
    grok.name('waeup.viewStudent')

class ViewStudentsTab(grok.Permission):
    grok.name('waeup.viewStudentsTab')

class ViewMyStudentDataTab(grok.Permission):
    grok.name('waeup.viewMyStudentDataTab')

class ViewStudentsContainer(grok.Permission):
    grok.name('waeup.viewStudentsContainer')

class PayStudent(grok.Permission):
    grok.name('waeup.payStudent')

class HandleAccommodation(grok.Permission):
    grok.name('waeup.handleAccommodation')

class UploadStudentFile(grok.Permission):
    grok.name('waeup.uploadStudentFile')

class ManageStudent(grok.Permission):
    grok.name('waeup.manageStudent')

class ClearStudent(grok.Permission):
    grok.name('waeup.clearStudent')

class ValidateStudent(grok.Permission):
    grok.name('waeup.validateStudent')

class EditStudyLevel(grok.Permission):
    grok.name('waeup.editStudyLevel')

class TriggerTransition(grok.Permission):
    grok.name('waeup.triggerTransition')

class LoginAsStudent(grok.Permission):
    grok.name('waeup.loginAsStudent')

# Local role
class StudentRecordOwner(grok.Role):
    grok.name('waeup.local.StudentRecordOwner')
    grok.title(u'Student Record Owner')
    grok.permissions('waeup.handleStudent', 'waeup.uploadStudentFile',
                     'waeup.viewStudent', 'waeup.payStudent',
                     'waeup.handleAccommodation', 'waeup.editStudyLevel')

# Site Roles
class StudentRole(grok.Role):
    grok.name('waeup.Student')
    grok.title(u'Student (do not assign)')
    grok.permissions('waeup.viewAcademics', 'waeup.viewMyStudentDataTab',
                     'waeup.Authenticated')

class StudentsOfficer(grok.Role):
    grok.name('waeup.StudentsOfficer')
    grok.title(u'Students Officer (view only)')
    grok.permissions('waeup.viewStudent','waeup.viewStudents',
          'waeup.viewStudentsTab', 'waeup.viewStudentsContainer')

class StudentsManager(grok.Role):
    grok.name('waeup.StudentsManager')
    grok.title(u'Students Manager')
    grok.permissions('waeup.viewStudent', 'waeup.viewStudents',
                     'waeup.manageStudent', 'waeup.viewStudentsContainer',
                     'waeup.payStudent', 'waeup.uploadStudentFile',
                     'waeup.viewStudentsTab', 'waeup.handleAccommodation')

class TranscriptOfficer(grok.Role):
    grok.name('waeup.TranscriptOfficer')
    grok.title(u'Transcript Officer')
    grok.permissions('waeup.viewAcademics',
                     'waeup.viewTranscript',
                     'waeup.viewStudent',
                     'waeup.viewStudents',
                     'waeup.viewStudentsTab',
                     'waeup.viewStudentsContainer',
                     )

class StudentsClearanceOfficer(grok.Role):
    grok.name('waeup.StudentsClearanceOfficer')
    grok.title(u'Clearance Officer (all students)')
    grok.permissions('waeup.clearStudent','waeup.viewStudent')

class StudentsCourseAdviser(grok.Role):
    grok.name('waeup.StudentsCourseAdviser')
    grok.title(u'Course Adviser (all students)')
    grok.permissions('waeup.validateStudent','waeup.viewStudent',
                     'waeup.editStudyLevel')

class StudentImpersonator(grok.Role):
    grok.name('waeup.StudentImpersonator')
    grok.title(u'Student Impersonator')
    grok.permissions('waeup.loginAsStudent')