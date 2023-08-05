## $Id: session_results_presentation.py 11254 2014-02-22 15:46:03Z uli $
##
## Copyright (C) 2013 Uli Fouquet & Henrik Bettermann
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
from zope.catalog.interfaces import ICatalog
from zope.component import queryUtility, getUtility
from zope.interface import implementer, Interface, Attribute
from waeup.kofa.interfaces import (
    IKofaUtils,
    academic_sessions_vocab, registration_states_vocab)
from waeup.kofa.students.interfaces import IStudentsUtils
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.browser.pdf import get_signature_tables
from waeup.kofa.reports import IReport
from waeup.kofa.students.reports.level_report import (
    ILevelReport, LevelReportGeneratorPage)
from waeup.kofa.students.reports.student_statistics import (
    StudentStatisticsReportPDFView)


class ISessionResultsPresentation(ILevelReport):

    """ Same interface as for level reports.
    """

def get_students(faccode, depcode, session, level=None):
    """Get students in a certain department who registered courses
    in a certain session at a certain level.

    Returns a list of lists of student data tuples.
    """
    site = grok.getSite()
    cat = queryUtility(ICatalog, name="students_catalog")
    result = cat.searchResults(
        depcode = (depcode, depcode), faccode = (faccode, faccode)
        )
    students_utils = getUtility(IStudentsUtils)
    table = []
    for i in range(len(students_utils.gpa_boundaries)+1):
        # The last list is reserved for students with more than one
        # level in the same session.
        table.append([])
    for stud in result:
        line = (stud.student_id,
                stud.matric_number,
                stud.display_fullname,
                )
        if level is not None:
            if not stud['studycourse'].has_key(str(level)):
                continue
            level_obj = stud['studycourse'][str(level)]
            if level_obj.level_session != session:
                continue
        else:
            itemcount = 0
            for item in stud['studycourse'].values():
                if item.level_session == session:
                    level_obj = item
                    itemcount += 1
            if itemcount == 0:
                # No level registered in this session
                continue
            if itemcount > 1:
                # Error: more than one session registered in this session
                table[len(students_utils.gpa_boundaries)].append(line)
                continue
        if level_obj.gpa_params[1] == 0:
            # Error: no credits weighted
            table[len(students_utils.gpa_boundaries)].append(line)
            continue
        # Session GPA can be determined
        table[students_utils.getClassFromCGPA(level_obj.gpa)[0]].append(line)
    return table

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Table, Spacer
from reportlab.platypus.flowables import Flowable
from waeup.kofa.reports import IReport, IReportGenerator
from waeup.kofa.reports import Report
from waeup.kofa.browser.interfaces import IPDFCreator
from waeup.kofa.university.vocabularies import course_levels

STYLE = getSampleStyleSheet()

TABLE_STYLE = [
    ('FONT', (0,0), (-1,-1), 'Helvetica', 8),
    ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 8), # 1st row
    ('ALIGN', (3,1), (-1,-1), 'RIGHT'),
    #('ALIGN', (1,0), (1,-1), 'LEFT'),
    #('ALIGN', (2,0), (2,-1), 'LEFT'),
    #('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
    #('BOX', (0,1), (-1,-1), 1, colors.black),
    ]

@implementer(ISessionResultsPresentation)
class SessionResultsPresentation(Report):
    data = None
    session = None
    level = None
    faccode = None
    depcode = None

    def __init__(self, faccode, depcode, session, level, author='System'):
        super(SessionResultsPresentation, self).__init__(
            args=[faccode, depcode, session, level], kwargs={'author':author})
        site = grok.getSite()
        self.session = academic_sessions_vocab.getTerm(session).title
        if level == None:
            self.level = 'All levels'
        else:
            self.level = course_levels.getTerm(level).title
        self.levelcode = level
        self.sessioncode = session
        self.faccode = faccode
        self.depcode = depcode
        self.factitle = site['faculties'][faccode].longtitle
        self.deptitle = site['faculties'][faccode][depcode].longtitle
        self.author = author
        self.creation_dt_string = self.creation_dt.astimezone(
            getUtility(IKofaUtils).tzinfo).strftime("%Y-%m-%d %H:%M:%S %Z")
        self.data = get_students(faccode, depcode, session, level)

    def create_pdf(self):
        creator = getUtility(IPDFCreator)
        #col_widths = [2*cm, 4*cm, 5*cm, 0.8*cm, 0.8*cm, 0.8*cm, 6*cm, ]
        pdf_data = [Paragraph('<b>%s</b>' % self.creation_dt_string,
                              STYLE["Normal"]),
                    Spacer(1, 12),]
        pdf_data += [Paragraph('%s<br />%s<br />Level: %s<br />Session: %s' % (
                    self.factitle, self.deptitle, self.level, self.session),
                    STYLE["Normal"]),
                    Spacer(1, 12),]
        students_utils = getUtility(IStudentsUtils)
        # Print classes in reverse order
        for gpa_class in range(len(students_utils.gpa_boundaries)-1,-1,-1):
            pdf_data.append(Spacer(1, 20))
            gpa_class_name = students_utils.gpa_boundaries[gpa_class][1]
            pdf_data += [Paragraph('<strong>%s</strong>' % gpa_class_name,
                         STYLE["Normal"])]
            table_data = [('Student Id', 'Matric No.', 'Name')] + self.data[gpa_class]
            pdf_data += [Table(table_data, style=TABLE_STYLE)]    #, colWidths=col_widths)]
            gpa_class += 1
        if self.data[-1]:
            pdf_data.append(Spacer(1, 20))
            pdf_data += [
                Paragraph('<strong>Erroneous Data</strong>', STYLE["Normal"])]
            table_data = [('Student Id', 'Matric No.', 'Name')] + self.data[-1]
            pdf_data += [Table(table_data, style=TABLE_STYLE)]

        doc_title = 'Presentation of Session Results'
        pdf_data.append(Spacer(1, 40))
        signatures = ['Ag. Head of Department',
                      'External Examiner', 'Dean of Faculty']
        signaturetables = get_signature_tables(signatures)
        pdf_data.append(signaturetables[0])

        pdf = creator.create_pdf(
            pdf_data, None, doc_title, self.author,
            'Session Results Presentation %s/%s/%s/%s' % (
            self.faccode, self.depcode, self.levelcode, self.sessioncode)
            )
        return pdf

@implementer(IReportGenerator)
class SessionResultsPresentationGenerator(grok.GlobalUtility):

    title = _('Session Results Presentation')
    grok.name('session_results_presentation')

    def generate(self, site, faccode=None, depcode=None,
                 session=None, level=None, author=None):
        result = SessionResultsPresentation(faccode=faccode, depcode=depcode,
                             session=session, level=level, author=author)
        return result

###############################################################
## Browser related stuff
##
## XXX: move to local browser module
###############################################################
from waeup.kofa.browser.layout import KofaPage
from waeup.kofa.interfaces import academic_sessions_vocab
from waeup.kofa.reports import get_generators
from waeup.kofa.browser.breadcrumbs import Breadcrumb
grok.templatedir('browser_templates')
class SessionResultsPresentationGeneratorPage(LevelReportGeneratorPage):

    grok.context(SessionResultsPresentationGenerator)
    grok.template('levelreportgeneratorpage')
    label = _('Create session results presentation')

    def update(self, CREATE=None, faccode_depcode=None,
               session=None, level=None):
        if level == 'all':
            level = None
        super(SessionResultsPresentationGeneratorPage, self).update(
            CREATE, faccode_depcode ,session, level)

    def _set_level_values(self):
        vocab_terms = course_levels.by_value.values()
        self.levels = [('All levels', 'all')] + sorted(
            [(x.title, x.token) for x in vocab_terms])
        return

class SessionResultsPresentationPDFView(StudentStatisticsReportPDFView):

    grok.context(ISessionResultsPresentation)
    grok.name('pdf')
    grok.require('waeup.Public')
    prefix = 'SessionResultsPresentation'

    def _filename(self):
        return 'SessionResultsPresentation_%s_%s_%s_%s_%s.pdf' % (
            self.context.faccode, self.context.depcode,
            self.context.sessioncode, self.context.levelcode,
            self.context.creation_dt_string)

class SessionResultsPresentationBreadcrumb(Breadcrumb):
    """A breadcrumb for reports.
    """
    grok.context(SessionResultsPresentationGenerator)
    title = _(u'Session Results Presentation')
    target = None