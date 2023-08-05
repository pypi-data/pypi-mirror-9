## $Id: prepare_jamb_file.py 8546 2012-05-29 12:24:32Z henrik $
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
"""
import csv
import datetime
import re
import sys

##
## CONFIGURATION SECTION
##
# keys are fieldnames in input file, values are methods of class
# Converter (see below)
OPTIONS = {
    'sex': 'gender',
    'session': 'session',
    'lga': 'lga',
    'firstname': 'name',
    'middlename': 'name',
    'lastname': 'uppername',
    'container_code': 'container_code',
    }

# Mapping input file colnames --> output file colnames
COLNAME_MAPPING = {
    'jambscore': 'jamb_score',
    'eng_score': 'jamb_subjects',
    }

##
## END OF CONFIG
##

# Look for the first sequence of numbers
RE_PHONE = re.compile('[^\d]*(\d*)[^\d]*')

def convert_fieldnames(fieldnames):
    """Replace input fieldnames by fieldnames of COLNAME_MAPPING.
    """
    header = dict([(name, name) for name in fieldnames])
    for in_name, out_name in COLNAME_MAPPING.items():
        if in_name not in header:
            continue
        header[in_name] = out_name
    return header

def merge_subjects(row):
    """Merge jamb subjects and scores into one field.
    """
    if 'eng_score' in row and 'Subj2'	in row and 'Subj2Score' in row \
        and 'Subj3' in row and 'Subj3Score' in row and 'Subj4' in row  \
        and 'Subj4Score' in row:
        subjectstring = "English: %s, %s: %s, %s: %s, %s: %s"
        row['eng_score'] =  subjectstring % (
            row['eng_score'],
            row['Subj2'], row['Subj2Score'],
            row['Subj3'], row['Subj3Score'],
            row['Subj4'], row['Subj4Score'],
            )
    else:
        pass

class Converters():
    """Converters to turn old-style values into new ones.
    """

    @classmethod
    def name(self, value):
        """ 'JOHN -> John'
        """
        return value.capitalize()

    @classmethod
    def uppername(self, value):
        """ 'John -> JOHN'
        """
        return value.upper()

    @classmethod
    def container_code(self, value):
        """ Return constant string.
        """
        return 'putme2012'

    @classmethod
    def lga(self, value):
        """ 
        """
        if value == 'akwa_ibom_uru_offong_oruko':
            return 'akwa_ibom_urue-offong-oruko'
        if value == 'edo_akoko_edo':
            return 'edo_akoko-edo'
        if value == 'edo_owan_east':
            return 'edo_owan-east'
        if value == 'kogi_mopa-muro-mopi':
            return 'kogi_mopa-muro'
        if value == 'foreign':
            return 'foreigner'
        try:
            value = value.replace("'","")
            value = value.lower()
        except:
            return ''
        return value


    @classmethod
    def session(self, value):
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
            #import pdb; pdb.set_trace()
            return 9999
        if number < 14:
            return number + 2000
        elif number in range(2000,2015):
            return number
        else:
            return 9999

    @classmethod
    def gender(self, value):
        """ 'True'/'False' --> 'f'/'m'
            'F'/'M' --> 'f'/'m'
        """
        if value in ('True','f','F'):
            value = 'f'
        elif value in ('False','m','M'):
            value = 'm'
        else:
            value = ''
        return value


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
        merge_subjects(row)
        for key, value in row.items():
            if not key in OPTIONS.keys():
                continue
            conv_name = OPTIONS[key]
            converter = getattr(Converters, conv_name, None)
            if converter is None:
                print "WARNING: cannot find converter %s" % conv_name
                continue
            row[key] = converter(row[key])
        try:
            writer.writerow(row)
        except:
            print row['reg_number']

    print "Output written to %s" % output_file


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s <filename>' % __file__
        sys.exit(1)
    main()
