## $Id: permissions.py 12440 2015-01-11 09:04:51Z henrik $
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
import grok
from zope.component import getUtilitiesFor
from zope.interface import Interface
from zope.securitypolicy.interfaces import IRole, IPrincipalRoleMap
from waeup.kofa.interfaces import ILocalRolesAssignable

class Public(grok.Permission):
    """Everyone-can-do-this-permission.

    This permission is meant to be applied to objects/views/pages
    etc., that should be usable/readable by everyone.

    We need this to be able to tune default permissions more
    restrictive and open up some dedicated objects like the front
    page.
    """
    grok.name('waeup.Public')

class Anonymous(grok.Permission):
    """Only-anonymous-can-do-this-permission.
    """
    grok.name('waeup.Anonymous')

class Authenticated(grok.Permission):
    """Only-logged-in-users-can-do-this-permission.
    """
    grok.name('waeup.Authenticated')

class ViewAcademicsPermission(grok.Permission):
    grok.name('waeup.viewAcademics')

class ManageAcademicsPermission(grok.Permission):
    grok.name('waeup.manageAcademics')

class ManagePortal(grok.Permission):
    grok.name('waeup.managePortal')

class ManageUsers(grok.Permission):
    grok.name('waeup.manageUsers')

class ShowStudents(grok.Permission):
    grok.name('waeup.showStudents')

class ClearAllStudents(grok.Permission):
    grok.name('waeup.clearAllStudents')

class EditScores(grok.Permission):
    grok.name('waeup.editScores')

class EditUser(grok.Permission):
    grok.name('waeup.editUser')

class ManageDataCenter(grok.Permission):
    grok.name('waeup.manageDataCenter')

class ImportData(grok.Permission):
    grok.name('waeup.importData')

class ExportData(grok.Permission):
    grok.name('waeup.exportData')

class ExportPaymentsOverview(grok.Permission):
    grok.name('waeup.exportPaymentsOverview')

class ExportBursaryData(grok.Permission):
    grok.name('waeup.exportBursaryData')

class ViewTranscript(grok.Permission):
    grok.name('waeup.viewTranscript')

class ManagePortalConfiguration(grok.Permission):
    grok.name('waeup.managePortalConfiguration')

class ManageACBatches(grok.Permission):
    grok.name('waeup.manageACBatches')

class PutBiometricDataPermission(grok.Permission):
    """Permission to upload/change biometric data.
    """
    grok.name('waeup.putBiometricData')

class GetBiometricDataPermission(grok.Permission):
    """Permission to read biometric data.
    """
    grok.name('waeup.getBiometricData')


# Local Roles
class ApplicationsManager(grok.Role):
    grok.name('waeup.local.ApplicationsManager')
    grok.title(u'Applications Manager')
    grok.permissions('waeup.viewAcademics')

class DepartmentManager(grok.Role):
    grok.name('waeup.local.DepartmentManager')
    grok.title(u'Department Manager')
    grok.permissions('waeup.manageAcademics',
                     'waeup.showStudents',
                     'waeup.exportData')

class DepartmentOfficer(grok.Role):
    grok.name('waeup.local.DepartmentOfficer')
    grok.title(u'Department Officer')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportPaymentsOverview')

class ClearanceOfficer(grok.Role):
    """The clearance officer role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.ClearanceOfficer')
    grok.title(u'Clearance Officer')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData',
                     'waeup.clearAllStudents')

class LocalStudentsManager(grok.Role):
    """The local students manager role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.LocalStudentsManager')
    grok.title(u'Students Manager')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData')

class LocalWorkflowManager(grok.Role):
    """The local workflow manager role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.LocalWorkflowManager')
    grok.title(u'Student Workflow Manager')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData')

class UGClearanceOfficer(grok.Role):
    """The clearance officer role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.UGClearanceOfficer')
    grok.title(u'UG Clearance Officer')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData',
                     'waeup.clearAllStudents')

class PGClearanceOfficer(grok.Role):
    """The clearance officer role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.PGClearanceOfficer')
    grok.title(u'PG Clearance Officer')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData',
                     'waeup.clearAllStudents')

class CourseAdviser100(grok.Role):
    """The 100 level course adviser role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.CourseAdviser100')
    grok.title(u'Course Adviser 100L')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData')

class CourseAdviser200(grok.Role):
    """The course 200 level adviser role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.CourseAdviser200')
    grok.title(u'Course Adviser 200L')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData')

class CourseAdviser300(grok.Role):
    """The 300 level course adviser role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.CourseAdviser300')
    grok.title(u'Course Adviser 300L')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData')

class CourseAdviser400(grok.Role):
    """The 400 level course adviser role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.CourseAdviser400')
    grok.title(u'Course Adviser 400L')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData')

class CourseAdviser500(grok.Role):
    """The 500 level course adviser role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.CourseAdviser500')
    grok.title(u'Course Adviser 500L')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData')

class CourseAdviser600(grok.Role):
    """The 600 level course adviser role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.CourseAdviser600')
    grok.title(u'Course Adviser 600L')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData')

class CourseAdviser700(grok.Role):
    """The 700 level course adviser role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.CourseAdviser700')
    grok.title(u'Course Adviser 700L')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData')

class CourseAdviser800(grok.Role):
    """The 800 level course adviser role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.CourseAdviser800')
    grok.title(u'Course Adviser 800L')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportData')

class Lecturer(grok.Role):
    """The lecturer role is meant for the
    assignment of dynamic roles only.
    """
    grok.name('waeup.local.Lecturer')
    grok.title(u'Lecturer')
    grok.permissions('waeup.showStudents',
                     'waeup.editScores',
                     'waeup.viewAcademics',
                     'waeup.exportData')

class Owner(grok.Role):
    grok.name('waeup.local.Owner')
    grok.title(u'Owner')
    grok.permissions('waeup.editUser')

# Site Roles
class AcademicsOfficer(grok.Role):
    grok.name('waeup.AcademicsOfficer')
    grok.title(u'Academics Officer (view only)')
    grok.permissions('waeup.viewAcademics')

class AcademicsManager(grok.Role):
    grok.name('waeup.AcademicsManager')
    grok.title(u'Academics Manager')
    grok.permissions('waeup.viewAcademics',
                     'waeup.manageAcademics')

class ACManager(grok.Role):
    grok.name('waeup.ACManager')
    grok.title(u'Access Code Manager')
    grok.permissions('waeup.manageACBatches')

class DataCenterManager(grok.Role):
    grok.name('waeup.DataCenterManager')
    grok.title(u'Datacenter Manager')
    grok.permissions('waeup.manageDataCenter')

class ImportManager(grok.Role):
    grok.name('waeup.ImportManager')
    grok.title(u'Import Manager')
    grok.permissions('waeup.manageDataCenter',
                     'waeup.importData')

class ExportManager(grok.Role):
    grok.name('waeup.ExportManager')
    grok.title(u'Export Manager')
    grok.permissions('waeup.manageDataCenter',
                     'waeup.exportData')

class BursaryOfficer(grok.Role):
    grok.name('waeup.BursaryOfficer')
    grok.title(u'Bursary Officer')
    grok.permissions('waeup.showStudents',
                     'waeup.viewAcademics',
                     'waeup.exportBursaryData')

class UsersManager(grok.Role):
    grok.name('waeup.UsersManager')
    grok.title(u'Users Manager')
    grok.permissions('waeup.manageUsers',
                     'waeup.editUser')

class WorkflowManager(grok.Role):
    grok.name('waeup.WorkflowManager')
    grok.title(u'Workflow Manager')
    grok.permissions('waeup.triggerTransition')

class PortalManager(grok.Role):
    grok.name('waeup.PortalManager')
    grok.title(u'Portal Manager')
    grok.permissions('waeup.managePortal',
                     'waeup.manageUsers',
                     'waeup.viewAcademics', 'waeup.manageAcademics',
                     'waeup.manageACBatches',
                     'waeup.manageDataCenter',
                     'waeup.importData',
                     'waeup.exportData',
                     'waeup.viewTranscript',
                     'waeup.viewDocuments', 'waeup.manageDocuments',
                     'waeup.managePortalConfiguration', 'waeup.viewApplication',
                     'waeup.manageApplication', 'waeup.handleApplication',
                     'waeup.viewApplicantsTab', 'waeup.payApplicant',
                     'waeup.viewApplicationStatistics',
                     'waeup.viewStudent', 'waeup.manageStudent',
                     'waeup.clearStudent', 'waeup.payStudent',
                     'waeup.uploadStudentFile', 'waeup.showStudents',
                     'waeup.clearAllStudents',
                     'waeup.editScores',
                     'waeup.triggerTransition',
                     'waeup.viewStudentsContainer','waeup.viewStudentsTab',
                     'waeup.handleAccommodation',
                     'waeup.viewHostels', 'waeup.manageHostels',
                     'waeup.editUser',
                     'waeup.loginAsStudent',
                     'waeup.manageReports',
                     'waeup.manageJobs',
                     )

class CCOfficer(grok.Role):
    """This is basically a copy of the the PortalManager class. We exclude some
    'dangerous' permissions by commenting them out.
    """
    grok.baseclass()
    grok.name('waeup.CCOfficer')
    grok.title(u'Computer Center Officer')
    grok.permissions(#'waeup.managePortal',
                     #'waeup.manageUsers',
                     'waeup.viewAcademics', 'waeup.manageAcademics',
                     #'waeup.manageACBatches',
                     'waeup.manageDataCenter',
                     #'waeup.importData',
                     'waeup.exportData',
                     'waeup.viewTranscript',
                     'waeup.viewDocuments', 'waeup.manageDocuments',
                     'waeup.managePortalConfiguration', 'waeup.viewApplication',
                     'waeup.manageApplication', 'waeup.handleApplication',
                     'waeup.viewApplicantsTab', 'waeup.payApplicant',
                     'waeup.viewApplicationStatistics',
                     'waeup.viewStudent', 'waeup.manageStudent',
                     'waeup.clearStudent', 'waeup.payStudent',
                     'waeup.uploadStudentFile', 'waeup.showStudents',
                     'waeup.clearAllStudents',
                     'waeup.editScores',
                     #'waeup.triggerTransition',
                     'waeup.viewStudentsContainer','waeup.viewStudentsTab',
                     'waeup.handleAccommodation',
                     'waeup.viewHostels', 'waeup.manageHostels',
                     #'waeup.editUser',
                     #'waeup.loginAsStudent',
                     'waeup.manageReports',
                     #'waeup.manageJobs',
                     )

def get_all_roles():
    """Return a list of tuples ``<ROLE-NAME>, <ROLE>``.
    """
    return getUtilitiesFor(IRole)

def get_waeup_roles(also_local=False):
    """Get all Kofa roles.

    Kofa roles are ordinary roles whose id by convention starts with
    a ``waeup.`` prefix.

    If `also_local` is ``True`` (``False`` by default), also local
    roles are returned. Local Kofa roles are such whose id starts
    with ``waeup.local.`` prefix (this is also a convention).

    Returns a generator of the found roles.
    """
    for name, item in get_all_roles():
        if not name.startswith('waeup.'):
            # Ignore non-Kofa roles...
            continue
        if not also_local and name.startswith('waeup.local.'):
            # Ignore local roles...
            continue
        yield item

def get_waeup_role_names():
    """Get the ids of all Kofa roles.

    See :func:`get_waeup_roles` for what a 'KofaRole' is.

    This function returns a sorted list of Kofa role names.
    """
    return sorted([x.id for x in get_waeup_roles()])

class LocalRolesAssignable(grok.Adapter):
    """Default implementation for `ILocalRolesAssignable`.

    This adapter returns a list for dictionaries for objects for which
    we want to know the roles assignable to them locally.

    The returned dicts contain a ``name`` and a ``title`` entry which
    give a role (``name``) and a description, for which kind of users
    the permission is meant to be used (``title``).

    Having this adapter registered we make sure, that for each normal
    object we get a valid `ILocalRolesAssignable` adapter.

    Objects that want to offer certain local roles, can do so by
    setting a (preferably class-) attribute to a list of role ids.

    You can also define different adapters for different contexts to
    have different role lookup mechanisms become available. But in
    normal cases it should be sufficient to use this basic adapter.
    """
    grok.context(Interface)
    grok.provides(ILocalRolesAssignable)

    _roles = []

    def __init__(self, context):
        self.context = context
        role_ids = getattr(context, 'local_roles', self._roles)
        self._roles = [(name, role) for name, role in get_all_roles()
                       if name in role_ids]
        return

    def __call__(self):
        """Get a list of dictionaries containing ``names`` (the roles to
        assign) and ``titles`` (some description of the type of user
        to assign each role to).
        """
        list_of_dict = [dict(
                name=name,
                title=role.title,
                description=role.description)
                for name, role in self._roles]
        return sorted(list_of_dict, key=lambda x: x['name'])

def get_all_users():
    """Get a list of dictionaries.
    """
    users = sorted(grok.getSite()['users'].items(), key=lambda x: x[1].title)
    for key, val in users:
        yield(dict(name=key, val=val))

def get_users_with_local_roles(context):
    """Get a list of dicts representing the local roles set for `context`.

    Each dict returns `user_name`, `user_title`, `local_role`,
    `local_role_title`, and `setting` for each entry in the local
    roles map of the `context` object.
    """
    try:
        role_map = IPrincipalRoleMap(context)
    except TypeError:
        # no map no roles.
        raise StopIteration
    for local_role, user_name, setting in role_map.getPrincipalsAndRoles():
        user = grok.getSite()['users'].get(user_name,None)
        user_title = getattr(user, 'title', user_name)
        local_role_title = getattr(
            dict(get_all_roles()).get(local_role, None), 'title', None)
        yield dict(user_name = user_name,
                   user_title = user_title,
                   local_role = local_role,
                   local_role_title = local_role_title,
                   setting = setting)

def get_users_with_role(role, context):
    """Get a list of dicts representing the usres who have been granted
    a role for `context`.
    """
    try:
        role_map = IPrincipalRoleMap(context)
    except TypeError:
        # no map no roles.
        raise StopIteration
    for user_name, setting in role_map.getPrincipalsForRole(role):
        user = grok.getSite()['users'].get(user_name,None)
        user_title = getattr(user, 'title', user_name)
        user_email = getattr(user, 'email', None)
        yield dict(user_name = user_name,
                   user_title = user_title,
                   user_email = user_email,
                   setting = setting)
