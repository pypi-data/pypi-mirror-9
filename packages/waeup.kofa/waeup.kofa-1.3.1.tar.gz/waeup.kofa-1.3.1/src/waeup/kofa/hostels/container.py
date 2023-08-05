## $Id: container.py 9197 2012-09-18 16:24:21Z henrik $
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
Containers which contain hostels.
"""
import grok
import pytz
from datetime import datetime
from waeup.kofa.hostels.interfaces import IHostelsContainer, IHostel
from waeup.kofa.utils.logger import Logger
from waeup.kofa.utils.helpers import attrs_to_fields

class HostelsContainer(grok.Container, Logger):
    """This is a container for all kind of hostels.
    """
    grok.implements(IHostelsContainer)
    grok.provides(IHostelsContainer)

    def __init__(self):
        super(HostelsContainer, self).__init__()
        return

    def archive(self, id=None):
        raise NotImplementedError()

    def clear(self, id=None, archive=True):
        raise NotImplementedError()

    def addHostel(self, hostel):
        """Add a hostel.
        """
        if not IHostel.providedBy(hostel):
            raise TypeError(
                'HostelsContainers contain only IHostel instances')
        self[hostel.hostel_id] = hostel
        return

    def clearAllHostels(self):
        """Clear all hostels.
        """
        for hostel in self.values():
            hostel.clearHostel()
        return

    logger_name = 'waeup.kofa.${sitename}.hostels'
    logger_filename = 'hostels.log'

    def logger_info(self, ob_class, target, comment=None):
        """Get the logger's info method.
        """
        self.logger.info('%s - %s - %s' % (
                ob_class, target, comment))
        return

    def loggerInfo(self, ob_class, comment=None):
        target = self.__name__
        return self.logger_info(ob_class,target,comment)

    @property
    def expired(self):
        # Check if application has started ...
        if not self.startdate or (
            self.startdate > datetime.now(pytz.utc)):
            return True
        # ... or ended
        if not self.enddate or (
            self.enddate < datetime.now(pytz.utc)):
            return True
        return False

HostelsContainer = attrs_to_fields(HostelsContainer)
