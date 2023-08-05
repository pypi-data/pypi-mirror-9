## $Id: browser.py 11680 2014-06-06 08:55:12Z henrik $
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
"""Views for mandates.
"""
import grok
from waeup.kofa.browser.layout import UtilityView
from waeup.kofa.interfaces import IUniversity
from waeup.kofa.interfaces import MessageFactory as _

class MandateView(UtilityView, grok.View):
    """View to execute mandate.
    """
    grok.context(IUniversity)
    grok.name('mandate')
    grok.require('waeup.Public')

    def update(self, *args, **kw):
        form = self.request.form
        mandate_id = form.get('mandate_id', None)
        if not mandate_id:
            self.flash(_('Misuse'))
            return
        mandates = grok.getSite()['mandates']
        mandate = mandates.get(mandate_id, None)
        if mandate is None:
            self.flash(_('No mandate.'))
            return
        msg = mandate.execute()
        self.flash(msg)
        return

    def render(self):
        self.redirect(self.url(self.context, 'login'))
        return
