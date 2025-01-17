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
%define usr_bin /usr/bin
%define lib_oozie /usr/lib/oozie
%define man_dir /usr/share/man
%define conf_oozie %{_sysconfdir}/%{name}/conf
%define conf_oozie_dist %{conf_oozie}.dist
%define tomcat_conf_oozie %{_sysconfdir}/%{name}/tomcat-conf
%define data_oozie /var/lib/oozie

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0

# FIXME: brp-repack-jars uses unzip to expand jar files
# Unfortunately aspectjtools-1.6.5.jar pulled by ivy contains some files and directories without any read permission
# and make whole process to fail.
# So for now brp-repack-jars is being deactivated until this is fixed.
# See BIGTOP-294
%define __os_install_post \
    /usr/lib/rpm/redhat/brp-compress ; \
    /usr/lib/rpm/redhat/brp-strip-static-archive %{__strip} ; \
    /usr/lib/rpm/redhat/brp-strip-comment-note %{__strip} %{__objdump} ; \
    /usr/lib/rpm/brp-python-bytecompile ; \
    %{nil}

  %define doc_oozie %{_docdir}/oozie-%{oozie_version}
  %define initd_dir %{_sysconfdir}/rc.d/init.d
  %define alternatives_cmd alternatives
%else

# Only tested on openSUSE 11.4. le'ts update it for previous release when confirmed
%if 0%{suse_version} > 1130
%define suse_check \# Define an empty suse_check for compatibility with older sles
%endif

# SLES is more strict anc check all symlinks point to valid path
# But we do point to a hadoop jar which is not there at build time
# (but would be at install time).
# Since our package build system does not handle dependencies,
# these symlink checks are deactivated
%define __os_install_post \
    %{suse_check} ; \
    /usr/lib/rpm/brp-compress ; \
    %{nil}

  %define doc_oozie %{_docdir}/oozie
  %define initd_dir %{_sysconfdir}/rc.d
  %define alternatives_cmd update-alternatives
%endif

Name: oozie
Version: %{oozie_version}
Release: %{oozie_release}
Summary:  Oozie is a system that runs workflows of Hadoop jobs.
URL: http://incubator.apache.org/oozie/
Group: Development/Libraries
Buildroot: %{_topdir}/INSTALL/%{name}-%{version}
License: ASL 2.0
Source0: %{name}-%{oozie_patched_version}.tar.gz
Source1: do-component-build
Source2: install_oozie.sh
Source3: oozie.1
Source4: oozie-env.sh
Source5: oozie.init
Source6: catalina.properties
Source7: context.xml
Source8: hive.xml
Source9: catalina.properties.mr1
Source10: tomcat-deployment.sh
Source11: packaging_functions.sh
Source12: filter-requires.sh
Requires(pre): /usr/sbin/groupadd, /usr/sbin/useradd
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig, /sbin/service
Requires: oozie-client = %{version}, hadoop-client, bigtop-tomcat
Requires: avro-libs, parquet, zookeeper, hadoop, hadoop-hdfs, hadoop-mapreduce, hadoop-yarn, hive >= 0.12.0+cdh5.1.0, hive-hcatalog >= 0.12.0+cdh5.1.0, hive-webhcat >= 0.12.0+cdh5.1.0, hbase, sqoop, pig, kite, spark-core >= 1.3.0+cdh5.4.0
BuildArch: noarch

%define _use_internal_dependency_generator 0
%define __find_requires %{SOURCE12} 'osgi'

%description 
 Oozie is a system that runs workflows of Hadoop jobs.
 Oozie workflows are actions arranged in a control dependency DAG (Direct
 Acyclic Graph).

 Oozie coordinator functionality allows to start workflows at regular
 frequencies and when data becomes available in HDFS.
 
 An Oozie workflow may contain the following types of actions nodes:
 map-reduce, map-reduce streaming, map-reduce pipes, pig, file-system,
 sub-workflows, java, hive, sqoop and ssh (deprecated).
 
 Flow control operations within the workflow can be done using decision,
 fork and join nodes. Cycles in workflows are not supported.
 
 Actions and decisions can be parameterized with job properties, actions
 output (i.e. Hadoop counters) and HDFS  file information (file exists,
 file size, etc). Formal parameters are expressed in the workflow definition
 as ${VARIABLE NAME} variables.
 
 A Workflow application is an HDFS directory that contains the workflow
 definition (an XML file), all the necessary files to run all the actions:
 JAR files for Map/Reduce jobs, shells for streaming Map/Reduce jobs, native
 libraries, Pig scripts, and other resource files.
 
 Running workflow jobs is done via command line tools, a WebServices API 
 or a Java API.
 
 Monitoring the system and workflow jobs can be done via a web console, the
 command line tools, the WebServices API and the Java API.
 
 Oozie is a transactional system and it has built in automatic and manual
 retry capabilities.
 
 In case of workflow job failure, the workflow job can be rerun skipping
 previously completed actions, the workflow application can be patched before
 being rerun.

 
%package client
Version: %{version}
Release: %{release} 
Summary:  Client for Oozie Workflow Engine
URL: http://incubator.apache.org/oozie/
Group: Development/Libraries
License: ASL 2.0
BuildArch: noarch
Requires: bigtop-utils >= 0.7, hadoop

%description client
 Oozie client is a command line client utility that allows remote
 administration and monitoring of worflows. Using this client utility
 you can submit worflows, start/suspend/resume/kill workflows and
 find out their status at any instance. Apart from such operations,
 you can also change the status of the entire system, get vesion
 information. This client utility also allows you to validate
 any worflows before they are deployed to the Oozie server.


%prep
%setup -n oozie-%{oozie_patched_version}

%build
    mkdir -p distro/downloads
    cd src ; env DO_MAVEN_DEPLOY="" FULL_VERSION=%{oozie_patched_version} bash -x %{SOURCE1}

%install
%__rm -rf $RPM_BUILD_ROOT
    %{SOURCE2} --extra-dir=$RPM_SOURCE_DIR --build-dir=. --server-dir=$RPM_BUILD_ROOT --client-dir=$RPM_BUILD_ROOT --docs-dir=$RPM_BUILD_ROOT%{doc_oozie} --initd-dir=$RPM_BUILD_ROOT%{initd_dir} --conf-dir=$RPM_BUILD_ROOT%{conf_oozie_dist}

%__ln_s -f %{data_oozie}/ext-2.2 $RPM_BUILD_ROOT/%{lib_oozie}/webapps/oozie/ext-2.2
%__rm  -rf              $RPM_BUILD_ROOT/%{lib_oozie}/webapps/oozie/docs
%__ln_s -f %{doc_oozie} $RPM_BUILD_ROOT/%{lib_oozie}/webapps/oozie/docs

%__install -d -m 0755 $RPM_BUILD_ROOT/usr/bin

%__install -d  -m 0755  %{buildroot}/%{_localstatedir}/log/oozie
%__install -d  -m 0755  %{buildroot}/%{_localstatedir}/run/oozie

%pre
getent group oozie >/dev/null || /usr/sbin/groupadd -r oozie >/dev/null
getent passwd oozie >/dev/null || /usr/sbin/useradd --comment "Oozie User" --shell /bin/false -M -r -g oozie --home %{data_oozie} oozie >/dev/null

%post 
%{alternatives_cmd} --install %{tomcat_conf_oozie} %{name}-tomcat-deployment %{tomcat_conf_oozie}.http 30
%{alternatives_cmd} --install %{tomcat_conf_oozie} %{name}-tomcat-deployment %{tomcat_conf_oozie}.https 20
%{alternatives_cmd} --install %{tomcat_conf_oozie} %{name}-tomcat-deployment %{tomcat_conf_oozie}.http.mr1 15
%{alternatives_cmd} --install %{tomcat_conf_oozie} %{name}-tomcat-deployment %{tomcat_conf_oozie}.https.mr1 10
%{alternatives_cmd} --install %{conf_oozie} %{name}-conf %{conf_oozie_dist} 30
%{alternatives_cmd} --install %{lib_oozie}/oozie-sharelib oozie-sharelib %{lib_oozie}/oozie-sharelib-yarn 30
%{alternatives_cmd} --install %{lib_oozie}/oozie-sharelib oozie-sharelib %{lib_oozie}/oozie-sharelib-mr1 20

/sbin/chkconfig --add oozie 

%preun
if [ "$1" = 0 ]; then
  /sbin/service oozie stop > /dev/null
  /sbin/chkconfig --del oozie
  %{alternatives_cmd} --remove %{name}-tomcat-deployment %{tomcat_conf_oozie}.http || :
  %{alternatives_cmd} --remove %{name}-tomcat-deployment %{tomcat_conf_oozie}.https || :
  %{alternatives_cmd} --remove %{name}-tomcat-deployment %{tomcat_conf_oozie}.http.mr1 || :
  %{alternatives_cmd} --remove %{name}-tomcat-deployment %{tomcat_conf_oozie}.https.mr1 || :
  %{alternatives_cmd} --remove %{name}-conf %{conf_oozie_dist} || :
  %{alternatives_cmd} --remove oozie-sharelib %{lib_oozie}/oozie-sharelib-yarn || :
  %{alternatives_cmd} --remove oozie-sharelib %{lib_oozie}/oozie-sharelib-mr1 || :
fi

%postun
if [ $1 -ge 1 ]; then
  /sbin/service oozie condrestart > /dev/null
fi

%files 
%defattr(-,root,root)
%config(noreplace) %{conf_oozie_dist}
%config(noreplace) %{tomcat_conf_oozie}.*
# https://jira.cloudera.com/browse/CDH-30420
%attr(0750,oozie,oozie) %{tomcat_conf_oozie}.https/conf/server.xml
%attr(0750,oozie,oozie) %{tomcat_conf_oozie}.https/conf/ssl/ssl-server.xml
%attr(0750,oozie,oozie) %{tomcat_conf_oozie}.https/conf/ssl/server.xml
%attr(0750,oozie,oozie) %{tomcat_conf_oozie}.https.mr1/conf/server.xml
%attr(0750,oozie,oozie) %{tomcat_conf_oozie}.https.mr1/conf/ssl/ssl-server.xml
%attr(0750,oozie,oozie) %{tomcat_conf_oozie}.https.mr1/conf/ssl/server.xml
%attr(0750,oozie,oozie) %{tomcat_conf_oozie}.http.mr1/conf/server.xml
%attr(0750,oozie,oozie) %{tomcat_conf_oozie}.http.mr1/conf/ssl/ssl-server.xml
%attr(0750,oozie,oozie) %{tomcat_conf_oozie}.http.mr1/conf/ssl/server.xml
%attr(0750,oozie,oozie) %{tomcat_conf_oozie}.http/conf/server.xml
%attr(0750,oozie,oozie) %{tomcat_conf_oozie}.http/conf/ssl/ssl-server.xml
%attr(0750,oozie,oozie) %{tomcat_conf_oozie}.http/conf/ssl/server.xml

%{usr_bin}/oozie-setup
%{lib_oozie}/bin/oozie-setup.sh
%{lib_oozie}/bin/oozie-sys.sh
%{lib_oozie}/bin/oozie-env.sh
%{lib_oozie}/bin/oozied.sh
%{lib_oozie}/bin/ooziedb.sh
%{lib_oozie}/webapps
%{lib_oozie}/libtools
%{lib_oozie}/libserver
%{lib_oozie}/oozie-sharelib*
%{lib_oozie}/libext
%{lib_oozie}/tomcat-deployment.sh
%{lib_oozie}/cloudera/
%{initd_dir}/oozie
%defattr(-, oozie, oozie)
%dir %{_sysconfdir}/%{name}
%dir %{_localstatedir}/log/oozie
%dir %{_localstatedir}/run/oozie
%attr(0755,oozie,oozie) %{data_oozie}

%files client
%defattr(-,root,root)
%{usr_bin}/oozie
%dir %{lib_oozie}/bin
%{lib_oozie}/bin/oozie
%{lib_oozie}/lib
%doc %{doc_oozie}
%{man_dir}/man1/oozie.1.*
