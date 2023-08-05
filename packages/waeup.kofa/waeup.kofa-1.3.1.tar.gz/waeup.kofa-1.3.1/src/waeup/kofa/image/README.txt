waeup.kofa.image -- handling image files
========================================

The image file widget is built on top of the :class:`KofaImageFile` object::

  >>> from waeup.kofa.image import KofaImageFile
  >>> file = KofaImageFile('foo.jpg', 'mydata')
  >>> file.filename
  'foo.jpg'
  >>> file.data
  'mydata'
  >>> file.size
  6
  >>> f = file.file
  >>> f.read()
  'mydata'

We can also create KofaImageFile objects from file-like objects::

  >>> from StringIO import StringIO
  >>> from zope import component
  >>> from hurry.file.interfaces import IFileRetrieval
  >>> fileretrieval = component.getUtility(IFileRetrieval)
  >>> file = fileretrieval.createFile('bar.jpg', StringIO('test data'))
  >>> file.filename
  'bar.jpg'
  >>> file.size
  9
  >>> file.data
  'test data'
  >>> f = file.file
  >>> f.read()
  'test data'

Tramline Support
----------------

The KofaImageFile object normally stores the file data using ZODB
persistence. Files can however also be stored by tramline.  If
tramline is installed in Apache, the Tramline takes care of generating
ids for files and storing the file on the filesystem directly. The ids
are then passed as file data to be stored in the ZODB.

Let's first enable tramline.

The tramline directory structure is a directory with two subdirectories,
one called 'repository' and the other called 'upload'::

  >>> import tempfile, os
  >>> dirpath = tempfile.mkdtemp()
  >>> repositorypath = os.path.join(dirpath, 'repository')
  >>> uploadpath = os.path.join(dirpath, 'upload')
  >>> os.mkdir(repositorypath)
  >>> os.mkdir(uploadpath)

We create a TramlineFileRetrieval object knowing about this directory,
and register it as a utility::

  >>> from hurry.file.file import TramlineFileRetrievalBase
  >>> class TramlineFileRetrieval(TramlineFileRetrievalBase):
  ...    def getTramlinePath(self):
  ...        return dirpath
  >>> retrieval = TramlineFileRetrieval()
  >>> component.provideUtility(retrieval, IFileRetrieval)

Now let's store a file the way tramline would during upload::

  >>> f = open(os.path.join(repositorypath, '1'), 'wb')
  >>> f.write('test data')
  >>> f.close()

The file with underlying name '1' (the data stored in the ZODB will be
just '1') will now be created::

  >>> file = KofaImageFile('foo.jpg', '1')

The data is now '1', referring to the real file::

  >>> file.data
  '1'

Retrieving the file results in the real file::

  >>> f = file.file
  >>> f.read()
  'test data'

We can also retrieve its size::

  >>> int(file.size)
  9

Now let's disable tramline in our utility::

  >>> class TramlineFileRetrieval(TramlineFileRetrievalBase):
  ...     def getTramlinePath(self):
  ...        return dirpath
  ...     def isTramlineEnabled(self):
  ...        return False
  >>> component.provideUtility(TramlineFileRetrieval(), IFileRetrieval)

We expect the same behavior as when tramline is not installed::

  >>> file = KofaImageFile('foo.jpg', 'data')
  >>> f = file.file
  >>> f.read()
  'data'
  >>> file.size
  4

Clean up:

  >>> import shutil
  >>> shutil.rmtree(dirpath)

Support for :mod:`waeup.kofa.imagestorage`
------------------------------------------

The behaviour shown above can be used for any Zope3 application. With
:mod:`waeup.kofa` we use a special file retrieval utility defined in
:mod:`waeup.kofa.imagestorage`. As this utility is based on
:mod:`waeup.kofa` internal stuff we do not show it here but in the
tests that come with that storage type.

Put roughly, an imagestorage stores file data in containers of blobs
belonging to a certain site. See the module itself for details.

`ImageFile` Field
-----------------

As every other field (most of them are defined in :mod:`zope.schema`)
`ImageFile` can be used in interfaces to tell, that the associated
attribute should be -- an image file.

The `ImageFile` field accepts only certain content types:

  >>> from waeup.kofa.image.schema import ImageFile
  >>> from zope.publisher.browser import TestRequest
  >>> field = ImageFile(__name__='foo', title=u'Foo')
  >>> field.validate('asd')
  Traceback (most recent call last):
  ...
  WrongType: ('asd', <class 'waeup.kofa.image.image.KofaImageFile'>, 'foo')

which means: `ImageFile` fields should better contain
:class:`KofaImageFile` instances.

We can store normal :class:`KofaImageFile` instances:

  >>> field.validate(KofaImageFile('bar.jpg', 'data')) is None
  True

The `ImageFile` field supports min and max values:

  >>> field = ImageFile(__name__='foo', title=u'Foo')
  >>> hasattr(field, 'min_size')
  True

  >>> hasattr(field, 'max_size')
  True

By default both attributes are set to ``None``:

  >>> field.min_size is field.max_size is None
  True

But we can set them:

  >>> field = ImageFile(__name__='bar', title=u'Bar',
  ...                   min_size=5, max_size=12)

and while these values are okay then:

  >>> field.validate(
  ...     KofaImageFile('bar.jpg', '123456789012')) is None
  True

  >>> field.validate(
  ...     KofaImageFile('bar.jpg', '12345')) is None
  True

the following are not:

  >>> field.validate(
  ...     KofaImageFile('bar.jpg', '1234567890123'))
  Traceback (most recent call last):
  ...
  TooBig: ('bar.jpg', '13 bytes (max: 12 bytes)')

  >>> field.validate(
  ...     KofaImageFile('bar.jpg', '1234'))
  Traceback (most recent call last):
  ...
  TooSmall: ('bar.jpg', '4 bytes (min: 5 bytes)')


Broken Unequality Comparison
----------------------------

KofaImageFile does not reproduce the broken unequal comparison from
its base:

  >>> f1 = KofaImageFile('bar.jpg', '123456789')
  >>> f2 = KofaImageFile('bar.jpg', '123456789')
  >>> f3 = KofaImageFile('baz.jpg', '1234')
  >>> f1 == f2
  True

  >>> f1 != f2
  False

  >>> f1 == f3
  False

  >>> f1 != f3
  True
