"""Add a new column old id with contents from col `student_id`
"""

###
### CONFIGURATION
###

IN_FILE = 'mytry.csv'

# new col name. 'old_id' is expected by fix_import_file.py
NEW_COL = 'old_id'

###
### CONFIGURATION - END
###


import csv
OUT_FILE = '%s_edited.csv' % IN_FILE.split('.')[0]
reader = csv.DictReader(open(IN_FILE, 'rb'))

for num, row in enumerate(reader):
    if num == 0:
        writer = csv.DictWriter(
            open(OUT_FILE, 'wb'), reader.fieldnames + [NEW_COL,])
        header = dict([(x, x) for x in writer.fieldnames])
        writer.writerow(header)
    row[NEW_COL] = row['student_id']
    writer.writerow(row)

print "RESULT in ", OUT_FILE
