## $Id: accommodation.py 9987 2013-02-24 11:15:47Z henrik $
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
Student accommodation components.
"""
from datetime import datetime
import grok
from zope.component import getUtility
from zope.component.interfaces import IFactory
from zope.interface import implementedBy
from waeup.kofa.interfaces import academic_sessions_vocab, IKofaUtils
from waeup.kofa.students.interfaces import (
    IStudentAccommodation, IStudentNavigation, IBedTicket, IStudentsUtils)
from waeup.kofa.utils.helpers import attrs_to_fields

class StudentAccommodation(grok.Container):
    """This is a container for bed tickets.
    """
    grok.implements(IStudentAccommodation, IStudentNavigation)
    grok.provides(IStudentAccommodation)

    def __init__(self):
        super(StudentAccommodation, self).__init__()
        return

    def addBedTicket(self, bedticket):
        """Add a bed ticket object.
        """
        if not IBedTicket.providedBy(bedticket):
            raise TypeError(
                'StudentAccommodation containers contain only IBedTicket instances')
        self[str(bedticket.booking_session)] = bedticket
        return

    @property
    def student(self):
        return self.__parent__

    def writeLogMessage(self, view, message):
        return self.__parent__.writeLogMessage(view, message)

StudentAccommodation = attrs_to_fields(StudentAccommodation)

class BedTicket(grok.Model):
    """This is a bed ticket which shows that the student has booked a bed.
    """
    grok.implements(IBedTicket, IStudentNavigation)
    grok.provides(IBedTicket)

    def __init__(self):
        super(BedTicket, self).__init__()
        self.booking_date = datetime.utcnow()
        self.bed = None
        return

    @property
    def student(self):
        try:
            return self.__parent__.__parent__
        except AttributeError:
            return None

    @property
    def display_coordinates(self):
        students_utils = getUtility(IStudentsUtils)
        return students_utils.getBedCoordinates(self)

    def writeLogMessage(self, view, message):
        return self.__parent__.__parent__.writeLogMessage(view, message)

    def getSessionString(self):
        return academic_sessions_vocab.getTerm(
            self.booking_session).title

BedTicket = attrs_to_fields(BedTicket, omit=['display_coordinates'])


# Bed tickets must be importable. So we might need a factory.
class BedTicketFactory(grok.GlobalUtility):
    """A factory for bed tickets.
    """
    grok.implements(IFactory)
    grok.name(u'waeup.BedTicket')
    title = u"Create a new bed ticket.",
    description = u"This factory instantiates new bed ticket instances."

    def __call__(self, *args, **kw):
        return BedTicket()

    def getInterfaces(self):
        return implementedBy(BedTicket)
