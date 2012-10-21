%define name    horde
%define version 3.3.11
%define release %mkrel 3

%define _requires_exceptions pear(Horde/Kolab/FreeBusy.php)\\|pear(PHPUnit/Framework.php)\\|pear(PHPUnit/Extensions/Story/TestCase.php)

Name:       %{name}
Version:    %{version}
Release:    %{release}
Summary:    The Horde framework
License:    GPL
Group:      System/Servers
Source0:    ftp://ftp.horde.org/pub/horde/%{name}-%{version}.tar.gz
############################
# domxml php4 - php5 wrapper
# Written by Alexandre Alapetite
# Licence: Creative Commons "Attribution-ShareAlike 2.0 France" BY-SA (FR)
# http://alexandre.alapetite.net/doc-alex/domxml-php4-php5
Source1:    http://alexandre.alapetite.net/doc-alex/domxml-php4-php5/domxml-php4-to-php5.php.txt
############################
Patch2:     %{name}-3.3.2-better-default-configuration.patch
Patch4:     %{name}-3.3.5-registry.patch
Patch6:     horde-3.2-usr_local.patch
URL:        http://www.horde.org/
Suggests:   horde-dimp
Suggests:   horde-gollem
Suggests:   horde-ingo
Suggests:   horde-mimp
Suggests:   horde-nag
Suggests:   horde-turba
Suggests:   horde-passwd
Suggests:   horde-kronolith
Suggests:   horde-imp
Suggests:   horde-vacation
Requires:   apache-mod_php
Suggests:   php-imagick
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

%description
The Horde Framework provides a common structure and interface for Horde
applications (such as IMP, a web-based mail program).  This RPM is required
for all other Horde module RPMS.

The Horde Project writes web applications in PHP and releases them under
the GNU Public License.  For more information (including help with Horde
and its modules) please visit http://www.horde.org/.

%prep
%setup -q
%patch2 -p 1
%patch4 -p 1
%patch6 -p 1

# fix perms
chmod 755 scripts/*.{php,sh,cron}

# nuke patch backup files
find . -type f -name "*.orig" | xargs rm -f

%build

%install
rm -rf %{buildroot}

# apache configuration
install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
# %{name} Apache configuration file
Alias /%{name} %{_datadir}/%{name}
<Directory %{_datadir}/%{name}>
    Order allow,deny
    Allow from localhost
</Directory>

<Directory %{_datadir}/%{name}/lib>
    Order allow,deny
    Deny from all
</Directory>

<Directory %{_datadir}/%{name}/locale>
    Order allow,deny
    Deny from all
</Directory>

<Directory %{_datadir}/%{name}/scripts>
    Order allow,deny
    Deny from all
</Directory>

<Directory %{_datadir}/%{name}/templates>
    Order allow,deny
    Deny from all
</Directory>
EOF

# remove .htaccess files
find . -name .htaccess -exec rm -f {} \;

# install files
install -d -m 755 %{buildroot}%{_datadir}/%{name}
cp -pR *.php %{buildroot}%{_datadir}/%{name}
cp -pR admin %{buildroot}%{_datadir}/%{name}
cp -pR js %{buildroot}%{_datadir}/%{name}
cp -pR services %{buildroot}%{_datadir}/%{name}
cp -pR themes %{buildroot}%{_datadir}/%{name}
cp -pR util %{buildroot}%{_datadir}/%{name}
cp -pR lib %{buildroot}%{_datadir}/%{name}
cp -pR locale %{buildroot}%{_datadir}/%{name}
cp -pR scripts %{buildroot}%{_datadir}/%{name}
cp -pR templates %{buildroot}%{_datadir}/%{name}

install -d -m 755 %{buildroot}%{_sysconfdir}
cp -pR config %{buildroot}%{_sysconfdir}/%{name}
pushd %{buildroot}%{_datadir}/%{name}
ln -s ../../..%{_sysconfdir}/%{name} config
popd

# put domxml-php4-to-php5.php in place
install -m0644 %{SOURCE1} %{buildroot}%{_datadir}/%{name}/lib/Horde/domxml-php4-to-php5.php

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
- the constant files are in /usr/share/horde

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
%if %mdkversion < 201010
%_post_webapp
%endif

if [ $1 = 1 ]; then
    # configuration
    %create_ghostfile %{_sysconfdir}/%{name}/conf.php.bak apache apache 644
fi

%if %mdkversion < 201010
%postun
%_postun_webapp
%endif

%files
%defattr(-,root,root)
%doc README README.mdv COPYING docs  scripts/SCRIPTS
%config(noreplace) %{_webappconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/hooks.php
%config(noreplace) %{_sysconfdir}/%{name}/conf.xml
%config(noreplace) %{_sysconfdir}/%{name}/mime_drivers.php
%config(noreplace) %{_sysconfdir}/%{name}/motd.php
%config(noreplace) %{_sysconfdir}/%{name}/nls.php
%config(noreplace) %{_sysconfdir}/%{name}/prefs.php
%config(noreplace) %{_sysconfdir}/%{name}/registry.d/README
%config(noreplace) %{_sysconfdir}/%{name}/registry.php
%attr(-,apache,apache) %config(noreplace) %{_sysconfdir}/%{name}/conf.php 
%{_datadir}/%{name}
%attr(-,apache,apache) %{_var}/log/%{name}


