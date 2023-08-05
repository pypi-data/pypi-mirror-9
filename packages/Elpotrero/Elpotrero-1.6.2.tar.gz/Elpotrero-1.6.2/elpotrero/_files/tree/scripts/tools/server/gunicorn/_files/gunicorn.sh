  #!/bin/bash
  set -e

  USER={{user}}
  GROUP={{group}}

  PROJECT={{project}}
  BRANCH={{branch}}
  DOMAIN={{domain}}

  HOST=$PROJECT.$DOMAIN
  ADDRESS={{address}}
  PORT={{port}}
  
  PROJDIR={{rootpath}}/$HOST/private/djangoproject
  ENVDIR={{rootpath}}/$HOST/private/virtual_environment

  #     It is very possible that ADDRESS will have a different value than host
  #
  #     In production branches, PORT will just have a slightly hire value than
  # in the development branch.

  LOGFILE={{rootpath}}/$HOST/logs/gunicorn/$BRANCH.log
  LOGDIR=$(dirname $LOGFILE)
  NUM_WORKERS=3
  


  cd $PROJDIR
  source $ENVDIR/bin/activate

  # for some incredibly screwed up reason, postactivate in virtualenv is NOT running when I use
  # supervisor.  So check and see if GEM_HOME was set, if so, ignore, otherwise - SET IT!
  if [ -z "$GEM_HOME" ]; then 
        GEM_HOME=$ENVDIR/gems
        export GEM_HOME
        echo ""
        echo "GEM_HOME = $GEM_HOME"
  fi
  PATH=$PATH:"$GEM_HOME/bin"

  test -d $LOGDIR || mkdir -p $LOGDIR

  exec $ENVDIR/bin/gunicorn $PROJECT.wsgi:application -w $NUM_WORKERS \
    --user=$USER --group=$GROUP --log-level=debug \
    --log-file=$LOGFILE 2>>$LOGFILE --bind $ADDRESS:$PORT
