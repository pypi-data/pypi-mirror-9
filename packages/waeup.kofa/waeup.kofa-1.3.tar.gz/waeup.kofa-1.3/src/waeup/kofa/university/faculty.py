## $Id: faculty.py 10684 2013-11-02 08:50:58Z henrik $
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
"""Faculty components.
"""

import grok
from zope.component.interfaces import IFactory
from zope.interface import implementedBy
from zope.component import getUtility
from waeup.kofa.interfaces import IKofaUtils
from waeup.kofa.university.interfaces import (
    IFaculty, IDepartment)

def longtitle(inst):
    insttypes_dict = getUtility(IKofaUtils).INST_TYPES_DICT
    if inst.title_prefix == 'none':
        return "%s (%s)" % (inst.title, inst.code)
    return "%s %s (%s)" % (
        insttypes_dict[inst.title_prefix],
        inst.title, inst.code)

class Faculty(grok.Container):
    """A university faculty.
    """
    grok.implements(IFaculty)

    local_roles = [
        'waeup.local.DepartmentOfficer',
        'waeup.local.DepartmentManager',
        'waeup.local.ClearanceOfficer',
        'waeup.local.UGClearanceOfficer',
        'waeup.local.PGClearanceOfficer',
        'waeup.local.CourseAdviser100',
        'waeup.local.CourseAdviser200',
        'waeup.local.CourseAdviser300',
        'waeup.local.CourseAdviser400',
        'waeup.local.CourseAdviser500',
        'waeup.local.CourseAdviser600',
        'waeup.local.CourseAdviser700',
        'waeup.local.CourseAdviser800',
        'waeup.local.LocalStudentsManager',
        'waeup.local.LocalWorkflowManager',
        ]

    def __init__(self,
                 title=u'Unnamed Faculty',
                 title_prefix=u'faculty',
                 code=u'NA', **kw):
        super(Faculty, self).__init__(**kw)
        self.title = title
        self.title_prefix = title_prefix
        self.code = code

    def addDepartment(self, department):
        """Add a department to the faculty.
        """
        if not IDepartment.providedBy(department):
            raise TypeError('Faculties contain only IDepartment instances')
        self[department.code] = department

    @property
    def longtitle(self):
        return longtitle(self)

class FacultyFactory(grok.GlobalUtility):
    """A factory for faculty containers.
    """
    grok.implements(IFactory)
    grok.name(u'waeup.Faculty')
    title = u"Create a new faculty.",
    description = u"This factory instantiates new faculty instances."

    def __call__(self, *args, **kw):
        return Faculty()

    def getInterfaces(self):
        return implementedBy(Faculty)
