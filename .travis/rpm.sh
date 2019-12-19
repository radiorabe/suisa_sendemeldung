#!/bin/bash
#
# RPM build wrapper for suisa_sendemeldung, runs inside the build container on travis-ci

set -xe

curl -o /etc/yum.repos.d/sendemeldung.repo https://download.opensuse.org/repositories/home:/radiorabe:/sendemeldung/CentOS_7/home:radiorabe:sendemeldung.repo

chown root:root suisa_sendemeldung.spec

create-source-tarball.sh /git suisa_sendemeldung-master.tar.gz

build-rpm-package.sh suisa_sendemeldung.spec
