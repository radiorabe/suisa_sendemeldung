#
# spec file for package suisa_sendemeldung
#
# Copyright (c) 2018 Radio Bern RaBe
#                    http://www.rabe.ch
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Please submit enhancements, bugfixes or comments via GitHub:
# https://github.com/radiorabe/suisa_sendemeldung
#
%global srcname suisa_sendemeldung

%{?el7:%global python3_pkgversion 36}

Name:           %{srcname}
Version:        master
Release:        0%{?dist}
Summary:        ACRCloud client for SUISA reporting

License:        MIT
URL:            https://github.com/radiorabe/suisa_sendemeldung
Source0:        https://github.com/radiorabe/suisa_sendemeldung/archive/%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python%{python3_pkgversion}-configargparse
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python%{python3_pkgversion}-requests
BuildRequires:  python3-devel
%{?systemd_requires}
BuildRequires:  systemd
Requires(pre):  shadow-utils
Requires:       python%{python3_pkgversion}-configargparse
Requires:       python%{python3_pkgversion}-requests
%{?python_enable_dependency_generator}

%description
ACRCloud client that fetches data on our playout history and
formats them in a CSV file format containing the data (like
Track, Title and, ISRC) requested by SUISA.
Also takes care of sending the report to SUISA via email for
hands-off operations.


%prep
%autosetup -n %{srcname}-%{version}

%build
%py3_build

%install
%py3_install
install -d %{buildroot}%{_unitdir}
install etc/systemd/%{srcname}.* %{buildroot}%{_unitdir}
install -d %{buildroot}%{_sysconfdir}
install etc/%{srcname}.conf %{buildroot}%{_sysconfdir}
install -d %{buildroot}%{_sysconfdir}/sysconfig
install etc/sysconfig/%{srcname} %{buildroot}%{_sysconfdir}/sysconfig

%check
%{__python3} setup.py test

%pre
getent group %{srcname} >/dev/null || groupadd -r %{srcname}
getent passwd %{srcname} >/dev/null || \
    useradd -r -g %{srcname} -d %{python3_sitelib}/%{srcname}/ -s /sbin/nologin \
    -c "SUISA ACRClient account" %{srcname}
exit 0

%post
%systemd_post %{srcname}.service
%systemd_post %{srcname}.timer

%preun
%systemd_preun %{srcname}.timer
%systemd_preun %{srcname}.service

%postun
%systemd_postun %{srcname}.timer
%systemd_postun %{srcname}.service

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/%{srcname}/
%{python3_sitelib}/%{srcname}-*.egg-info/
%{_bindir}/%{srcname}
%{_unitdir}/%{srcname}.*
%config(noreplace)%{_sysconfdir}/%{srcname}.conf
%config(noreplace)%{_sysconfdir}/sysconfig/%{srcname}
