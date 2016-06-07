#!/bin/bash

echo 'IMPORTANT: Make sure to set the database to use utf8 encoding before running this!'
echo 'Press any key to continue...'
read

#Note that $0 contains the full path of the script being executed.
script_path=`dirname $0`
cd "${script_path}/.."

python manage.py sqlall wiki
python manage.py syncdb
