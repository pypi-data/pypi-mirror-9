## $Id: studylevel.py 10631 2013-09-21 05:12:49Z henrik $
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
Container which holds the data of a student study level
and contains the course tickets.
"""
import grok
from zope.component.interfaces import IFactory
from zope.catalog.interfaces import ICatalog
from zope.component import createObject, queryUtility
from zope.interface import implementedBy
from waeup.kofa.interfaces import academic_sessions_vocab, VALIDATED
from waeup.kofa.students.interfaces import (
    IStudentStudyLevel, IStudentNavigation, ICourseTicket)
from waeup.kofa.utils.helpers import attrs_to_fields
from waeup.kofa.students.vocabularies import StudyLevelSource

def find_carry_over(ticket):
    studylevel = ticket.__parent__
    studycourse = ticket.__parent__.__parent__
    levels = sorted(studycourse.keys())
    index = levels.index(str(studylevel.level))
    try:
        next_level = levels[index+1]
    except IndexError:
        return None
    next_studylevel = studycourse[next_level]
    co_ticket = next_studylevel.get(ticket.code, None)
    return co_ticket

def getGradeWeightFromScore(score):
    if score is None:
        return (None, None)
    if score >= 70:
        return ('A',5)
    if score >= 60:
        return ('B',4)
    if score >= 50:
        return ('C',3)
    if score >= 45:
        return ('D',2)
    if score >= 40:
        return ('E',1)
    return ('F',0)

class StudentStudyLevel(grok.Container):
    """This is a container for course tickets.
    """
    grok.implements(IStudentStudyLevel, IStudentNavigation)
    grok.provides(IStudentStudyLevel)

    def __init__(self):
        super(StudentStudyLevel, self).__init__()
        self.level = None
        return

    @property
    def student(self):
        try:
            return self.__parent__.__parent__
        except AttributeError:
            return None

    @property
    def certcode(self):
        try:
            return self.__parent__.certificate.code
        except AttributeError:
            return None

    @property
    def number_of_tickets(self):
        return len(self)

    @property
    def total_credits(self):
        total = 0
        for ticket in self.values():
            total += ticket.credits
        return total

    @property
    def getSessionString(self):
        return academic_sessions_vocab.getTerm(
            self.level_session).title

    @property
    def gpa_params_rectified(self):
        """Calculate corrected corrected level (sesional) gpa parameters.

        The corrected gpa is displayed on transcripts only.
        """
        credits_weighted = 0.0
        credits_counted = 0
        level_gpa = 0.0
        for ticket in self.values():
            if ticket.carry_over is False and ticket.score:
                if ticket.score < ticket.passmark:
                    co_ticket = find_carry_over(ticket)
                    if co_ticket is not None and co_ticket.weight is not None:
                        credits_counted += co_ticket.credits
                        credits_weighted += co_ticket.credits * co_ticket.weight
                    continue
                credits_counted += ticket.credits
                credits_weighted += ticket.credits * ticket.weight
        if credits_counted:
            level_gpa = round(credits_weighted/credits_counted, 3)
        return level_gpa, credits_counted, credits_weighted

    @property
    def gpa_params(self):
        """Calculate gpa parameters for this level.
        """
        credits_weighted = 0.0
        credits_counted = 0
        level_gpa = 0.0
        for ticket in self.values():
            if ticket.score is not None:
                credits_counted += ticket.credits
                credits_weighted += ticket.credits * ticket.weight
        if credits_counted:
            level_gpa = round(credits_weighted/credits_counted, 3)
        return level_gpa, credits_counted, credits_weighted

    @property
    def gpa(self):
        return self.gpa_params[0]

    @property
    def passed_params(self):
        """Determine the number and credits of passed and failed courses.

        This method is used for level reports.
        """
        passed = failed = 0
        courses_failed = []
        credits_failed = 0
        credits_passed = 0
        for ticket in self.values():
            if ticket.score is not None:
                if ticket.score < ticket.passmark:
                    failed += 1
                    credits_failed += ticket.credits
                    courses_failed.append(ticket.code)
                else:
                    passed += 1
                    credits_passed += ticket.credits
        return passed, failed, credits_passed, credits_failed, courses_failed

    @property
    def cumulative_params(self):
        """Calculate the cumulative gpa and other cumulative parameters
        for this level.

        All levels below this level are taken under consideration
        (including repeating levels). This method is used for level reports.
        """
        credits_passed = 0
        total_credits = 0
        total_credits_counted = 0
        total_credits_weighted = 0
        cgpa = 0.0
        for level in self.__parent__.values():
            if level.level > self.level:
                continue
            credits_passed += level.passed_params[2]
            total_credits += level.total_credits
            gpa_params = level.gpa_params
            total_credits_counted += gpa_params[1]
            total_credits_weighted += gpa_params[2]
        if total_credits_counted:
            cgpa = round(total_credits_weighted / total_credits_counted, 3)
        return (cgpa, total_credits_counted, total_credits_weighted,
               total_credits, credits_passed)

    @property
    def is_current_level(self):
        try:
            return self.__parent__.current_level == self.level
        except AttributeError:
            return False

    def writeLogMessage(self, view, message):
        return self.__parent__.__parent__.writeLogMessage(view, message)

    @property
    def level_title(self):
        studylevelsource = StudyLevelSource()
        return studylevelsource.factory.getTitle(self.__parent__, self.level)

    def addCourseTicket(self, ticket, course):
        """Add a course ticket object.
        """
        if not ICourseTicket.providedBy(ticket):
            raise TypeError(
                'StudentStudyLeves contain only ICourseTicket instances')
        ticket.code = course.code
        ticket.title = course.title
        ticket.fcode = course.__parent__.__parent__.__parent__.code
        ticket.dcode = course.__parent__.__parent__.code
        ticket.credits = course.credits
        ticket.passmark = course.passmark
        ticket.semester = course.semester
        self[ticket.code] = ticket
        return

    def addCertCourseTickets(self, cert):
        """Collect all certificate courses and create course
        tickets automatically.
        """
        if cert is not None:
            for key, val in cert.items():
                if val.level != self.level:
                    continue
                ticket = createObject(u'waeup.CourseTicket')
                ticket.automatic = True
                ticket.mandatory = val.mandatory
                ticket.carry_over = False
                self.addCourseTicket(ticket, val.course)
        return

StudentStudyLevel = attrs_to_fields(
    StudentStudyLevel, omit=['total_credits', 'gpa'])

class StudentStudyLevelFactory(grok.GlobalUtility):
    """A factory for student study levels.
    """
    grok.implements(IFactory)
    grok.name(u'waeup.StudentStudyLevel')
    title = u"Create a new student study level.",
    description = u"This factory instantiates new student study level instances."

    def __call__(self, *args, **kw):
        return StudentStudyLevel()

    def getInterfaces(self):
        return implementedBy(StudentStudyLevel)

class CourseTicket(grok.Model):
    """This is a course ticket which allows the
    student to attend the course. Lecturers will enter scores and more at
    the end of the term.

    A course ticket contains a copy of the original course and
    certificate course data. If the courses and/or the referrin certificate
    courses are removed, the corresponding tickets remain unchanged.
    So we do not need any event
    triggered actions on course tickets.
    """
    grok.implements(ICourseTicket, IStudentNavigation)
    grok.provides(ICourseTicket)

    def __init__(self):
        super(CourseTicket, self).__init__()
        self.code = None
        return

    @property
    def student(self):
        """Get the associated student object.
        """
        try:
            return self.__parent__.__parent__.__parent__
        except AttributeError:
            return None

    @property
    def certcode(self):
        try:
            return self.__parent__.__parent__.certificate.code
        except AttributeError:
            return None

    @property
    def removable_by_student(self):
        return not self.mandatory

    @property
    def editable_by_lecturer(self):
        cas = grok.getSite()['configuration'].current_academic_session
        if self.student.state == VALIDATED and self.student.current_session == cas:
            return True
        return False

    def writeLogMessage(self, view, message):
        return self.__parent__.__parent__.__parent__.writeLogMessage(view, message)

    @property
    def level(self):
        """Returns the id of the level the ticket has been added to.
        """
        try:
            return self.__parent__.level
        except AttributeError:
            return None

    @property
    def level_session(self):
        """Returns the session of the level the ticket has been added to.
        """
        try:
            return self.__parent__.level_session
        except AttributeError:
            return None

    @property
    def grade(self):
        """Returns the grade calculated from score.
        """
        return getGradeWeightFromScore(self.score)[0]

    @property
    def weight(self):
        """Returns the weight calculated from score.
        """
        return getGradeWeightFromScore(self.score)[1]

    @property
    def course(self):
        """Returns the course the ticket is referring to. Returns
        None if the course has been removed.

        This method is not used in Kofa anymore.
        """
        cat = queryUtility(ICatalog, name='courses_catalog')
        result = cat.searchResults(code=(self.code, self.code))
        if len(result) != 1:
            return None
        return list(result)[0]

CourseTicket = attrs_to_fields(CourseTicket)

class CourseTicketFactory(grok.GlobalUtility):
    """A factory for student study levels.
    """
    grok.implements(IFactory)
    grok.name(u'waeup.CourseTicket')
    title = u"Create a new course ticket.",
    description = u"This factory instantiates new course ticket instances."

    def __call__(self, *args, **kw):
        return CourseTicket()

    def getInterfaces(self):
        return implementedBy(CourseTicket)
