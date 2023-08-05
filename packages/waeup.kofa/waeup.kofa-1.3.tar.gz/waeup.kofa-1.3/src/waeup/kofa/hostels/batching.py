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
"""Batch processing components for hostels.

"""
import grok
from zope.interface import Interface
from waeup.kofa.interfaces import IBatchProcessor, IGNORE_MARKER
from waeup.kofa.utils.batching import BatchProcessor
from waeup.kofa.hostels.interfaces import IHostel
from waeup.kofa.interfaces import MessageFactory as _

class HostelProcessor(BatchProcessor):
    """A batch processor for IHostel objects.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'hostelprocessor'
    grok.name(util_name)

    name = _('Hostel Processor')
    iface = IHostel

    location_fields = ['hostel_id',]
    factory_name = 'waeup.Hostel'

    mode = None

    def parentsExist(self, row, site):
        return 'hostels' in site.keys()

    def entryExists(self, row, site):
        return row['hostel_id'] in site['hostels'].keys()

    def getParent(self, row, site):
        return site['hostels']

    def getEntry(self, row, site):
        if not self.entryExists(row, site):
            return None
        parent = self.getParent(row, site)
        return parent.get(row['hostel_id'])

    def addEntry(self, obj, row, site):
        parent = self.getParent(row, site)
        parent.addHostel(obj)
        return

    def updateEntry(self, obj, row, site, filename):
        """Update obj to the values given in row.
        """
        changed = []
        for key, value in row.items():
            # Skip fields to be ignored.
            if value == IGNORE_MARKER:
                continue
            if not hasattr(obj, key):
                continue
            try:
                evalvalue = eval(value)
                if isinstance(evalvalue, list):
                    value = evalvalue
            except:
                pass
            setattr(obj, key, value)
            log_value = getattr(value, 'code', value)
            changed.append('%s=%s' % (key, log_value))

        # Log actions...
        location_field = self.location_fields[0]
        items_changed = ', '.join(changed)
        grok.getSite()['hostels'].logger.info(
            '%s - %s - %s - updated: %s'
            % (self.name, filename, row[location_field], items_changed))
        return