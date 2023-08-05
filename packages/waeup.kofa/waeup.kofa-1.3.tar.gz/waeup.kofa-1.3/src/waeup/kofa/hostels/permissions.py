## $Id: permissions.py 7195 2011-11-25 07:34:07Z henrik $
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
Permissions for the accommdation section.
"""
import grok

# Accommodation section permissions

class ViewHostels(grok.Permission):
    grok.name('waeup.viewHostels')

class ManageHostels(grok.Permission):
    grok.name('waeup.manageHostels')

# Site Roles
class AccommodationOfficer(grok.Role):
    grok.name('waeup.AccommodationOfficer')
    grok.title(u'Accommodation Officer')
    grok.permissions('waeup.viewHostels', 'waeup.manageHostels')
