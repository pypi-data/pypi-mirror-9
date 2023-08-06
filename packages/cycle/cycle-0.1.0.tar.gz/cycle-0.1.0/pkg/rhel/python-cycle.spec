%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define shortname cycle

Name: python-cycle
Version: 0.1.0
Release: 0%{?dist}
Summary: A Python software build management tool inspired by Maven

Group: Development/Tools
License: ASL 2.0
URL: https://github.com/refnode/python-cycle
#Source: https://github.com/refnode/python-cycle/archive/v%{version}.tar.gz
Source: cycle-0.1.0.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

BuildRequires: python-setuptools

%description
A Python software build management tool inspired by Maven.


%prep
%setup -q -n %{shortname}-%{version}


%build
%{__python} setup.py build


%install
rm -rf %{buildroot}

%{__python} setup.py install -O1 --skip-build --root %{buildroot}


%clean
rm -rf $RPM_BUILD_ROOT


%preun
exit 0


%postun
exit 0


%files
%defattr(-,root,root,-)
%doc LICENSE
%{python_sitelib}/*
%{_bindir}/cycle


%changelog
* Sun Apr 12 2015 refnode <refnode@gmail.com> - 0.1.0-0
- Initialization
