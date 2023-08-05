
# activate the TEMPENV we created in bootstrap.sh
# NOTE: We have to re-source and reactivate in here, otherwise will be in a world of shit, 
# because virtualenvwrapper does not play nice with child bash scripts 
source /usr/local/bin/virtualenvwrapper.sh
workon $TEMPENVNAME

PROJECT=`eval "$conftoolcommand -k project"`
DOMAIN=`eval "$conftoolcommand -k domain"`
BRANCH=`eval "$conftoolcommand -k branch"`
PROJECTPATH=`eval "$conftoolcommand --projectpath"`


ENVIRONMENT=`eval "$conftoolcommand -k environment"`

pip freeze

# we got the variables we needed, now delete the virtualenv
deactivate
rmvirtualenv $TEMPENVNAME


echo "PROJECT = $PROJECT"
echo "DOMAIN = $DOMAIN"
echo "BRANCH = $BRANCH"
echo "PROJECTPATH = $PROJECTPATH"
echo "ENVIRONMENT = $ENVIRONMENT"


PYLIBS='$HOME/lib/py'

if [ -n "$PYTHONPATH" ]; then
    echo "PYTHONPATH already set to $PYTHONPATH" 
else
    echo "" >> ~/.bashrc
    echo "# variable used for PYTHONPATH" >> ~/.bashrc 
    echo "export PYTHONPATH='$PYLIBS:$PYTHONPATH'" >> ~/.bashrc
    exec bash
   # execute the bash function to reload the bash script
    # so that we can set the PYTHONPATH variable
    # otherwise if we rerun this script for whatever reason
    # it will re-add the above commands, even tho we already
    # added them.
    #
    # don't bother using source ~/.bashrc because any commands
    # generally run from a shell script don't transfer to the 
    # parent shell
fi

if [ -n "$WORKON_HOME" ]; then
    echo "WORKON_HOME already set to $WORKON_HOME" 
else
    echo "" >> ~/.bashrc
    echo "# variable used for virtualenvwrapper" >> ~/.bashrc 
    echo "export WORKON_HOME='$ENVIRONMENT'" >> ~/.bashrc
    exec bash
    # execute the bash function to reload the bash script
    # so that we can set the WORKON_HOME variable
    # otherwise if we rerun this script for whatever reason
    # it will re-add the above commands, even tho we already
    # added them.
    #
    # don't bother using source ~/.bashrc because any commands
    # generally run from a shell script don't transfer to the 
    # parent shell
fi


mkvirtualenv $PROJECT.$BRANCH
pip install -r $PROJECTPATH/scripts/meta/virtualenv/requirements.$BRANCH.conf --allow-all-external
