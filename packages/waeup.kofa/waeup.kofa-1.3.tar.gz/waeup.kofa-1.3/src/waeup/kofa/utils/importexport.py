## $Id: importexport.py 10028 2013-03-15 01:12:42Z uli $
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
import unicodecsv as csv # XXX: csv ops should move to dedicated module
import grok
import cPickle
import zope.xmlpickle
from cStringIO import StringIO
from zope.interface import Interface
from waeup.kofa.interfaces import (IKofaObject, IKofaExporter,
                                   IKofaXMLExporter, IKofaXMLImporter)

def readFile(f):
    """read a CSV file"""
    headers = []
    rows = []
    f = csv.reader(f)
    headers = f.next()
    for line in f:
        rows.append(line)
    return (headers, rows)

def writeFile(data):
    writer = csv.writer(open("export.csv", "wb"))
    writer.writerows(data)

class Exporter(grok.Adapter):
    """Export a Kofa object as pickle.

    This all-purpose exporter exports attributes defined in schemata
    and contained objects (if the exported thing is a container).
    """
    grok.context(IKofaObject)
    grok.provides(IKofaExporter)

    def __init__(self, context):
        self.context = context

    def export(self, filepath=None):
        if filepath is None:
            filelike_obj = StringIO()
        else:
            filelike_obj = open(filepath, 'wb')
        exported_obj = cPickle.dump(self.context, filelike_obj)
        filelike_obj.close()
        return filelike_obj

class XMLExporter(grok.Adapter):
    """Export a Kofa object as XML.

    This all-purpose exporter exports XML representations of pickable
    objects.
    """
    grok.context(Interface)
    grok.provides(IKofaXMLExporter)

    def __init__(self, context):
        self.context = context

    def export(self, filepath=None):
        pickled_obj = cPickle.dumps(self.context)
        result = zope.xmlpickle.toxml(pickled_obj)
        if filepath is None:
            filelike_obj = StringIO()
        else:
            filelike_obj = open(filepath, 'wb')
        filelike_obj.write(result)
        filelike_obj.seek(0)
        return filelike_obj

class XMLImporter(grok.Adapter):
    """Import a Kofa object from XML.
    """
    grok.context(Interface)
    grok.provides(IKofaXMLImporter)

    def __init__(self, context):
        self.context = context

    def doImport(self, filepath):
        xml = None
        if isinstance(filepath, basestring):
            xml = open(filepath, 'rb').read()
        else:
            xml = filepath.read()
        obj = zope.xmlpickle.loads(xml)
        return obj
