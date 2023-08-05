## $Id: fileviewlets.py 12456 2015-01-13 06:23:01Z henrik $
##
## Copyright (C) 2014 Uli Fouquet & Henrik Bettermann
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
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.browser.layout import UtilityView
from waeup.kofa.browser.fileviewlets import (
    FileDisplay, FileUpload, Image)

from waeup.kofa.documents.document import PDFDocument
from waeup.kofa.documents.browser import (
    DocumentManageFormPage, DocumentDisplayFormPage)

from waeup.kofa.documents.workflow import PUBLISHED


# File viewlets for documents

class PDFScanManageUpload(FileUpload):
    """Scan upload viewlet for officers.
    """
    grok.view(DocumentManageFormPage)
    grok.context(PDFDocument)
    grok.require('waeup.manageDocuments')
    label = _(u'PDF File')
    title = _(u'PDF File')
    mus = 1024 * 200
    download_name = u'file.pdf'
    tab_redirect = '#tab2'

    @property
    def download_filename(self):
        return u"%s.pdf" % self.context.document_id


class PDFScanDisplay(FileDisplay):
    """Scan display viewlet.
    """
    grok.order(1)
    grok.context(PDFDocument)
    grok.require('waeup.viewDocuments')
    grok.view(DocumentDisplayFormPage)
    label = _(u'PDF Scan')
    title = _(u'PDF Scan')
    download_name = u'file.pdf'

    @property
    def download_filename(self):
        return u"%s.pdf" % self.context.document_id


class PDFScanImage(UtilityView, Image):
    """Scan document.
    """
    ##: Needs to be protected if not published
    grok.name('file.pdf')
    grok.context(PDFDocument)
    grok.require('waeup.Public')
    download_name = u'file.pdf'

    @property
    def download_filename(self):
        return self.context.document_id

    def update(self):
        if self.context.state != PUBLISHED:
            self.flash(_('The document requested has not yet been published.'),
                type="warning")
            self.redirect(self.application_url())
        return
