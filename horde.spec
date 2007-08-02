%define name    horde
%define version 3.1.4
%define release %mkrel 1

Name:       %{name}
Version:    %{version}
Release:    %{release}
Summary:    The Horde framework
License:    GPL
Group:      System/Servers
Source0:    ftp://ftp.horde.org/pub/horde/%{name}-%{version}.tar.bz2
############################
# domxml php4 - php5 wrapper
# Written by Alexandre Alapetite
# Licence: Creative Commons "Attribution-ShareAlike 2.0 France" BY-SA (FR)
# http://alexandre.alapetite.net/doc-alex/domxml-php4-php5
Source1:    http://alexandre.alapetite.net/doc-alex/domxml-php4-php5/domxml-php4-to-php5.php.txt
############################
Patch2:     %{name}-3.0.2-better-default-configuration.patch
Patch4:     %{name}-3.1.4-registry.patch
Patch5:     horde-3.1.4-kolab_php-reference.patch
Patch6:     horde-3.1.3-usr_local.patch
Patch7:     horde-no_icalenderdata_debug_log.diff
Patch8:     horde-3.1.2-kolab_php-php5.patch
URL:        http://www.horde.org/
Requires:   apache-mod_php
Requires:   php-xml
Requires:   php-dom
# webapp macros and scriptlets
%if %mdkversion < 200700
%define _webconfdir %{_sysconfdir}/httpd/conf
%define _webappconfdir %_webconfdir/webapps.d
Requires(post): rpm-helper
Requires(postun): rpm-helper
BuildRequires: rpm-helper
BuildRequires: rpm-mandriva-setup
%else
Requires(post):     rpm-helper >= 0.16
Requires(postun):   rpm-helper >= 0.16
BuildRequires:  rpm-helper >= 0.16
BuildRequires:  rpm-mandriva-setup >= 1.23
%endif
Conflicts:  horde-accounts <= 2.1.2
Conflicts:  horde-forwards <= 2.2.2
Conflicts:  horde-password <= 2.2.2
Conflicts:  horde-vacation <= 2.2.2
BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}

%description
The Horde Framework provides a common structure and interface for Horde
applications (such as IMP, a web-based mail program).  This RPM is required
for all other Horde module RPMS.

The Horde Project writes web applications in PHP and releases them under
the GNU Public License.  For more information (including help with Horde
and its modules) please visit http://www.horde.org/.

%prep

%setup -q
%patch2
%patch4
%patch5 -p1
%patch6 -p1
%patch7 -p0
%patch8 -p1

# fix perms
chmod 755 scripts/*.{php,sh,cron}

# fix encoding
for file in `find . -type f`; do
    perl -pi -e 'BEGIN {exit unless -T $ARGV[0];} s/\r\n$/\n/;' $file
done

# nuke patch backup files
find . -type f -name "*.orig" | xargs rm -f

%build

%install
rm -rf %{buildroot}

# apache configuration
install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
# %{name} Apache configuration file
Alias /%{name} %{_var}/www/%{name}
<Directory %{_var}/www/%{name}>
    Allow from all
</Directory>
EOF

# remove .htaccess files
find . -name .htaccess -exec rm -f {} \;

# install files
install -d -m 755 %{buildroot}%{_var}/www/%{name}
install -d -m 755 %{buildroot}%{_datadir}/%{name}
install -d -m 755 %{buildroot}%{_sysconfdir}
cp -pR *.php %{buildroot}%{_var}/www/%{name}
cp -pR admin %{buildroot}%{_var}/www/%{name}
cp -pR js %{buildroot}%{_var}/www/%{name}
cp -pR services %{buildroot}%{_var}/www/%{name}
cp -pR themes %{buildroot}%{_var}/www/%{name}
cp -pR util %{buildroot}%{_var}/www/%{name}
cp -pR lib %{buildroot}%{_datadir}/%{name}
cp -pR locale %{buildroot}%{_datadir}/%{name}
cp -pR scripts %{buildroot}%{_datadir}/%{name}
cp -pR templates %{buildroot}%{_datadir}/%{name}
cp -pR config %{buildroot}%{_sysconfdir}/%{name}

# put domxml-php4-to-php5.php in place
install -m0644 %{SOURCE1} %{buildroot}%{_datadir}/%{name}/lib/Horde/domxml-php4-to-php5.php

# use symlinks to recreate original structure
pushd %{buildroot}%{_var}/www/%{name}
ln -s ../../..%{_sysconfdir}/%{name} config
ln -s ../../..%{_datadir}/%{name}/lib .
ln -s ../../..%{_datadir}/%{name}/locale .
ln -s ../../..%{_datadir}/%{name}/templates .
popd
pushd %{buildroot}%{_datadir}/%{name}
ln -s ../../..%{_sysconfdir}/%{name} config
popd

# activate configuration files
for file in %{buildroot}%{_sysconfdir}/%{name}/*.dist; do
    mv $file ${file%.dist}
done

# fix script shellbang
for file in `find %{buildroot}%{_datadir}/%{name}/scripts`; do
    perl -pi -e 's|/usr/local/bin/php|/usr/bin/php|' $file
done

# registry dir
install -d -m 755 %{buildroot}%{_sysconfdir}/%{name}/registry.d

# logs
install -d -m 755 %{buildroot}%{_var}/log/%{name}
install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
cat > %{buildroot}%{_sysconfdir}/logrotate.d/%{name} <<EOF
%{_var}/log/%{name}/*.log {
    missingok
    compress
}
EOF

cat > README.mdv <<EOF
Mandriva RPM specific notes

setup
-----
The setup used here differs from default one, to achieve better FHS compliance.
- the configuration files are in /etc/horde
- the log files are in /var/log/horde
- the files accessibles from the web are in /var/www/horde
- the files non accessibles from the web are in /usr/share/horde

post-installation
-----------------
You have to either use a browser to http://your.server.url/horde, so as to
configure proper configuration.

Additional useful packages
--------------------------
- either a SQL database (MySQL or PostgreSQL), an LDAP (openldap) or a Kolab
  server for storing preferences
- php-mcrypt for better encryption
- php-iconv and php-mbstring for better utf8 support
- php-gd for image manipulations
- php-pear-File for CVS import support
- php-Date to deal with calendar data
- php-Services_Weather to the weather.com block on the portal page


Additional horde applications
-----------------------------
They are all packaged as horde-<application>. Warning, some have still not been
ported to horde 3, and have been removed from the distribution (vacation,
forwards and accounts notably).
EOF

%clean
rm -rf %{buildroot}

%post
%if %mdkversion < 200700
if [ "$1" = "1" ]; then
	/sbin/service httpd condrestart
fi
%else
%_post_webapp
%endif

if [ $1 = 1 ]; then
    # configuration
    %create_ghostfile %{_sysconfdir}/%{name}/conf.php.bak apache apache 644
fi

%postun
%if %mdkversion < 200700
if [ "$1" = "0" ]; then
	/sbin/service httpd condrestart
else
	/sbin/service httpd condreload
fi
%else
%_postun_webapp
%endif

%files
%defattr(-,root,root)
%doc README README.mdv COPYING docs  scripts/SCRIPTS
%config(noreplace) %{_webappconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}
%attr(-,apache,apache) %config(noreplace) %{_sysconfdir}/%{name}/conf.php 
%{_datadir}/%{name}
%{_var}/www/%{name}
%attr(-,apache,apache) %{_var}/log/%{name}


