
# this variable is used for the temporary virtualenv
# export this variabled so child process environment.sh can use it
TEMPENVNAME="TEMPENV_`date +%S%d%M%H`"
export TEMPENVNAME

source virtualenvwrapper.sh
mkvirtualenv $TEMPENVNAME

pip install pyyaml
pip install shyaml
pip install elpotrero

# create a symlink in site-packages so we can import the shyaml commands in programs
PYSITEPACKAGES=`python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`
eval `ln -s $VIRTUAL_ENV/bin/shyaml $PYSITEPACKAGES/shyaml.py`

# export this variabled so child process environment.sh can use it
conftoolcommand=`eval ./loadconfigtools.py -k conftool`
export conftoolcommand 

PROJECT=`eval "$conftoolcommand -k project"`
BRANCH=`eval "$conftoolcommand -k branch"`

# let the user choose the branch for this installation
# (otherwise we have no idea which BRANCH variable to pull up)
branchtoolcommand=`eval ./loadconfigtools.py -k branchtool`
eval "$branchtoolcommand"

# set up the environment variables
# make sure to deativate before we go into environment.sh
deactivate

bash ./environment.sh

workon $PROJECT.$BRANCH

# create a symlink in site-packages so we can import the shyaml commands in programs
PYSITEPACKAGES=`python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`
eval `ln -s $VIRTUAL_ENV/bin/shyaml $PYSITEPACKAGES/shyaml.py`

# generate all the configuration scripts we are going to use to 
# set up the server
gentoolcommand=`eval ./loadconfigtools.py -k generatetool`
eval "$gentoolcommand"

# set all the paths in the working directory, including those
# we need to symlink to the virtualenv, the project dir, scripts, etc.
python createdirstruct.py 

# start project creates a basic django-admin startproject
# and then copies a custom settings.py file into the project directory
python startproject.py
