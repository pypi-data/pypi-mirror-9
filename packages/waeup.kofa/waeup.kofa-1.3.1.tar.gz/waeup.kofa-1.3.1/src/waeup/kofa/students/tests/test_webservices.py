# Tests for webservices
import xmlrpclib
import os
from cStringIO import StringIO
from zope.app.testing.xmlrpc import ServerProxy
from zope.component import getUtility
from waeup.kofa.interfaces import IExtFileStore, IFileStoreNameChooser
from waeup.kofa.testing import FunctionalLayer
from waeup.kofa.students.payments import StudentOnlinePayment
from waeup.kofa.students.tests.test_browser import StudentsFullSetup
from waeup.kofa.students.studylevel import StudentStudyLevel, CourseTicket


class XMLRPCTests(StudentsFullSetup):
    # check XMLRPC services for university portal

    layer = FunctionalLayer

    def setup_student(self, student):
        study_level = StudentStudyLevel()
        study_level.level_session = 2012
        study_level.level_verdict = "A"
        study_level.level = 100
        study_level.validated_by = u"my adviser"
        student['studycourse'].addStudentStudyLevel(
            self.certificate, study_level)

        ticket = CourseTicket()
        ticket.automatic = True
        ticket.carry_over = True
        ticket.code = u'CRS1'
        ticket.title = u'Course 1'
        ticket.fcode = u'FAC1'
        ticket.dcode = u'DEP1'
        ticket.credits = 100
        ticket.passmark = 100
        ticket.semester = 2
        study_level[ticket.code] = ticket

    def create_passport_img(self, student):
        # create some passport file for `student`
        storage = getUtility(IExtFileStore)
        image_path = os.path.join(os.path.dirname(__file__), 'test_image.jpg')
        self.image_contents = open(image_path, 'rb').read()
        file_id = IFileStoreNameChooser(student).chooseName(
            attr='passport.jpg')
        storage.createFile(file_id, StringIO(self.image_contents))

    def create_fpm_file(self, student, finger_num):
        # create some .fpm file for `student` finger `finger_num`
        storage = getUtility(IExtFileStore)
        file_id = IFileStoreNameChooser(student).chooseName(
            attr='%s.fpm' % finger_num)
        storage.createFile(file_id, StringIO('FP1FakedMintiaeFile1'))

    def XMLRPC_post(self, body):
        self.browser.addHeader('Authorization', 'Basic mgr:mgrpw')
        self.browser.addHeader('Content-Length', len(body))
        self.browser.post('http://localhost/app', body,
            'text/xml; charset=utf-8')
        return self.browser.contents

    def test_get_student_id_no_match(self):
        # w/o any students we get none
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        result = server.get_student_id('Nonsense')
        self.assertTrue(result is None)
        return

    def test_get_student_id_regno_exists(self):
        # we can get the id of an existing student with matching reg_no
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        result = server.get_student_id('123')
        self.assertEqual(result, 'K1000000')
        self.assertEqual(self.student_id, result)
        REQUEST_XML = """\
<?xml version="1.0"?>
<methodCall>
<methodName>get_student_id</methodName>
<params>
<param>
<value><string>123</string></value>
</param>
</params>
</methodCall>"""
        RESPONSE_XML = """\
<?xml version='1.0'?>
<methodResponse>
<params>
<param>
<value><string>K1000000</string></value>
</param>
</params>
</methodResponse>
"""
        xmlout = self.XMLRPC_post(REQUEST_XML)
        self.assertEqual(xmlout, RESPONSE_XML)
        return

    def test_get_student_id_block_unauthorized(self):
        # requests from unauthorized users are blocked
        # no username nor password
        server = ServerProxy('http://localhost/app')
        self.assertRaises(
            xmlrpclib.ProtocolError, server.get_student_id, '123')
        # wrong password
        server = ServerProxy('http://mgr:WRONGPW@localhost/app')
        self.assertRaises(
            xmlrpclib.ProtocolError, server.get_student_id, '123')
        # wrong username
        server = ServerProxy('http://WRONGUSER:mgrpw@localhost/app')
        self.assertRaises(
            xmlrpclib.ProtocolError, server.get_student_id, '123')
        return

    def test_get_courses_by_session(self):
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        result = server.get_courses_by_session('K1000000')
        self.assertEqual(result, None)
        self.setup_student(self.student)
        result = server.get_courses_by_session('K1000000', '2010')
        self.assertEqual(result, None)
        result = server.get_courses_by_session('K1000000', '2012')
        self.assertEqual(result,
            {'100|CRS1': 'Course 1', '100|COURSE1': 'Unnamed Course'})
        result = server.get_courses_by_session('K1000000')
        self.assertEqual(result,
            {'100|CRS1': 'Course 1', '100|COURSE1': 'Unnamed Course'})
        # Also matric_number ...
        result = server.get_courses_by_session('234')
        self.assertEqual(result,
            {'100|CRS1': 'Course 1', '100|COURSE1': 'Unnamed Course'})
        # ... or reg_number can be used.
        result = server.get_courses_by_session('123')
        self.assertEqual(result,
            {'100|CRS1': 'Course 1', '100|COURSE1': 'Unnamed Course'})
        result = server.get_courses_by_session('Nonsense')
        self.assertEqual(result, None)
        REQUEST_XML = """\
<?xml version="1.0"?>
<methodCall>
<methodName>get_courses_by_session</methodName>
<params>
<param>
<value><string>K1000000</string></value>
</param>
</params>
</methodCall>"""
        RESPONSE_XML = """\
<?xml version='1.0'?>
<methodResponse>
<params>
<param>
<value><struct>
<member>
<name>100|CRS1</name>
<value><string>Course 1</string></value>
</member>
<member>
<name>100|COURSE1</name>
<value><string>Unnamed Course</string></value>
</member>
</struct></value>
</param>
</params>
</methodResponse>
"""
        xmlout = self.XMLRPC_post(REQUEST_XML)
        self.assertEqual(xmlout, RESPONSE_XML)
        return

    def test_get_students_by_course(self):
        self.setup_student(self.student)
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        result = server.get_students_by_course('CRS1', '2010')
        self.assertEqual(result, None)
        result = server.get_students_by_course('CRS1', '2012')
        self.assertEqual(result, [['K1000000', '234', 'my adviser', 0], ])
        result = server.get_students_by_course('CRS1')
        self.assertEqual(result, [['K1000000', '234', 'my adviser', 0], ])
        payment = StudentOnlinePayment()
        payment.p_id = 'my-id'
        payment.p_session = 2012
        payment.amount_auth = 12.12
        payment.p_state = u'paid'
        payment.p_category = u'schoolfee'
        self.student['payments']['my-payment'] = payment
        result = server.get_students_by_course('CRS1')
        self.assertEqual(result, [['K1000000', '234', 'my adviser', 12.12], ])
        REQUEST_XML = """\
<?xml version="1.0"?>
<methodCall>
<methodName>get_students_by_course</methodName>
<params>
<param>
<value><string>CRS1</string></value>
<value><string>2012</string></value>
</param>
</params>
</methodCall>"""
        RESPONSE_XML = """\
<?xml version='1.0'?>
<methodResponse>
<params>
<param>
<value><array><data>
<value><array><data>
<value><string>K1000000</string></value>
<value><string>234</string></value>
<value><string>my adviser</string></value>
<value><double>12.12</double></value>
</data></array></value>
</data></array></value>
</param>
</params>
</methodResponse>
"""
        xmlout = self.XMLRPC_post(REQUEST_XML)
        self.assertEqual(xmlout, RESPONSE_XML)
        return

    def test_get_student_info(self):
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        result = server.get_student_info('123')
        self.assertEqual(result,
            ['Anna Tester', 'CERT1', '1234', 'aa@aa.ng'])
        REQUEST_XML = """\
<?xml version="1.0"?>
<methodCall>
<methodName>get_student_info</methodName>
<params>
<param>
<value><string>K1000000</string></value>
</param>
</params>
</methodCall>"""
        RESPONSE_XML = """\
<?xml version='1.0'?>
<methodResponse>
<params>
<param>
<value><array><data>
<value><string>Anna Tester</string></value>
<value><string>CERT1</string></value>
<value><string>1234</string></value>
<value><string>aa@aa.ng</string></value>
</data></array></value>
</param>
</params>
</methodResponse>
"""
        xmlout = self.XMLRPC_post(REQUEST_XML)
        self.assertEqual(xmlout, RESPONSE_XML)
        return

    def test_get_student_passport(self):
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        self.create_passport_img(self.student)
        result = server.get_student_passport('123')
        img = getUtility(IExtFileStore).getFileByContext(
            self.student, attr='passport.jpg')
        binary = img.read()
        self.assertEqual(binary, result)
        REQUEST_XML = """\
<?xml version="1.0"?>
<methodCall>
<methodName>get_student_passport</methodName>
<params>
<param>
<value><string>K1000000</string></value>
</param>
</params>
</methodCall>"""
        RESPONSE_XML = """\
<?xml version='1.0'?>
<methodResponse>
<params>
<param>
<value><base64>
/9j/4AAQSkZJRgABAgAAZABkAAD/7AARRHVja3kAAQAEAAAAPAAA/+4ADkFkb2JlAGTAAAAAAf/b
"""
        xmlout = self.XMLRPC_post(REQUEST_XML)
        self.assertTrue(xmlout.startswith(RESPONSE_XML))

    def test_get_paid_sessions(self):
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        payment = StudentOnlinePayment()
        payment.p_id = 'my-id'
        payment.p_session = 2009
        payment.amount_auth = 12.12
        payment.p_state = u'paid'
        payment.p_category = u'schoolfee'
        self.student['payments']['my-payment'] = payment
        result = server.get_paid_sessions('123')
        self.assertEqual(result, {'2009': 12.12})
        REQUEST_XML = """\
<?xml version="1.0"?>
<methodCall>
<methodName>get_paid_sessions</methodName>
<params>
<param>
<value><string>K1000000</string></value>
</param>
</params>
</methodCall>"""
        RESPONSE_XML = """\
<?xml version='1.0'?>
<methodResponse>
<params>
<param>
<value><struct>
<member>
<name>2009</name>
<value><double>12.12</double></value>
</member>
</struct></value>
</param>
</params>
</methodResponse>
"""
        xmlout = self.XMLRPC_post(REQUEST_XML)
        self.assertEqual(xmlout, RESPONSE_XML)
        return

    def test_check_student_credentials(self):
        # make sure we can get student infos providing valid creds
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        stud_id = self.student.student_id
        result = server.check_student_credentials(stud_id, 'spwd')
        self.assertEqual(
            result, {
                'description': 'Anna Tester',
                'email': 'aa@aa.ng',
                'id': 'K1000000',
                'type': 'student'}
            )
        return

    def test_get_student_moodle_data(self):
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        result = server.get_student_moodle_data(self.student.student_id)
        self.assertEqual(result,
            {'lastname': 'Tester', 'email': 'aa@aa.ng', 'firstname': 'Anna'})
        REQUEST_XML = """\
<?xml version="1.0"?>
<methodCall>
<methodName>get_student_moodle_data</methodName>
<params>
<param>
<value><string>K1000000</string></value>
</param>
</params>
</methodCall>"""
        RESPONSE_XML = """\
<?xml version='1.0'?>
<methodResponse>
<params>
<param>
<value><struct>
<member>
<name>lastname</name>
<value><string>Tester</string></value>
</member>
<member>
<name>email</name>
<value><string>aa@aa.ng</string></value>
</member>
<member>
<name>firstname</name>
<value><string>Anna</string></value>
</member>
</struct></value>
</param>
</params>
</methodResponse>
"""
        xmlout = self.XMLRPC_post(REQUEST_XML)
        self.assertEqual(xmlout, RESPONSE_XML)
        return

    def test_put_student_fingerprints_no_stud(self):
        # invalid student ids will result in `False`
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.assertRaises(
            xmlrpclib.Fault, server.put_student_fingerprints,
            'invalid id', {})

    def test_put_student_fingerprints_non_dict(self):
        # fingerprints must be passed in in a dict
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        self.assertRaises(
            xmlrpclib.Fault, server.put_student_fingerprints,
            self.student.student_id, 'not-a-dict')

    def test_put_student_fingerprints_non_num_keys_ignored(self):
        # non-numeric keys in fingerprint dict are ignored
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        result = server.put_student_fingerprints(
            self.student.student_id, {'not-a-num': 'foo',
                                      '12.2': 'bar',
                                      '123': 'baz'})
        self.assertEqual(result, False)

    def test_put_student_fingerprints_non_fpm_data(self):
        # we cannot pass non-.fpm files as values
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        self.assertRaises(
            xmlrpclib.Fault, server.put_student_fingerprints,
            self.student.student_id, {'1': 'not-a-fingerprint'})

    def test_put_student_fingerprints_invalid_file_format(self):
        # invalid files will result in `False`
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        invalid_fpm = xmlrpclib.Binary('invalid file')
        self.assertRaises(
            xmlrpclib.Fault, server.put_student_fingerprints,
            self.student.student_id, {'1': invalid_fpm})

    def test_put_student_fingerprints(self):
        # we can store fingerprints
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        fpm = xmlrpclib.Binary('FP1faked_fpm')
        result = server.put_student_fingerprints(
            self.student.student_id, {'1': fpm})
        self.assertEqual(result, True)
        stored_file = getUtility(IExtFileStore).getFileByContext(
            self.student, attr="1.fpm")
        self.assertEqual(stored_file.read(), 'FP1faked_fpm')

    def test_put_student_fingerprints_existing(self):
        # existing fingerprints are overwritten
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        self.create_fpm_file(self.student, '1')
        fpm1 = xmlrpclib.Binary('FP1faked_fpm1')
        fpm2 = xmlrpclib.Binary('FP1faked_fpm2')
        result = server.put_student_fingerprints(
            self.student.student_id, {'1': fpm1, '3': fpm2})
        self.assertEqual(result, True)
        stored_file1 = getUtility(IExtFileStore).getFileByContext(
            self.student, attr="1.fpm")
        stored_file2 = getUtility(IExtFileStore).getFileByContext(
            self.student, attr="3.fpm")
        self.assertEqual(stored_file1.read(), 'FP1faked_fpm1')
        self.assertEqual(stored_file2.read(), 'FP1faked_fpm2')

    def test_get_student_fingerprints_no_stud(self):
        # invalid student ids result in empty dict
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        result = server.get_student_fingerprints('invalid id')
        self.assertEqual(result, {})

    def test_get_student_fingerprints_no_files(self):
        # we get student data, but no fingerprints if not stored before
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        result = server.get_student_fingerprints(self.student.student_id)
        self.assertEqual(
            result,
            {'lastname': 'Tester',
             'email': 'aa@aa.ng',
             'firstname': 'Anna',
             'fingerprints': {},
             'img': None,
             'img_name': None,
             })

    def test_get_student_fingerprints_passport(self):
        # we get a photograph of the student if avail.
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        self.create_passport_img(self.student)
        result = server.get_student_fingerprints(self.student.student_id)
        self.assertTrue(
            isinstance(result['img'], xmlrpclib.Binary))
        self.assertEqual(result['img_name'], 'passport_K1000000.jpg')

    def test_get_student_fingerprints_fpm(self):
        # we get minutiae files if any are avail.
        server = ServerProxy('http://mgr:mgrpw@localhost/app')
        self.setup_student(self.student)
        self.create_fpm_file(self.student, '1')
        result = server.get_student_fingerprints(self.student.student_id)
        self.assertTrue('1' in result['fingerprints'].keys())
        self.assertTrue(
            isinstance(result['fingerprints']['1'], xmlrpclib.Binary))

    def test_get_student_fingerprints_block_unauthorized(self):
        # requests from unauthorized users are blocked
        # no username nor password
        server = ServerProxy('http://localhost/app')
        self.setup_student(self.student)
        stud_id = self.student.student_id
        self.assertRaises(
            xmlrpclib.ProtocolError, server.get_student_id, stud_id)
        # wrong password
        server = ServerProxy('http://mgr:WRONGPW@localhost/app')
        self.assertRaises(
            xmlrpclib.ProtocolError, server.get_student_id, stud_id)
        # wrong username
        server = ServerProxy('http://WRONGUSER:mgrpw@localhost/app')
        self.assertRaises(
            xmlrpclib.ProtocolError, server.get_student_id, stud_id)
        return
