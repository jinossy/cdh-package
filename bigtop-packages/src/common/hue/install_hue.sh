#!/bin/bash

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

usage() {
  echo "
usage: $0 <options>
  Required not-so-options:
     --build-dir=DIR             path to Hue dist.dir
     --prefix=PREFIX             path to install into

  Optional options:
     --doc-dir=DIR               path to install docs into [/usr/share/doc/hue]
     --lib-dir=DIR               path to install Hue home [/usr/lib/hue]
     --installed-lib-dir=DIR     path where lib-dir will end up on target system
     --bin-dir=DIR               path to install bins [/usr/bin]
     ... [ see source for more similar options ]
  "
  exit 1
}

OPTS=$(getopt \
  -n $0 \
  -o '' \
  -l 'prefix:' \
  -l 'doc-dir:' \
  -l 'lib-dir:' \
  -l 'installed-lib-dir:' \
  -l 'bin-dir:' \
  -l 'build-dir:' -- "$@")

if [ $? != 0 ] ; then
    usage
fi

eval set -- "$OPTS"
while true ; do
    case "$1" in
        --prefix)
        PREFIX=$2 ; shift 2
        ;;
        --build-dir)
        BUILD_DIR=$2 ; shift 2
        ;;
        --doc-dir)
        DOC_DIR=$2 ; shift 2
        ;;
        --lib-dir)
        LIB_DIR=$2 ; shift 2
        ;;
        --installed-lib-dir)
        INSTALLED_LIB_DIR=$2 ; shift 2
        ;;
        --bin-dir)
        BIN_DIR=$2 ; shift 2
        ;;
        --)
        shift ; break
        ;;
        *)
        echo "Unknown option: $1"
        usage
        exit 1
        ;;
    esac
done

for var in PREFIX BUILD_DIR ; do
  if [ -z "$(eval "echo \$$var")" ]; then
    echo Missing param: $var
    usage
  fi
done

PREFIX=`echo $PREFIX | sed -e 's#/*$##'`
BUILD_DIR=`echo $BUILD_DIR | sed -e 's#/*$##'`

DOC_DIR=${DOC_DIR:-/usr/share/doc/hue}
CONF_DIR=${CONF_DIR:-/etc/hue}
LIB_DIR=${LIB_DIR:-/usr/lib/hue}
VAR_DIR=${VAR_DIR:-/var/lib/hue}
LOG_DIR=${LOG_DIR:-/var/log/hue}
HADOOP_DIR=${HADOOP_DIR:-/usr/lib/hadoop/lib}

# Adding local PyPi URL
f=~/.pydistutils.cfg
url='https://pypi.infra.cloudera.com/api/pypi/pypi-public/simple/'
echo "[easy_install]" >> "$f"
echo "index_url=$url" >> "$f"
export PYPI_MIRROR="$url"

#Needed to build the egg for cx_oracle
if [ -z $ORACLE_HOME ] ; then
    echo "Environment variable ORACLE_HOME not defined"
    exit 1
fi
if [ ! -d $ORACLE_HOME ] ; then
    echo "Directory $ORACLE_HOME ( environment variable ORACLE_HOME ) missing"
    exit 1
fi
BUNDLED_BUILD_DIR=$PREFIX/$LIB_DIR/build

# Install all the files 
(cd $BUILD_DIR ; PREFIX=`dirname $PREFIX/$LIB_DIR` make install)
rm -rf $PREFIX/$LIB_DIR/apps/logs

# Install plugins
install -d -m 0755 $PREFIX/$HADOOP_DIR
PLUGIN_PATH='desktop/libs/hadoop/java-lib'
PLUGIN_NAME=`basename $BUILD_DIR/$PLUGIN_PATH/*plugin*jar`
ln -fs ../../hue/$PLUGIN_PATH/$PLUGIN_NAME $PREFIX/$HADOOP_DIR/

# Remove app registry and then recreate it, but with just the "right" apps
rm -f $PREFIX/$LIB_DIR/app.reg
APPS="about filebrowser help proxy useradmin jobbrowser jobsub oozie metastore"
export DESKTOP_LOG_DIR=$BUILD_DIR
export DESKTOP_LOGLEVEL=WARN
export ROOT=$PREFIX/$LIB_DIR
for app in $APPS ; do
  (cd $PREFIX/$LIB_DIR ; ./build/env/bin/python tools/app_reg/app_reg.py --install apps/$app --relative-paths)
done
find $PREFIX/$LIB_DIR -iname \*.py[co]  -exec rm -f {} \;

# Making the resulting tree relocatable
(cd $PREFIX/$LIB_DIR ; bash tools/relocatable.sh)

# Move app.reg, hue.pth, and desktop.db to a var location
install -d -m 0755 $PREFIX/$VAR_DIR

mv $PREFIX/$LIB_DIR/app.reg $PREFIX/$VAR_DIR/
ln -s $VAR_DIR/app.reg $PREFIX/$LIB_DIR/

mv $PREFIX/$LIB_DIR/build/env/lib/python*/site-packages/hue.pth $PREFIX/$VAR_DIR/
ln -s $VAR_DIR/hue.pth $PREFIX/$LIB_DIR//build/env/lib/python*/site-packages/

mv $PREFIX/$LIB_DIR/desktop/desktop.db $PREFIX/$VAR_DIR
ln -s $VAR_DIR/desktop.db $PREFIX/$LIB_DIR/desktop/

# Install conf files
install -d -m 0755 $PREFIX/$CONF_DIR
mv -f $PREFIX/$LIB_DIR/desktop/conf $PREFIX/${CONF_DIR}/conf.empty
ln -fs $CONF_DIR/conf $PREFIX/$LIB_DIR/desktop/conf
sed -i -e '/\[\[database\]\]/a\
    engine=sqlite3\
    name=/var/lib/hue/desktop.db' $PREFIX/${CONF_DIR}/conf.empty/hue.ini
sed -i -e '/\[\[yarn_clusters\]\]/,+20s@## submit_to=False@submit_to=True@' \
    $PREFIX/${CONF_DIR}/conf.empty/hue.ini

# Relink logs subdirectory just in case
install -d -m 0755 $PREFIX/$LOG_DIR
rm -rf $PREFIX/$LIB_DIR/desktop/logs
ln -s $LOG_DIR $PREFIX/$LIB_DIR/desktop/logs

# Make binary scripts executables
chmod 755 $BUNDLED_BUILD_DIR/env/bin/*

# Preparing filtering command
SED_FILT="-e s|$PREFIX|| -e s|$BUILD_DIR|$LIB_DIR|"

# Fix broken symlinks
for sm in $BUNDLED_BUILD_DIR/env/lib*; do
  if [ -h ${sm} ] ; then
    SM_ORIG_DEST_FILE=`ls -l "${sm}" | sed -e 's/.*-> //' `
    SM_DEST_FILE=`echo $SM_ORIG_DEST_FILE | sed $SED_FILT`

    rm ${sm}
    ln -s ${SM_DEST_FILE} ${sm}
  fi
done

# Fix broken python scripts
ALL_PYTHON_BORKED=`find $PREFIX -iname "*.egg-link"`
HUE_BIN_SCRIPTS=$BUNDLED_BUILD_DIR/env/bin/*
HUE_EGG_SCRIPTS=$BUNDLED_BUILD_DIR/env/lib*/python*/site-packages/*/EGG-INFO/scripts/*
for file in $HUE_BIN_SCRIPTS $HUE_EGG_SCRIPTS $ALL_PTH_BORKED $ALL_REG_BORKED $ALL_PYTHON_BORKED ;
do
  if [ -f ${file} ]
  then
    sed -i $SED_FILT ${file}
  fi
done

# Remove bogus files
rm -fv `find $PREFIX -iname "build_log.txt"`

install -d ${PREFIX}/${DOC_DIR}
cp -r ${BUILD_DIR}/docs/* ${PREFIX}/${DOC_DIR}/

cp ${BUILD_DIR}/NOTICE.txt ${PREFIX}/${LIB_DIR}/

cp ${BUILD_DIR}/ext/thirdparty/README.md ${PREFIX}/${LIB_DIR}/ext/thirdparty/README.md

# Cloudera specific
install -d -m 0755 $PREFIX/$LIB_DIR/cloudera
cp $BUILD_DIR/cloudera/cdh_version.properties $PREFIX/$LIB_DIR/cloudera
install -d -m 0755 $PREFIX/$HADOOP_DIR/../cloudera
grep -v 'cloudera.pkg.name=' < $BUILD_DIR/cloudera/cdh_version.properties > $PREFIX/$HADOOP_DIR/../cloudera/cm_version.properties
echo 'cloudera.pkg.name=hue-common' >> $PREFIX/$HADOOP_DIR/../cloudera/cm_version.properties

