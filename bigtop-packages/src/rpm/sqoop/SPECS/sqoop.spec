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
%define lib_sqoop /usr/lib/sqoop
%define conf_sqoop %{_sysconfdir}/%{name}/conf
%define conf_sqoop_dist %{conf_sqoop}.dist

# Disabling the following scripts from running:
# symbol stripping - not relevant here.
# jar repacking - to save time.
# byte-compiling python code - not relevant here.
# brp-compress - not relevant here.
#              - This compresses man and info pages under
#                 ./usr/man/man* ./usr/man/*/man* ./usr/info \
#                 ./usr/share/man/man* ./usr/share/man/*/man* ./usr/share/info \
#                 ./usr/kerberos/man ./usr/X11R6/man/man* ./usr/lib/perl5/man/man* \
#                 ./usr/share/doc/*/man/man* ./usr/lib/*/man/man*
%define __os_install_post %{nil}

%if  %{?suse_version:1}0

%define doc_sqoop %{_docdir}/sqoop
%global initd_dir %{_sysconfdir}/rc.d
%define alternatives_cmd update-alternatives

%else

%define doc_sqoop %{_docdir}/sqoop-%{sqoop_version}
%global initd_dir %{_sysconfdir}/rc.d/init.d
%define alternatives_cmd alternatives

%endif


Name: sqoop
Version: %{sqoop_version}
Release: %{sqoop_release}
Summary:   Sqoop allows easy imports and exports of data sets between databases and the Hadoop Distributed File System (HDFS).
URL: http://incubator.apache.org/sqoop/
Group: Development/Libraries
Buildroot: %{_topdir}/INSTALL/%{name}-%{version}
License: ASL 2.0
Source0: %{name}-%{sqoop_patched_version}.tar.gz
Source1: do-component-build
Source2: install_%{name}.sh
Source3: sqoop-metastore.sh
Source4: sqoop-metastore.sh.suse
Source5: packaging_functions.sh
Buildarch: noarch
BuildRequires: asciidoc, xmlto
Requires: hadoop-client, bigtop-utils >= 0.7
Requires: avro-libs, parquet, kite

%description 
Sqoop allows easy imports and exports of data sets between databases and the Hadoop Distributed File System (HDFS).

%package metastore
Summary: Shared metadata repository for Sqoop.
URL: http://incubator.apache.org/sqoop/
Group: System/Daemons
Provides: sqoop-metastore
Requires: sqoop = %{version}-%{release} 

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
# Required for init scripts
Requires: /lib/lsb/init-functions
%endif


%description metastore
Shared metadata repository for Sqoop. This optional package hosts a metadata
server for Sqoop clients across a network to use.

%prep
%setup -n sqoop-%{sqoop_patched_version}

%build
env FULL_VERSION=%{sqoop_patched_version} bash %{SOURCE1}

%install
%__rm -rf $RPM_BUILD_ROOT
bash %{SOURCE2} \
          --build-dir=build/sqoop-%{sqoop_patched_version} \
          --conf-dir=%{conf_sqoop_dist} \
          --doc-dir=%{doc_sqoop} \
          --prefix=$RPM_BUILD_ROOT \
          --extra-dir=$RPM_SOURCE_DIR

%__install -d -m 0755 $RPM_BUILD_ROOT/usr/bin
%__install -d -m 0755 $RPM_BUILD_ROOT/%{initd_dir}/

%__rm -f $RPM_BUILD_ROOT/%{lib_sqoop}/lib/hadoop-mrunit*.jar

%if  %{?suse_version:1}0
orig_init_file=$RPM_SOURCE_DIR/sqoop-metastore.sh.suse
%else
orig_init_file=$RPM_SOURCE_DIR/sqoop-metastore.sh
%endif

init_file=$RPM_BUILD_ROOT/%{initd_dir}/sqoop-metastore
%__cp $orig_init_file $init_file
chmod 0755 $init_file

%__install -d  -m 0755 $RPM_BUILD_ROOT/var/log/sqoop

%pre
getent group sqoop >/dev/null || groupadd -r sqoop
getent passwd sqoop > /dev/null || useradd -c "Sqoop" -s /sbin/nologin \
	-g sqoop -r -d /var/lib/sqoop sqoop 2> /dev/null || :

%post
%{alternatives_cmd} --install %{conf_sqoop} %{name}-conf %{conf_sqoop_dist} 30

%preun
if [ "$1" = 0 ]; then
  %{alternatives_cmd} --remove %{name}-conf %{conf_sqoop_dist} || :
fi

%post metastore
chkconfig --add sqoop-metastore

%preun metastore
if [ $1 = 0 ] ; then
  service sqoop-metastore stop > /dev/null 2>&1
  chkconfig --del sqoop-metastore
fi

%postun metastore
if [ $1 -ge 1 ]; then
  service sqoop-metastore condrestart > /dev/null 2>&1
fi

%files metastore
%attr(0755,root,root) %{initd_dir}/sqoop-metastore
%attr(0755,sqoop,sqoop) /var/log/sqoop

# Files for main package
%files 
%defattr(0755,root,root)
%{lib_sqoop}
%attr(0644,root,root) %{lib_sqoop}/*.jar
%config(noreplace) %{conf_sqoop_dist}
%{_bindir}/sqoop
%{_bindir}/sqoop-codegen
%{_bindir}/sqoop-create-hive-table
%{_bindir}/sqoop-eval
%{_bindir}/sqoop-export
%{_bindir}/sqoop-help
%{_bindir}/sqoop-import
%{_bindir}/sqoop-import-all-tables
%{_bindir}/sqoop-job
%{_bindir}/sqoop-list-databases   
%{_bindir}/sqoop-list-tables
%{_bindir}/sqoop-metastore
%{_bindir}/sqoop-version
%{_bindir}/sqoop-merge
%attr(0755,sqoop,sqoop) /var/lib/sqoop

%defattr(0644,root,root,0755)
%{_mandir}/man1/*
%doc %{doc_sqoop}
