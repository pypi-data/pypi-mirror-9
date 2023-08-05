## $Id: interfaces.py 10683 2013-11-02 08:18:00Z henrik $
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
from  grok import getSite
from datetime import datetime
from zope.component import getUtility
from zope.catalog.interfaces import ICatalog
from zope.interface import invariant, Invalid, Attribute
from zope import schema
from waeup.kofa.interfaces import (
    IKofaObject, academic_sessions_vocab, registration_states_vocab)
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.hostels.vocabularies import (
    bed_letters, blocks, SpecialHandlingSource,
    NOT_OCCUPIED)

class IHostelsContainer(IKofaObject):
    """A container for all kind of hostel objects.

    """

    startdate = schema.Datetime(
        title = _(u'Hostel Allocation Start Date'),
        required = False,
        description = _('Example:') + u'2011-12-01 18:30:00+01:00',
        )

    enddate = schema.Datetime(
        title = _(u'Hostel Allocation Closing Date'),
        required = False,
        description = _('Example:') + u'2011-12-31 23:59:59+01:00',
        )

    accommodation_session = schema.Choice(
        title = _(u'Booking Session'),
        source = academic_sessions_vocab,
        default = datetime.now().year,
        required = False,
        readonly = False,
        )

    accommodation_states = schema.List(
        title = _(u'Allowed States'),
        value_type = schema.Choice(
            vocabulary = registration_states_vocab,
            ),
        default = [],
        )

    def clearAllHostels():
        """Clear all hostels.
        """

class IHostel(IKofaObject):
    """A base representation of hostels.

    """

    bed_statistics = Attribute('Number of booked and total beds')

    def loggerInfo(ob_class, comment):
        """Adds an INFO message to the log file
        """

    def clearHostel():
        """Remove all beds.
        """

    def updateBeds():
        """Fill hostel with beds or update beds.
        """

    hostel_id = schema.TextLine(
        title = _(u'Hostel Id'),
        )

    sort_id = schema.Int(
        title = _(u'Sort Id'),
        required = True,
        default = 10,
        )

    hostel_name = schema.TextLine(
        title = _(u'Hostel Name'),
        required = True,
        default = u'Hall 1',
        )

    floors_per_block = schema.Int(
        title = _(u'Floors per Block'),
        required = True,
        default = 1,
        )

    rooms_per_floor = schema.Int(
        title = _(u'Rooms per Floor'),
        required = True,
        default = 2,
        )

    beds_reserved = schema.List(
        title = _(u'Reserved Beds'),
        value_type = schema.TextLine(
            default = u'',
            required = False,
        ),
        required = True,
        readonly = False,
        default = [],
        )

    blocks_for_female = schema.List(
        title = _(u'Blocks for Female Students'),
        value_type = schema.Choice(
            vocabulary = blocks
            ),
        )

    blocks_for_male = schema.List(
        title = _(u'Blocks for Male Students'),
        value_type = schema.Choice(
            vocabulary = blocks
            ),
        )

    beds_for_pre= schema.List(
        title = _(u'Beds for Pre-Study Students'),
        value_type = schema.Choice(
            vocabulary = bed_letters
            ),
        )

    beds_for_fresh = schema.List(
        title = _(u'Beds for Fresh Students'),
        value_type = schema.Choice(
            vocabulary = bed_letters
            ),
        )

    beds_for_returning = schema.List(
        title = _(u'Beds for Returning Students'),
        value_type = schema.Choice(
            vocabulary = bed_letters
            ),
        )

    beds_for_final = schema.List(
        title = _(u'Beds for Final Year Students'),
        value_type = schema.Choice(
            vocabulary = bed_letters
            ),
        )

    beds_for_all = schema.List(
        title = _(u'Beds without category'),
        value_type = schema.Choice(
            vocabulary = bed_letters
            ),
        )

    special_handling = schema.Choice(
        title = _(u'Special Handling'),
        source = SpecialHandlingSource(),
        required = True,
        default = u'regular',
        )

    maint_fee = schema.Float(
        title = _(u'Rent'),
        default = 0.0,
        required = False,
        )

    @invariant
    def blocksOverlap(hostel):
        bfe = hostel.blocks_for_female
        bma = hostel.blocks_for_male
        if set(bfe).intersection(set(bma)):
            raise Invalid(_('Female and male blocks overlap.'))

    @invariant
    def bedsOverlap(hostel):
        beds = (hostel.beds_for_fresh +
                hostel.beds_for_returning +
                hostel.beds_for_final +
                hostel.beds_for_pre +
                hostel.beds_for_all)
        if len(beds) != len(set(beds)):
            raise Invalid(_('Bed categories overlap.'))

class IBed(IKofaObject):
    """A base representation of beds.

    """

    coordinates = Attribute('The coordinates of the bed from bed_id')

    def loggerInfo(ob_class, comment):
        """Adds an INFO message to the log file
        """

    def bookBed(student_id):
        """Book a bed for a student.
        """

    def switchReservation():
        """Reserves bed or relases reserved bed respectively.
        """

    bed_id = schema.TextLine(
        title = _(u'Bed Id'),
        required = True,
        default = u'',
        )

    bed_type = schema.TextLine(
        title = _(u'Bed Type'),
        required = True,
        default = u'',
        )

    bed_number = schema.Int(
        title = _(u'Bed Number'),
        required = True,
        )

    owner = schema.TextLine(
        title = _(u'Owner (Student)'),
        description = _('Enter valid student id.'),
        required = True,
        default = u'',
        )

    @invariant
    def allowed_owners(bed):
        if bed.owner == NOT_OCCUPIED:
            return
        catalog = getUtility(ICatalog, name='students_catalog')
        accommodation_session = getSite()['hostels'].accommodation_session
        students = catalog.searchResults(current_session=(
            accommodation_session,accommodation_session))
        student_ids = [student.student_id for student in students]
        if not bed.owner in student_ids:
            raise Invalid(_(
                "Either student does not exist or student "
                "is not in accommodation session."))
        catalog = getUtility(ICatalog, name='beds_catalog')
        beds = catalog.searchResults(owner=(bed.owner,bed.owner))
        if len(beds):
            allocated_bed = [bed.bed_id for bed in beds][0]
            raise Invalid(_(
                "This student resides in bed ${a}.", mapping = {'a':allocated_bed}))
