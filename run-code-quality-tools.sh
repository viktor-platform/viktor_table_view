#!/bin/bash
: '
First install and setup a virtual environment in this folder:

Use the following cmd from this folder to install a virtual environment:
python -m venv venv
This will install a new virtual environment in the folder venv

Install the required packages by first activating the venv and then installing the packages:
source venv/bin/activate
pip install -r dev-requirements.txt

When this is done you can run this script from this folder
'

APP=.
echo -e "Activate virtual environment\n"
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    source $APP/venv/Scripts/activate
else
    source $APP/venv/bin/activate
fi
python -m pip install --upgrade pip > /dev/null
echo -e "Installing dev-requirements.txt\n"
pip install -r dev-requirements.txt > /dev/null

echo -e "Running black\n"
python -m black $APP/viktor_table_view;
echo -e "Running isort\n"
python -m isort $APP/viktor_table_view;
echo -e "Running pylint\n"
python -m pylint $APP/viktor_table_view --rcfile=$APP/pyproject.toml;
echo -e "Running tests\n"
viktor-cli test

echo -e "Deactivate virtual environment\n"
deactivate
