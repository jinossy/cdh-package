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
%define etc_flume /etc/flume-ng/conf
%define bin_flume %{_bindir}
%define man_flume %{_mandir}
%define lib_flume /usr/lib/flume-ng
%define log_flume /var/log/flume-ng
%define run_flume /var/run/flume-ng
%define vlb_flume /var/lib/flume-ng

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

%define doc_flume %{_docdir}/flume-ng
%define alternatives_cmd update-alternatives
%global initd_dir %{_sysconfdir}/rc.d

%else

%define doc_flume %{_docdir}/flume-ng-%{flume_ng_version}
%define alternatives_cmd alternatives
%global initd_dir %{_sysconfdir}/rc.d/init.d

%endif



Name: flume-ng
Version: %{flume_ng_version}
Release: %{flume_ng_release}
Summary:  Flume is a reliable, scalable, and manageable distributed log collection application for collecting data such as logs and delivering it to data stores such as Hadoop's HDFS.
URL: http://incubator.apache.org/projects/flume.html
Group: Development/Libraries
Buildroot: %{_topdir}/INSTALL/%{name}-%{version}
BuildArch: noarch
License: ASL 2.0
Source0: %{name}-%{flume_ng_patched_version}.tar.gz
Source1: do-component-build
Source2: install_%{name}.sh
Source3: %{name}-agent.init
Source4: flume-ng-agent.default
Source5: packaging_functions.sh
Source6: filter-requires.sh
Requires: /usr/sbin/useradd
Requires: coreutils
Requires: hadoop-hdfs
Requires: bigtop-utils >= 0.7, hive-jdbc >= 1.1.0+cdh5.4.0, hive >= 1.1.0+cdh5.4.0
Requires: avro-libs, parquet, hadoop-mapreduce, hadoop-yarn, kite >= 0.10.0+cdh5.1.0, hadoop

%if  0%{?mgaversion}
Requires: bsh-utils
%else
Requires: sh-utils
%endif

%define _use_internal_dependency_generator 0
%define __find_requires %{SOURCE6} 'osgi'

%description 
Flume is a reliable, scalable, and manageable distributed data collection application for collecting data such as logs and delivering it to data stores such as Hadoop's HDFS.  It can efficiently collect, aggregate, and move large amounts of log data.  It has a simple, but flexible, architecture based on streaming data flows.  It is robust and fault tolerant with tunable reliability mechanisms and many failover and recovery mechanisms.  The system is centrally managed and allows for intelligent dynamic management. It uses a simple extensible data model that allows for online analytic applications.

%package agent
Summary: The flume agent daemon is a core element of flume's data path and is responsible for generating, processing, and delivering data.
Group: Development/Libraries
BuildArch: noarch
Requires: %{name} = %{version}-%{release}
Requires: /sbin/service
Requires(pre): %{name} = %{version}-%{release}
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig

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

%description agent
Flume is a reliable, scalable, and manageable distributed data collection application for collecting data such as logs and delivering it to data stores such as Hadoop's HDFS.  It can efficiently collect, aggregate, and move large amounts of log data.  It has a simple, but flexible, architecture based on streaming data flows.  It is robust and fault tolerant with tunable reliability mechanisms and many failover and recovery mechanisms.  The system is centrally managed and allows for intelligent dynamic management. It uses a simple extensible data model that allows for online analytic applications.


%package doc
Summary: Flume NG Documentation
Group: Documentation
BuildArch: noarch

%description doc
Documentation for Flume NG


%prep
%setup -n %{name}-%{flume_ng_patched_version}

%build
env FULL_VERSION=%{flume_ng_patched_version} bash %{SOURCE1}

%install
%__rm -rf $RPM_BUILD_ROOT
bash %{SOURCE2} \
          --build-dir=$PWD \
          --prefix=$RPM_BUILD_ROOT \
          --doc-dir=%{doc_flume} \
          --extra-dir=$RPM_SOURCE_DIR
%__install -d -m 0755 $RPM_BUILD_ROOT/%{initd_dir}/


# Install init script
init_file=$RPM_BUILD_ROOT/%{initd_dir}/%{name}-agent
%__cp %{SOURCE3} $init_file
chmod 755 $init_file


%__install -d -m 0755 $RPM_BUILD_ROOT/usr/bin

%__install -d -m 0755 $RPM_BUILD_ROOT/etc/default
%__cp %{SOURCE4} $RPM_BUILD_ROOT/etc/default/%{name}-agent


%pre
getent group flume >/dev/null || groupadd -r flume
getent passwd flume >/dev/null || useradd -c "Flume" -s /sbin/nologin -g flume -r -d %{vlb_flume} flume 2> /dev/null || :
%__install -d -o flume -g flume -m 0755 %{log_flume}
%__install -d -o flume -g flume -m 0755 %{run_flume}
%__install -d -o flume -g flume -m 0755 %{vlb_flume}

# Manage configuration symlink
%post
%{alternatives_cmd} --install %{etc_flume} %{name}-conf %{etc_flume}.empty 30

%preun
if [ "$1" = 0 ]; then
        %{alternatives_cmd} --remove %{name}-conf %{etc_flume}.empty || :
fi

%post agent
chkconfig --add %{name}-agent

%preun agent
if [ $1 = 0 ] ; then
        service %{name}-agent stop > /dev/null 2>&1
        chkconfig --del %{name}-agent
fi
%postun agent
if [ $1 -ge 1 ]; then
        service %{name}-agent condrestart >/dev/null 2>&1
fi


%files 
%defattr(644,root,root,755)
%dir %{etc_flume}.empty
%dir %{lib_flume}
%dir %{lib_flume}/bin
%dir %{lib_flume}/lib
%dir %{lib_flume}/tools
%dir %{lib_flume}/cloudera
%{lib_flume}/NOTICE
%{lib_flume}/LICENSE

%config(noreplace) %{etc_flume}.empty/*
%{etc_flume}.dist
%attr(0755,root,root) %{bin_flume}/flume-ng
%attr(0755,root,root) %{lib_flume}/bin/flume-ng
%{lib_flume}/cloudera/cdh_version.properties
%{lib_flume}/lib/*.jar
%{lib_flume}/tools/*.jar
%{lib_flume}/conf

%files agent
%attr(0755,root,root)/%{initd_dir}/%{name}-agent
%attr(0644,root,root) %config(noreplace) /etc/default/%{name}-agent

%files doc
%defattr(644,root,root,755)
%doc %{doc_flume}/

