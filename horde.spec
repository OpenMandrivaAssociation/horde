Name:       horde
Version:    3.3.11
Release:    5
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




%changelog
* Sat Apr 14 2012 Thomas Spuhler <tspuhler@mandriva.org> 3.3.11-3mdv2012.0
+ Revision: 791021
+ rebuild (emptylog)

* Thu Mar 01 2012 Thomas Spuhler <tspuhler@mandriva.org> 3.3.11-2
+ Revision: 781515
+ rebuild (emptylog)

* Sat Jun 25 2011 Guillaume Rousse <guillomovitch@mandriva.org> 3.3.11-1
+ Revision: 687150
- new version

* Wed Mar 30 2011 Adam Williamson <awilliamson@mandriva.org> 3.3.9-3
+ Revision: 648801
- turn all tspuhler's spurious 'requires' into suggests: horde is modular for
  a *reason*

* Wed Mar 30 2011 Adam Williamson <awilliamson@mandriva.org> 3.3.9-2
+ Revision: 648792
- make php-imagick a suggests not a requires, as it's not strictly required
  and causes a dependency on GTK+

* Tue Mar 29 2011 Adam Williamson <awilliamson@mandriva.org> 3.3.9-1
+ Revision: 648763
- new release 3.3.9

* Mon Aug 30 2010 Thomas Spuhler <tspuhler@mandriva.org> 3.3.8-3mdv2011.0
+ Revision: 574251
- +Requires:   horde-imp
  +Requires:   horde-vacation
  +Requires:   php-imagick

* Mon Aug 16 2010 Thomas Spuhler <tspuhler@mandriva.org> 3.3.8-2mdv2011.0
+ Revision: 570272
- added requires so that the packages has actually some use

* Sun Aug 08 2010 Thomas Spuhler <tspuhler@mandriva.org> 3.3.8-1mdv2011.0
+ Revision: 567485
- Updated to version 3.3.8
- Updated to version 3.3.8

* Mon Jan 18 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.3.6-2mdv2010.1
+ Revision: 493340
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise

* Sat Dec 26 2009 Funda Wang <fwang@mandriva.org> 3.3.6-1mdv2010.1
+ Revision: 482411
- new version 3.3.6

* Mon Nov 30 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.3.5-4mdv2010.1
+ Revision: 472079
- restrict default access permissions to localhost only, as per new policy

* Tue Sep 15 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.3.5-3mdv2010.0
+ Revision: 443224
- update registry patch for new files setup

* Tue Sep 15 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.3.5-2mdv2010.0
+ Revision: 443219
- simpler setup (easier to maintain)

* Tue Sep 15 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.3.5-1mdv2010.0
+ Revision: 442820
- new version

* Tue Jun 09 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.3.4-1mdv2010.0
+ Revision: 384537
- update to new version 3.3.4

* Fri Jan 30 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.3.3-1mdv2009.1
+ Revision: 335494
- update to new version 3.3.3

* Mon Dec 29 2008 Guillaume Rousse <guillomovitch@mandriva.org> 3.3.2-2mdv2009.1
+ Revision: 320739
- fix automatic dependencies

* Sun Dec 14 2008 Guillaume Rousse <guillomovitch@mandriva.org> 3.3.2-1mdv2009.1
+ Revision: 314343
- new version
- rediff patch to avoid fuzz

* Sun Oct 19 2008 Guillaume Rousse <guillomovitch@mandriva.org> 3.3-1mdv2009.1
+ Revision: 295259
- new version

* Thu Sep 11 2008 Guillaume Rousse <guillomovitch@mandriva.org> 3.2.2-1mdv2009.0
+ Revision: 283884
- update to new version 3.2.2

* Wed Jun 25 2008 Guillaume Rousse <guillomovitch@mandriva.org> 3.2.1-1mdv2009.0
+ Revision: 228893
- new version

* Thu Jun 12 2008 Guillaume Rousse <guillomovitch@mandriva.org> 3.2-3mdv2009.0
+ Revision: 218443
- really fix wrong automatic dependency issue

* Wed Jun 11 2008 Guillaume Rousse <guillomovitch@mandriva.org> 3.2-2mdv2009.0
+ Revision: 218230
- fix wrong include name triggering a false automatic dependency (#41288)

* Wed May 28 2008 Guillaume Rousse <guillomovitch@mandriva.org> 3.2-1mdv2009.0
+ Revision: 212813
- new version
  drop kolab patches 5, 7 and 8 (merged/unappliable anymore)
  update patches 4 and 6

* Wed Jan 16 2008 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.6-1mdv2008.1
+ Revision: 153777
- new version
- update to new version 3.1.6

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Nov 22 2007 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.5-1mdv2008.1
+ Revision: 111213
- update to new version 3.1.5

* Mon Aug 27 2007 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.4-2mdv2008.0
+ Revision: 71859
- don't fix eols in spec file, spec-helper is doing it
- fix new webroot detection by hardcoding it in registry (fix #32220)

* Thu Aug 02 2007 Funda Wang <fwang@mandriva.org> 3.1.4-1mdv2008.0
+ Revision: 58123
- Rediff patch5
- Rediff patch4
- New version 3.1.4


* Mon Feb 19 2007 Oden Eriksson <oeriksson@mandriva.com> 3.1.3-2mdv2007.0
+ Revision: 122754
- sync with opensuse to enable a possible furure kolab2 update...

  + Andreas Hasenack <andreas@mandriva.com>
    - Import horde

* Sat Aug 26 2006 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.3-1mdv2007.0
- New version 3.1.3

* Sat Aug 12 2006 Andreas Hasenack <andreas@mandriva.com> 3.1.2-2mdv2007.0
- make somewhat backportable

* Tue Jul 11 2006 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.2-1mdv2007.0
- New version 3.1.2

* Sat Jul 01 2006 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.1-3mdv2007.0
- relax buildrequires versionning

* Tue Jun 27 2006 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.1-2mdv2007.0
- new webapp macros 
- decompress all patches
- use herein document for README.mdv

* Thu Mar 30 2006 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.1-1mdk
- New release 3.1.1
- rediff registry patch

* Tue Mar 07 2006 Guillaume Rousse <guillomovitch@mandriva.org> 3.1-1mdk
- new version
- pre-10.2 compatibility
- drop non-interactive setup patch, unused anway
- rediff registry patch

* Wed Jan 11 2006 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.9-2mdk
- add conflict with horde 2 applications
- update README.mdk with application packages mention

* Tue Dec 27 2005 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.9-1mdk
- New release 3.0.9
- %%mkrel

* Wed Nov 02 2005 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.6-1mdk
- New release 3.0.6
- rediff patches 1 and 4

* Sat Aug 20 2005 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.5-1mdk
- New release 3.0.5
- rediff patch 4
- better fix encoding
- drop manual pear requires

* Thu Jun 30 2005 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.4-3mdk 
- better requires
- better fix encoding
- fix requires
- use new rpm macros
- fix scripts shellbang

* Tue Jun 14 2005 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.4-2mdk 
- new apache setup
- requires

* Sun Apr 17 2005 Guillaume Rousse <guillomovitch@mandrake.org> 3.0.4-1mdk
- New release 3.0.4

* Fri Feb 18 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 3.0.2-4mdk
- spec file cleanups, remove the ADVX-build stuff
- strip away annoying ^M

* Thu Jan 27 2005 Guillaume Rousse <guillomovitch@mandrake.org> 3.0.2-3mdk 
- reload apache instead of restarting it
- no more automatic config generation, incorrect default values
- README.mdk
- spec cleanup
- don't touch log file, make log dir owned by apache

* Mon Jan 17 2005 Guillaume Rousse <guillomovitch@mandrake.org> 3.0.2-2mdk 
- herein document instead of external source for apache config
- fix inclusions from /usr/share/horde
- fix configuration perms
- generate configuration at postinstall
- better default configuration (logs)
- rpm-helper is now a prereq

* Thu Jan 13 2005 Guillaume Rousse <guillomovitch@mandrake.org> 3.0.2-1mdk 
- New version
- top-level is now /var/www/horde
- config is now in /etc/horde
- other non-accessible files are now in /usr/share/horde
- drop safemode build
- drop patches 0, 2 and 3
- rediff patch 4
- drop old obsoletes
- clean up redundant requires
- no more order for apache configuration

* Wed Oct 27 2004 Guillaume Rousse <guillomovitch@mandrakesoft.com> 2.2.7-1mdk
- New release 2.2.7

* Tue Sep 28 2004 Guillaume Rousse <guillomovitch@mandrakesoft.com> 2.2.6-1mdk
- New release 2.2.6
- rpmbuildupdate aware

* Mon Jul 19 2004 Guillaume Rousse <guillomovitch@mandrake.org> 2.2.5-3mdk 
- apache config file in /etc/httpd/webapps.d

* Sun May 02 2004 Guillaume Rousse <guillomovitch@mandrake.org> 2.2.5-2mdk
- registry patch (stolen from Debian)
- standard perms for /etc/httpd/conf.d/%%{order}_horde.conf
- don't provide useless ADVXpackage virtual package

* Tue Apr 06 2004 Guillaume Rousse <guillomovitch@mandrake.org> 2.2.5-1mdk
- new version
- dropped original configuration patch, it's up to application packages to
  register themselves
- fixed sendmail path in configuration

