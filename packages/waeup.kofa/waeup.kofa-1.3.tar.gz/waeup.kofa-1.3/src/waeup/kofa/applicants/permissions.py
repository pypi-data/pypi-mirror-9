## $Id: permissions.py 10226 2013-05-24 17:54:10Z henrik $
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
Local permissions for applicants/applications.
"""
import grok

# Application permissions

class HandleApplication(grok.Permission):
    grok.name('waeup.handleApplication')

class ViewApplication(grok.Permission):
    grok.name('waeup.viewApplication')

class ViewApplicationsTab(grok.Permission):
    grok.name('waeup.viewApplicantsTab')

class ViewMyApplicationDataTab(grok.Permission):
    grok.name('waeup.viewMyApplicationDataTab')

class ManageApplication(grok.Permission):
    grok.name('waeup.manageApplication')

class ViewApplicationStatistics(grok.Permission):
    grok.name('waeup.viewApplicationStatistics')

class PayApplicant(grok.Permission):
    grok.name('waeup.payApplicant')

# Local role
class ApplicationOwner(grok.Role):
    grok.name('waeup.local.ApplicationOwner')
    grok.title(u'Application Owner')
    grok.permissions('waeup.handleApplication', 'waeup.viewApplication',
                     'waeup.payApplicant')

# Site role

class ApplicantRole(grok.Role):
    grok.name('waeup.Applicant')
    grok.permissions('waeup.viewAcademics', 'waeup.viewMyApplicationDataTab',
                     'waeup.Authenticated')

class ApplicationsOfficer(grok.Role):
    grok.name('waeup.ApplicationsOfficer')
    grok.title(u'Applications Officer (view only)')
    grok.permissions('waeup.viewApplication', 'waeup.viewApplicantsTab')

class ApplicationsManager(grok.Role):
    grok.name('waeup.ApplicationsManager')
    grok.title(u'Applications Manager')
    grok.permissions('waeup.manageApplication', 'waeup.viewApplication',
                     'waeup.viewApplicantsTab', 'waeup.payApplicant')
