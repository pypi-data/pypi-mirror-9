## $Id: batching.py 12180 2014-12-09 05:21:31Z henrik $
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
"""Batch processing components for student objects.

Batch processors eat CSV files to add, update or remove large numbers
of certain kinds of objects at once.

Here we define the processors for students specific objects like
students, studycourses, payment tickets and accommodation tickets.
"""
import grok
import unicodecsv as csv # XXX: csv ops should move to dedicated module.
from time import time
from datetime import datetime
from zope.i18n import translate
from zope.interface import Interface
from zope.schema import getFields
from zope.component import queryUtility, getUtility, createObject
from zope.event import notify
from zope.catalog.interfaces import ICatalog
from hurry.workflow.interfaces import IWorkflowState, IWorkflowInfo
from waeup.kofa.interfaces import (
    IBatchProcessor, FatalCSVError, IObjectConverter, IUserAccount,
    IObjectHistory, VALIDATED, REGISTERED, IGNORE_MARKER)
from waeup.kofa.interfaces import IKofaUtils
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.students.interfaces import (
    IStudent, IStudentStudyCourse, IStudentStudyCourseTransfer,
    IStudentUpdateByRegNo, IStudentUpdateByMatricNo,
    IStudentStudyLevel, ICourseTicketImport,
    IStudentOnlinePayment, IStudentVerdictUpdate)
from waeup.kofa.students.workflow import  (
    IMPORTABLE_STATES, IMPORTABLE_TRANSITIONS,
    FORBIDDEN_POSTGRAD_TRANS, FORBIDDEN_POSTGRAD_STATES)
from waeup.kofa.utils.batching import BatchProcessor

class StudentProcessor(BatchProcessor):
    """A batch processor for IStudent objects.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'studentprocessor'
    grok.name(util_name)

    name = _('Student Processor')
    iface = IStudent
    iface_byregnumber = IStudentUpdateByRegNo
    iface_bymatricnumber = IStudentUpdateByMatricNo

    location_fields = []
    factory_name = 'waeup.Student'

    @property
    def available_fields(self):
        fields = getFields(self.iface)
        return sorted(list(set(
            ['student_id','reg_number','matric_number',
            'password', 'state', 'transition'] + fields.keys())))

    def checkHeaders(self, headerfields, mode='create'):
        if 'state' in headerfields and 'transition' in headerfields:
            raise FatalCSVError(
                "State and transition can't be imported at the same time!")
        if not 'reg_number' in headerfields and not 'student_id' \
            in headerfields and not 'matric_number' in headerfields:
            raise FatalCSVError(
                "Need at least columns student_id or reg_number " +
                "or matric_number for import!")
        if mode == 'create':
            for field in self.required_fields:
                if not field in headerfields:
                    raise FatalCSVError(
                        "Need at least columns %s for import!" %
                        ', '.join(["'%s'" % x for x in self.required_fields]))
        # Check for fields to be ignored...
        not_ignored_fields = [x for x in headerfields
                              if not x.startswith('--')]
        if len(set(not_ignored_fields)) < len(not_ignored_fields):
            raise FatalCSVError(
                "Double headers: each column name may only appear once.")
        return True

    def parentsExist(self, row, site):
        return 'students' in site.keys()

    def getLocator(self, row):
        if row.get('student_id',None) not in (None, IGNORE_MARKER):
            return 'student_id'
        elif row.get('reg_number',None) not in (None, IGNORE_MARKER):
            return 'reg_number'
        elif row.get('matric_number',None) not in (None, IGNORE_MARKER):
            return 'matric_number'
        else:
            return None

    # The entry never exists in create mode.
    def entryExists(self, row, site):
        return self.getEntry(row, site) is not None

    def getParent(self, row, site):
        return site['students']

    def getEntry(self, row, site):
        if not 'students' in site.keys():
            return None
        if self.getLocator(row) == 'student_id':
            if row['student_id'] in site['students']:
                student = site['students'][row['student_id']]
                return student
        elif self.getLocator(row) == 'reg_number':
            reg_number = row['reg_number']
            cat = queryUtility(ICatalog, name='students_catalog')
            results = list(
                cat.searchResults(reg_number=(reg_number, reg_number)))
            if results:
                return results[0]
        elif self.getLocator(row) == 'matric_number':
            matric_number = row['matric_number']
            cat = queryUtility(ICatalog, name='students_catalog')
            results = list(
                cat.searchResults(matric_number=(matric_number, matric_number)))
            if results:
                return results[0]
        return None

    def addEntry(self, obj, row, site):
        parent = self.getParent(row, site)
        parent.addStudent(obj)
        # Reset _curr_stud_id if student_id has been imported
        if self.getLocator(row) == 'student_id':
            parent._curr_stud_id -= 1
        # We have to log this if state is provided. If not,
        # logging is done by the event handler handle_student_added
        if 'state' in row:
            parent.logger.info('%s - Student record created' % obj.student_id)
        history = IObjectHistory(obj)
        history.addMessage(_('Student record created'))
        return

    def delEntry(self, row, site):
        student = self.getEntry(row, site)
        if student is not None:
            parent = self.getParent(row, site)
            parent.logger.info('%s - Student removed' % student.student_id)
            del parent[student.student_id]
        pass

    def checkUpdateRequirements(self, obj, row, site):
        """Checks requirements the object must fulfill when being updated.

        This method is not used in case of deleting or adding objects.

        Returns error messages as strings in case of requirement
        problems.
        """
        transition = row.get('transition', IGNORE_MARKER)
        if transition not in (IGNORE_MARKER, ''):
            allowed_transitions = IWorkflowInfo(obj).getManualTransitionIds()
            if transition not in allowed_transitions:
                return 'Transition not allowed.'
            if transition in FORBIDDEN_POSTGRAD_TRANS and \
                obj.is_postgrad:
                return 'Transition not allowed (pg student).'
        state = row.get('state', IGNORE_MARKER)
        if state not in (IGNORE_MARKER, ''):
            if state in FORBIDDEN_POSTGRAD_STATES and \
                obj.is_postgrad:
                return 'State not allowed (pg student).'
        return None

    def updateEntry(self, obj, row, site, filename):
        """Update obj to the values given in row.
        """
        items_changed = ''

        # Remove student_id from row if empty
        if 'student_id' in row and row['student_id'] in (None, IGNORE_MARKER):
            row.pop('student_id')

        # Update password
        # XXX: Take DELETION_MARKER into consideration
        if 'password' in row:
            passwd = row.get('password', IGNORE_MARKER)
            if passwd not in ('', IGNORE_MARKER):
                if passwd.startswith('{SSHA}'):
                    # already encrypted password
                    obj.password = passwd
                else:
                    # not yet encrypted password
                    IUserAccount(obj).setPassword(passwd)
                items_changed += ('%s=%s, ' % ('password', passwd))
            row.pop('password')

        # Update registration state
        if 'state' in row:
            state = row.get('state', IGNORE_MARKER)
            if state not in (IGNORE_MARKER, ''):
                value = row['state']
                IWorkflowState(obj).setState(value)
                msg = _("State '${a}' set", mapping = {'a':value})
                history = IObjectHistory(obj)
                history.addMessage(msg)
                items_changed += ('%s=%s, ' % ('state', state))
            row.pop('state')

        if 'transition' in row:
            transition = row.get('transition', IGNORE_MARKER)
            if transition not in (IGNORE_MARKER, ''):
                value = row['transition']
                IWorkflowInfo(obj).fireTransition(value)
                items_changed += ('%s=%s, ' % ('transition', transition))
            row.pop('transition')

        # apply other values...
        items_changed += super(StudentProcessor, self).updateEntry(
            obj, row, site, filename)

        # Log actions...
        parent = self.getParent(row, site)
        if hasattr(obj,'student_id'):
            # Update mode: the student exists and we can get the student_id.
            # Create mode: the record contains the student_id
            parent.logger.info(
                '%s - %s - %s - updated: %s'
                % (self.name, filename, obj.student_id, items_changed))
        else:
            # Create mode: the student does not yet exist
            # XXX: It seems that this never happens because student_id
            # is always set.
            parent.logger.info(
                '%s - %s - %s - imported: %s' 
                % (self.name, filename, obj.student_id, items_changed))
        return items_changed

    def getMapping(self, path, headerfields, mode):
        """Get a mapping from CSV file headerfields to actually used fieldnames.
        """
        result = dict()
        reader = csv.reader(open(path, 'rb'))
        raw_header = reader.next()
        for num, field in enumerate(headerfields):
            if field not in ['student_id', 'reg_number', 'matric_number'
                             ] and mode == 'remove':
                continue
            if field == u'--IGNORE--':
                # Skip ignored columns in failed and finished data files.
                continue
            result[raw_header[num]] = field
        return result

    def checkConversion(self, row, mode='create'):
        """Validates all values in row.
        """
        iface = self.iface
        if mode in ['update', 'remove']:
            if self.getLocator(row) == 'reg_number':
                iface = self.iface_byregnumber
            elif self.getLocator(row) == 'matric_number':
                iface = self.iface_bymatricnumber
        converter = IObjectConverter(iface)
        errs, inv_errs, conv_dict =  converter.fromStringDict(
            row, self.factory_name, mode=mode)
        if 'transition' in row:
            if row['transition'] not in IMPORTABLE_TRANSITIONS:
                if row['transition'] not in (IGNORE_MARKER, ''):
                    errs.append(('transition','not allowed'))
        if 'state' in row:
            if row['state'] not in IMPORTABLE_STATES:
                if row['state'] not in (IGNORE_MARKER, ''):
                    errs.append(('state','not allowed'))
                else:
                    # State is an attribute of Student and must not
                    # be changed if empty.
                    conv_dict['state'] = IGNORE_MARKER
        try:
            # Correct stud_id counter. As the IConverter for students
            # creates student objects that are not used afterwards, we
            # have to fix the site-wide student_id counter.
            site = grok.getSite()
            students = site['students']
            students._curr_stud_id -= 1
        except (KeyError, TypeError, AttributeError):
                pass
        return errs, inv_errs, conv_dict


class StudentProcessorBase(BatchProcessor):
    """A base for student subitem processor.

    Helps reducing redundancy.
    """
    grok.baseclass()

    # additional available fields
    # beside 'student_id', 'reg_number' and 'matric_number'
    additional_fields = []

    #: header fields additionally required
    additional_headers = []

    @property
    def available_fields(self):
        fields = ['student_id','reg_number','matric_number'
                  ] + self.additional_fields
        return sorted(list(set(fields + getFields(
                self.iface).keys())))

    def checkHeaders(self, headerfields, mode='ignore'):
        if not 'reg_number' in headerfields and not 'student_id' \
            in headerfields and not 'matric_number' in headerfields:
            raise FatalCSVError(
                "Need at least columns student_id " +
                "or reg_number or matric_number for import!")
        for name in self.additional_headers:
            if not name in headerfields:
                raise FatalCSVError(
                    "Need %s for import!" % name)

        # Check for fields to be ignored...
        not_ignored_fields = [x for x in headerfields
                              if not x.startswith('--')]
        if len(set(not_ignored_fields)) < len(not_ignored_fields):
            raise FatalCSVError(
                "Double headers: each column name may only appear once.")
        return True

    def _getStudent(self, row, site):
        NON_VALUES = ['', IGNORE_MARKER]
        if not 'students' in site.keys():
            return None
        if row.get('student_id', '') not in NON_VALUES:
            if row['student_id'] in site['students']:
                student = site['students'][row['student_id']]
                return student
        elif row.get('reg_number', '') not in NON_VALUES:
            reg_number = row['reg_number']
            cat = queryUtility(ICatalog, name='students_catalog')
            results = list(
                cat.searchResults(reg_number=(reg_number, reg_number)))
            if results:
                return results[0]
        elif row.get('matric_number', '') not in NON_VALUES:
            matric_number = row['matric_number']
            cat = queryUtility(ICatalog, name='students_catalog')
            results = list(
                cat.searchResults(matric_number=(matric_number, matric_number)))
            if results:
                return results[0]
        return None

    def parentsExist(self, row, site):
        return self.getParent(row, site) is not None

    def entryExists(self, row, site):
        return self.getEntry(row, site) is not None

    def checkConversion(self, row, mode='ignore'):
        """Validates all values in row.
        """
        converter = IObjectConverter(self.iface)
        errs, inv_errs, conv_dict =  converter.fromStringDict(
            row, self.factory_name, mode=mode)
        return errs, inv_errs, conv_dict

    def getMapping(self, path, headerfields, mode):
        """Get a mapping from CSV file headerfields to actually used fieldnames.
        """
        result = dict()
        reader = csv.reader(open(path, 'rb'))
        raw_header = reader.next()
        for num, field in enumerate(headerfields):
            if field not in ['student_id', 'reg_number', 'matric_number',
                             'p_id', 'code', 'level'
                             ] and mode == 'remove':
                continue
            if field == u'--IGNORE--':
                # Skip ignored columns in failed and finished data files.
                continue
            result[raw_header[num]] = field
        return result


class StudentStudyCourseProcessor(StudentProcessorBase):
    """A batch processor for IStudentStudyCourse objects.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'studycourseupdater'
    grok.name(util_name)

    name = _('StudentStudyCourse Processor (update only)')
    iface = IStudentStudyCourse
    iface_transfer = IStudentStudyCourseTransfer
    factory_name = 'waeup.StudentStudyCourse'

    location_fields = []
    additional_fields = []

    def getParent(self, row, site):
        return self._getStudent(row, site)

    def getEntry(self, row, site):
        student = self.getParent(row, site)
        if student is None:
            return None
        return student.get('studycourse')

    def updateEntry(self, obj, row, site, filename):
        """Update obj to the values given in row.
        """
        entry_mode = row.get('entry_mode', None)
        certificate = row.get('certificate', None)
        current_session = row.get('current_session', None)
        student = self.getParent(row, site)
        if entry_mode == 'transfer':
            # We do not expect any error here since we
            # checked all constraints in checkConversion and
            # in checkUpdateRequirements
            student.transfer(
                certificate=certificate, current_session=current_session)
            obj = student['studycourse']
        items_changed = super(StudentStudyCourseProcessor, self).updateEntry(
            obj, row, site, filename)
        student.__parent__.logger.info(
            '%s - %s - %s - updated: %s'
            % (self.name, filename, student.student_id, items_changed))
        # Update the students_catalog
        notify(grok.ObjectModifiedEvent(student))
        return

    def checkConversion(self, row, mode='ignore'):
        """Validates all values in row.
        """
        # We have to use the correct interface. Transfer
        # updates have different constraints.
        entry_mode = row.get('entry_mode', None)
        if entry_mode == 'transfer':
            converter = IObjectConverter(self.iface_transfer)
        else:
            converter = IObjectConverter(self.iface)
        errs, inv_errs, conv_dict =  converter.fromStringDict(
            row, self.factory_name, mode=mode)

        # We have to check if current_level is in range of certificate.
        if 'certificate' in conv_dict and 'current_level' in conv_dict:
            cert = conv_dict['certificate']
            level = conv_dict['current_level']
            if level < cert.start_level or level > cert.end_level+120:
                errs.append(('current_level','not in range'))
        return errs, inv_errs, conv_dict

    def checkUpdateRequirements(self, obj, row, site):
        """Checks requirements the object must fulfill when being updated.

        Returns error messages as strings in case of requirement
        problems.
        """
        certificate = getattr(obj, 'certificate', None)
        entry_session = getattr(obj, 'entry_session', None)
        current_level = row.get('current_level', None)
        entry_mode = row.get('entry_mode', None)
        # We have to ensure that the student can be transferred.
        if entry_mode == 'transfer':
            if certificate is None or entry_session is None:
                return 'Former study course record incomplete.'
            if 'studycourse_1' in obj.__parent__.keys() and \
                'studycourse_2' in obj.__parent__.keys():
                return 'Maximum number of transfers exceeded.'
        if current_level:
            if current_level == 999 and \
                obj.__parent__.state in FORBIDDEN_POSTGRAD_STATES:
                return 'Not a pg student.'
            cert = row.get('certificate', None)
            if certificate is None and cert is None:
                return 'No certificate to check level.'
            if certificate is not None and cert is None and (
                current_level < certificate.start_level or \
                current_level > certificate.end_level+120):
                return 'current_level not in range.'
        return None

class StudentStudyLevelProcessor(StudentProcessorBase):
    """A batch processor for IStudentStudyLevel objects.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'studylevelprocessor'
    grok.name(util_name)

    name = _('StudentStudyLevel Processor')
    iface = IStudentStudyLevel
    factory_name = 'waeup.StudentStudyLevel'

    location_fields = []

    additional_fields = ['level']
    additional_headers = ['level']

    @property
    def available_fields(self):
        fields = super(StudentStudyLevelProcessor, self).available_fields
        fields.remove('total_credits')
        fields.remove('gpa')
        return  fields

    def getParent(self, row, site):
        student = self._getStudent(row, site)
        if student is None:
            return None
        return student['studycourse']

    def getEntry(self, row, site):
        studycourse = self.getParent(row, site)
        if studycourse is None:
            return None
        return studycourse.get(row['level'])

    def delEntry(self, row, site):
        studylevel = self.getEntry(row, site)
        parent = self.getParent(row, site)
        if studylevel is not None:
            student = self._getStudent(row, site)
            student.__parent__.logger.info('%s - Level removed: %s'
                % (student.student_id, studylevel.__name__))
            del parent[studylevel.__name__]
        return

    def updateEntry(self, obj, row, site, filename):
        """Update obj to the values given in row.
        """
        items_changed = super(StudentStudyLevelProcessor, self).updateEntry(
            obj, row, site, filename)
        obj.level = int(row['level'])
        student = self.getParent(row, site).__parent__
        student.__parent__.logger.info(
            '%s - %s - %s - updated: %s'
            % (self.name, filename, student.student_id, items_changed))
        return

    def addEntry(self, obj, row, site):
        parent = self.getParent(row, site)
        obj.level = int(row['level'])
        parent[row['level']] = obj
        return

    def checkConversion(self, row, mode='ignore'):
        """Validates all values in row.
        """
        errs, inv_errs, conv_dict = super(
            StudentStudyLevelProcessor, self).checkConversion(row, mode=mode)

        # We have to check if level is a valid integer.
        # This is not done by the converter.
        try:
            level = int(row['level'])
            if level not in range(0,1000,10) + [999]:
                errs.append(('level','no valid integer'))
        except ValueError:
            errs.append(('level','no integer'))
        return errs, inv_errs, conv_dict

class CourseTicketProcessor(StudentProcessorBase):
    """A batch processor for ICourseTicket objects.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'courseticketprocessor'
    grok.name(util_name)

    name = _('CourseTicket Processor')
    iface = ICourseTicketImport
    factory_name = 'waeup.CourseTicket'

    location_fields = []
    additional_fields = ['level', 'code']
    additional_headers = ['level', 'code']

    @property
    def available_fields(self):
        fields = [
            'student_id','reg_number','matric_number',
            'mandatory', 'score', 'carry_over', 'automatic',
            'level_session'
            ] + self.additional_fields
        return sorted(fields)

    def getParent(self, row, site):
        student = self._getStudent(row, site)
        if student is None:
            return None
        return student['studycourse'].get(row['level'])

    def getEntry(self, row, site):
        level = self.getParent(row, site)
        if level is None:
            return None
        return level.get(row['code'])

    def updateEntry(self, obj, row, site, filename):
        """Update obj to the values given in row.
        """
        items_changed = super(CourseTicketProcessor, self).updateEntry(
            obj, row, site, filename)
        parent = self.getParent(row, site)
        student = self.getParent(row, site).__parent__.__parent__
        student.__parent__.logger.info(
            '%s - %s - %s - %s - updated: %s'
            % (self.name, filename, student.student_id, parent.level, items_changed))
        return

    def addEntry(self, obj, row, site):
        parent = self.getParent(row, site)
        catalog = getUtility(ICatalog, name='courses_catalog')
        entries = list(catalog.searchResults(code=(row['code'],row['code'])))
        obj.fcode = entries[0].__parent__.__parent__.__parent__.code
        obj.dcode = entries[0].__parent__.__parent__.code
        obj.title = entries[0].title
        #if getattr(obj, 'credits', None) is None:
        obj.credits = entries[0].credits
        #if getattr(obj, 'passmark', None) is None:
        obj.passmark = entries[0].passmark
        obj.semester = entries[0].semester
        parent[row['code']] = obj
        return

    def delEntry(self, row, site):
        ticket = self.getEntry(row, site)
        parent = self.getParent(row, site)
        if ticket is not None:
            student = self._getStudent(row, site)
            student.__parent__.logger.info('%s - Course ticket in %s removed: %s'
                % (student.student_id, parent.level, ticket.code))
            del parent[ticket.code]
        return

    def checkConversion(self, row, mode='ignore'):
        """Validates all values in row.
        """
        errs, inv_errs, conv_dict = super(
            CourseTicketProcessor, self).checkConversion(row, mode=mode)
        if mode == 'remove':
            return errs, inv_errs, conv_dict
        # In update and create mode we have to check if course really exists.
        # This is not done by the converter.
        catalog = getUtility(ICatalog, name='courses_catalog')
        entries = catalog.searchResults(code=(row['code'],row['code']))
        if len(entries) == 0:
            errs.append(('code','non-existent'))
            return errs, inv_errs, conv_dict
        # If level_session is provided in row we have to check if
        # the parent studylevel exists and if its level_session
        # attribute corresponds with the expected value in row.
        level_session = conv_dict.get('level_session', IGNORE_MARKER)
        if level_session not in (IGNORE_MARKER, None):
            site = grok.getSite()
            studylevel = self.getParent(row, site)
            if studylevel is not None:
                if studylevel.level_session != level_session:
                    errs.append(('level_session','does not match %s'
                        % studylevel.level_session))
            else:
                errs.append(('level','does not exist'))
        return errs, inv_errs, conv_dict

class StudentOnlinePaymentProcessor(StudentProcessorBase):
    """A batch processor for IStudentOnlinePayment objects.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'paymentprocessor'
    grok.name(util_name)

    name = _('StudentOnlinePayment Processor')
    iface = IStudentOnlinePayment
    factory_name = 'waeup.StudentOnlinePayment'

    location_fields = []
    additional_fields = ['p_id']
    additional_headers = []

    def checkHeaders(self, headerfields, mode='ignore'):
        super(StudentOnlinePaymentProcessor, self).checkHeaders(headerfields)
        if mode in ('update', 'remove') and not 'p_id' in headerfields:
            raise FatalCSVError(
                "Need p_id for import in update and remove modes!")
        return True

    def parentsExist(self, row, site):
        return self.getParent(row, site) is not None

    def getParent(self, row, site):
        student = self._getStudent(row, site)
        if student is None:
            return None
        return student['payments']

    def getEntry(self, row, site):
        payments = self.getParent(row, site)
        if payments is None:
            return None
        p_id = row.get('p_id', None)
        if p_id is None:
            return None
        # We can use the hash symbol at the end of p_id in import files
        # to avoid annoying automatic number transformation
        # by Excel or Calc
        p_id = p_id.strip('#')
        if len(p_id.split('-')) != 3 and not p_id.startswith('p'):
            # For data migration from old SRP only
            p_id = 'p' + p_id[7:] + '0'
        entry = payments.get(p_id)
        return entry

    def updateEntry(self, obj, row, site, filename):
        """Update obj to the values given in row.
        """
        items_changed = super(StudentOnlinePaymentProcessor, self).updateEntry(
            obj, row, site, filename)
        student = self.getParent(row, site).__parent__
        student.__parent__.logger.info(
            '%s - %s - %s - updated: %s'
            % (self.name, filename, student.student_id, items_changed))
        return

    def addEntry(self, obj, row, site):
        parent = self.getParent(row, site)
        p_id = row['p_id'].strip('#')
        if len(p_id.split('-')) != 3 and not p_id.startswith('p'):
            # For data migration from old SRP
            obj.p_id = 'p' + p_id[7:] + '0'
            parent[obj.p_id] = obj
        else:
            parent[p_id] = obj
        return

    def delEntry(self, row, site):
        payment = self.getEntry(row, site)
        parent = self.getParent(row, site)
        if payment is not None:
            student = self._getStudent(row, site)
            student.__parent__.logger.info('%s - Payment ticket removed: %s'
                % (student.student_id, payment.p_id))
            del parent[payment.p_id]
        return

    def checkConversion(self, row, mode='ignore'):
        """Validates all values in row.
        """
        errs, inv_errs, conv_dict = super(
            StudentOnlinePaymentProcessor, self).checkConversion(row, mode=mode)

        # We have to check p_id.
        p_id = row.get('p_id', None)
        if not p_id:
            timestamp = ("%d" % int(time()*10000))[1:]
            p_id = "p%s" % timestamp
            conv_dict['p_id'] = p_id
            return errs, inv_errs, conv_dict
        else:
            p_id = p_id.strip('#')
        if p_id.startswith('p'):
            if not len(p_id) == 14:
                errs.append(('p_id','invalid length'))
                return errs, inv_errs, conv_dict
        elif len(p_id.split('-')) == 3:
            # The SRP used either pins as keys ...
            if len(p_id.split('-')[2]) not in (9, 10):
                errs.append(('p_id','invalid pin'))
                return errs, inv_errs, conv_dict
        else:
            # ... or order_ids.
            if not len(p_id) == 19:
                errs.append(('p_id','invalid format'))
                return errs, inv_errs, conv_dict
        return errs, inv_errs, conv_dict

class StudentVerdictProcessor(StudentStudyCourseProcessor):
    """A special batch processor for verdicts.

    Import verdicts and perform workflow transitions.
    """

    util_name = 'verdictupdater'
    grok.name(util_name)

    name = _('Verdict Processor (special processor, update only)')
    iface = IStudentVerdictUpdate
    factory_name = 'waeup.StudentStudyCourse'

    def checkUpdateRequirements(self, obj, row, site):
        """Checks requirements the studycourse and the student must fulfill
        before being updated.
        """
        # Check if current_levels correspond
        if obj.current_level != row['current_level']:
            return 'Current level does not correspond.'
        # Check if current_sessions correspond
        if obj.current_session != row['current_session']:
            return 'Current session does not correspond.'
        # Check if new verdict is provided
        if row['current_verdict'] in (IGNORE_MARKER, ''):
            return 'No verdict in import file.'
        # Check if studylevel exists
        level_string = str(obj.current_level)
        if obj.get(level_string) is None:
            return 'Study level object is missing.'
        # Check if student is in state REGISTERED or VALIDATED
        if row.get('bypass_validation'):
            if obj.student.state not in (VALIDATED, REGISTERED):
                return 'Student in wrong state.'
        else:
            if obj.student.state != VALIDATED:
                return 'Student in wrong state.'
        return None

    def updateEntry(self, obj, row, site, filename):
        """Update obj to the values given in row.
        """
        # Don't set current_session, current_level
        vals_to_set = dict((key, val) for key, val in row.items()
                           if key not in ('current_session','current_level'))
        super(StudentVerdictProcessor, self).updateEntry(
            obj, vals_to_set, site, filename)
        parent = self.getParent(row, site)
        # Set current_vedict in corresponding studylevel
        level_string = str(obj.current_level)
        obj[level_string].level_verdict = row['current_verdict']
        # Fire transition and set studylevel attributes
        # depending on student's state
        if obj.__parent__.state == REGISTERED:
            validated_by = row.get('validated_by', '')
            if validated_by in (IGNORE_MARKER, ''):
                portal_language = getUtility(IKofaUtils).PORTAL_LANGUAGE
                system = translate(_('System'),'waeup.kofa',
                                  target_language=portal_language)
                obj[level_string].validated_by = system
            else:
                obj[level_string].validated_by = validated_by
            obj[level_string].validation_date = datetime.utcnow()
            IWorkflowInfo(obj.__parent__).fireTransition('bypass_validation')
        else:
            IWorkflowInfo(obj.__parent__).fireTransition('return')
        # Update the students_catalog
        notify(grok.ObjectModifiedEvent(obj.__parent__))
        return
