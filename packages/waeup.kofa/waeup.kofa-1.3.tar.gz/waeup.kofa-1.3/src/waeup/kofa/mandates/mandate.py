## $Id: mandate.py 11681 2014-06-06 12:01:03Z henrik $
##
## Copyright (C) 2012 Uli Fouquet & Henrik Bettermann
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
These are the mandates.
"""
import grok
import hashlib
import os
from datetime import datetime, timedelta
from grok import index
from waeup.kofa.interfaces import IUserAccount
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.mandates.interfaces import IMandate

class Mandate(grok.Model):
    """This is a mandate.
    """
    grok.implements(IMandate)
    grok.provides(IMandate)
    grok.baseclass()

    def __init__(self, days=1, mandate_id=None):
        super(Mandate, self).__init__()
        self.creation_date = datetime.utcnow() # offset-naive datetime
        delta = timedelta(days=days)
        self.expires = datetime.utcnow() + delta
        if mandate_id is None:
            mandate_id = os.urandom(20)
            mandate_id = hashlib.md5(mandate_id).hexdigest()
        self.mandate_id = mandate_id
        self.params = {}
        return

    def execute(self):
        return _('Nothing to do.')

class PasswordMandate(Mandate):
    """This is a mandate which can set a password.
    """

    def _setPassword(self):
        user = self.params.get('user', None)
        pwd = self.params.get('password', None)
        if not None in (user, pwd):
            try:
                IUserAccount(user).setPassword(pwd)
                return True
            except:
                return False
        return False

    def execute(self):
        msg = _('Wrong mandate parameters.')
        if self.expires < datetime.utcnow():
            msg = _('Mandate expired.')
        if self._setPassword():
            msg = _('Password has been successfully set. '
                    'Login with your new password.')
            username = IUserAccount(self.params['user']).name
            grok.getSite().logger.info(
                'PasswordMandate used: %s ' % username)
        del self.__parent__[self.mandate_id]
        return msg
