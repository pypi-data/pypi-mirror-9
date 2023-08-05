#!/bin/sh

## We expect at least three arguments...
if [ $# -ne 3 ]; then
    echo "Usage: $0 [user name] [password] [exporter]"
    exit
fi

wget --save-cookies cookies.txt --keep-session-cookies --post-data "form.login=$1&form.password=$2" https://uniben-kofa.waeup.org/login 
wget --load-cookies cookies.txt  --output-document $3.csv https://uniben-kofa.waeup.org/datacenter/export.csv?exporter=$3
tar -czf Kofa$3.tar.gz $3.csv
rm $3.csv
mv Kofa$3.tar.gz /home/ftp/uniben
