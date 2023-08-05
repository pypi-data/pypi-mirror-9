## $Id: department.py 11891 2014-10-28 20:02:45Z henrik $
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
"""University departments.
"""
import grok
import zope.location.location
from zope.component.interfaces import IFactory
from zope.interface import implementedBy
from zope.component import getUtility
from zope.schema import getFields
from waeup.kofa.university.faculty import longtitle
from waeup.kofa.university.coursescontainer import CoursesContainer
from waeup.kofa.university.certificatescontainer import CertificatesContainer
from waeup.kofa.utils.batching import VirtualExportJobContainer
from waeup.kofa.interfaces import IKofaUtils, IKofaPluggable
from waeup.kofa.utils.helpers import attrs_to_fields
from waeup.kofa.university.interfaces import IDepartment

class VirtualDepartmentExportJobContainer(VirtualExportJobContainer):
    """A virtual export job container for departments.
    """

class Department(grok.Container):
    """A university department.
    """
    grok.implements(IDepartment)

    local_roles = [
        'waeup.local.ApplicationsManager',
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
        ]

    def __init__(self,
                 title=u'Unnamed Department',
                 title_prefix=u'department',
                 code=u"NA", **kw):
        super(Department, self).__init__(**kw)
        self.title = title
        self.title_prefix = title_prefix
        self.code = code
        self.courses = CoursesContainer()
        self.courses.__parent__ = self
        self.courses.__name__ = 'courses'
        self.certificates = CertificatesContainer()
        self.certificates.__parent__ = self
        self.certificates.__name__ = 'certificates'
        self.score_editing_disabled = False

    def traverse(self, name):
        """Deliver appropriate containers, if someone wants to go to courses
        or departments.
        """
        if name == 'courses':
            return self.courses
        elif name == 'certificates':
            return self.certificates
        elif name == 'exports':
            # create a virtual exports container and return it
            container = VirtualDepartmentExportJobContainer()
            zope.location.location.located(container, self, 'exports')
            return container
        return None

    @property
    def longtitle(self):
        return longtitle(self)

class DepartmentFactory(grok.GlobalUtility):
    """A factory for department containers.
    """
    grok.implements(IFactory)
    grok.name(u'waeup.Department')
    title = u"Create a new department.",
    description = u"This factory instantiates new department instances."

    def __call__(self, *args, **kw):
        return Department(*args, **kw)

    def getInterfaces(self):
        """Get interfaces of objects provided by this factory.
        """
        return implementedBy(Department)

class DepartmentsPlugin(grok.GlobalUtility):
    """A plugin that updates courses.
    """

    grok.implements(IKofaPluggable)
    grok.name('departments')

    deprecated_attributes = []

    def setup(self, site, name, logger):
        return

    def update(self, site, name, logger):
        items = getFields(IDepartment).items()
        for faculty in site['faculties'].values():
            for department in faculty.values():
                # Add new attributes
                for i in items:
                    if not hasattr(department,i[0]):
                        setattr(department,i[0],i[1].missing_value)
                        logger.info(
                            'DepartmentsPlugin: %s attribute %s added.' % (
                            department.code,i[0]))
                # Remove deprecated attributes
                for i in self.deprecated_attributes:
                    try:
                        delattr(department,i)
                        logger.info(
                            'DepartmentsPlugin: %s attribute %s deleted.' % (
                            department.code,i))
                    except AttributeError:
                        pass
        return