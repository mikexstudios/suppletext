#!/bin/bash

#Note that $0 contains the full path of the script being executed.
script_path=`dirname $0`
cd "${script_path}/.."
env/bin/python manage.py runserver 0.0.0.0:8000
