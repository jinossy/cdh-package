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
#
# Hadoop RPM spec file
#

# FIXME: we need to disable a more strict checks on native files for now,
# since Hadoop build system makes it difficult to pass the kind of flags
# that would make newer RPM debuginfo generation scripts happy.
%undefine _missing_build_ids_terminate_build

%define hadoop_name hadoop
%define etc_hadoop /etc/%{name}
%define etc_yarn /etc/yarn
%define etc_httpfs /etc/%{name}-httpfs
%define etc_kms /etc/%{name}-kms
%define config_hadoop %{etc_hadoop}/conf
%define config_yarn %{etc_yarn}/conf
%define config_httpfs %{etc_httpfs}/conf
%define config_kms %{etc_kms}/conf
%define tomcat_deployment_httpfs %{etc_httpfs}/tomcat-conf
%define tomcat_deployment_kms %{etc_kms}/tomcat-conf
%define lib_hadoop_dirname /usr/lib
%define lib_hadoop %{lib_hadoop_dirname}/%{name}
%define lib_httpfs %{lib_hadoop_dirname}/%{name}-httpfs
%define lib_kms %{lib_hadoop_dirname}/%{name}-kms
%define lib_hdfs %{lib_hadoop_dirname}/%{name}-hdfs
%define lib_yarn %{lib_hadoop_dirname}/%{name}-yarn
%define lib_mapreduce %{lib_hadoop_dirname}/%{name}-mapreduce
%define lib_mapreduce_mr1 %{lib_hadoop_dirname}/%{name}-0.20-mapreduce
%define log_hadoop_dirname /var/log
%define log_hadoop %{log_hadoop_dirname}/%{name}
%define log_yarn %{log_hadoop_dirname}/%{name}-yarn
%define log_hdfs %{log_hadoop_dirname}/%{name}-hdfs
%define log_httpfs %{log_hadoop_dirname}/%{name}-httpfs
%define log_kms %{log_hadoop_dirname}/%{name}-kms
%define log_mapreduce %{log_hadoop_dirname}/%{name}-mapreduce
%define run_hadoop_dirname /var/run
%define run_hadoop %{run_hadoop_dirname}/hadoop
%define run_yarn %{run_hadoop_dirname}/%{name}-yarn
%define run_hdfs %{run_hadoop_dirname}/%{name}-hdfs
%define run_httpfs %{run_hadoop_dirname}/%{name}-httpfs
%define run_kms %{run_hadoop_dirname}/%{name}-https
%define run_mapreduce %{run_hadoop_dirname}/%{name}-mapreduce
%define state_hadoop_dirname /var/lib
%define state_hadoop %{state_hadoop_dirname}/hadoop
%define state_yarn %{state_hadoop_dirname}/%{name}-yarn
%define state_hdfs %{state_hadoop_dirname}/%{name}-hdfs
%define state_mapreduce %{state_hadoop_dirname}/%{name}-mapreduce
%define state_httpfs %{state_hadoop_dirname}/%{name}-httpfs
%define state_kms %{state_hadoop_dirname}/%{name}-kms
%define bin_hadoop %{_bindir}
%define man_hadoop %{_mandir}
%define doc_hadoop %{_docdir}/%{name}-%{hadoop_version}
%define doc_hadoop_mr1 %{_docdir}/hadoop-0.20-mapreduce
%define httpfs_services httpfs
%define kms_services kms-server
%define mapreduce_services mapreduce-historyserver
%define mapreduce_mr1_services 0.20-mapreduce-jobtracker 0.20-mapreduce-tasktracker 0.20-mapreduce-zkfc 0.20-mapreduce-jobtrackerha
%define hdfs_services hdfs-namenode hdfs-secondarynamenode hdfs-datanode hdfs-zkfc hdfs-journalnode hdfs-nfs3
%define yarn_services yarn-resourcemanager yarn-nodemanager yarn-proxyserver
%define hadoop_services %{hdfs_services} %{mapreduce_services} %{yarn_services} %{httpfs_services} %{kms_services} %{mapreduce_mr1_services}
# Hadoop outputs built binaries into %{hadoop_build}
%define hadoop_build_path build
%define static_images_dir src/webapps/static/images
%define libexecdir /usr/lib

%ifarch i386 i686
%global hadoop_arch Linux-i386-32
%global requires_lib_tag %{nil}
%endif
%ifarch amd64 x86_64
%global hadoop_arch Linux-amd64-64
%global requires_lib_tag ()(64bit)
%endif

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

%define netcat_package nc
%define doc_hadoop %{_docdir}/%{name}-%{hadoop_version}
%define alternatives_cmd alternatives
%global initd_dir %{_sysconfdir}/rc.d/init.d
%endif


%if  %{?suse_version:1}0

# Only tested on openSUSE 11.4. le'ts update it for previous release when confirmed
%if 0%{suse_version} > 1130
%define suse_check \# Define an empty suse_check for compatibility with older sles
%endif

# Deactivating symlinks checks
%define __os_install_post \
    %{suse_check} ; \
    /usr/lib/rpm/brp-compress ; \
    %{nil}

%define netcat_package netcat-openbsd
%define doc_hadoop %{_docdir}/%{name}
%define alternatives_cmd update-alternatives
%global initd_dir %{_sysconfdir}/rc.d
%endif

%if  0%{?mgaversion}
%define netcat_package netcat-openbsd
%define doc_hadoop %{_docdir}/%{name}-%{hadoop_version}
%define alternatives_cmd update-alternatives
%global initd_dir %{_sysconfdir}/rc.d/init.d
%endif


# Even though we split the RPM into arch and noarch, it still will build and install
# the entirety of hadoop. Defining this tells RPM not to fail the build
# when it notices that we didn't package most of the installed files.
%define _unpackaged_files_terminate_build 0

# RPM searches perl files for dependancies and this breaks for non packaged perl lib
# like thrift so disable this
%define _use_internal_dependency_generator 0

Name: %{hadoop_name}
Version: %{hadoop_version}
Release: %{hadoop_release}
Summary: Hadoop is a software platform for processing vast amounts of data
License: ASL 2.0
URL: http://hadoop.apache.org/core/
Group: Development/Libraries
Source0: %{name}-%{hadoop_patched_version}.tar.gz
Source1: do-component-build
Source2: install_%{name}.sh
Source3: hadoop.default
Source4: hadoop-fuse.default
Source5: httpfs.default
Source6: hadoop.1
Source7: hadoop-fuse-dfs.1
Source8: hdfs.conf
Source9: yarn.conf
Source10: mapreduce.conf
Source11: init.d.tmpl 
Source12: hadoop-hdfs-namenode.svc
Source13: hadoop-hdfs-datanode.svc
Source14: hadoop-hdfs-secondarynamenode.svc
Source15: hadoop-mapreduce-historyserver.svc
Source16: hadoop-yarn-resourcemanager.svc
Source17: hadoop-yarn-nodemanager.svc
Source18: hadoop-httpfs.svc
Source19: mapreduce.default
Source20: hdfs.default
Source21: yarn.default
Source22: hadoop-layout.sh
Source23: hadoop-hdfs-zkfc.svc
Source24: hadoop-hdfs-journalnode.svc
Source25: hadoop-0.20-mapreduce-jobtracker.svc
Source26: hadoop-0.20-mapreduce-tasktracker.svc
Source27: hadoop-0.20-mapreduce-zkfc.svc
Source28: hadoop-0.20-mapreduce-jobtrackerha.svc
Source29: %{name}-bigtop-packaging.tar.gz
Source30: 0.20.default
Source31: hadoop-hdfs-nfs3.svc
Source32: httpfs-tomcat-deployment.sh
Source33: packaging_functions.sh
Source34: yarn.1
Source35: hdfs.1
Source36: mapred.1
Source37: hadoop-kms-server.svc
Source38: kms.default
Source39: kms-tomcat-deployment.sh
Source40: filter-provides.sh
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id} -u -n)
BuildRequires: fuse-devel, fuse, cmake
Requires: coreutils, /usr/sbin/useradd, /usr/sbin/usermod, /sbin/chkconfig, /sbin/service, bigtop-utils >= 0.7, zookeeper >= 3.4.0
Requires: psmisc, %{netcat_package}
Requires: avro-libs, parquet
Conflicts: hadoop-0.20
# Sadly, Sun/Oracle JDK in RPM form doesn't provide libjvm.so, which means we have
# to set AutoReq to no in order to minimize confusion. Not ideal, but seems to work.
# I wish there was a way to disable just one auto dependency (libjvm.so)
AutoReq: no

%define _use_internal_dependency_generator 0
%define __find_provides %{SOURCE40} 'libnativetask\\|libsnappy'

%if  %{?suse_version:1}0
BuildRequires: pkg-config, libfuse2, libopenssl-devel, gcc-c++
# Required for init scripts
Requires: sh-utils, insserv
%endif

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0
BuildRequires: pkgconfig, fuse-libs, redhat-rpm-config, lzo-devel, openssl-devel, libtool, snappy-devel
# Required for init scripts
Requires: sh-utils, /lib/lsb/init-functions
%endif

%if  0%{?mgaversion}
BuildRequires: pkgconfig, libfuse-devel, libfuse2 , libopenssl-devel, gcc-c++, liblzo-devel, zlib-devel, libtool, automake, autoconf, make
Requires: chkconfig, xinetd-simple-services, zlib, initscripts
%endif


%description
Hadoop is a software platform that lets one easily write and
run applications that process vast amounts of data.

Here's what makes Hadoop especially useful:
* Scalable: Hadoop can reliably store and process petabytes.
* Economical: It distributes the data and processing across clusters
              of commonly available computers. These clusters can number
              into the thousands of nodes.
* Efficient: By distributing the data, Hadoop can process it in parallel
             on the nodes where the data is located. This makes it
             extremely rapid.
* Reliable: Hadoop automatically maintains multiple copies of data and
            automatically redeploys computing tasks based on failures.

Hadoop implements MapReduce, using the Hadoop Distributed File System (HDFS).
MapReduce divides applications into many small blocks of work. HDFS creates
multiple replicas of data blocks for reliability, placing them on compute
nodes around the cluster. MapReduce can then process the data where it is
located.

%package hdfs
Summary: The Hadoop Distributed File System
Group: System/Daemons
Requires(pre): %{name} = %{version}-%{release}
Requires: %{name} = %{version}-%{release}, bigtop-jsvc
# Workaround for 4.0 to 4.X upgrade (CDH-7856) (upgrades from 4.1 onwards are fine)
Requires: libhadoop.so.1.0.0%{requires_lib_tag}

%description hdfs
Hadoop Distributed File System (HDFS) is the primary storage system used by
Hadoop applications. HDFS creates multiple replicas of data blocks and
distributes them on cluster hosts to enable reliable and extremely rapid
computations.

%package yarn
Summary: The Hadoop NextGen MapReduce (YARN)
Group: System/Daemons
Requires(pre): %{name} = %{version}-%{release}
Requires: %{name} = %{version}-%{release}
# Workaround for 4.0 to 4.X upgrade (CDH-7856) (upgrades from 4.1 onwards are fine)
Requires: libhadoop.so.1.0.0%{requires_lib_tag}
Requires: avro-libs, zookeeper

%description yarn
YARN (Hadoop NextGen MapReduce) is a general purpose data-computation framework.
YARN splits up the functionalities of JobTracker, resource management, 
job scheduling, and job monitoring into separate daemons called 
ResourceManager and NodeManager.

ResourceManager is the ultimate authority that arbitrates resources 
among all applications in the system. NodeManager is a per-host slave
that manages allocation of computational resources on a single host. 
Both daemons work in support of ApplicationMaster (AM).

ApplicationMaster is a framework-specific library that negotiates resources 
from ResourceManager and works with NodeManager(s) to execute and monitor 
the tasks.

%package mapreduce
Summary: The Hadoop MapReduce (MRv2)
Group: System/Daemons
Requires(pre): %{name} = %{version}-%{release}
Requires: %{name}-yarn = %{version}-%{release}, %{name} = %{version}-%{release}
Requires: avro-libs, zookeeper

%description mapreduce
Hadoop MapReduce is a programming model and software framework for
writing applications that rapidly process vast amounts of data
in parallel on large clusters of hosts.

%package 0.20-mapreduce
Summary: Hadoop is a software platform for processing vast amounts of data
Group: System/Daemons
Requires(pre): %{name} = %{version}-%{release}
Requires: %{name} = %{version}-%{release}, %{name}-hdfs = %{version}-%{release}
Requires: avro-libs, zookeeper

%description 0.20-mapreduce
Hadoop is a software platform that lets one easily write and
run applications that process vast amounts of data.

Here's what makes Hadoop especially useful:
* Scalable: Hadoop can reliably store and process petabytes.
* Economical: It distributes the data and processing across clusters
              of commonly available computers. These clusters can number
              into the thousands of nodes.
* Efficient: By distributing the data, Hadoop can process it in parallel
             on the nodes where the data is located. This makes it
             extremely rapid.
* Reliable: Hadoop automatically maintains multiple copies of data and
            automatically redeploys computing tasks based on failures.

Hadoop implements MapReduce, using the Hadoop Distributed File System (HDFS).
MapReduce divides applications into many small blocks of work. HDFS creates
multiple replicas of data blocks for reliability, placing them on compute
nodes around the cluster. MapReduce can then process the data where it is
located.

%package hdfs-namenode
Summary: The Hadoop namenode manages the block locations of HDFS files
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-hdfs = %{version}-%{release}

%description hdfs-namenode
The Hadoop Distributed Filesystem (HDFS) requires one unique server, the
namenode, which manages the block locations of files on the filesystem.


%package hdfs-secondarynamenode
Summary: Hadoop Secondary namenode
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-hdfs = %{version}-%{release}

%description hdfs-secondarynamenode
The Secondary Name Node periodically compacts the Name Node EditLog
into a checkpoint.  This compaction ensures that Name Node restarts
do not incur unnecessary downtime.

%package hdfs-zkfc
Summary: Hadoop HDFS failover controller
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-hdfs = %{version}-%{release}

%description hdfs-zkfc
The Hadoop HDFS failover controller is a ZooKeeper client which also
monitors and manages the state of the NameNode. Each of the machines
which runs a NameNode also runs a ZKFC, and that ZKFC is responsible
for: Health monitoring, ZooKeeper session management, ZooKeeper-based
election.

%package hdfs-journalnode
Summary: Hadoop HDFS JournalNode
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}

%description hdfs-journalnode
The HDFS JournalNode is responsible for persisting NameNode edit logs. 
In a typical deployment the JournalNode daemon runs on at least three 
separate machines in the cluster.

%package hdfs-datanode
Summary: Hadoop Data Node
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-hdfs = %{version}-%{release}

%description hdfs-datanode
The Data Nodes in the Hadoop Cluster are responsible for serving up
blocks of data over the network to Hadoop Distributed Filesystem
(HDFS) clients.

%package kms
Summary: KMS for Hadoop
Group: Development/Libraries
Requires: %{name}-client = %{version}-%{release}, bigtop-tomcat

%description kms
Hadoop KMS is a cryptographic Key Management Server based on Hadoop KeyProvider API.

%package kms-server
Summary: KMS for Hadoop
Group: System/Daemons
Requires: %{name}-kms = %{version}-%{release}

%description kms-server
Bundles KMS init scripts.


%package hdfs-nfs3
Summary: Hadoop HDFS NFS v3 gateway service
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}, portmap
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-hdfs = %{version}-%{release}

%description hdfs-nfs3
Hadoop HDFS NFS v3 gateway service

%package httpfs
Summary: HTTPFS for Hadoop
Group: System/Daemons
Requires: %{name}-hdfs = %{version}-%{release}, bigtop-tomcat
Requires: avro-libs, zookeeper
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-hdfs = %{version}-%{release}

%description httpfs
The server providing HTTP REST API support for the complete FileSystem/FileContext
interface in HDFS.

%package yarn-resourcemanager
Summary: Yarn Resource Manager
Group: System/Daemons
Requires: %{name}-yarn = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-yarn = %{version}-%{release}

%description yarn-resourcemanager
The resource manager manages the global assignment of compute resources to applications

%package yarn-nodemanager
Summary: Yarn Node Manager
Group: System/Daemons
Requires: %{name}-yarn = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-yarn = %{version}-%{release}

%description yarn-nodemanager
The NodeManager is the per-machine framework agent who is responsible for
containers, monitoring their resource usage (cpu, memory, disk, network) and
reporting the same to the ResourceManager/Scheduler.

%package yarn-proxyserver
Summary: Yarn Web Proxy
Group: System/Daemons
Requires: %{name}-yarn = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-yarn = %{version}-%{release}

%description yarn-proxyserver
The web proxy server sits in front of the YARN application master web UI.

%package mapreduce-historyserver
Summary: MapReduce History Server
Group: System/Daemons
Requires: %{name}-mapreduce = %{version}-%{release}
Requires: %{name}-hdfs = %{version}-%{release}
Requires(pre): %{name} = %{version}-%{release}
Requires(pre): %{name}-mapreduce = %{version}-%{release}

%description mapreduce-historyserver
The History server keeps records of the different activities being performed on a Apache Hadoop cluster

%package 0.20-mapreduce-jobtracker
Summary: Hadoop JobTracker
Group: System/Daemons
Requires: %{name}-0.20-mapreduce = %{version}-%{release}
Conflicts: hadoop-0.20-jobtracker, %{name}-jobtrackerha

%description 0.20-mapreduce-jobtracker
The jobtracker is a central service which is responsible for managing
the tasktracker services running on all nodes in a Hadoop Cluster.
The jobtracker allocates work to the tasktracker nearest to the data
with an available work slot.

%package 0.20-mapreduce-tasktracker
Summary: Hadoop Task Tracker
Group: System/Daemons
Requires: %{name}-0.20-mapreduce = %{version}-%{release}
Conflicts: hadoop-0.20-tasktracker

%description 0.20-mapreduce-tasktracker
The tasktracker has a fixed number of work slots.  The jobtracker
assigns MapReduce work to the tasktracker that is nearest the data
with an available work slot.

%package 0.20-conf-pseudo
Summary: Hadoop installation in pseudo-distributed mode with MRv1
Group: System/Daemons
Requires: %{name} = %{version}-%{release}, %{name}-hdfs-namenode = %{version}-%{release}, %{name}-hdfs-datanode = %{version}-%{release}, %{name}-hdfs-secondarynamenode = %{version}-%{release}, %{name}-0.20-mapreduce-tasktracker = %{version}-%{release}, %{name}-0.20-mapreduce-jobtracker = %{version}-%{release}
Conflicts: hadoop-conf-pseudo

%description 0.20-conf-pseudo
Installation of this RPM will setup your machine to run in pseudo-distributed mode
where each Hadoop daemon runs in a separate Java process. You will be getting old
style daemons (MRv1) for Hadoop jobtracker and Hadoop tasktracker instead of new
YARN (MRv2) ones.

%package 0.20-mapreduce-jobtrackerha
Summary: Hadoop JobTracker High Availability
Group: System/Daemons
Requires: %{name}-0.20-mapreduce = %{version}-%{release}
Conflicts: hadoop-0.20-jobtracker, %{name}-0.20-mapreduce-jobtracker

%description 0.20-mapreduce-jobtrackerha
The Hadoop MapReduce JobTracker High Availability Daemon provides a
High Availability JobTracker. JobTracker (installed by
hadoop-0.20-mapreduce-jobtracker) and JobTracker High Availability
(installed by this package - hadoop-0.20-mapreduce-jobtrackerha)
can not be installed together on the same machine. Only one of them should
be installed on a given machine at any given time. When used in coordination
with Hadoop MapReduce failover controller (installed by
hadoop-0.20-mapreduce-zkfc), this JobTracker provides automatic failover.
The jobtracker is a central service which is responsible for managing
the tasktracker services running on all nodes in a Hadoop Cluster.
The jobtracker allocates work to the tasktracker nearest to the data
with an available work slot.

%package 0.20-mapreduce-zkfc
Summary: Hadoop MapReduce failover controller
Group: System/Daemons
Requires: %{name}-0.20-mapreduce-jobtrackerha = %{version}-%{release}, zookeeper >= 3.4.0

%description 0.20-mapreduce-zkfc
The Hadoop MapReduce failover controller is a Zookeeper client which also
manages the state of the JobTracker. Any machines running ZKFC also need to
run High Availability JobTracker (installed by hadoop-0.20-mapreduce-jobtrackerha).
The ZKFC is responsible for: Health monitoring, Zookeeper
session management and Zookeeper-based election.

%package client
Summary: Hadoop client side dependencies
Group: System/Daemons
Requires: %{name} = %{version}-%{release}
Requires: %{name}-hdfs = %{version}-%{release}
Requires: %{name}-yarn = %{version}-%{release}
Requires: %{name}-mapreduce = %{version}-%{release}
Requires: %{name}-0.20-mapreduce = %{version}-%{release}
Requires(pre): %{name}-0.20-mapreduce = %{version}-%{release}
Requires: avro-libs, zookeeper

%description client
Installation of this package will provide you with all the dependencies for Hadoop clients.

%package conf-pseudo
Summary: Hadoop installation in pseudo-distributed mode
Group: System/Daemons
Requires: %{name} = %{version}-%{release}
Requires: %{name}-hdfs-namenode = %{version}-%{release}
Requires: %{name}-hdfs-datanode = %{version}-%{release}
Requires: %{name}-hdfs-secondarynamenode = %{version}-%{release}
Requires: %{name}-yarn-resourcemanager = %{version}-%{release}
Requires: %{name}-yarn-nodemanager = %{version}-%{release}
Requires: %{name}-mapreduce-historyserver = %{version}-%{release}

%description conf-pseudo
Installation of this RPM will setup your machine to run in pseudo-distributed mode
where each Hadoop daemon runs in a separate Java process.

%package doc
Summary: Hadoop Documentation
Group: Documentation
Obsoletes: %{name}-docs
%description doc
Documentation for Hadoop

%package libhdfs
Summary: Hadoop Filesystem Library
Group: Development/Libraries
Requires: %{name}-hdfs = %{version}-%{release}
# TODO: reconcile libjvm
AutoReq: no

%description libhdfs
Hadoop Filesystem Library

%package libhdfs-devel
Summary: Development support for libhdfs
Group: Development/Libraries
Requires: hadoop = %{version}-%{release}, hadoop-libhdfs = %{version}-%{release}

%description libhdfs-devel
Includes examples and header files for accessing HDFS from C

%package hdfs-fuse
Summary: Mountable HDFS
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: %{name}-libhdfs = %{version}-%{release}
Requires: %{name}-client = %{version}-%{release}
Requires: fuse
AutoReq: no

%if %{?suse_version:1}0
Requires: libfuse2
%else
Requires: fuse-libs
%endif


%description hdfs-fuse
These projects (enumerated below) allow HDFS to be mounted (on most flavors of Unix) as a standard file system using


%prep
%setup -n %{name}-%{hadoop_patched_version}
tar -C `dirname %{SOURCE29}` -xzf %{SOURCE29}

%build
# This assumes that you installed Java JDK 6 and set JAVA_HOME
# This assumes that you installed Java JDK 5 and set JAVA5_HOME
# This assumes that you installed Forrest and set FORREST_HOME

env FULL_VERSION=%{hadoop_patched_version} HADOOP_VERSION=%{hadoop_version} HADOOP_ARCH=%{hadoop_arch} bash %{SOURCE1}

%clean
%__rm -rf $RPM_BUILD_ROOT

#########################
#### INSTALL SECTION ####
#########################
%install
%__rm -rf $RPM_BUILD_ROOT

%__install -d -m 0755 $RPM_BUILD_ROOT/%{lib_hadoop}

bash %{SOURCE2} \
  --distro-dir=$RPM_SOURCE_DIR \
  --source-dir=$PWD \
  --build-dir=$PWD/build/%{name}-%{hadoop_patched_version} \
  --hadoop-version=%{hadoop_patched_version} \
  --httpfs-dir=$RPM_BUILD_ROOT%{lib_httpfs} \
  --system-include-dir=$RPM_BUILD_ROOT%{_includedir} \
  --system-lib-dir=$RPM_BUILD_ROOT%{_libdir} \
  --system-libexec-dir=$RPM_BUILD_ROOT/%{lib_hadoop}/libexec \
  --hadoop-etc-dir=$RPM_BUILD_ROOT%{etc_hadoop} \
  --httpfs-etc-dir=$RPM_BUILD_ROOT%{etc_httpfs} \
  --prefix=$RPM_BUILD_ROOT \
  --doc-dir=$RPM_BUILD_ROOT%{doc_hadoop} \
  --example-dir=$RPM_BUILD_ROOT%{doc_hadoop}/examples \
  --native-build-string=%{hadoop_arch} \
  --installed-lib-dir=%{lib_hadoop} \
  --man-dir=$RPM_BUILD_ROOT%{man_hadoop} \
  --kms-dir=$RPM_BUILD_ROOT%{lib_kms} \
  --kms-etc-dir=$RPM_BUILD_ROOT%{etc_kms} \

# Forcing Zookeeper dependency to be on the packaged jar
%__ln_s -f /usr/lib/zookeeper/zookeeper.jar $RPM_BUILD_ROOT/%{lib_hadoop}/lib/zookeeper*.jar
# Workaround for BIGTOP-583
%__rm -f $RPM_BUILD_ROOT/%{lib_hadoop}*/lib/slf4j-log4j12-*.jar
%__ln_s -f /usr/lib/zookeeper/lib/slf4j-log4j12.jar $RPM_BUILD_ROOT/%{lib_hadoop}/lib/slf4j-log4j12.jar

# Init.d scripts
%__install -d -m 0755 $RPM_BUILD_ROOT/%{initd_dir}/

# Install top level /etc/default files
%__install -d -m 0755 $RPM_BUILD_ROOT/etc/default
%__cp $RPM_SOURCE_DIR/hadoop.default $RPM_BUILD_ROOT/etc/default/hadoop
# FIXME: BIGTOP-463
echo 'export JSVC_HOME=%{libexecdir}/bigtop-utils' >> $RPM_BUILD_ROOT/etc/default/hadoop
%__cp $RPM_SOURCE_DIR/%{name}-fuse.default $RPM_BUILD_ROOT/etc/default/%{name}-fuse

# Generate the init.d scripts
for service in %{hadoop_services}
do
       bash %{SOURCE11} $RPM_SOURCE_DIR/%{name}-${service}.svc rpm $RPM_BUILD_ROOT/%{initd_dir}/%{name}-${service}
       cp $RPM_SOURCE_DIR/${service/-*/}.default $RPM_BUILD_ROOT/etc/default/%{name}-${service}
       chmod 644 $RPM_BUILD_ROOT/etc/default/%{name}-${service}
done

# Install security limits
%__install -d -m 0755 $RPM_BUILD_ROOT/etc/security/limits.d
%__install -m 0644 %{SOURCE8} $RPM_BUILD_ROOT/etc/security/limits.d/hdfs.conf
%__install -m 0644 %{SOURCE9} $RPM_BUILD_ROOT/etc/security/limits.d/yarn.conf
%__install -m 0644 %{SOURCE10} $RPM_BUILD_ROOT/etc/security/limits.d/mapreduce.conf
# MR1 hack
%__install -m 0644 %{SOURCE10} $RPM_BUILD_ROOT/etc/security/limits.d/mapred.conf

# Install KMS default file
%__install -d -m 0755 $RPM_BUILD_ROOT/etc/default
%__cp %{SOURCE38} $RPM_BUILD_ROOT/etc/default/hadoop-kms

# Install fuse default file
%__install -d -m 0755 $RPM_BUILD_ROOT/etc/default
%__cp %{SOURCE4} $RPM_BUILD_ROOT/etc/default/hadoop-fuse
# FIXME: we need to think how to get rid of the following file
%__cp %{SOURCE30} $RPM_BUILD_ROOT/etc/default/hadoop-0.20-mapreduce

# /var/lib/*/cache
%__install -d -m 1777 $RPM_BUILD_ROOT/%{state_yarn}/cache
%__install -d -m 1777 $RPM_BUILD_ROOT/%{state_hdfs}/cache
%__install -d -m 1777 $RPM_BUILD_ROOT/%{state_mapreduce}/cache
# /var/log/*
%__install -d -m 0755 $RPM_BUILD_ROOT/%{log_yarn}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{log_hdfs}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{log_mapreduce}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{log_httpfs}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{log_kms}
# /var/run/*
%__install -d -m 0755 $RPM_BUILD_ROOT/%{run_yarn}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{run_hdfs}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{run_mapreduce}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{run_httpfs}
%__install -d -m 0755 $RPM_BUILD_ROOT/%{run_kms}

%pre
getent group hadoop >/dev/null || groupadd -r hadoop

%pre hdfs
getent group hadoop >/dev/null || groupadd -r hadoop
getent group hdfs >/dev/null   || groupadd -r hdfs
getent passwd hdfs >/dev/null || /usr/sbin/useradd --comment "Hadoop HDFS" --shell /bin/bash -M -r -g hdfs -G hadoop --home %{state_hdfs} hdfs

%pre httpfs 
getent group httpfs >/dev/null   || groupadd -r httpfs
getent passwd httpfs >/dev/null || /usr/sbin/useradd --comment "Hadoop HTTPFS" --shell /bin/bash -M -r -g httpfs -G httpfs --home %{state_httpfs} httpfs

%pre kms 
getent group kms >/dev/null   || groupadd -r kms
getent passwd kms >/dev/null || /usr/sbin/useradd --comment "Hadoop KMS" --shell /bin/bash -M -r -g kms -G kms --home %{state_kms} kms

%pre yarn
getent group hadoop >/dev/null || groupadd -r hadoop
getent group yarn >/dev/null   || groupadd -r yarn
getent passwd yarn >/dev/null || /usr/sbin/useradd --comment "Hadoop Yarn" --shell /bin/bash -M -r -g yarn -G hadoop --home %{state_yarn} yarn

%pre mapreduce
getent group hadoop >/dev/null || groupadd -r hadoop
getent group mapred >/dev/null   || groupadd -r mapred
getent passwd mapred >/dev/null || /usr/sbin/useradd --comment "Hadoop MapReduce" --shell /bin/bash -M -r -g mapred -G hadoop --home %{state_mapreduce} mapred

%pre 0.20-mapreduce
getent group hadoop >/dev/null || groupadd -r hadoop
getent group mapred >/dev/null || groupadd -r mapred
getent passwd mapred >/dev/null || /usr/sbin/useradd --comment "Hadoop MapReduce" --shell /bin/bash -M -r -g mapred -G hadoop --home %{lib_hadoop} mapred

%post
%{alternatives_cmd} --install %{config_hadoop} %{name}-conf %{etc_hadoop}/conf.empty 10

%post httpfs
%{alternatives_cmd} --install %{config_httpfs} %{name}-httpfs-conf %{etc_httpfs}/conf.empty 10
%{alternatives_cmd} --install %{tomcat_deployment_httpfs} %{name}-httpfs-tomcat-conf %{etc_httpfs}/tomcat-conf.dist 10
%{alternatives_cmd} --install %{tomcat_deployment_httpfs} %{name}-httpfs-tomcat-conf %{etc_httpfs}/tomcat-conf.https 5
chkconfig --add %{name}-httpfs

%post kms
%{alternatives_cmd} --install %{config_kms} %{name}-kms-conf %{etc_kms}/conf.dist 10
%{alternatives_cmd} --install %{tomcat_deployment_kms} %{name}-kms-tomcat-conf %{etc_kms}/tomcat-conf.http 5
%{alternatives_cmd} --install %{tomcat_deployment_kms} %{name}-kms-tomcat-conf %{etc_kms}/tomcat-conf.https 5

%post kms-server
chkconfig --add %{name}-kms-server

%preun
if [ "$1" = 0 ]; then
  %{alternatives_cmd} --remove %{name}-conf %{etc_hadoop}/conf.empty || :
fi

%post hdfs
%{alternatives_cmd} --install %{config_hadoop} %{name}-conf %{etc_hadoop}/conf.impala 5

%preun hdfs
if [ "$1" = 0 ]; then
  %{alternatives_cmd} --remove %{name}-conf %{etc_hadoop}/conf.impala || :
fi

%preun httpfs
if [ $1 = 0 ]; then
  service %{name}-httpfs stop > /dev/null 2>&1
  chkconfig --del %{name}-httpfs
  %{alternatives_cmd} --remove %{name}-httpfs-conf %{etc_httpfs}/conf.empty || :
  %{alternatives_cmd} --remove %{name}-httpfs-tomcat-conf %{etc_httpfs}/tomcat-conf.dist || :
  %{alternatives_cmd} --remove %{name}-httpfs-tomcat-conf %{etc_httpfs}/tomcat-conf.https || :
fi

%preun kms
if [ $1 = 0 ]; then
  %{alternatives_cmd} --remove %{name}-kms-conf %{etc_kms}/conf.dist || :
  %{alternatives_cmd} --remove %{name}-kms-tomcat-conf %{etc_kms}/tomcat-conf.http || :
  %{alternatives_cmd} --remove %{name}-kms-tomcat-conf %{etc_kms}/tomcat-conf.https || :
fi

%preun kms-server
if [ $1 = 0 ]; then
  service %{name}-kms-server stop > /dev/null 2>&1
  chkconfig --del %{name}-kms-server
fi


%postun httpfs
if [ $1 -ge 1 ]; then
  service %{name}-httpfs condrestart >/dev/null 2>&1
fi

%postun kms-server
if [ $1 -ge 1 ]; then
  service %{name}-kms-server condrestart >/dev/null 2>&1
fi


%files yarn
%defattr(-,root,root)
%config(noreplace) %{etc_hadoop}/conf.empty/yarn-env.sh
%config(noreplace) %{etc_hadoop}/conf.empty/yarn-site.xml
%config(noreplace) %{etc_hadoop}/conf.empty/capacity-scheduler.xml
%config(noreplace) %{etc_hadoop}/conf.empty/container-executor.cfg
%config(noreplace) /etc/security/limits.d/yarn.conf
%{lib_hadoop}/libexec/yarn-config.sh
%{lib_yarn}
%attr(4754,root,yarn) %{lib_yarn}/bin/container-executor
%{bin_hadoop}/yarn
%attr(0775,yarn,hadoop) %{run_yarn}
%attr(0775,yarn,hadoop) %{log_yarn}
%attr(0755,yarn,hadoop) %{state_yarn}
%attr(1777,yarn,hadoop) %{state_yarn}/cache

%files hdfs
%defattr(-,root,root)
%config(noreplace) %{etc_hadoop}/conf.empty/hdfs-site.xml
%config(noreplace) %{etc_hadoop}/conf.impala
%config(noreplace) /etc/security/limits.d/hdfs.conf
%{lib_hdfs}
%{lib_hadoop}/libexec/hdfs-config.sh
%{bin_hadoop}/hdfs
%attr(0755,hdfs,hadoop) %{run_hdfs}
%attr(0775,hdfs,hadoop) %{log_hdfs}
%attr(0755,hdfs,hadoop) %{state_hdfs}
%attr(1777,hdfs,hadoop) %{state_hdfs}/cache
%{lib_hadoop}/libexec/init-hdfs.sh

%files mapreduce
%defattr(-,root,root)
%config(noreplace) %{etc_hadoop}/conf.empty/mapred-site.xml
%config(noreplace) %{etc_hadoop}/conf.empty/mapred-queues.xml.template
%config(noreplace) %{etc_hadoop}/conf.empty/mapred-site.xml.template
%config(noreplace) /etc/security/limits.d/mapreduce.conf
%{lib_mapreduce}
%{lib_hadoop}/libexec/mapred-config.sh
%{bin_hadoop}/mapred
%attr(0775,mapred,hadoop) %{run_mapreduce}
%attr(0775,mapred,hadoop) %{log_mapreduce}
%attr(0775,mapred,hadoop) %{state_mapreduce}
%attr(1777,mapred,hadoop) %{state_mapreduce}/cache

%files
%defattr(-,root,root)
%config(noreplace) %{etc_hadoop}/conf.empty/core-site.xml
%config(noreplace) %{etc_hadoop}/conf.empty/hadoop-metrics.properties
%config(noreplace) %{etc_hadoop}/conf.empty/hadoop-metrics2.properties
%config(noreplace) %{etc_hadoop}/conf.empty/log4j.properties
%config(noreplace) %{etc_hadoop}/conf.empty/slaves
%config(noreplace) %{etc_hadoop}/conf.empty/ssl-client.xml.example
%config(noreplace) %{etc_hadoop}/conf.empty/ssl-server.xml.example
%config(noreplace) %{etc_hadoop}/conf.empty/configuration.xsl
# FIXME: CDH-12105
# %config(noreplace) %{etc_hadoop}/conf.empty/hadoop-env.sh
%config(noreplace) %{etc_hadoop}/conf.empty/hadoop-policy.xml
%config(noreplace) /etc/default/hadoop
%{etc_hadoop}/conf.dist
%{lib_hadoop}/*.jar
%{lib_hadoop}/lib
%{lib_hadoop}/sbin
%{lib_hadoop}/bin
%{lib_hadoop}/etc
%{lib_hadoop}/LICENSE.txt
%{lib_hadoop}/NOTICE.txt
%{lib_hadoop}/etc
%{lib_hadoop}/cloudera
%{lib_hadoop}/libexec/hadoop-config.sh
%{lib_hadoop}/libexec/hadoop-layout.sh
%{bin_hadoop}/hadoop
%{man_hadoop}/man1/hadoop.1.*
%{man_hadoop}/man1/yarn.1.*
%{man_hadoop}/man1/hdfs.1.*
%{man_hadoop}/man1/mapred.1.*
%{state_hadoop}/extra/native

# Shouldn't the following be moved to hadoop-hdfs?
%exclude %{lib_hadoop}/bin/fuse_dfs

%files kms
%defattr(-,root,root)
%config(noreplace) %{etc_kms}
%config(noreplace) /etc/default/%{name}-kms
%{lib_hadoop}/libexec/kms-config.sh
%{lib_kms}
%attr(0775,kms,kms) %{run_kms}
%attr(0775,kms,kms) %{log_kms}
%attr(0775,kms,kms) %{state_kms}

%files kms-server
%{initd_dir}/%{name}-kms-server

%files doc
%defattr(-,root,root)
%doc %{doc_hadoop}
%doc %{doc_hadoop_mr1}

%files httpfs
%defattr(-,root,root)
%config(noreplace) %{etc_httpfs}
%config(noreplace) /etc/default/%{name}-httpfs
%{lib_hadoop}/libexec/httpfs-config.sh
%{initd_dir}/%{name}-httpfs
%{lib_httpfs}
%attr(0775,httpfs,httpfs) %{run_httpfs}
%attr(0775,httpfs,httpfs) %{log_httpfs}
%attr(0775,httpfs,httpfs) %{state_httpfs}
%attr(0750,httpfs,httpfs) %{etc_httpfs}/tomcat-conf.https/conf/server.xml
%attr(0750,httpfs,httpfs) %{etc_httpfs}/tomcat-conf.dist/conf/server.xml

# Service file management RPMs
%define service_macro() \
%files %1 \
%defattr(-,root,root) \
%{initd_dir}/%{name}-%1 \
%config(noreplace) /etc/default/%{name}-%1 \
%post %1 \
chkconfig --add %{name}-%1 \
\
%preun %1 \
if [ $1 = 0 ]; then \
  service %{name}-%1 stop > /dev/null 2>&1 \
  chkconfig --del %{name}-%1 \
fi \
%postun %1 \
if [ $1 -ge 1 ]; then \
  service %{name}-%1 condrestart >/dev/null 2>&1 \
fi

%service_macro hdfs-namenode
%service_macro hdfs-secondarynamenode
%service_macro hdfs-zkfc
%service_macro hdfs-journalnode
%service_macro hdfs-datanode
%service_macro hdfs-nfs3
%service_macro yarn-resourcemanager
%service_macro yarn-nodemanager
%service_macro yarn-proxyserver
%service_macro mapreduce-historyserver
%service_macro 0.20-mapreduce-jobtracker
%service_macro 0.20-mapreduce-tasktracker
%service_macro 0.20-mapreduce-zkfc
%service_macro 0.20-mapreduce-jobtrackerha


# Pseudo-distributed Hadoop installation
%post conf-pseudo
%{alternatives_cmd} --install %{config_hadoop} %{name}-conf %{etc_hadoop}/conf.pseudo 30

# Pseudo-distributed Hadoop installation
%post 0.20-conf-pseudo
%{alternatives_cmd} --install %{config_hadoop} %{name}-conf %{etc_hadoop}/conf.pseudo.mr1 30

%preun conf-pseudo
if [ "$1" = 0 ]; then
        %{alternatives_cmd} --remove %{name}-conf %{etc_hadoop}/conf.pseudo
fi

%preun 0.20-conf-pseudo
if [ "$1" = 0 ]; then
        %{alternatives_cmd} --remove %{name}-conf %{etc_hadoop}/conf.pseudo.mr1
fi

%files conf-pseudo
%defattr(-,root,root)
%config(noreplace) %attr(755,root,root) %{etc_hadoop}/conf.pseudo

%files client
%defattr(-,root,root)
%{lib_hadoop}/client
%{lib_hadoop}/client-0.20

%files libhdfs
%defattr(-,root,root)
%{_libdir}/libhdfs*

%files libhdfs-devel
%{_includedir}/hdfs.h
#%doc %{_docdir}/libhdfs-%{hadoop_version}

%files hdfs-fuse
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) /etc/default/hadoop-fuse
%attr(0755,root,root) %{lib_hadoop}/bin/fuse_dfs
%attr(0755,root,root) %{bin_hadoop}/hadoop-fuse-dfs

%files 0.20-conf-pseudo
%defattr(-,root,root)
%config(noreplace) %attr(755,root,root) %{etc_hadoop}/conf.pseudo.mr1

%files 0.20-mapreduce
%defattr(-,root,root)
%config(noreplace) %{etc_hadoop}/conf.empty/fair-scheduler.xml
%config(noreplace) /etc/security/limits.d/mapred.conf
# FIXME: we need to think how to get rid of the following file
%config(noreplace) /etc/default/hadoop-0.20-mapreduce
%attr(4754,root,mapred) %{lib_mapreduce_mr1}/sbin/Linux/task-controller
%{lib_mapreduce_mr1}
%{bin_hadoop}/hadoop-0.20
# %{man_hadoop}/man1/%{hadoop_name}.1.gz
%attr(0775,root,hadoop) /var/run/hadoop-0.20-mapreduce
%attr(0775,root,hadoop) /var/log/hadoop-0.20-mapreduce
