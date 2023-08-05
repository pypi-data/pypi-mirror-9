## $Id: fix_import_file.py 9478 2012-10-30 20:19:06Z henrik $
## 
## Copyright (C) 2012 Uli Fouquet & Henrik Bettermann
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
"""
Fix exports from old SRP portal and other data sources to make
them importable by current portal.

Usage:

Change into this directory, set the options below (files are assumed
to be in the same directory) and then run

  python fix_import_file.py <filename>

Errors/warnings will be displayed on the shell, the output will be put
into the specified output file.


The lgas.py module must be copied into the same folder where this script
is started.
"""
import csv
import datetime
import os
import re
import sys

try:
    from lgas import LGAS
except:
    print 'ERROR: lgas.py is missing.'
    sys.exit(1)

def strip(string):
    string = string.replace('_', '')
    string = string.replace('/', '')
    string = string.replace('-', '')
    string = string.replace(' ', '')
    string = string.lower()
    return string

LGAS_inverted_stripped = dict([(strip(i[1]), i[0]) for i in LGAS])
LGAS_dict = dict(LGAS)

##
## CONFIGURATION SECTION
##
# keys are fieldnames in input file, values are methods of class
# Converter (see below)
OPTIONS = {
    'student_id': 'student_id',
    'sex': 'gender',
    'birthday': 'date',
    'marit_stat': 'marit_stat',
    'session': 'session',
    'entry_session': 'session',
    'current_session': 'session',
    'session_id': 'session',
    'entry_mode': 'mode',
    'reg_state': 'reg_state',
    'password': 'password',
    'phone': 'phone',
    'nationality': 'nationality',
    'level': 'level',
    'start_level': 'level',
    'end_level': 'level',
    'level_id': 'level',
    'current_level': 'level',
    'semester': 'semester',
    'application_category': 'application_category',
    'lga': 'lga',
    'order_id': 'no_int',
    'uniben': 'former',
    'nysc_year': 'year',
    'alr_date': 'date',
    'fst_sit_date': 'date',
    'scd_sit_date': 'date',
    'emp_start': 'date',
    'emp_end': 'date',
    'emp_start2': 'date',
    'emp_end2': 'date',
    'fst_sit_results': 'result',
    'scd_sit_results': 'result',
    'alr_results': 'result',
    'email': 'email',
    'fst_sit_type': 'sittype',
    'scd_sit_type': 'sittype',
    'resp_pay_reference': 'no_int',
    'type': 'company',
    'date': 'date',
    'core_or_elective': 'bool',
    'category': 'p_category',
    'reg_transition': 'reg_state',  # we completely change this column,
                                    # since reg_state import is usually intended
    'transition': 'reg_transition',
    'payment_date': 'date',
    'validation_date': 'date',
    'resp_approved_amount': 'amount',
    'amount': 'amount',
    'amount_auth': 'amount',
    'surcharge': 'amount'
    }

# Mapping input file colnames --> output file colnames
COLNAME_MAPPING = {
    # base data
    'id': 'student_id',
    'reg_state': 'state',
    'reg_transition': 'state',
    'jamb_reg_no': 'reg_number',
    'matric_no': 'matric_number',
    'birthday': 'date_of_birth',
    'clr_ac_pin': 'clr_code',
    # clearance
    'hq_grade': 'hq_degree',
    'uniben': 'former_matric',
    'hq_type2': 'hq2_type',
    'hq_grade2': 'hq2_degree',
    'hq_school2': 'hq2_school',
    'hq_matric_no2': 'hq2_matric_no',
    'hq_session2': 'hq2_session',
    'hq_disc2': 'hq2_disc',
    'emp': 'employer',
    'emp2': 'employer2',
    'emp_position2': 'emp2_position',
    'emp_start2': 'emp2_start',
    'emp_end2': 'emp2_end',
    'emp_reason2': 'emp2_reason',
    # study course
    'study_course': 'certificate',
    # study level
    'session': 'level_session',
    'verdict': 'level_verdict',
    # course ticket
    'level_id': 'level',
    'core_or_elective': 'mandatory',
    # payment ticket
    'order_id': 'p_id',
    'status': 'p_state',
    'category': 'p_category',
    'resp_pay_reference': 'r_pay_reference',
    'resp_desc': 'r_desc',
    'resp_approved_amount': 'r_amount_approved',
    'item': 'p_item',
    'amount': 'amount_auth',
    'resp_card_num': 'r_card_num',
    'resp_code': 'r_code',
    'date': 'creation_date',
    'surcharge': 'surcharge_1',
    'session_id': 'p_session',
    'type': 'r_company',
    'old_id': 'old_id',
    }

# Mapping input state --> output state
REGSTATE_MAPPING = {
    'student_created': 'created',
    'admitted': 'admitted',
    'objection_raised': 'clearance started',
    'clearance_pin_entered': 'clearance started',
    'clearance_requested': 'clearance requested',
    'cleared_and_validated': 'cleared',
    'school_fee_paid': 'school fee paid',
    'returning': 'returning',
    'courses_registered': 'courses registered',
    'courses_validated': 'courses validated',
    'admit': 'admitted',
    'return': 'returning'
    }

# Mapping of special cases, where new id is not deductible from old id
# Set to `None`, if no such special cases should be considered.
ID_MAP_CSV = None
ID_MAP_CSV = "id_mapping.csv"

##
## END OF CONFIG
##

# Look for the first sequence of numbers
RE_PHONE = re.compile('[^\d]*(\d*)[^\d]*')

def get_id_mapping():
    """Returns a dict mapping from old (SRP) ids to new ids.

    The dict is read from ID_MAP_CSV file. If this var is set to
    ``None`` an empty dict is returned. The ID_MAP_CSV contains only
    the student ids of those students, for which the standard method
    (new_id=CHAR+old_id) does not work.
    """
    if ID_MAP_CSV is None:
        return {}
    if not os.path.isfile(ID_MAP_CSV):
        raise IOError(
            "No such file for mapping old to new ids: %s" % ID_MAP_CSV)
    result = dict()
    reader = csv.DictReader(open(ID_MAP_CSV, 'rb'))
    for row in reader:
        result[row['student_id']] = row['new_id']
    return result


def convert_fieldnames(fieldnames):
    """Replace input fieldnames by fieldnames of COLNAME_MAPPING.
    """
    # Remove whitespaces
    header = dict([(name, name.strip()) for name in fieldnames])
    for in_name, out_name in COLNAME_MAPPING.items():
        if in_name not in header.values():
            continue
        # Inverse dictionary lookup
        key = [key for key,value in header.items() if value==in_name][0]
        header[key] = out_name
    return header

class Converters():
    """Converters to turn old-style values into new ones.
    """

    old_new_id_map = get_id_mapping()

    @classmethod
    def student_id(cls, value, row):
        """ 'A123456' --> 'EA123456'
        """
        value = cls.old_new_id_map.get(value, value)
        if len(value) == 7:
            return 'B' + value
        return value

    @classmethod
    def reg_state(self, value, row):
        """ 'courses_validated' --> 'courses validated'
        """
        return REGSTATE_MAPPING.get(value,value)

    @classmethod
    def reg_transition(self, value, row):
        if value == "admitted":
            return "admit"
        if value == "returning":
            return "return"
        return value

    @classmethod
    def level(self, value, row):
        """ '000' --> '10'
        '800' --> '999' if pg student
        """
        try:
            number = int(value)
        except ValueError:
            return 9999
        if number == 0:
            return 10
        if row.get('entry_mode') and row.get('entry_mode').startswith('pg'):
            return 999
        return number

    @classmethod
    def semester(self, value, row):
        """ '0' --> '9'
        """
        try:
            number = int(value)
        except ValueError:
            return 9999
        if number == 0:
            return 9
        return number

    @classmethod
    def application_category(self, value, row):
        """ '' --> 'no'
        """
        if value == '':
            return 'no'
        return value

    @classmethod
    def lga(self, value, row):
        """ Remove apostrophe
        """
        if value == 'akwa_ibom_uru_offong_oruko':
            return 'akwa_ibom_urue-offong-oruko'
        if value == 'edo_ohionmwon':
            return 'edo_orhionmwon'

        if value == 'nassarawa_nassarawa':
            return 'nassarawa_nassawara'

        if value == 'kogi_mopa-muro-mopi':
            return 'kogi_mopa-muro'

        if value == 'delta_osimili-north':
            return 'delta_oshielli-north'

        if value == 'delta_osimili':
            return 'delta_oshimili'

        if value == 'delta_osimili-south':
            return 'delta_oshimili-south'
        try:
            value = value.replace("'","")
        except:
            return ''
        lower = value.lower()
        if lower in LGAS_dict.keys():
            return lower
        # If real names are given, let's see if a similar value
        # in LGAS exist.
        value = value.replace('_',' ')
        value = LGAS_inverted_stripped.get(strip(lower), value)
        return value


    @classmethod
    def session(self, value, row):
        """ '08' --> '2008'
        '2008/2009' --> '2008'
        """
        if '/' in value:
            numbers = value.split('/')
            number = int(numbers[0])
            if number in range(2000,2015):
                return number
            else:
                return 9999
        try:
            number = int(value)
        except ValueError:
            return 9999
        if number < 14:
            return number + 2000
        elif number in range(2000,2015):
            return number
        else:
            return 9999

    @classmethod
    def former(self, value, row):
        """ True --> yes
        '2008/2009' --> '2008'
        """
        if value == 'True':
            return 'yes'
        return

    @classmethod
    def bool(self, value, row):
        """ True --> 1
        """
        if value in ('TRUE', 'True'):
            return '1'
        elif value in ('FALSE', 'False'):
            return '0'
        return

    @classmethod
    def year(self, value, row):
        """ '0' --> ''
        """
        if value == '0':
            return
        if value == 'None':
            return
        return value


    @classmethod
    def marit_stat(self, value, row):
        """ 'True'/'False' --> 'married'/'unmarried'
        """
        if value in ('True','married'):
            value = 'married'
        elif value in ('False','unmarried'):
            value = 'unmarried'
        else:
            value = ''
        return value

    @classmethod
    def gender(self, value, row):
        """ 'True'/'False' --> 'f'/'m'
        """
        if value.strip() in ('F', 'True','f'):
            value = 'f'
        elif value.strip() in ('M', 'False','m'):
            value = 'm'
        else:
            value = ''
        return value

    @classmethod
    def date(self, value, row):
        """ 'yyyy/mm/dd' --> 'yyyy-mm-dd'
        """
        if value == "None":
            value = ""
        elif value == "":
            value = ""
        else:
            value = value.replace('/', '-')
            # We add the hash symbol to avoid automatic date transformation
            # in Excel and Calc for further processing
            value += '#'
        return value

    @classmethod
    def no_int(self, value, row):
        """ Add hash and skip numbers starting with 999999
        """
        # We add the hash symbol to avoid automatic number transformation
        # in Excel and Calc for further processing
        try:
            intvalue = int(value)
            value += '#'
        except:
            pass
        if value.startswith('999999'):
            return
        return value

    @classmethod
    def amount(self, value, row):
        """ Amounts must be integers
        """
        try:
            return float(value)
        except:
            return

    @classmethod
    def mode(self, value, row):
        if value == "transfer_fulltime":
            return "transfer_ft"
        if value == "ume_ft":
            return "utme_ft"
        return value

    @classmethod
    def password(self, value, row):
        if value == "not set":
            return ""
        return value

    @classmethod
    def nationality(self, value, row):
        if value in ('nigeria', 'Nigeria'):
            return "NG"
        if value in ('niger', 'Niger'):
            return "NE"
        return value

    @classmethod
    def sittype(self, value, row):
        if value == "nabtec":
            return "nabteb"
        return value

    @classmethod
    def company(self, value, row):
        if value == "online":
            return "interswitch"
        return value

    @classmethod
    def p_category(self, value, row):
        if value == "acceptance":
            return "clearance"
        return value

    @classmethod
    def email(self, value, row):
        return value.strip()

    @classmethod
    def phone(self, value, row):
        """ '<num-seq1>-<num-seq2> asd' -> '--<num-seq1><num-seq2>'

        Dashes and slashes are removed before looking for sequences
        of numbers.
        """
        if not value:
            return
        if len(value) < 5:
            return
        value = value.strip('#')
        value = value.replace('-', '')
        value = value.replace('/', '')
        match = RE_PHONE.match(value)
        phone = match.groups()[0]
        if value.startswith('234'):
            value = '+' + value[:3] + '-' + value[3:]
        elif value.startswith('+234'):
            value = value[:4] + '-' + value[4:]
        else:
            value = '-%s' % phone
        return value + '#'

    @classmethod
    def result(self, value, row):
        try:
            liste = eval(value)
        except:
            return
        if isinstance(liste,list):
            return [(i[0].lower(),i[1]) for i in liste]
        return


def main():
    input_file = '%s' % sys.argv[1]
    output_file = '%s_edited.csv' % sys.argv[1].split('.')[0]
    reader = csv.DictReader(open(input_file, 'rb'))
    writer = None

    for num, row in enumerate(reader):
        if num == 0:
            writer = csv.DictWriter(open(output_file, 'wb'), reader.fieldnames)
            print "FIELDS: "
            for x, y in enumerate(reader.fieldnames):
                print x, y
            header = convert_fieldnames(reader.fieldnames)
            writer.writerow(header)
        #if row.get('reg_state') == 'student_created':
        #    # We do not reimport student records which have never been accessed.
        #    continue
        if row.get('status') == 'started':
            # We do not reimport started payments.
            continue
        for key, value in row.items():
            # Remove unwanted whitespaces.
            row[key] = row[key].strip()
            if not key in OPTIONS.keys():
                continue
            conv_name = OPTIONS[key]
            converter = getattr(Converters, conv_name, None)
            if converter is None:
                print "WARNING: cannot find converter %s" % conv_name
                continue
            row[key] = converter(row[key], row)
        try:
            writer.writerow(row)
        except:
            print row['student_id']

    print "Output written to %s" % output_file


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s <filename>' % __file__
        sys.exit(1)
    main()
