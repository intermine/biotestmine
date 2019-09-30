#!/bin/bash

# Build and release a biological test mine.

set -e
set -o pipefail # Pipes are considered failed if any of their commands fail.

DIR="$(cd $(dirname "$0"); pwd)"
MINENAME=biotestmine
PROD_DB=$MINENAME
ITEMS_DB=items-$MINENAME
USERPROFILE_DB=userprofile-$MINENAME
IMDIR=$HOME/.intermine
PROP_FILE=${MINENAME}.properties
DATA_DIR=$HOME/${MINENAME}-sample-data
LOAD_LOG="${LOG_DIR}/setup.log"
PRIORITIES=$DIR/dbmodel/resources/genomic_priorities.properties

# Inherit SERVER, PORT, PSQL_USER, PSQL_PWD, TOMCAT_USER and TOMCAT_PWD if in env.
if test -z $SERVER; then
    SERVER=localhost
fi
if test -z $PORT; then
    PORT=8080
fi
if test -z $PSQL_USER; then
    PSQL_USER=$USER
fi
if test -z $PSQL_PWD; then
    PSQL_PWD=$USER;
fi
if test -z $TOMCAT_USER; then
    TOMCAT_USER=manager
fi
if test -z $TOMCAT_PWD; then
    TOMCAT_PWD=manager
fi
if test -z $DB_ENCODING; then
    DB_ENCODING=SQL_ASCII
fi

for dep in perl psql createdb; do
  if test -z $(which $dep); then
    echo "ERROR: $dep not found - please make sure $dep is installed and configured correctly"
    exit 1
  fi
done

perl -MXML::Parser::PerlSAX \
     -MText::Glob \
     -MCwd \
     -MGetopt::Std \
     -e 'print "#--- Perl dependencies satisfied\n";'

# Report settings before we do anything.
if test $DEBUG; then
    echo '# SETTINGS:'
    echo "#  DIR = $DIR"
    echo "#  MINENAME = $MINENAME"
    echo "#  PROD_DB = $PROD_DB"
    echo "#  ITEMS_DB = $ITEMS_DB"
    echo "#  USERPROFILE_DB = $USERPROFILE_DB"
    echo "#  IMDIR = $IMDIR"
    echo "#  PROP_FILE = $PROP_FILE"
    echo "#  DATA_DIR = $DATA_DIR"
    echo "#  SERVER = $SERVER"
    echo "#  PORT = $PORT"
    echo "#  PSQL_USER = $PSQL_USER"
    echo "#  PSQL_PWD = $PSQL_PWD"
    echo "#  TOMCAT_USER = $TOMCAT_USER"
    echo "#  TOMCAT_PWD = $TOMCAT_PWD"
    echo "#  DB_ENCODING = $DB_ENCODING"
fi

if test ! -d $IMDIR; then
    echo '#---> Making .intermine configuration directory.'
    mkdir $IMDIR
fi

if test ! -f $IMDIR/$PROP_FILE; then
    echo "#---> $PROP_FILE not found. Providing default properties file..."
    cd $IMDIR
    wget https://raw.githubusercontent.com/intermine/biotestmine/master/data/biotestmine.properties
    sed -i=bak "s/PSQL_USER/$PSQL_USER/g" $PROP_FILE
    sed -i=bak "s/PSQL_PWD/$PSQL_PWD/g" $PROP_FILE
    sed -i=bak "s/TOMCAT_USER/$TOMCAT_USER/g" $PROP_FILE
    sed -i=bak "s/TOMCAT_PWD/$TOMCAT_PWD/g" $PROP_FILE
    echo "#--- Created $PROP_FILE"
    cd $DIR
fi

echo '#---> Checking databases...'
for db in $USERPROFILE_DB $PROD_DB $ITEMS_DB; do
    if psql --list | egrep -q '\s'$db'\s'; then
        echo "#--- $db exists."
    else
        echo "#---> Creating $db with encoding $DB_ENCODING ..."
        createdb --template template0 \
                 --username $PSQL_USER \
                 --encoding $DB_ENCODING \
                 $db
    fi
done

if test -d $HOME/${MINENAME}-sample-data; then
    echo '#--- Sample data already exists.'
else
    cd $HOME
    mkdir $DATA_DIR
    cd $DATA_DIR
    wget https://github.com/intermine/biotestmine/blob/master/data/malaria-data.tar.gz?raw=true -O malaria-data.tar.gz
    echo '#---> Unpacking sample data...'
    tar -zxvf malaria-data.tar.gz 
    rm malaria-data.tar.gz
fi

cd $DIR
if test ! -f project.xml; then
    echo '#---> Copying over malariamine project.xml'
    wget https://raw.githubusercontent.com/intermine/biotestmine/master/data/project.xml
fi

echo '#---> Personalising project.xml'
sed -i "s!DATA_DIR!$DATA_DIR!g" project.xml

if egrep -q ProteinDomain.shortName $PRIORITIES; then
    echo '#--- Integration key exists.'
else
    echo '#---> Adjusting priorities.'
    echo 'ProteinDomain.shortName = interpro, uniprot-malaria' >> $PRIORITIES
fi

#echo '#---> Building DB'
#./gradlew builddb 

if test ! -f "project_build"; then
    echo '#---> Copying over the InterMine build script'
    wget https://raw.githubusercontent.com/intermine/intermine-scripts/master/project_build
    chmod a+x project_build
fi

echo '#---> Loading data (this may take some time) ...'

./project_build -b -v $SERVER $HOME/${MINENAME}-dump

echo '#--- Finished loading data.'

echo '#---> Building userprofile..'
./gradlew buildUserDB
echo '#---> Releasing web-application'
./gradlew tomcatStartWar

echo BUILD COMPLETE

