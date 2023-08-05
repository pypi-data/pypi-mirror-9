## $Id: utils.py 11969 2014-11-16 13:06:34Z uli $
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
"""General helper utilities for Kofa.
"""
import grok
import psutil
import string
import pytz
from copy import deepcopy
from random import SystemRandom as r
from zope.i18n import translate
from waeup.kofa.interfaces import IKofaUtils
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.smtp import send_mail as send_mail_internally
from waeup.kofa.utils.helpers import get_sorted_preferred


def send_mail(from_name, from_addr,
              rcpt_name, rcpt_addr,
              subject, body, config):
    """Wrapper for the real SMTP functionality in :mod:`waeup.kofa.smtp`.

    Merely here to stay compatible with lots of calls to this place.
    """
    mail_id = send_mail_internally(
        from_name, from_addr, rcpt_name, rcpt_addr,
        subject, body, config)
    return True


#: A list of phone prefixes (order num, country, prefix).
#: Items with same order num will be sorted alphabetically.
#: The lower the order num, the higher the precedence.
INT_PHONE_PREFIXES = [
    (99, _('Germany'), '49'),
    (1, _('Nigeria'), '234'),
    (99, _('U.S.'), '1'),
    ]


def sorted_phone_prefixes(data=INT_PHONE_PREFIXES, request=None):
    """Sorted tuples of phone prefixes.

    Ordered as shown above and formatted for use in select boxes.

    If request is given, we'll try to translate all country names in
    order to sort alphabetically correctly.

    XXX: This is a function (and not a constant) as different
    languages might give different orders. This is not tested yet.

    XXX: If we really want to use alphabetic ordering here, we might
    think about caching results of translations.
    """
    if request is not None:
        data = [
            (x, translate(y, context=request), z)
            for x, y, z in data]
    return tuple([
        ('%s (+%s)' % (x[1], x[2]), '+%s' % x[2])
        for x in sorted(data)
        ])


class KofaUtils(grok.GlobalUtility):
    """A collection of parameters and methods subject to customization.

    """
    grok.implements(IKofaUtils)
    # This the only place where we define the portal language
    # which is used for the translation of system messages
    # (e.g. object histories).
    PORTAL_LANGUAGE = 'en'

    PREFERRED_LANGUAGES_DICT = {
        'en': (1, u'English'),
        'fr': (2, u'Fran&ccedil;ais'),
        'de': (3, u'Deutsch'),
        'ha': (4, u'Hausa'),
        'yo': (5, u'Yoruba'),
        'ig': (6, u'Igbo'),
        }

    #: A function to return
    @classmethod
    def sorted_phone_prefixes(cls, data=INT_PHONE_PREFIXES, request=None):
        return sorted_phone_prefixes(data, request)

    EXAM_SUBJECTS_DICT = {
        'math': 'Mathematics',
        'computer_science': 'Computer Science',
        }

    #: Exam grades. The tuple is sorted as it should be displayed in
    #: select boxes.
    EXAM_GRADES = (
        ('A', 'Best'),
        ('B', 'Better'),
        ('C', 'Good'),
        )

    INST_TYPES_DICT = {
        'none': '',
        'faculty': 'Faculty of',
        'department': 'Department of',
        'school': 'School of',
        'office': 'Office for',
        'centre': 'Centre for',
        'institute': 'Institute of',
        'school_for': 'School for',
        'college': 'College of',
        'directorate': 'Directorate of',
        }

    STUDY_MODES_DICT = {
        'transfer': 'Transfer',
        'ug_ft': 'Undergraduate Full-Time',
        'ug_pt': 'Undergraduate Part-Time',
        'pg_ft': 'Postgraduate Full-Time',
        'pg_pt': 'Postgraduate Part-Time',
        }

    DISABLE_PAYMENT_GROUP_DICT = {
        'sf_all': 'School Fee - All Students',
        }

    APP_CATS_DICT = {
        'basic': 'Basic Application',
        'no': 'no application',
        'pg': 'Postgraduate',
        'sandwich': 'Sandwich',
        'cest': 'Part-Time, Diploma, Certificate'
        }

    SEMESTER_DICT = {
        1: '1st Semester',
        2: '2nd Semester',
        3: 'Combined',
        9: 'N/A'
        }

    SPECIAL_HANDLING_DICT = {
        'regular': 'Regular Hostel',
        'blocked': 'Blocked Hostel',
        'pg': 'Postgraduate Hostel'
        }

    SPECIAL_APP_DICT = {
        'transcript': 'Transcript Fee Payment',
        'clearance': 'Acceptance Fee',
        }

    PAYMENT_CATEGORIES = {
        'schoolfee': 'School Fee',
        'clearance': 'Acceptance Fee',
        'bed_allocation': 'Bed Allocation Fee',
        'hostel_maintenance': 'Hostel Maintenance Fee',
        'transfer': 'Transfer Fee',
        'gown': 'Gown Hire Fee',
        'application': 'Application Fee',
        'transcript': 'Transcript Fee',
        }

    SELECTABLE_PAYMENT_CATEGORIES = deepcopy(PAYMENT_CATEGORIES)

    PREVIOUS_PAYMENT_CATEGORIES = deepcopy(SELECTABLE_PAYMENT_CATEGORIES)

    BALANCE_PAYMENT_CATEGORIES = {
        'schoolfee': 'School Fee',
        }

    MODE_GROUPS = {
        'All': ('all',),
        'Undergraduate Full-Time': ('ug_ft',),
        'Undergraduate Part-Time': ('ug_pt',),
        'Postgraduate Full-Time': ('pg_ft',),
        'Postgraduate Part-Time': ('pg_pt',),
        }

    #: Set positive number for allowed max, negative for required min
    #: avail.
    #:
    #: Use integer for bytes value, float for percent
    #: value. `cpu-load`, of course, accepts float values only.
    #: `swap-mem` = Swap Memory, `virt-mem` = Virtual Memory,
    #: `cpu-load` = CPU load in percent.
    SYSTEM_MAX_LOAD = {
        'swap-mem': None,
        'virt-mem': None,
        'cpu-load': 100.0,
        }

    def sendContactForm(self, from_name, from_addr, rcpt_name, rcpt_addr,
                        from_username, usertype, portal, body, subject):
        """Send an email with data provided by forms.
        """
        config = grok.getSite()['configuration']
        text = _(u"""Fullname: ${a}
User Id: ${b}
User Type: ${c}
Portal: ${d}

${e}
""")
        text = _(text, mapping={
            'a': from_name,
            'b': from_username,
            'c': usertype,
            'd': portal,
            'e': body})
        body = translate(text, 'waeup.kofa',
            target_language=self.PORTAL_LANGUAGE)
        if not (from_addr and rcpt_addr):
            return False
        return send_mail(
            from_name, from_addr, rcpt_name, rcpt_addr,
            subject, body, config)

    @property
    def tzinfo(self):
        # For Nigeria: pytz.timezone('Africa/Lagos')
        # For Germany: pytz.timezone('Europe/Berlin')
        return pytz.utc

    def fullname(self, firstname, lastname, middlename=None):
        """Full name constructor.
        """
        # We do not necessarily have the middlename attribute
        if middlename:
            name = '%s %s %s' % (firstname, middlename, lastname)
        else:
            name = '%s %s' % (firstname, lastname)
        return string.capwords(
            name.replace('-', ' - ')).replace(' - ', '-')

    def genPassword(self, length=8, chars=string.letters + string.digits):
        """Generate a random password.
        """
        return ''.join([r().choice(chars) for i in range(length)])

    def sendCredentials(self, user, password=None, url_info=None, msg=None):
        """Send credentials as email.

        Input is the applicant for which credentials are sent and the
        password.

        Returns True or False to indicate successful operation.
        """
        subject = 'Your Kofa credentials'
        text = _(u"""Dear ${a},

${b}
Student Registration and Information Portal of
${c}.

Your user name: ${d}
Your password: ${e}
${f}

Please remember your user name and keep
your password secret!

Please also note that passwords are case-sensitive.

Regards
""")
        config = grok.getSite()['configuration']
        from_name = config.name_admin
        from_addr = config.email_admin
        rcpt_name = user.title
        rcpt_addr = user.email
        text = _(text, mapping={
            'a': rcpt_name,
            'b': msg,
            'c': config.name,
            'd': user.name,
            'e': password,
            'f': url_info})

        body = translate(text, 'waeup.kofa',
            target_language=self.PORTAL_LANGUAGE)
        return send_mail(
            from_name, from_addr, rcpt_name, rcpt_addr,
            subject, body, config)

    def getPaymentItem(self, payment):
        """Return payment item.

        This method can be used to customize the display_item property method.
        """
        return payment.p_item

    def expensive_actions_allowed(self, type=None, request=None):
        """Tell, whether expensive actions are currently allowed.

        Check system load/health (or other external circumstances) and
        locally set values to see, whether expensive actions should be
        allowed (`True`) or better avoided (`False`).

        Use this to allow or forbid exports, report generations, or
        similar actions.
        """
        max_values = self.SYSTEM_MAX_LOAD
        for (key, func) in (
            ('swap-mem', psutil.swap_memory),
            ('virt-mem', psutil.virtual_memory),
            ):
            max_val = max_values.get(key, None)
            if max_val is None:
                continue
            mem_val = func()
            if isinstance(max_val, float):
                # percents
                if max_val < 0.0:
                    max_val = 100.0 + max_val
                if mem_val.percent > max_val:
                    return False
            else:
                # number of bytes
                if max_val < 0:
                    max_val = mem_val.total + max_val
                if mem_val.used > max_val:
                    return False
        return True
