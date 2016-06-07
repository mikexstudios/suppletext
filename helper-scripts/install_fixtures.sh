#!/bin/bash

#Note that $0 contains the full path of the script being executed.
script_path=`dirname $0`
cd "${script_path}/.."

python manage.py loaddata initial_wiki
python manage.py loaddata initial_pages
