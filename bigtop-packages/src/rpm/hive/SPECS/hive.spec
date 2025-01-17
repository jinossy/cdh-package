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
%define hadoop_username hadoop
%define etc_hive /etc/%{name}
%define config_hive %{etc_hive}/conf
%define conf_hcatalog %{_sysconfdir}/hive-hcatalog/conf
%define conf_webhcat  %{_sysconfdir}/hive-webhcat/conf
%define usr_lib_hive /usr/lib/%{name}
%define usr_lib_hcatalog /usr/lib/hive-hcatalog
%define var_lib_hive /var/lib/%{name}
%define var_lib_hcatalog /var/lib/%{name}-hcatalog
%define var_log_hcatalog /var/log/%{name}-hcatalog
%define usr_bin /usr/bin
%define hive_config_virtual hive_active_configuration
%define man_dir %{_mandir}
%define hive_services hive-server hive-metastore hive-server2 hive-webhcat-server
# After we run "ant package" we'll find the distribution here
%define hive_dist build/hive-%{hive_patched_version}

%if  %{!?suse_version:1}0

%define doc_hive %{_docdir}/%{name}-%{hive_version}
%define alternatives_cmd alternatives

%global initd_dir %{_sysconfdir}/rc.d/init.d

%else

# Only tested on openSUSE 11.4. le'ts update it for previous release when confirmed
%if 0%{suse_version} > 1130
%define suse_check \# Define an empty suse_check for compatibility with older sles
%endif

%define doc_hive %{_docdir}/%{name}
%define alternatives_cmd update-alternatives

%global initd_dir %{_sysconfdir}/rc.d

%define __os_install_post \
    %{suse_check} ; \
    /usr/lib/rpm/brp-compress ; \
    %{nil}

%endif


Name: hive
Version: %{hive_version}
Release: %{hive_release}
Summary: Hive is a data warehouse infrastructure built on top of Hadoop
License: ASL 2.0
URL: http://hive.apache.org/
Group: Development/Libraries
Buildroot: %{_topdir}/INSTALL/%{name}-%{version}
BuildArch: noarch
Source0: %{name}-%{hive_patched_version}.tar.gz
Source1: do-component-build
Source2: install_hive.sh
Source3: init.d.tmpl
Source4: hive-site.xml
Source5: hive-server.default
Source6: hive-metastore.default
Source7: hive.1
Source8: hive-site.xml
Source9: hive-server.svc
Source10: hive-metastore.svc
Source11: hive-server2.default
Source12: hive-server2.svc
Source13: hive-hcatalog.1
Source14: hive-webhcat-server.svc
Source15: hive-webhcat-server.default
Source16: packaging_functions.sh
Source17: filter-requires.sh
Requires: hadoop-client, bigtop-utils >= 0.7, zookeeper, %{name}-jdbc = %{version}-%{release}
Requires: avro-libs, parquet, sentry
Conflicts: hadoop-hive
Obsoletes: %{name}-webinterface

%define _use_internal_dependency_generator 0
%define __find_requires %{SOURCE17} 'osgi'

%description 
Hive is a data warehouse infrastructure built on top of Hadoop that provides tools to enable easy data summarization, adhoc querying and analysis of large datasets data stored in Hadoop files. It provides a mechanism to put structure on this data and it also provides a simple query language called Hive QL which is based on SQL and which enables users familiar with SQL to query this data. At the same time, this language also allows traditional map/reduce programmers to be able to plug in their custom mappers and reducers to do more sophisticated analysis which may not be supported by the built-in capabilities of the language. 

%package server
Summary: Provides a Hive Thrift service.
Group: System/Daemons
Requires: %{name} = %{version}-%{release}

%package server2
Summary: Provides a Hive Thrift service with improved concurrency support.
Group: System/Daemons
Requires: %{name} = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}

%if  %{?suse_version:1}0
# Required for init scripts
Requires: insserv
%else
# Required for init scripts
Requires: /lib/lsb/init-functions
%endif


%description server
This optional package hosts a Thrift server for Hive clients across a network to use.

%description server2
This optional package hosts a Thrift server for Hive clients across a network to use with improved concurrency support.

%package metastore
Summary: Shared metadata repository for Hive.
Group: System/Daemons
Requires: %{name} = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}

%if  %{?suse_version:1}0
# Required for init scripts
Requires: insserv
%else
# Required for init scripts
Requires: /lib/lsb/init-functions
%endif


%description metastore
This optional package hosts a metadata server for Hive clients across a network to use.


%package hbase
Summary: Provides integration between Apache HBase and Apache Hive
Group: Development/Libraries
Requires: hive = %{version}-%{release}, hbase

%description hbase
This optional package provides integration between Apache HBase and Apache Hive

%package jdbc
Summary: Provides libraries necessary to connect to Apache Hive via JDBC
Group: Development/Libraries
Requires: hadoop-client

%description jdbc
This package provides libraries necessary to connect to Apache Hive via JDBC

%package hcatalog
Summary: Apache Hcatalog is a data warehouse infrastructure built on top of Hadoop
Group: Development/Libraries
Requires: hadoop, hadoop-hdfs, hive, bigtop-utils >= 0.7
Requires: avro-libs

%description hcatalog
Apache HCatalog is a table and storage management service for data created using Apache Hadoop.
This includes:
    * Providing a shared schema and data type mechanism.
    * Providing a table abstraction so that users need not be concerned with where or how their data is stored.
    * Providing interoperability across data processing tools such as Pig, Map Reduce, Streaming, and Hive.


%package webhcat
Summary: WebHcat provides a REST-like web API for HCatalog and related Hadoop components.
Group: Development/Libraries
Requires: %{name}-hcatalog = %{version}-%{release}

%description webhcat
WebHcat provides a REST-like web API for HCatalog and related Hadoop components.

%package webhcat-server
Summary: Init scripts for WebHcat server
Group: System/Daemons
Requires: %{name}-webhcat = %{version}-%{release}

%if  %{?suse_version:1}0
# Required for init scripts
Requires: insserv
%endif

%if  0%{?mgaversion}
# Required for init scripts
Requires: initscripts
%endif

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0
%define __os_install_post \
    /usr/lib/rpm/redhat/brp-compress ; \
    /usr/lib/rpm/redhat/brp-strip-static-archive %{__strip} ; \
    /usr/lib/rpm/redhat/brp-strip-comment-note %{__strip} %{__objdump} ; \
    /usr/lib/rpm/brp-python-bytecompile ; \
    %{nil}
# Required for init scripts
Requires: /lib/lsb/init-functions
%endif

%description webhcat-server
Init scripts for WebHcat server.

%prep
%setup -n %{name}-%{hive_patched_version}

%build
env FULL_VERSION=%{hive_patched_version} bash %{SOURCE1}

#########################
#### INSTALL SECTION ####
#########################
%install
%__rm -rf $RPM_BUILD_ROOT

cp $RPM_SOURCE_DIR/hive.1 .
cp $RPM_SOURCE_DIR/hive-hcatalog.1 .
cp $RPM_SOURCE_DIR/hive-site.xml .
/bin/bash %{SOURCE2} \
  --prefix=$RPM_BUILD_ROOT \
  --build-dir=%{hive_dist} \
  --doc-dir=$RPM_BUILD_ROOT/%{doc_hive} \
  --extra-dir=$RPM_SOURCE_DIR

%__install -d -m 0755 $RPM_BUILD_ROOT/%{initd_dir}/
%__install -d -m 0755 $RPM_BUILD_ROOT/etc/default/
%__install -m 0644 $RPM_SOURCE_DIR/hive-metastore.default $RPM_BUILD_ROOT/etc/default/%{name}-metastore
%__install -m 0644 $RPM_SOURCE_DIR/hive-server.default $RPM_BUILD_ROOT/etc/default/%{name}-server
%__install -m 0644 $RPM_SOURCE_DIR/hive-server2.default $RPM_BUILD_ROOT/etc/default/%{name}-server2
%__install -m 0644 $RPM_SOURCE_DIR/hive-webhcat-server.default $RPM_BUILD_ROOT/etc/default/%{name}-webhcat-server

%__install -d -m 0755 $RPM_BUILD_ROOT/%{_localstatedir}/log/%{name}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{_localstatedir}/run/%{name}

# We need to get rid of jars that happen to be shipped in other CDH packages
%__rm -f $RPM_BUILD_ROOT/%{usr_lib_hive}/lib/hbase-common*.jar $RPM_BUILD_ROOT/%{usr_lib_hive}/lib/hbase-client*.jar \
$RPM_BUILD_ROOT/%{usr_lib_hive}/lib/hbase-server*.jar $RPM_BUILD_ROOT/%{usr_lib_hive}/lib/hbase-hadoop-compat*.jar \
$RPM_BUILD_ROOT/%{usr_lib_hive}/lib/hbase-hadoop2-compat*.jar $RPM_BUILD_ROOT/%{usr_lib_hive}/lib/hbase-protocol*.jar \
$RPM_BUILD_ROOT/%{usr_lib_hive}/lib/htrace-core*.jar
%__ln_s  /usr/lib/hbase/hbase-common.jar /usr/lib/hbase/hbase-client.jar /usr/lib/hbase/hbase-server.jar \
/usr/lib/hbase/hbase-hadoop-compat.jar /usr/lib/hbase/hbase-hadoop2-compat.jar /usr/lib/hbase/hbase-protocol.jar \
/usr/lib/hbase/lib/htrace-core.jar $RPM_BUILD_ROOT/%{usr_lib_hive}/lib/

for service in %{hive_services}
do
    # Install init script
    init_file=$RPM_BUILD_ROOT/%{initd_dir}/${service}
    bash $RPM_SOURCE_DIR/init.d.tmpl $RPM_SOURCE_DIR/${service}.svc rpm $init_file
done

%pre
getent group hive >/dev/null || groupadd -r hive
getent passwd hive >/dev/null || useradd -c "Hive" -s /sbin/nologin -g hive -r -d %{var_lib_hive} hive 2> /dev/null || :

# Manage configuration symlink
%post

# Install config alternatives
%{alternatives_cmd} --install %{config_hive} %{name}-conf %{etc_hive}/conf.dist 30

# Upgrade
if [ "$1" -gt 1 ]; then
  old_metastore="${var_lib_hive}/metastore/\${user.name}_db"
  new_metastore="${var_lib_hive}/metastore/metastore_db"
  if [ -d $old_metastore ]; then
    mv $old_metastore $new_metastore || echo "Failed to automatically rename old metastore. Make sure to resolve this before running Hive."
  fi
fi

%preun
if [ "$1" = 0 ]; then
  %{alternatives_cmd} --remove %{name}-conf %{etc_hive}/conf.dist || :
fi


%post hcatalog
%{alternatives_cmd} --install %{conf_hcatalog} hive-hcatalog-conf %{conf_hcatalog}.dist 30

%preun hcatalog
if [ "$1" = 0 ]; then
        %{alternatives_cmd} --remove hive-hcatalog-conf %{conf_hcatalog}.dist || :
fi

%post webhcat
%{alternatives_cmd} --install %{conf_webhcat} hive-webhcat-conf %{conf_webhcat}.dist 30

%preun webhcat
if [ "$1" = 0 ]; then
        %{alternatives_cmd} --remove hive-webhcat-conf %{conf_webhcat}.dist || :
fi

#######################
#### FILES SECTION ####
#######################
%files
%attr(1777,hive,hive) %dir %{var_lib_hive}/metastore
%defattr(-,root,root,755)
%config(noreplace) %{etc_hive}/conf.dist
%{usr_lib_hive}
%{usr_bin}/hive
%{usr_bin}/beeline
%{usr_bin}/hiveserver2
%dir %{var_lib_hive}
%attr(-,hive,hive) %{var_lib_hive}
%attr(0755,hive,hive) %dir %{_localstatedir}/log/%{name}
%attr(0755,hive,hive) %dir %{_localstatedir}/run/%{name}
%doc %{doc_hive}
%{man_dir}/man1/hive.1.*
%exclude %{usr_lib_hive}/lib/hbase-common.jar
%exclude %{usr_lib_hive}/lib/hbase-client.jar
%exclude %{usr_lib_hive}/lib/hbase-server.jar
%exclude %{usr_lib_hive}/lib/hbase-hadoop-compat.jar
%exclude %{usr_lib_hive}/lib/hbase-hadoop2-compat.jar
%exclude %{usr_lib_hive}/lib/hbase-protocol.jar
%exclude %{usr_lib_hive}/lib/hive-jdbc*.jar
%exclude %{usr_lib_hive}/lib/hive-metastore*.jar
%exclude %{usr_lib_hive}/lib/hive-serde*.jar
%exclude %{usr_lib_hive}/lib/hive-exec*.jar
%exclude %{usr_lib_hive}/lib/libthrift-*.jar
%exclude %{usr_lib_hive}/lib/hive-service*.jar
%exclude %{usr_lib_hive}/lib/libfb303-*.jar
%exclude %{usr_lib_hive}/lib/log4j-*.jar
%exclude %{usr_lib_hive}/lib/commons-logging-*.jar
%exclude %{usr_lib_hive}/lib/htrace-core.jar

%files hbase
%defattr(-,root,root,755)
%{usr_lib_hive}/lib/hbase-common.jar
%{usr_lib_hive}/lib/hbase-client.jar
%{usr_lib_hive}/lib/hbase-server.jar
%{usr_lib_hive}/lib/hbase-hadoop-compat.jar
%{usr_lib_hive}/lib/hbase-hadoop2-compat.jar
%{usr_lib_hive}/lib/hbase-protocol.jar
%{usr_lib_hive}/lib/htrace-core.jar

%files jdbc
%defattr(-,root,root,755)
%{usr_lib_hive}/lib/hive-jdbc*.jar
%{usr_lib_hive}/lib/hive-metastore*.jar
%{usr_lib_hive}/lib/hive-serde*.jar
%{usr_lib_hive}/lib/hive-exec*.jar
%{usr_lib_hive}/lib/libthrift-*.jar
%{usr_lib_hive}/lib/hive-service*.jar
%{usr_lib_hive}/lib/libfb303-*.jar
%{usr_lib_hive}/lib/log4j-*.jar
%{usr_lib_hive}/lib/commons-logging-*.jar

%files hcatalog
%defattr(-,root,root,755)
%config(noreplace) %attr(755,root,root) %{conf_hcatalog}.dist
%attr(0775,hive,hive) %{var_lib_hcatalog}
%attr(0775,hive,hive) %{var_log_hcatalog}
%dir %{usr_lib_hcatalog}
%{usr_lib_hcatalog}/bin
%{usr_lib_hcatalog}/cloudera
%{usr_lib_hcatalog}/etc/hcatalog
%{usr_lib_hcatalog}/libexec
%{usr_lib_hcatalog}/share/hcatalog
%{usr_lib_hcatalog}/sbin/update-hcatalog-env.sh
%{usr_lib_hcatalog}/sbin/hcat*
%{usr_bin}/hcat
%{man_dir}/man1/hive-hcatalog.1.*

%files webhcat
%defattr(-,root,root,755)
%config(noreplace) %attr(755,root,root) %{conf_webhcat}.dist
%{usr_lib_hcatalog}/share/webhcat
%{usr_lib_hcatalog}/etc/webhcat
%{usr_lib_hcatalog}/sbin/webhcat*

%define service_macro() \
%files %1 \
%attr(0755,root,root)/%{initd_dir}/%{name}-%1 \
%config(noreplace) /etc/default/%{name}-%1 \
%post %1 \
chkconfig --add %{name}-%1 \
\
%preun %1 \
if [ "$1" = 0 ] ; then \
        service %{name}-%1 stop > /dev/null \
        chkconfig --del %{name}-%1 \
fi \
%postun %1 \
if [ $1 -ge 1 ]; then \
	service %{name}-%1 condrestart >/dev/null 2>&1 || : \
fi
%service_macro server
%service_macro server2
%service_macro metastore
%service_macro webhcat-server
