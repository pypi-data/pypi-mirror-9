## $Id: fileviewlets.py 12448 2015-01-12 11:00:55Z henrik $
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

import os
import grok
from zope.component import getUtility
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.interfaces import (
    IExtFileStore, IFileStoreNameChooser, IKofaObject)
from waeup.kofa.utils.helpers import string_from_bytes, file_size
from waeup.kofa.browser import DEFAULT_IMAGE_PATH

from waeup.kofa.students.interfaces import IStudent, IStudentsUtils

from waeup.kofa.browser.fileviewlets import (
    FileDisplay, FileUpload, Image)

from waeup.kofa.browser.layout import (
    default_filedisplay_template,
    default_fileupload_template)

from waeup.kofa.students.browser import (
    StudentBaseDisplayFormPage, StudentBaseManageFormPage,
    StudentClearanceDisplayFormPage, StudentClearanceManageFormPage,
    ExportPDFClearanceSlipPage, StudentFilesUploadPage)

grok.context(IKofaObject) # Make IKofaObject the default context
grok.templatedir('browser_templates')

# File viewlet baseclasses for student base page

class StudentFileDisplay(FileDisplay):
    """Base file display viewlet.
    """
    grok.baseclass()
    grok.context(IStudent)
    grok.view(StudentClearanceDisplayFormPage)
    grok.order(1)
    grok.require('waeup.viewStudent')


class StudentFileUpload(FileUpload):
    """Base upload viewlet.
    """
    grok.baseclass()
    grok.context(IStudent)
    grok.view(StudentClearanceManageFormPage)
    grok.require('waeup.uploadStudentFile')

    @property
    def show_viewlet(self):
        students_utils = getUtility(IStudentsUtils)
        if self.__name__ in students_utils.SKIP_UPLOAD_VIEWLETS:
            return False
        return True


class StudentImage(Image):
    """Renders images for students.
    """
    grok.baseclass()
    grok.context(IStudent)
    grok.require('waeup.viewStudent')


# File viewlets for student base page

class PassportDisplay(StudentFileDisplay):
    """Passport display viewlet.
    """
    grok.order(1)
    grok.context(IStudent)
    grok.view(StudentBaseDisplayFormPage)
    grok.require('waeup.viewStudent')
    grok.template('imagedisplay')
    label = _(u'Passport Picture')
    download_name = u'passport.jpg'


class PassportUploadManage(StudentFileUpload):
    """Passport upload viewlet for officers.
    """
    grok.order(1)
    grok.context(IStudent)
    grok.view(StudentBaseManageFormPage)
    grok.require('waeup.manageStudent')
    grok.template('imageupload')
    label = _(u'Passport Picture (jpg only)')
    mus = 1024 * 50
    download_name = u'passport.jpg'
    tab_redirect = '#tab2'


class PassportUploadEdit(PassportUploadManage):
    """Passport upload viewlet for students.
    """
    grok.view(StudentFilesUploadPage)
    grok.require('waeup.uploadStudentFile')


class BirthCertificateDisplay(StudentFileDisplay):
    """Birth Certificate display viewlet.
    """
    grok.order(1)
    label = _(u'Birth Certificate')
    title = _(u'Birth Certificate Scan')
    download_name = u'birth_certificate'


class BirthCertificateSlip(BirthCertificateDisplay):
    grok.view(ExportPDFClearanceSlipPage)


class BirthCertificateUpload(StudentFileUpload):
    """Birth Certificate upload viewlet.
    """
    grok.order(1)
    label = _(u'Birth Certificate')
    title = _(u'Birth Certificate Scan')
    mus = 1024 * 150
    download_name = u'birth_certificate'
    tab_redirect = '#tab2-top'


class Passport(StudentImage):
    """Renders jpeg passport picture.
    """
    grok.name('passport.jpg')
    download_name = u'passport.jpg'
    grok.context(IStudent)


class ApplicationSlipImage(StudentImage):
    """Renders application slip scan.
    """
    grok.name('application_slip')
    download_name = u'application_slip'


class BirthCertificateImage(StudentImage):
    """Renders birth certificate scan.
    """
    grok.name('birth_certificate')
    download_name = u'birth_certificate'
