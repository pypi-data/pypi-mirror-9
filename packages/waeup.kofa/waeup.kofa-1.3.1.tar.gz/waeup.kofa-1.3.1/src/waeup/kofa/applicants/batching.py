## $Id: batching.py 11891 2014-10-28 20:02:45Z henrik $
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
"""Batch processing for applicants.
"""
import unicodecsv as csv # XXX: csv ops should move to dedicated module.
import grok
from zope.schema import getFields
from zope.interface import Interface
from zope.component import queryUtility
from hurry.workflow.interfaces import IWorkflowState
from zope.catalog.interfaces import ICatalog
from waeup.kofa.interfaces import (
    IBatchProcessor, IObjectConverter, FatalCSVError, IGNORE_MARKER,
    IObjectHistory, IUserAccount)
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.utils.batching import BatchProcessor
from waeup.kofa.applicants.interfaces import (
    IApplicantsContainer, IApplicant, IApplicantUpdateByRegNo)
from waeup.kofa.applicants.workflow import  IMPORTABLE_STATES, CREATED

class ApplicantsContainerProcessor(BatchProcessor):
    """A processor for applicants containers.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'applicantscontainerprocessor'
    grok.name(util_name)

    name = _('ApplicantsContainer Processor')
    mode = u'create'
    iface = IApplicantsContainer

    location_fields = ['code',]
    factory_name = 'waeup.ApplicantsContainer'

    def parentsExist(self, row, site):
        return 'applicants' in site.keys()

    def entryExists(self, row, site):
        return row['code'] in site['applicants'].keys()

    def getParent(self, row, site):
        return site['applicants']

    def getEntry(self, row, site):
        if not self.entryExists(row, site):
            return None
        parent = self.getParent(row, site)
        return parent.get(row['code'])

    def addEntry(self, obj, row, site):
        parent = self.getParent(row, site)
        parent[row['code']] = obj
        return

    def delEntry(self, row, site):
        parent = self.getParent(row, site)
        del parent[row['code']]
        return

class ApplicantProcessor(BatchProcessor):
    """A batch processor for IApplicant objects.

    In create mode container_code is required. If application_number is given
    an applicant with this number is created in the designated container.
    If application_number is not given a random application_number is assigned.
    applicant_id is being determined by the system and can't be imported.

    In update or remove mode container_code and application_number columns
    must not exist. The applicant object is solely searched by its applicant_id
    or reg_number.
    """
    grok.implements(IBatchProcessor)
    grok.provides(IBatchProcessor)
    grok.context(Interface)
    util_name = 'applicantprocessor'
    grok.name(util_name)
    name = _('Applicant Processor')
    iface = IApplicant
    iface_byregnumber = IApplicantUpdateByRegNo
    location_fields = ['']
    factory_name = 'waeup.Applicant'

    mode = None

    @property
    def available_fields(self):
        return sorted(list(set(
            ['application_number',
            'container_code','state','password'] + getFields(
                self.iface).keys())))

    def checkHeaders(self, headerfields, mode='create'):
        cond1 = 'container_code' in headerfields
        cond2 = 'application_number' in headerfields
        cond3 = 'applicant_id' in headerfields
        cond4 = 'reg_number' in headerfields
        if mode == 'create':
            if not cond1:
                raise FatalCSVError(
                    "Need at least container_code column!")
            if cond3:
                raise FatalCSVError(
                    "applicant_id can't be imported in create mode!")
            for field in self.required_fields:
                if not field in headerfields:
                    raise FatalCSVError(
                        "Need at least columns %s for import!" %
                        ', '.join(["'%s'" % x for x in self.required_fields]))
        if mode in ('update', 'remove'):
            if not cond3 and not cond4:
                raise FatalCSVError(
                    "Need at least column reg_number or applicant_id!")
            if cond1 or cond2:
                raise FatalCSVError(
                    "container_code or application_number can't be imported " +
                    "in update or remove mode!")
        # Check for fields to be ignored...
        not_ignored_fields = [x for x in headerfields
                              if not x.startswith('--')]
        if len(set(not_ignored_fields)) < len(not_ignored_fields):
            raise FatalCSVError(
                "Double headers: each column name may only appear once.")
        return True

    def getLocator(self, row):
        if row.get('container_code', None) not in (IGNORE_MARKER, None):
            # create mode
            return 'container_code'
        elif row.get('applicant_id', None) not in (IGNORE_MARKER, None):
            # update or remove mode
            return 'applicant_id'
        elif row.get('reg_number', None) not in (IGNORE_MARKER, None):
            # update or remove mode
            return 'reg_number'
        else:
            return None

    def getParent(self, row, site):
        result = None
        if self.getLocator(row) == 'container_code':
            result = site['applicants'].get(row['container_code'], None)
        elif self.getLocator(row) == 'reg_number':
            reg_number = row['reg_number']
            cat = queryUtility(ICatalog, name='applicants_catalog')
            results = list(
                cat.searchResults(reg_number=(reg_number, reg_number)))
            if results:
                result = results[0].__parent__
        elif self.getLocator(row) == 'applicant_id':
            applicant_id = row['applicant_id']
            cat = queryUtility(ICatalog, name='applicants_catalog')
            results = list(
                cat.searchResults(applicant_id=(applicant_id, applicant_id)))
            if results:
                result = results[0].__parent__
        return result

    def parentsExist(self, row, site):
        return self.getParent(row, site) is not None

    def getEntry(self, row, site):
        if self.getLocator(row) == 'container_code':
            if row.get('application_number', None) not in (IGNORE_MARKER, None):
                if not self.parentsExist(row, site):
                    return None
                parent = self.getParent(row, site)
                return parent.get(row['application_number'])
            return None
        if self.getLocator(row) == 'applicant_id':
            applicant_id = row['applicant_id']
            cat = queryUtility(ICatalog, name='applicants_catalog')
            results = list(
                cat.searchResults(applicant_id=(applicant_id, applicant_id)))
            if results:
                return results[0]
        if self.getLocator(row) == 'reg_number':
            reg_number = row['reg_number']
            cat = queryUtility(ICatalog, name='applicants_catalog')
            results = list(
                cat.searchResults(reg_number=(reg_number, reg_number)))
            if results:
                return results[0]
        return None

    def entryExists(self, row, site):
        return self.getEntry(row, site) is not None

    def addEntry(self, obj, row, site):
        parent = self.getParent(row, site)
        parent.addApplicant(obj)
        #parent.__parent__.logger.info(
        #    'Applicant imported: %s' % obj.applicant_id)
        history = IObjectHistory(obj)
        history.addMessage(_('Application record imported'))
        return

    def delEntry(self, row, site):
        applicant = self.getEntry(row, site)
        if applicant is not None:
            parent = applicant.__parent__
            del parent[applicant.application_number]
            #parent.__parent__.logger.info(
            #    'Applicant removed: %s' % applicant.applicant_id)
        pass

    def updateEntry(self, obj, row, site, filename):
        """Update obj to the values given in row.
        """
        items_changed = ''
        # Remove application_number from row if empty
        if 'application_number' in row and row['application_number'] in (
            None, IGNORE_MARKER):
            row.pop('application_number')

        # Update applicant_id fom application_number and container code
        # if application_number is given
        if 'application_number' in row:
            obj.applicant_id = u'%s_%s' % (
                row['container_code'], row['application_number'])
            items_changed += ('%s=%s, ' % ('applicant_id', obj.applicant_id))
            row.pop('application_number')

        # Update password
        if 'password' in row:
            passwd = row.get('password', IGNORE_MARKER)
            if passwd not in ('', IGNORE_MARKER):
                if passwd.startswith('{SSHA}'):
                    # already encrypted password
                    obj.password = passwd
                else:
                    # not yet encrypted password
                    IUserAccount(obj).setPassword(passwd)
                items_changed += ('%s=%s, ' % ('password', passwd))
            row.pop('password')

        # Update registration state
        if 'state' in row:
            state = row.get('state', IGNORE_MARKER)
            if state not in (IGNORE_MARKER, ''):
                IWorkflowState(obj).setState(state)
                msg = _("State '${a}' set", mapping = {'a':state})
                history = IObjectHistory(obj)
                history.addMessage(msg)
                items_changed += ('%s=%s, ' % ('state', state))
            row.pop('state')

        # apply other values...
        items_changed += super(ApplicantProcessor, self).updateEntry(
            obj, row, site, filename)

        # Log actions...
        parent = self.getParent(row, site)
        if self.getLocator(row) == 'container_code':
            parent.__parent__.logger.info(
                '%s - %s - imported: %s' % (self.name, filename, items_changed))
        else:
            parent.__parent__.logger.info(
                '%s - %s - updated: %s' % (self.name, filename, items_changed))
        return items_changed

    def getMapping(self, path, headerfields, mode):
        """Get a mapping from CSV file headerfields to actually used fieldnames.
        """
        result = dict()
        reader = csv.reader(open(path, 'rb'))
        raw_header = reader.next()
        for num, field in enumerate(headerfields):
            if field not in ['applicant_id', 'reg_number'] and mode == 'remove':
                continue
            if field == u'--IGNORE--':
                # Skip ignored columns in failed and finished data files.
                continue
            result[raw_header[num]] = field
        return result

    def checkConversion(self, row, mode='create'):
        """Validates all values in row.
        """
        iface = self.iface
        if self.getLocator(row) == 'reg_number' or mode == 'remove':
            iface = self.iface_byregnumber
        converter = IObjectConverter(iface)
        errs, inv_errs, conv_dict =  converter.fromStringDict(
            row, self.factory_name, mode=mode)
        cert = conv_dict.get('course1', None)
        if cert is not None and (mode in ('create', 'update')):
            # course1 application category must match container's.
            parent = self.getParent(row, self.site)
            if parent is None:
                errs.append(('container', 'not found'))
            elif cert.application_category != parent.application_category:
                errs.append(('course1', 'wrong application category'))
        if 'state' in row and \
            not row['state'] in IMPORTABLE_STATES:
            if row['state'] not in (IGNORE_MARKER, ''):
                errs.append(('state','not allowed'))
            else:
                # state is an attribute of Applicant and must not
                # be changed if empty
                conv_dict['state'] = IGNORE_MARKER
        application_number = row.get('application_number', None)
        if application_number in (IGNORE_MARKER, ''):
                conv_dict['application_number'] = IGNORE_MARKER
        return errs, inv_errs, conv_dict

    def checkUpdateRequirements(self, obj, row, site):
        """Checks requirements the object must fulfill when being updated.

        This method is not used in case of deleting or adding objects.

        Returns error messages as strings in case of requirement
        problems.
        """
        if obj.state == CREATED:
            return 'Applicant is blocked.'
        return None

    def doImport(self, *args, **kw):
        # XXX: Not thread-safe.  Parallel applicant imports into
        # different sites could mean a mess.  Luckily this is not a
        # typical use-case. On the other hand it spares thousands of
        # site lookups during large imports.
        # XXX: Maybe this should go into Importer base.
        self.site = grok.getSite() # needed by checkConversion()
        return super(ApplicantProcessor, self).doImport(*args, **kw)
