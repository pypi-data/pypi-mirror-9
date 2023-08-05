## $Id: level_report.py 11254 2014-02-22 15:46:03Z uli $
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
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.reports import IReport
from waeup.kofa.browser.pdf import get_signature_tables
from waeup.kofa.students.reports.student_statistics import (
    StudentStatisticsReportPDFView)

class ILevelReport(IReport):

    session = Attribute('Session to report')
    level = Attribute('Level to report')
    faccode = Attribute('Faculty to report')
    depcode = Attribute('Department to report')
    creation_dt_string = Attribute('Human readable report creation datetime')

def get_students(faccode, depcode, session, level):
    """Get students in a certain department who registered courses
    in a certain session at a certain level.

    Returns a list of student data tuples.
    """
    site = grok.getSite()
    cat = queryUtility(ICatalog, name="students_catalog")
    result = cat.searchResults(
        depcode = (depcode, depcode), faccode = (faccode, faccode)
        )
    table = []
    for stud in result:
        if not stud['studycourse'].has_key(str(level)):
            continue
        level_obj = stud['studycourse'][str(level)]
        if level_obj.level_session != session:
            continue
        passed_params = level_obj.passed_params
        line = (
                #stud.student_id,
                stud.matric_number,
                stud.display_fullname,
                level_obj.total_credits,
                passed_params[2],
                level_obj.gpa,
                passed_params[4],
                level_obj.cumulative_params[3],
                level_obj.cumulative_params[4],
                level_obj.cumulative_params[0],
                )
        table.append(line)
    return sorted(table, key=lambda value:value[0])

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

class TTR(Flowable): #TableTextRotate
    '''Rotates a text in a table cell.'''

    def __init__(self, text):
        Flowable.__init__(self)
        self.text=text

    def draw(self):
        canvas = self.canv
        canvas.rotate(45)
        canvas.drawString( 0, -1, self.text)

    #def wrap(self,aW,aH):
    #    canv = self.canv
    #    return canv._leading, canv.stringWidth(self.text)

def tbl_data_to_table(data):
    result = []
    col_names = (
            #'Student Id',
            'S/N',
            'Matric No.',
            'Name',
            TTR('Total Credits'),
            TTR('Total Credits Passed'),
            TTR('GPA'),
            'Courses Failed',
            TTR('Cum. Credits Taken'),
            TTR('Cum. Credits Passed'),
            TTR('CGPA'))
    table = [col_names]
    sn = 1
    for line in data:
        line = (sn,) + line
        table.append(line)
        sn += 1
    return table

TABLE_STYLE = [
    ('FONT', (0,0), (-1,-1), 'Helvetica', 8),
    #('FONT', (0,0), (0,-1), 'Helvetica-Bold', 8), # 1st column
    ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 8), # 1st row
    #('FONT', (0,-1), (-1,-1), 'Helvetica-Bold', 8), # last row
    #('FONT', (-1,0), (-1,-1), 'Helvetica-Bold', 8), # last column
    ('ALIGN', (3,1), (-1,-1), 'RIGHT'),
    ('ALIGN', (0,0), (0,-1), 'RIGHT'),
    ('ALIGN', (6,0), (6,-1), 'LEFT'),
    ('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
    ('BOX', (0,1), (-1,-1), 1, colors.black),
    ]

@implementer(ILevelReport)
class LevelReport(Report):
    data = None
    session = None
    level = None
    faccode = None
    depcode = None

    def __init__(self, faccode, depcode, session, level, author='System'):
        super(LevelReport, self).__init__(
            args=[faccode, depcode, session, level], kwargs={'author':author})
        site = grok.getSite()
        self.session = academic_sessions_vocab.getTerm(session).title
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
        creator = getUtility(IPDFCreator, name='landscape')
        table_data = tbl_data_to_table(self.data)
        #col_widths = [3.5*cm] * len(self.data[0])
        col_widths = [1*cm, 4*cm, 5*cm, 0.8*cm, 0.8*cm, 0.8*cm,
                      6*cm, 0.8*cm, 0.8*cm, 0.8*cm]
        pdf_data = [Paragraph('<b>%s</b>' % self.creation_dt_string,
                              STYLE["Normal"]),
                    Spacer(1, 12),]
        pdf_data += [Paragraph('%s<br />%s<br />Level: %s<br />Session: %s' % (
                    self.factitle, self.deptitle, self.level, self.session),
                    STYLE["Normal"]),
                    Spacer(1, 12),]
        pdf_data += [
            Table(table_data, style=TABLE_STYLE, colWidths=col_widths)]
        doc_title = 'Level Report'

        pdf_data.append(Spacer(1, 40))
        signatures = ['Ag. Head of Department', 'Dean of Faculty']
        signaturetables = get_signature_tables(signatures, landscape=True)
        pdf_data.append(signaturetables[0])

        pdf = creator.create_pdf(
            pdf_data, None, doc_title, self.author,
            'Level Report %s/%s/%s/%s' % (
            self.faccode, self.depcode, self.levelcode, self.sessioncode)
            )
        return pdf

@implementer(IReportGenerator)
class LevelReportGenerator(grok.GlobalUtility):

    title = _('Level Report')
    grok.name('level_report')

    def generate(self, site, faccode=None, depcode=None,
                 session=None, level=None, author=None):
        result = LevelReport(faccode=faccode, depcode=depcode,
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
class LevelReportGeneratorPage(KofaPage):

    grok.context(LevelReportGenerator)
    grok.name('index.html')
    grok.require('waeup.manageReports')

    label = _('Create level report')

    @property
    def generator_name(self):
        for name, gen in get_generators():
            if gen == self.context:
                return name
        return None

    def update(self, CREATE=None, faccode_depcode=None,
               session=None, level=None):
        self.parent_url = self.url(self.context.__parent__)
        self._set_session_values()
        self._set_level_values()
        self._set_faccode_depcode_values()
        if CREATE and session:
            # create a new report job for students by session
            faccode = faccode_depcode.split('_')[0]
            depcode = faccode_depcode.split('_')[1]
            container = self.context.__parent__
            user_id = self.request.principal.id
            if level is not None:
                level = int(level)
            if session is not None:
                session = int(session)
            kw = dict(
                session=session,
                level=level,
                faccode=faccode,
                depcode=depcode)
            self.flash(_('New report is being created in background'))
            job_id = container.start_report_job(
                self.generator_name, user_id, kw=kw)
            ob_class = self.__implemented__.__name__.replace('waeup.kofa.','')
            grok.getSite().logger.info(
                '%s - report %s created: %s (faculty=%s, department=%s, session=%s, level=%s)' % (
                ob_class, job_id, self.context.title, faccode, depcode, session, level))
            self.redirect(self.parent_url)
            return
        return

    def _set_session_values(self):
        vocab_terms = academic_sessions_vocab.by_value.values()
        self.sessions = [(x.title, x.token) for x in vocab_terms]
        return

    def _set_level_values(self):
        vocab_terms = course_levels.by_value.values()
        self.levels = sorted([(x.title, x.token) for x in vocab_terms])
        return

    def _set_faccode_depcode_values(self):
        faccode_depcodes = []
        faculties = grok.getSite()['faculties']
        for fac in faculties.values():
            for dep in fac.values():
                faccode_depcodes.append(
                    ('%s (%s)' %(dep.longtitle, fac.longtitle),
                     '%s_%s' %(fac.code, dep.code)))
        self.faccode_depcodes = sorted(
            faccode_depcodes, key=lambda value: value[0])
        return

class LevelReportPDFView(StudentStatisticsReportPDFView):

    grok.context(ILevelReport)
    grok.name('pdf')
    grok.require('waeup.Public')
    prefix = 'LevelReport'

    def _filename(self):
        return 'LevelReport_%s_%s_%s_%s_%s.pdf' % (
            self.context.faccode, self.context.depcode,
            self.context.sessioncode, self.context.levelcode,
            self.context.creation_dt_string)

class LevelReportBreadcrumb(Breadcrumb):
    """A breadcrumb for reports.
    """
    grok.context(LevelReportGenerator)
    title = _(u'Level Report')
    target = None