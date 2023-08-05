## $Id: batching.py 11891 2014-10-28 20:02:45Z henrik $
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
"""Batch processing components for academics objects.

Batch processors eat CSV files to add, update or remove large numbers
of certain kinds of objects at once.

Here we define the processors for academics specific objects like
faculties, departments and the like.
"""
import grok
from zope.interface import Interface
from zope.component import queryUtility
from zope.schema import getFields
from zope.catalog.interfaces import ICatalog
from zope.event import notify
from zope.securitypolicy.interfaces import (
    IPrincipalRoleManager, IPrincipalRoleMap)
from waeup.kofa.authentication import LocalRoleSetEvent
from waeup.kofa.interfaces import (
    IBatchProcessor, IGNORE_MARKER, DELETION_MARKER, FatalCSVError)
from waeup.kofa.university.interfaces import (
    IFacultiesContainer, IFaculty, ICourse, IDepartment, ICertificate,
    ICertificateCourse)
from waeup.kofa.university import (
    Faculty, Department, Course, Certificate)
from waeup.kofa.utils.batching import BatchProcessor
from waeup.kofa.interfaces import MessageFactory as _

class FacultyProcessor(BatchProcessor):
    """A batch processor for IFaculty objects.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'facultyprocessor'
    grok.name(util_name)

    name = _('Faculty Processor')
    iface = IFaculty
    allowed_roles = Faculty.local_roles

    location_fields = ['code',]
    factory_name = 'waeup.Faculty'

    mode = None

    def parentsExist(self, row, site):
        return 'faculties' in site.keys()

    @property
    def available_fields(self):
        fields = getFields(self.iface)
        return sorted(list(set(
            self.location_fields + fields.keys() + ['local_roles']
            )))

    def entryExists(self, row, site):
        return row['code'] in site['faculties'].keys()

    def getParent(self, row, site):
        return site['faculties']

    def getEntry(self, row, site):
        if not self.entryExists(row, site):
            return None
        parent = self.getParent(row, site)
        return parent.get(row['code'])

    def addEntry(self, obj, row, site):
        parent = self.getParent(row, site)
        parent.addFaculty(obj)
        return

    def delEntry(self, row, site):
        parent = self.getParent(row, site)
        del parent[row['code']]
        pass

    def updateEntry(self, obj, row, site, filename):
        """Update obj to the values given in row.
        """
        items_changed = ''

        if 'local_roles' in row and row['local_roles'] not in (
            None, IGNORE_MARKER):
            role_manager = IPrincipalRoleManager(obj)
            role_map = IPrincipalRoleMap(obj)
            # Remove all existing local roles.
            for local_role, user_name, setting in role_map.getPrincipalsAndRoles():
                role_manager.unsetRoleForPrincipal(local_role, user_name)
                notify(LocalRoleSetEvent(
                        obj, local_role, user_name, granted=False))
            # Add new local roles.
            if row['local_roles'] != DELETION_MARKER:
                local_roles = eval(row['local_roles'])
                for rolemap in local_roles:
                    user = rolemap['user_name']
                    local_role = rolemap['local_role']
                    role_manager.assignRoleToPrincipal(local_role, user)
                    notify(LocalRoleSetEvent(obj, local_role, user, granted=True))
                    items_changed += (
                        '%s=%s, ' % ('local_roles', '%s|%s' % (user,local_role)))
            row.pop('local_roles')

        # apply other values...
        items_changed += super(FacultyProcessor, self).updateEntry(
            obj, row, site, filename)

        # Log actions...
        location_field = self.location_fields[0]
        grok.getSite().logger.info('%s - %s - %s - updated: %s'
            % (self.name, filename, row[location_field], items_changed))
        return items_changed

    def checkConversion(self, row, mode='create'):
        """Validates all values in row.
        """
        errs, inv_errs, conv_dict =  super(
            FacultyProcessor, self).checkConversion(row, mode=mode)
        if 'local_roles' in row:
            if row['local_roles'] in (None, DELETION_MARKER, IGNORE_MARKER):
                return errs, inv_errs, conv_dict
            try:
                local_roles = eval(row['local_roles'])
            except:
                errs.append(('local_roles','Error'))
                return errs, inv_errs, conv_dict
            if not isinstance(local_roles, list):
                errs.append(('local_roles','no list'))
                return errs, inv_errs, conv_dict
            for rolemap in local_roles:
                if not isinstance(rolemap, dict):
                    errs.append(('local_roles','no dicts'))
                    return errs, inv_errs, conv_dict
                if not 'user_name' in rolemap.keys() or not \
                    'local_role' in rolemap.keys():
                    errs.append(('local_roles','user_name or local_role missing'))
                    return errs, inv_errs, conv_dict
                local_role = rolemap['local_role']
                if not local_role in self.allowed_roles:
                    errs.append(('local_roles','%s not allowed' % local_role))
                    return errs, inv_errs, conv_dict
                user = rolemap['user_name']
                users = grok.getSite()['users']
                if not user in users.keys():
                    errs.append(('local_roles','%s does not exist' % user))
                    return errs, inv_errs, conv_dict
        return errs, inv_errs, conv_dict

class DepartmentProcessor(FacultyProcessor):
    """A batch processor for IDepartment objects.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'departmentprocessor'
    grok.name(util_name)

    name = _('Department Processor')
    iface = IDepartment
    allowed_roles = Department.local_roles

    location_fields = ['code', 'faculty_code']
    factory_name = 'waeup.Department'

    mode = None

    def parentsExist(self, row, site):
        if not 'faculties' in site.keys():
            return False
        return row['faculty_code'] in site['faculties']

    def entryExists(self, row, site):
        if not self.parentsExist(row, site):
            return False
        parent = self.getParent(row, site)
        return row['code'] in parent.keys()

    def getParent(self, row, site):
        return site['faculties'][row['faculty_code']]

    def getEntry(self, row, site):
        if not self.entryExists(row, site):
            return None
        parent = self.getParent(row, site)
        return parent.get(row['code'])

    def addEntry(self, obj, row, site):
        parent = self.getParent(row, site)
        parent.addDepartment(obj)
        return

    def delEntry(self, row, site):
        parent = self.getParent(row, site)
        del parent[row['code']]
        return

class CertificateProcessor(FacultyProcessor):
    """A batch processor for ICertificate objects.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'certificateprocessor'
    grok.name(util_name)

    name = _('Certificate Processor')
    iface = ICertificate
    allowed_roles = Certificate.local_roles

    location_fields = ['code']
    factory_name = 'waeup.Certificate'

    mode = None

    @property
    def available_fields(self):
        fields = getFields(self.iface)
        return sorted(list(set(
            ['faculty_code','department_code'] + fields.keys()
            + ['local_roles'])))

    def checkHeaders(self, headerfields, mode='create'):
        super(CertificateProcessor, self).checkHeaders(headerfields, mode)
        if mode == 'create':
            if not 'faculty_code' in headerfields \
                and not 'department_code' in headerfields :
                raise FatalCSVError(
                    "Need at least columns faculty_code and department_code")
        return True

    def parentsExist(self, row, site):
        return self.getParent(row,site) is not None

    def entryExists(self, row, site):
        parent = self.getParent(row, site)
        if parent is not None:
            return row['code'] in parent.keys()
        return False

    def getParent(self, row, site):
        if not 'faculties' in site.keys():
            return None
        # If both faculty and department codes are provided, use
        # these to get parent.
        if row.get('faculty_code',None) not in (None, IGNORE_MARKER) and \
            row.get('department_code',None) not in (None, IGNORE_MARKER):
            if not row['faculty_code'] in site['faculties'].keys():
                return None
            faculty = site['faculties'][row['faculty_code']]
            if not row['department_code'] in faculty.keys():
                return None
            dept = faculty[row['department_code']]
            return dept.certificates
        # If department code or faculty code is missing,
        # use catalog to get parent. Makes only sense in update mode but
        # does also work in create mode.
        cat = queryUtility(ICatalog, name='certificates_catalog')
        results = list(
            cat.searchResults(code=(row['code'], row['code'])))
        if results:
            return results[0].__parent__
        return None

    def getEntry(self, row, site):
        parent = self.getParent(row, site)
        if parent is not None:
            return parent.get(row['code'])
        return None

    def addEntry(self, obj, row, site):
        parent = self.getParent(row, site)
        parent.addCertificate(obj)
        return

    def delEntry(self, row, site):
        parent = self.getParent(row, site)
        del parent[row['code']]
        return

class CourseProcessor(CertificateProcessor):
    """A batch processor for ICourse objects.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'courseprocessor'
    grok.name(util_name)

    name = _('Course Processor')
    iface = ICourse
    allowed_roles = Course.local_roles

    location_fields = ['code']
    factory_name = 'waeup.Course'

    mode = None

    def getParent(self, row, site):
        if not 'faculties' in site.keys():
            return None
        # If both faculty and department codes are provided, use
        # these to get parent.
        if row.get('faculty_code',None) not in (None, IGNORE_MARKER) and \
            row.get('department_code',None) not in (None, IGNORE_MARKER):
            if not row['faculty_code'] in site['faculties'].keys():
                return None
            faculty = site['faculties'][row['faculty_code']]
            if not row['department_code'] in faculty.keys():
                return None
            dept = faculty[row['department_code']]
            return dept.courses
        # If department code or faculty code is missing,
        # use catalog to get parent. Makes only sense in update mode but
        # does also work in create mode.
        cat = queryUtility(ICatalog, name='courses_catalog')
        results = list(
            cat.searchResults(code=(row['code'], row['code'])))
        if results:
            return results[0].__parent__
        return None

    def addEntry(self, obj, row, site):
        parent = self.getParent(row, site)
        parent.addCourse(obj)
        return

class CertificateCourseProcessor(FacultyProcessor):
    """A batch processor for ICertificateCourse objects.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'certificatecourseprocessor'
    grok.name(util_name)

    name = _('CertificateCourse Processor')
    iface = ICertificateCourse

    location_fields = ['certificate_code', 'course', 'level', 'faculty_code',
                       'department_code',]
    factory_name = 'waeup.CertificateCourse'

    mode = None

    def parentsExist(self, row, site):
        if not 'faculties' in site.keys():
            return False
        if not row['faculty_code'] in site['faculties'].keys():
            return False
        faculty = site['faculties'][row['faculty_code']]
        if not row['department_code'] in faculty.keys():
            return False
        dept = faculty[row['department_code']]
        return row['certificate_code'] in dept.certificates.keys()

    def entryExists(self, row, site):
        if not self.parentsExist(row, site):
            return False
        parent = self.getParent(row, site)
        code = "%s_%s" % (row['course'].code, row['level'])
        return code in parent.keys()

    def getParent(self, row, site):
        dept = site['faculties'][row['faculty_code']][row['department_code']]
        return dept.certificates[row['certificate_code']]

    def getEntry(self, row, site):
        if not self.entryExists(row, site):
            return None
        parent = self.getParent(row, site)
        return parent.get("%s_%s" % (row['course'].code, row['level']))

    def addEntry(self, obj, row, site):
        parent = self.getParent(row, site)
        parent.addCertCourse(row['course'],
                            row['level'], row.get('mandatory',None))
                            # mandatory is not a required and might be missing
        return

    def delEntry(self, row, site):
        parent = self.getParent(row, site)
        parent.delCertCourses(row['course'].code, row['level'])
        return
