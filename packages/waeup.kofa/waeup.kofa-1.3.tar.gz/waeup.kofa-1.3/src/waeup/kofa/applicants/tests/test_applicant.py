## $Id: test_applicant.py 10092 2013-04-22 15:15:19Z henrik $
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
"""Tests for applicants and related.
"""
import grok
import shutil
import tempfile
from StringIO import StringIO
from zope.component import adapts, queryUtility
from zope.component.interfaces import IFactory
from zope.interface import verify, implements
from zope.location.interfaces import ILocation
from waeup.kofa.image.interfaces import IKofaImageFile
from waeup.kofa.imagestorage import DefaultStorage
from waeup.kofa.interfaces import IFileStoreHandler, IFileStoreNameChooser
from waeup.kofa.applicants import (
    Applicant, ApplicantFactory,
    ApplicantImageStoreHandler, ApplicantImageNameChooser,
    )
from waeup.kofa.applicants.interfaces import IApplicant
from waeup.kofa.testing import FunctionalTestCase, FunctionalLayer

class FakeImageLocation(object):
    implements(ILocation)
    adapts(IKofaImageFile)
    def __init__(self, context):
        pass

class HelperTests(FunctionalTestCase):

    layer = FunctionalLayer

    def setUp(self):
        super(HelperTests, self).setUp()
        self.workdir = tempfile.mkdtemp()
        return

    def tearDown(self):
        super(HelperTests, self).tearDown()
        shutil.rmtree(self.workdir)
        return

    def test_image_store_handler_util_accessible(self):
        # we can get an IFileStoreHandler utility for applicants
        handler = queryUtility(IFileStoreHandler, name='img-applicant')
        self.assertTrue(
            isinstance(handler, ApplicantImageStoreHandler))
        return

    def test_image_store_handler(self):
        store = DefaultStorage()
        handler = queryUtility(IFileStoreHandler, name='img-applicant')
        result1 = handler.pathFromFileID(
            store, '/fake-root', '__img-applicant__sample.jpg')
        result2 = handler.pathFromFileID(
            store, '/fake-root', '__img-applicant__dir1/sample.jpg')
        result3 = handler.pathFromFileID(
            store, '/fake-root', '__img-applicant__dir1/dir2/sample.jpg')
        self.assertEqual(
            result1, '/fake-root/applicants/sample')
        self.assertEqual(
            result2, '/fake-root/applicants/dir1/sample')
        self.assertEqual(
            result3, '/fake-root/applicants/dir1/dir2/sample')
        return

    def test_image_store_handler_create(self):
        # we can create files in image store with the applicant image
        # store handler
        store = DefaultStorage(self.workdir)
        handler = queryUtility(IFileStoreHandler, name='img-applicant')
        file_obj, path, waeup_file = handler.createFile(
            store, store.root, 'sample.jpg', '__img_applicant__sample',
            StringIO('I am a JPG file'))
        self.assertEqual(path[-21:], 'applicants/sample.jpg')
        return

    #def test_image_store_handler_invalid_filename_ext(self):
    #    # we only accept '.jpg' and '.png' as filename extensions.
    #    store = DefaultStorage(self.workdir)
    #    handler = queryUtility(IFileStoreHandler, name='img-applicant')
    #    self.assertRaises(
    #        ValueError,
    #        handler.createFile,
    #        store, store.root, 'sample.txt', '__img_applicant__sample',
    #        StringIO('I am a txt file'))
    #    return

class ApplicantImageNameChooserTests(FunctionalTestCase):

    layer = FunctionalLayer

    def test_iface(self):
        # make sure we implement promised interfaces
        obj = ApplicantImageNameChooser(None) # needs a context normally
        verify.verifyClass(IFileStoreNameChooser, ApplicantImageNameChooser)
        verify.verifyObject(IFileStoreNameChooser, obj)
        return

    def test_name_chooser_available(self):
        # we can get a name chooser for applicant objects as adapter
        appl = Applicant()
        chooser = IFileStoreNameChooser(appl)
        self.assertTrue(chooser is not None)
        return

    def test_name_chooser_applicant_wo_container(self):
        # we can get an image filename for applicants not in a container
        appl = Applicant()
        appl.applicant_id = u'dummy_123456'
        chooser = IFileStoreNameChooser(appl)
        result = chooser.chooseName()
        # the file would be stored in a ``_default`` directory.
        self.assertEqual(
            result, '__img-applicant___default/dummy_123456.jpg')
        return

    def test_name_chooser_applicant_w_container(self):
        fake_container = grok.Container()
        fake_container.__name__ = 'folder'
        fake_container.code = 'folder'
        appl = Applicant()
        appl.applicant_id = u'folder_123456'
        appl.__parent__ = fake_container
        chooser = IFileStoreNameChooser(appl)
        result = chooser.chooseName()
        self.assertEqual(
            result, '__img-applicant__folder/%s.jpg' % appl.applicant_id)
        return

    def test_name_chooser_applicant_nonpassport_w_container(self):
        fake_container = grok.Container()
        fake_container.__name__ = 'folder'
        fake_container.code = 'folder'
        appl = Applicant()
        appl.applicant_id = u'folder_123456'
        appl.__parent__ = fake_container
        chooser = IFileStoreNameChooser(appl)
        result = chooser.chooseName(attr='anything.pdf')
        self.assertEqual(
            result, '__img-applicant__folder/anything_%s.pdf' % appl.applicant_id)
        return

    def test_name_chooser_check_name(self):
        # we can check file ids for applicants
        fake_container = grok.Container()
        fake_container.__name__ = 'folder'
        fake_container.code = 'folder'
        appl = Applicant()
        appl.applicant_id = u'folder_123456'
        appl.__parent__ = fake_container
        chooser = IFileStoreNameChooser(appl)
        result1 = chooser.checkName('foo')
        result2 = chooser.checkName(
            '__img-applicant__folder/%s.jpg' % appl.applicant_id)
        self.assertEqual(result1, False)
        self.assertEqual(result2, True)
        return

class ApplicantTest(FunctionalTestCase):

    layer = FunctionalLayer

    def setUp(self):
        super(ApplicantTest, self).setUp()
        self.applicant = Applicant()
        return

    def tearDown(self):
        super(ApplicantTest, self).tearDown()
        return

    def test_interfaces(self):
        verify.verifyClass(IApplicant, Applicant)
        verify.verifyObject(IApplicant, self.applicant)
        return

class ApplicantFactoryTest(FunctionalTestCase):

    layer = FunctionalLayer

    def setUp(self):
        super(ApplicantFactoryTest, self).setUp()
        self.factory = ApplicantFactory()
        return

    def tearDown(self):
        super(ApplicantFactoryTest, self).tearDown()
        return

    def test_interfaces(self):
        verify.verifyClass(IFactory, ApplicantFactory)
        verify.verifyObject(IFactory, self.factory)

    def test_factory(self):
        obj = self.factory()
        assert isinstance(obj, Applicant)

    def test_getInterfaces(self):
        implemented_by = self.factory.getInterfaces()
        assert implemented_by.isOrExtends(IApplicant)
