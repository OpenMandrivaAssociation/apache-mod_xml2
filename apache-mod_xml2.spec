#Module-Specific definitions
%define mod_name mod_xml2
%define mod_conf B12_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Mod_xml2 is a DSO module for the apache web server
Name:		apache-%{mod_name}
Version:	0
Release:	%mkrel 2
Group:		System/Servers
License:	Apache License
URL:		http://www.heute-morgen.de/modules/mod_xml2/
Source0:	%{mod_name}.tar.gz
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	libxml2-devel
BuildRequires:	file

%description
This is mod_xml2. It has nothing to do with mod_xml. The name is as it is
because it is a wrapper to the gnome libxml2 and mod_libxml2 is ugly. It is
runs the libxml2 SAX2 parser and converts its input into SAX buckets. These are
SAX events wrapped into buckets. They morph back into heap buckets if you call
their bucket read function. This means that nothing needs to be done to convert
them back. It also means that you have to be carefull, once you treat them as
ordinary buckets (e.g. by using an "ordinary" filter), they are. So if you only
run the xml2 filter on XML input you will rarely notice it. Whitespace inside
tags is normalized.

It also provides functionality for converting portions of the document into
document trees and using tree transformation functions on them. See
tree_transform.h and mod_i18n.c on how to do this.

This module should work as a drop in replacement for mod_expat, which I will
not maintain.

Filters using SAX buckets currently are mod_i18n and mod_xi.

The module should be able to run on large files, which is actually the point
with both SAX and Apache filters. Allocation of per request memory is done once
for every tag name, attribute name and namespace. So as long as your XML file
is not permanently introducing new tags or new namespaces this is limited.
Check sax_unify_name to see what exactly happens.

%package	devel
Summary:	Development API for the mod_xml2 apache module
Group:		Development/C

%description	devel
This package contains the development API for the mod_xml2 apache module.


%prep

%setup -q -n %{mod_name}

cp %{SOURCE1} %{mod_conf}

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type d -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;

for i in `find . -type d -name CVS` `find . -type d -name .svn` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

%{_sbindir}/apxs -c `xml2-config --cflags` mod_xml2.c buckets_sax.c \
    frag_buffer.c sax_util.c sxpath.c tree_transform.c %{_libdir}/libxml2.la

head -60 mod_xml2.c > README

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_libdir}/apache-extramodules

install -d %{buildroot}%{_includedir}/%{mod_name}

install -m0755 .libs/%{mod_so} %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}
install -m0644 *.h %{buildroot}%{_includedir}/%{mod_name}/

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}

%files devel
%defattr(-,root,root)
%dir %{_includedir}/%{mod_name}
%attr(0644,root,root) %{_includedir}/%{mod_name}/*.h
