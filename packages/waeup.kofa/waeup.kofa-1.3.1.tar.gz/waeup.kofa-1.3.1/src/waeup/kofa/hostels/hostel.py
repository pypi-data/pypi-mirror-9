## $Id: hostel.py 9701 2012-11-20 11:16:38Z henrik $
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
These are the hostels.
"""
import grok
from zope.event import notify
from zope.component import getUtility
from zope.component.interfaces import IFactory
from datetime import datetime
from waeup.kofa.utils.helpers import attrs_to_fields
from waeup.kofa.hostels.vocabularies import NOT_OCCUPIED
from waeup.kofa.hostels.interfaces import IHostel, IBed
from waeup.kofa.students.interfaces import IBedTicket
from waeup.kofa.interfaces import IKofaUtils
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.utils.helpers import now

class Hostel(grok.Container):
    """This is a hostel.
    """
    grok.implements(IHostel)
    grok.provides(IHostel)

    def loggerInfo(self, ob_class, comment=None):
        target = self.__name__
        return grok.getSite()['hostels'].logger_info(ob_class,target,comment)

    @property
    def bed_statistics(self):
        total = len(self.keys())
        booked = 0
        for value in self.values():
            if value.owner != NOT_OCCUPIED:
                booked += 1
        return {'booked':booked, 'total':total}

    def clearHostel(self):
        """Remove all beds
        """
        keys = [i for i in self.keys()] # create deep copy
        for bed in keys:
            del self[bed]
        return

    def addBed(self, bed):
        """Add a bed.
        """
        if not IBed.providedBy(bed):
            raise TypeError(
                'Hostels contain only IBed instances')
        self[bed.bed_id] = bed
        return

    def updateBeds(self):
        """Fill hostel with beds or update beds.
        """
        added_counter = 0
        modified_counter = 0
        removed_counter = 0
        modified_beds = u''

        # Remove all empty beds. Occupied beds remain in hostel!
        keys = list(self.keys()) # create list copy
        for key in keys:
            if self[key].owner == NOT_OCCUPIED:
                del self[key]
                self._p_changed = True
                removed_counter += 1
            else:
                self[key].bed_number = 9999
        remaining = len(keys) - removed_counter

        blocks_for_female = getattr(self,'blocks_for_female',[])
        blocks_for_male = getattr(self,'blocks_for_male',[])
        beds_for_fresh = getattr(self,'beds_for_fresh',[])
        beds_for_pre = getattr(self,'beds_for_pre',[])
        beds_for_returning = getattr(self,'beds_for_returning',[])
        beds_for_final = getattr(self,'beds_for_final',[])
        beds_for_all = getattr(self,'beds_for_all',[])
        beds_reserved = getattr(self,'beds_reserved',[])
        all_blocks = blocks_for_female + blocks_for_male
        all_beds = (beds_for_pre + beds_for_fresh +
            beds_for_returning + beds_for_final + beds_for_all)
        for block in all_blocks:
            sex = 'male'
            if block in blocks_for_female:
                sex = 'female'
            for floor in range(1,int(self.floors_per_block)+1):
                for room in range(1,int(self.rooms_per_floor)+1):
                    for bed in all_beds:
                        room_nr = floor*100 + room
                        bt = 'all'
                        if '%s_%s_%s' % (block,room_nr,bed) in beds_reserved:
                            bt = "reserved"
                        elif bed in beds_for_fresh:
                            bt = 'fr'
                        elif bed in beds_for_pre:
                            bt = 'pr'
                        elif bed in beds_for_final:
                            bt = 'fi'
                        elif bed in beds_for_returning:
                            bt = 're'
                        bt = u'%s_%s_%s' % (self.special_handling,sex,bt)
                        uid = u'%s_%s_%d_%s' % (self.hostel_id,block,room_nr,bed)
                        if uid in self:
                            bed = self[uid]
                            # Renumber remaining beds
                            bed.bed_number = len(self) + 1 - remaining
                            remaining -= 1
                            if bed.bed_type != bt:
                                bed.bed_type = bt
                                modified_counter += 1
                                modified_beds += '%s, ' % uid
                                notify(grok.ObjectModifiedEvent(bed))
                        else:
                            bed = Bed()
                            bed.bed_id = uid
                            bed.bed_type = bt
                            bed.bed_number = len(self) + 1 - remaining
                            bed.owner = NOT_OCCUPIED
                            self.addBed(bed)
                            added_counter +=1
        return removed_counter, added_counter, modified_counter, modified_beds

Hostel = attrs_to_fields(Hostel)

class Bed(grok.Container):
    """This is a bed.
    """
    grok.implements(IBed)
    grok.provides(IBed)

    @property
    def coordinates(self):
        """Determine the coordinates from the bed_id.
        """
        return self.bed_id.split('_')

    # The following property attributes are only needed
    # for the exporter to ease evaluation with  Excel.

    @property
    def hall(self):
        return self.coordinates[0]

    @property
    def block(self):
        return self.coordinates[1]

    @property
    def room(self):
        return self.coordinates[2]

    @property
    def bed(self):
        return self.coordinates[3]

    @property
    def special_handling(self):
        return self.bed_type.split('_')[0]

    @property
    def sex(self):
        return self.bed_type.split('_')[1]

    @property
    def bt(self):
        return self.bed_type.split('_')[2]


    def bookBed(self, student_id):
        if self.owner == NOT_OCCUPIED:
            self.owner = student_id
            notify(grok.ObjectModifiedEvent(self))
            return None
        else:
            return self.owner

    def switchReservation(self):
        """Reserves or unreserve bed respectively.
        """
        sh, sex, bt = self.bed_type.split('_')
        hostel_id, block, room_nr, bed = self.coordinates
        hostel = self.__parent__
        beds_for_fresh = getattr(hostel,'beds_for_fresh',[])
        beds_for_pre = getattr(hostel,'beds_for_pre',[])
        beds_for_returning = getattr(hostel,'beds_for_returning',[])
        beds_for_final = getattr(hostel,'beds_for_final',[])
        bed_string = u'%s_%s_%s' % (block, room_nr, bed)
        if bt == 'reserved':
            bt = 'all'
            if bed in beds_for_fresh:
                bt = 'fr'
            elif bed in beds_for_pre:
                bt = 'pr'
            elif bed in beds_for_final:
                bt = 'fi'
            elif bed in beds_for_returning:
                bt = 're'
            bt = u'%s_%s_%s' % (sh, sex, bt)

            # Comment of Martijn:
            # If you have a non-Persistent subobject (like a list) and
            # you change it, you need to manually flag the persistence
            # machinery on the object that its subobject changed, with
            # _p_changed. This is only necessary if some of the
            # objects are not sublclasses of Persistent. For common
            # built-in collections in Python such as list and
            # dictionary there are replacements (PersistentList,
            # PersistentMapping), and more advanced building blocks
            # for indexes (BTrees), that don't have this issue.
            #hostel._p_changed = True

            # Henrik: Unfortunately, this doesn't work in our case.
            # After restarting the portal,
            # added or removed list items are gone. The only way to ensure
            # persistance is to reassign the list attribute.
            br = hostel.beds_reserved
            br.remove(bed_string)
            hostel.beds_reserved = br
            message = _(u'unreserved')
        else:
            bt = u'%s_%s_reserved' % (sh, sex)
            # See comment above
            br = hostel.beds_reserved
            br.append(bed_string)
            hostel.beds_reserved = br
            message = _(u'reserved')
        self.bed_type = bt
        notify(grok.ObjectModifiedEvent(self))
        return message

    def releaseBed(self):
        if self.owner == NOT_OCCUPIED:
            return
        else:
            old_owner = self.owner
            self.owner = NOT_OCCUPIED
            notify(grok.ObjectModifiedEvent(self))
            accommodation_session = grok.getSite()[
                'hostels'].accommodation_session
            try:
                bedticket = grok.getSite()['students'][old_owner][
                              'accommodation'][str(accommodation_session)]
            except KeyError:
                return '%s without bed ticket' % old_owner
            bedticket.bed = None
            tz = getUtility(IKofaUtils).tzinfo
            timestamp = now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
            bedticket.bed_coordinates = u'-- booking cancelled on %s --' % (
                timestamp,)
            return old_owner

    def loggerInfo(self, ob_class, comment=None):
        target = self.__name__
        return grok.getSite()['hostels'].logger_info(ob_class,target,comment)

Bed = attrs_to_fields(Bed)

class HostelFactory(grok.GlobalUtility):
    """A factory for hostels.

    We need this factory for the hostel processor.
    """
    grok.implements(IFactory)
    grok.name(u'waeup.Hostel')
    title = u"Create a new hostel.",
    description = u"This factory instantiates new hostel instances."

    def __call__(self, *args, **kw):
        return Hostel()

    def getInterfaces(self):
        return implementedBy(Hostel)


@grok.subscribe(IBedTicket, grok.IObjectRemovedEvent)
def handle_bedticket_removed(bedticket, event):
    """If a bed ticket is deleted, we make sure that also the owner attribute
    of the bed is cleared (set to NOT_OCCUPIED).
    """
    if bedticket.bed != None:
        bedticket.bed.owner = NOT_OCCUPIED
        notify(grok.ObjectModifiedEvent(bedticket.bed))

