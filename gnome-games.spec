%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define gettext_package gnome-games

%define build_card 1
%define build_tali 1

%if %{build_card}
%define card_schemas aisleriot.schemas
%define card_schemas_extra blackjack.schemas
%define card_desktops $RPM_BUILD_ROOT%{_datadir}/applications/gnome-sol.desktop $RPM_BUILD_ROOT%{_datadir}/applications/gnome-freecell.desktop
%else
%define card_schemas %{nil}
%define card_schemas_extra %{nil}
%define card_desktops %{nil}
%endif

%if %{build_tali}
%define gtali_schemas gtali.schemas
%else
%define gtali_schemas %{nil}
%endif

%if !%{build_card} && !%{build_tali}
%define omitgames --enable-omitgames=aisleriot,blackjack,gtali
%else
%if !%{build_card}
%define omitgames --enable-omitgames=aisleriot,blackjack
%else
%if !%{build_tali}
%define omitgames --enable-omitgames=gtali
%else
%define omitgames %{nil}
%endif
%endif
%endif

%define glib2_version 2.12.0
%define pango_version 1.8.0
%define gtk2_version 2.6.0
%define libgnomeui_version 2.5.0
%define desktop_file_utils_version 0.2.90
%define gnome_python_desktop 2.17.3
%define gstreamer_version 0.10.3

Summary: Games for the GNOME desktop
Name: gnome-games
Version: 2.28.2
Release: 2%{?dist}
Epoch: 1
License: GPLv2+ and GFDL
Group: Amusements/Games
Source: http://download.gnome.org/sources/gnome-games/2.28/gnome-games-%{version}.tar.bz2
# http://bugzilla.gnome.org/show_bug.cgi?id=551455
Patch0: ggz-api-changes.patch
Patch1: gnome-games-2.19.4-gnometris-rebrand.patch
# https://bugzilla.gnome.org/show_bug.cgi?id=613634
Patch2: gnome-games-dir-prefix.patch

BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Obsoletes: gnome-games-devel
URL: http://projects.gnome.org/gnome-games/

Requires(pre): GConf2
Requires(post): GConf2
Requires(preun): GConf2

Requires: GConf2
Requires: pygtk2
Requires: gnome-python2-gconf
Requires: hicolor-icon-theme

BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: pango-devel >= %{pango_version}
BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: pygtk2-devel
BuildRequires: gnome-python2-desktop >= %{gnome_python_desktop}
BuildRequires: libgnomeui-devel >= %{libgnomeui_version}
BuildRequires: desktop-file-utils >= %{desktop_file_utils_version}
BuildRequires: librsvg2-devel
BuildRequires: guile-devel >= 1.6.5
BuildRequires: expat-devel
BuildRequires: gstreamer-devel >= %{gstreamer_version}
BuildRequires: libcanberra-devel
BuildRequires: clutter-devel clutter-gtk-devel
BuildRequires: intltool

# Newer than internal gettext needed
BuildRequires: gettext
BuildRequires: autoconf >= 2.60
BuildRequires: gnome-doc-utils >= 0.3.2

BuildRequires: libggz-devel
BuildRequires: ggz-client-libs-devel
Requires(post): ggz-client-libs
Requires(preun): ggz-client-libs

Provides: gnome-sudoku
Obsoletes: gnome-sudoku

Provides: glchess
Obsoletes: glchess < 2.0


%description
The gnome-games package is a collection of some small "five-minute" games
in a variety of styles and genres for the GNOME desktop.


%package extra
Group: Amusements/Games
Summary: More games for the GNOME desktop
Requires: %{name} = %{epoch}:%{version}-%{release}
Requires: pygtkglext
Requires: PyOpenGL
Requires: gnuchess

%description extra
The gnome-games-extra package contains additional small "five-minute" games
in a variety of styles and genres for the GNOME desktop.


%package help
Group: Applications/Productivity
Summary: Help files for %{name}
Requires: %{name} = %{epoch}:%{version}-%{release}
BuildArch: noarch

%description help
This package contains user documentation for %{name}.

%prep
%setup -q
%patch0 -p1 -b .ggz-api-changes
# rebrand gnometris as some think the name is to similar to a trademark
%patch1 -p1 -b .rebrand
%patch2 -p1 -b .dir-prefix

sed -i -e 's/Gnometris/GnomeFallingBlocks/g' \
  -e 's/GNOMEtris/GnomeFallingBlocks/g' \
  po/*.po gnometris/help/*/*.po gnometris/help/C/gnometris.xml \
  gnometris/*.cpp gnometris/gnometris.desktop.in.in

#cp -f gnometris/sounds/gameover.wav gnobots2/bad.wav
#cp -f gnometris/sounds/gameover.wav gnibbles/sounds/pop.wav

%build

autoconf
export CFLAGS="$RPM_OPT_FLAGS -DNO_HOWL"
%configure --localstatedir=/var/lib \
           --disable-gnuchess \
           --disable-introspection \
           %{omitgames}
make

# strip unneeded translations from .mo files
# ideally intltool (ha!) would do that for us
# http://bugzilla.gnome.org/show_bug.cgi?id=474987
cd po
grep -v ".*[.]desktop[.]in[.]in$\|.*[.]server[.]in[.]in$" POTFILES.in > POTFILES.keep
mv POTFILES.keep POTFILES.in
intltool-update --pot
for p in *.po; do
  msgmerge $p %{gettext_package}.pot > $p.out
  msgfmt -o `basename $p .po`.gmo $p.out
done


%install
rm -rf $RPM_BUILD_ROOT

export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

mv $RPM_BUILD_ROOT%{_bindir}/gnometris \
  $RPM_BUILD_ROOT%{_bindir}/gnome-falling-blocks

## things we just don't want in the package

rm -rf $RPM_BUILD_ROOT%{_libdir}/libgdkcardimage.*a
rm -rf $RPM_BUILD_ROOT/var/lib/scrollkeeper

## install desktop files
desktop-file-install --vendor gnome --delete-original       \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications             \
  --remove-category Application				    \
  --remove-category PuzzleGame				    \
  $RPM_BUILD_ROOT%{_datadir}/applications/*

desktop-file-install --vendor gnome --delete-original       \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications             \
  $RPM_BUILD_ROOT%{_datadir}/applications/gnome-glines.desktop \
  $RPM_BUILD_ROOT%{_datadir}/applications/gnome-gnect.desktop \
  %{card_desktops}

%if %{build_tali}
perl -pi -e 's@<default></default>@<default>[Joe,Jim,James]</default>@g' $RPM_BUILD_ROOT%{_sysconfdir}/gconf/schemas/gtali.schemas
%endif

# we need this in %%post
cp gnect/data/gnect-client.dsc $RPM_BUILD_ROOT%{_datadir}/ggz
cp gnibbles/gnibbles-client.dsc $RPM_BUILD_ROOT%{_datadir}/ggz
cp iagno/iagno-client.dsc $RPM_BUILD_ROOT%{_datadir}/ggz

# but we don't want this
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/ggz.modules

%find_lang %{gettext_package} --all-name --with-gnome
grep "/usr/share/locale" %{gettext_package}.lang > translations.lang
grep -v "/usr/share/locale" %{gettext_package}.lang > help.lang

%clean
rm -rf $RPM_BUILD_ROOT

%post
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
(cd %{_sysconfdir}/gconf/schemas;   \
gconftool-2 --makefile-install-rule \
	%{card_schemas}             \
	gnomine.schemas             \
	iagno.schemas               \
	same-gnome.schemas          \
	gnome-sudoku.schemas	    \
> /dev/null || : )

touch %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi

ggz-config -i -f -m %{_datadir}/ggz/iagno-client.dsc >& /dev/null || :

%post extra
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
(cd %{_sysconfdir}/gconf/schemas;   \
gconftool-2 --makefile-install-rule \
	%{card_schemas_extra}       \
	%{gtali_schemas}            \
	glchess.schemas             \
	glines.schemas              \
	gnect.schemas               \
	gnibbles.schemas            \
	gnobots2.schemas            \
	gnometris.schemas           \
	gnotravex.schemas           \
	gnotski.schemas             \
	mahjongg.schemas            \
> /dev/null || : )

touch %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi

ggz-config -i -f -m %{_datadir}/ggz/gnect-client.dsc >& /dev/null || :
ggz-config -i -f -m %{_datadir}/ggz/gnibbles-client.dsc >& /dev/null || :

%pre
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  (cd %{_sysconfdir}/gconf/schemas;   \
  gconftool-2 --makefile-uninstall-rule \
	%{card_schemas}             \
	gnomine.schemas             \
	iagno.schemas               \
	same-gnome.schemas          \
	gnome-sudoku.schemas	    \
> /dev/null || : )
fi

%pre extra
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  (cd %{_sysconfdir}/gconf/schemas;   \
  gconftool-2 --makefile-uninstall-rule \
	%{card_schemas_extra}       \
	%{gtali_schemas}            \
	glchess.schemas             \
	glines.schemas              \
	gnect.schemas               \
	gnibbles.schemas            \
	gnobots2.schemas            \
	gnometris.schemas           \
	gnotravex.schemas           \
	gnotski.schemas             \
	mahjongg.schemas            \
> /dev/null || : )
fi

%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  (cd %{_sysconfdir}/gconf/schemas;   \
  gconftool-2 --makefile-uninstall-rule \
	%{card_schemas}             \
	gnomine.schemas             \
	iagno.schemas               \
	same-gnome.schemas          \
	gnome-sudoku.schemas	    \
> /dev/null || : )

  ggz-config -r -m %{_datadir}/ggz/iagno-client.dsc >& /dev/null || :
fi

%preun extra
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  (cd %{_sysconfdir}/gconf/schemas;   \
  gconftool-2 --makefile-uninstall-rule \
	%{card_schemas_extra}       \
	%{gtali_schemas}            \
	glchess.schemas             \
	glines.schemas              \
	gnect.schemas               \
	gnibbles.schemas            \
	gnobots2.schemas            \
	gnometris.schemas           \
	gnotravex.schemas           \
	gnotski.schemas             \
	mahjongg.schemas            \
> /dev/null || : )

  ggz-config -r -m %{_datadir}/ggz/gnect-client.dsc >& /dev/null || :
  ggz-config -r -m %{_datadir}/ggz/gnibbles-client.dsc >& /dev/null || :
fi

%postun
touch %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi

%postun extra
touch %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi

%files help -f help.lang

%files -f translations.lang
%defattr(-, root, root)
%doc AUTHORS COPYING README
%{_datadir}/applications/gnome-sol.desktop
%{_datadir}/applications/gnome-gnomine.desktop
%{_datadir}/applications/gnome-iagno.desktop
%{_datadir}/applications/gnome-same-gnome.desktop
%{_datadir}/applications/gnome-sudoku.desktop

%dir %{_datadir}/gnome-games
%{_datadir}/gnome-games/aisleriot
%{_datadir}/gnome-games/gnomine
%{_datadir}/gnome-games/iagno
%{_datadir}/gnome-games/same-gnome
%{_datadir}/gnome-games/icons
%{_datadir}/gnome-games/sounds
%{_datadir}/gnome-games/pixmaps
%{_datadir}/gnome-games-common
%{_datadir}/gnome-sudoku

%{_datadir}/icons/hicolor/*/apps/gnome-aisleriot.*
%{_datadir}/icons/hicolor/*/apps/gnome-iagno.*
%{_datadir}/icons/hicolor/*/apps/gnome-mines.*
%{_datadir}/icons/hicolor/*/apps/gnome-samegnome.*
%{_datadir}/icons/hicolor/*/apps/gnome-sudoku.*

%verify(not md5 size mtime) %config(noreplace) %attr(664, games, games) /var/lib/games/same-gnome.*
%verify(not md5 size mtime) %config(noreplace) %attr(664, games, games) /var/lib/games/gnomine.*

%{_libdir}/gnome-games

%{python_sitelib}/gnome_sudoku

# gconf schemas
%if %{build_card}
%{_sysconfdir}/gconf/schemas/aisleriot.schemas
%endif
%{_sysconfdir}/gconf/schemas/gnomine.schemas
%{_sysconfdir}/gconf/schemas/iagno.schemas
%{_sysconfdir}/gconf/schemas/same-gnome.schemas
%{_sysconfdir}/gconf/schemas/gnome-sudoku.schemas

%{_datadir}/ggz/gnome-games
%{_datadir}/ggz/iagno-client.dsc

# these are not setgid games
%{_bindir}/sol
%{_bindir}/gnome-sudoku

# these are setgid games
%attr(2551, root, games) %{_bindir}/same-gnome
%attr(2551, root, games) %{_bindir}/iagno
%attr(2551, root, games) %{_bindir}/gnomine

%{_mandir}/man6/same-gnome.6.gz
%{_mandir}/man6/iagno.6.gz
%{_mandir}/man6/gnomine.6.gz
%{_mandir}/man6/gnome-sudoku.6.gz
%{_mandir}/man6/sol.6.gz

%files extra
%defattr(-, root, root)

%{python_sitelib}/glchess
%{_datadir}/glchess

%{_datadir}/applications/gnome-blackjack.desktop
%{_datadir}/applications/gnome-freecell.desktop
%{_datadir}/applications/gnome-glchess.desktop
%{_datadir}/applications/gnome-glines.desktop
%{_datadir}/applications/gnome-gnect.desktop
%{_datadir}/applications/gnome-gnibbles.desktop
%{_datadir}/applications/gnome-gnobots2.desktop
%{_datadir}/applications/gnome-gnotravex.desktop
%{_datadir}/applications/gnome-gnotski.desktop
%{_datadir}/applications/gnome-gtali.desktop
%{_datadir}/applications/gnome-mahjongg.desktop
%{_datadir}/applications/gnometris.desktop

%{_mandir}/man6/blackjack.6.gz
%{_mandir}/man6/glchess.6.gz
%{_mandir}/man6/glines.6.gz
%{_mandir}/man6/gnect.6.gz
%{_mandir}/man6/gnibbles.6.gz
%{_mandir}/man6/gnobots2.6.gz
%{_mandir}/man6/gnometris.6.gz
%{_mandir}/man6/gnotravex.6.gz
%{_mandir}/man6/gnotski.6.gz
%{_mandir}/man6/gtali.6.gz
%{_mandir}/man6/mahjongg.6.gz

%verify(not md5 size mtime) %config(noreplace) %attr(664, games, games) /var/lib/games/glines.*
%verify(not md5 size mtime) %config(noreplace) %attr(664, games, games) /var/lib/games/gnibbles.*
%verify(not md5 size mtime) %config(noreplace) %attr(664, games, games) /var/lib/games/gnobots2.*
%verify(not md5 size mtime) %config(noreplace) %attr(664, games, games) /var/lib/games/gnometris.*
%verify(not md5 size mtime) %config(noreplace) %attr(664, games, games) /var/lib/games/gnotravex.*
%verify(not md5 size mtime) %config(noreplace) %attr(664, games, games) /var/lib/games/gnotski.*
%verify(not md5 size mtime) %config(noreplace) %attr(664, games, games) /var/lib/games/gtali.*
%verify(not md5 size mtime) %config(noreplace) %attr(664, games, games) /var/lib/games/mahjongg.*


# these are not setgid games
%{_bindir}/gnect
%if %{build_card}
%{_bindir}/blackjack
%endif
%{_bindir}/glchess

# these are setgid games
%attr(2551, root, games) %{_bindir}/mahjongg
%if %{build_tali}
%attr(2551, root, games) %{_bindir}/gtali
%endif
%attr(2551, root, games) %{_bindir}/gnobots2
%attr(2551, root, games) %{_bindir}/gnome-falling-blocks
%attr(2551, root, games) %{_bindir}/gnotravex
%attr(2551, root, games) %{_bindir}/gnotski
%attr(2551, root, games) %{_bindir}/gnibbles
%attr(2551, root, games) %{_bindir}/glines

# gconf schemas
%if %{build_card}
%{_sysconfdir}/gconf/schemas/blackjack.schemas
%endif
%{_sysconfdir}/gconf/schemas/glines.schemas
%{_sysconfdir}/gconf/schemas/gnect.schemas
%{_sysconfdir}/gconf/schemas/gnibbles.schemas
%{_sysconfdir}/gconf/schemas/gnobots2.schemas
%{_sysconfdir}/gconf/schemas/gnometris.schemas
%{_sysconfdir}/gconf/schemas/gnotravex.schemas
%{_sysconfdir}/gconf/schemas/gnotski.schemas
%if %{build_tali}
%{_sysconfdir}/gconf/schemas/gtali.schemas
%endif
%{_sysconfdir}/gconf/schemas/mahjongg.schemas
%{_sysconfdir}/gconf/schemas/glchess.schemas

%{_datadir}/gnome-games/blackjack
%{_datadir}/gnome-games/glines
%{_datadir}/gnome-games/gnect
%{_datadir}/gnome-games/gnibbles
%{_datadir}/gnome-games/gnobots2
%{_datadir}/gnome-games/gnometris
%{_datadir}/gnome-games/gtali
%{_datadir}/gnome-games/mahjongg
%{_datadir}/gnome-games/gnotski

%{_datadir}/ggz/gnect-client.dsc
%{_datadir}/ggz/gnibbles-client.dsc

%{_datadir}/icons/hicolor/*/apps/gnome-blackjack.*
%{_datadir}/icons/hicolor/*/apps/gnome-freecell.*
%{_datadir}/icons/hicolor/*/apps/gnome-glchess.*
%{_datadir}/icons/hicolor/*/apps/gnome-glines.*
%{_datadir}/icons/hicolor/*/apps/gnome-gnect.*
%{_datadir}/icons/hicolor/*/apps/gnome-gnibbles.*
%{_datadir}/icons/hicolor/*/apps/gnome-gnometris.*
%{_datadir}/icons/hicolor/*/apps/gnome-klotski.*
%{_datadir}/icons/hicolor/*/apps/gnome-mahjongg.*
%{_datadir}/icons/hicolor/*/apps/gnome-robots.*
%{_datadir}/icons/hicolor/*/apps/gnome-tali.*
%{_datadir}/icons/hicolor/*/apps/gnome-tetravex.*


%changelog
* Mon Mar 22 2010 Ray Strode <rstrode@redhat.com> 2.28.2-2
Resolves: #575937
- Allow .gnome2 to be relocated

* Mon Jan  4 2010 Matthias Clasen <mclasen@redhat.com> 2.28.2-1
- Update to 2.28.2, sync with Fedora 12

* Mon Oct 19 2009 Matthias Clasen <mclasen@redhat.com> 2.28.1-1
- Update to 2.28.1

* Mon Sep 22 2009 Matthias Clasen <mclasen@redhat.com> 2.28.0-1
- Update to 2.28.0

* Mon Sep  7 2009 Matthias Clasen <mclasen@redhat.com> 2.27.92-1
- Update to 2.27.92

* Sun Aug 23 2009 Matthias Clasen <mclasen@redhat.com> 2.27.90-2
- Fix various issues in Mines

* Fri Aug 14 2009 Matthias Clasen <mclasen@redhat.com> 2.27.90-1
- Updated to 2.27.90

* Fri Jul 31 2009 Matthias Clasen <mclasen@redhat.com> 2.27.5-5
- Drop unneeded python deps

* Fri Jul 31 2009 Matthias Clasen <mclasen@redhat.com> 2.27.5-4
- Fix a typo (#515033)

* Fri Jul 31 2009 Matthias Clasen <mclasen@redhat.com> 2.27.5-3
- Split off a subset of games to include on the live cd

* Thu Jul 30 2009 Bastien Nocera <bnocera@redhat.com> 2.27.5-2
- Rebuild for new clutter-gtk and clutter

* Tue Jul 28 2009 Matthias Clasen <mclasen@redhat.com> 2.27.5-1
- Update to 2.27.5

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.27.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Matthias Clasen <mclasen@redhat.com> 2.27.4-1
- Update to 2.27.4

* Sat Jun 20 2009 Bastien Nocera <bnocera@redhat.com> 2.27.3-1
- Update to 2.27.3

* Sun Jun 14 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.2-2
- Minor directory ownership cleanup

* Wed May 27 2009 Bastien Nocera <bnocera@redhat.com> 2.27.2-1
- Update to 2.27.2

* Mon May 18 2009 Bastien Nocera <bnocera@redhat.com> 2.27.1-1
- Update to 2.27.1

* Mon Apr 27 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.26.1-2
- don't drop schemas translations from po files

* Tue Apr 14 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/gnome-games/2.26/gnome-games-2.26.1.news

* Wed Apr  1 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.26.0-2
- Add a workaround for sudoku crashing on certain saved games (#492962)

* Mon Mar 16 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.26.0-1
- Update to 2.26.0

* Mon Mar  2 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.25.92-1
- Update 2.25.92

* Tue Feb 24 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.25.91-2
- Make gnome-games-help noarch

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Feb 19 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.25.91-1
- Update to 2.25.91

* Tue Feb  3 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.25.90-1
- Update to 2.25.90

* Fri Jan 23 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.25.5-1
- Update to 2.25.5

* Tue Jan  6 2009 Matthias Clasen <mclasen@redhat.com> - 1:2.25.4-1
- Update to 2.25.4

* Wed Dec 17 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.25.3-1
- Update to 2.25.3

* Thu Dec  4 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.25.2-2
- Rebuild for Python 2.6

* Wed Dec  3 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.25.2-1
- Update to 2.25.2

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1:2.25.1-4
- Rebuild for Python 2.6

* Fri Nov 21 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.25.1-3
- Better URL
- Tweak description

* Thu Nov 13 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.25.1-2
- Update to 2.25.1

* Mon Oct 20 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.24.1-1
- Update to 2.24.1

* Thu Sep 25 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.24.0-2
- Save some space

* Sun Sep 21 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.24.0-1
- Update to 2.24.0

* Mon Sep  8 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.92-1
- Update to 2.23.92
- Adapt to api changes in the ggz snapshot we ship

* Sat Aug 23 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.90-1
- Update to 2.23.90

* Fri Aug  8 2008 Colin Walters <walters@redhat.com> - 1:2.23.6-2
- Split out -help into separate package for size reasons

* Tue Aug  5 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.6-1
- Update to 2.23.6

* Wed Jul 23 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1:2.23.5-2
- fix license tag

* Tue Jul 22 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.5-1
- Update to 2.23.5

* Wed Jun 18 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.4-1
- Update to 2.23.4

* Tue Jun  3 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.3-1
- Update to 2.23.3

* Sun May 11 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.1-2
- Add missing Requires for gnome-sudoko (#445941)

* Fri Apr 25 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.23.1-1
- Update to 2.23.1

* Fri Apr 18 2008 Ray Strode <rstrode@redhat.com> - 1:2.22.1.1-4
- Use gtk-missing-image instead of image-missing since a lot of
  icon themes don't have missing-image and gtk-missing-image is
  guaranteed to be available (bug 440686)

* Thu Apr 17 2008 Ray Strode <rstrode@redhat.com> - 1:2.22.1.1-3
- Fix typo in previous patch (bug 440686)

* Wed Apr 16 2008 Ray Strode <rstrode@redhat.com> - 1:2.22.1.1-2
- Make glchess behave better in case of incomplete icon themes
  (bug 440686)

* Tue Apr  8 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.22.1.1-1
- Update to 2.22.1 (sudoko crasher fixes)

* Mon Apr  7 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.22.1-1
- Update to 2.22.1

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.22.0-1
- Update to 2.22.0

* Thu Mar  6 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.21.92-2
- Drop OnlyShowIn=GNOME

* Tue Feb 26 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.21.92-1
- Update to 2.21.92

* Wed Feb 13 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.21.91-1
- Update to 2.21.91

* Fri Feb  8 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.21.90-2
- Fix ggz deps

* Tue Jan 29 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.21.90-1
- Update to 2.21.90 

* Tue Jan 15 2008 Matthias Clasen <mclasen@redhat.com> - 1:2.21.5-1
- Update to 2.21.5

* Tue Dec 18 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.21.4-1
- Update to 2.21.4

* Tue Dec 11 2007 Hans de Goede <j.w.r.degoede@hhs.nl> - 1:2.21.3-2
- Fix rpm --verify complaining about the highscore files once a highscore has
  been added (bz 418991)

* Thu Dec  6 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.21.3-1
- Update to 2.21.3
- Build against system ggz packages

* Tue Nov 13 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.21.2-1
- Update to 2.21.2

* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.20.1-1
- Update to 2.20.1 (bug fixes)
- Drop obsolete patch

* Tue Oct  9 2007 Hans de Goede <j.w.r.degoede@hhs.nl> - 1:2.20.0.1-2
- Fix gnobots from crashing with certain combinations of options (bz 324221)

* Tue Sep 18 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.20.0.1-1
- Update to 2.20.0.1

* Tue Sep 18 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.20.0-1
- Update to 2.20.0

* Tue Sep  4 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.92-1
- 2.19.92

* Tue Aug 28 2007 Hans de Goede <j.w.r.degoede@hhs.nl> - 1:2.19.90.1-2
- Rebuild for new expat 2.0

* Tue Aug 14 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.90.1-1
- 2.19.90.1

* Sun Aug 12 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.90b-1
- 2.19.90b

* Sat Aug 11 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.90-1
- 2.19.90

* Tue Aug  7 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.6-4
- Add documentation license

* Sun Aug  5 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.6-3
- Use find-lang for help files, too

* Fri Aug  3 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.6-2
- Update the license field

* Sat Jul 28 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.6-1
- Update to 2.19.6

* Sat Jul 21 2007 Hans de Goede <j.w.r.degoede@hhs.nl> - 1:2.19.4-3
- Don't build a private copy of gnuchess, instead require gnuchess (bz 215110)
- Rename / rebrand Gnometris to GnomeFallingBlocks, so that it stays clear of
  the Tetris trademark, and include it (bz 238651)
- Don't own dirs under /usr/share/icons/hicolor, instead add
  Requires: hicolor-icon-theme
- Cleanup handling of with_card and with_tali defines using --enable-omitgames

* Thu Jul  5 2007 Ray Strode <rstrode@redhat.com> - 1:2.19.4-2
- Add glchess back (bug 234127)

* Mon Jun 18 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.4-1
- Update to 2.19.4

* Sat Jun 16 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.3-2
- More complete runtime requirements for sudoko (#241884)

* Mon Jun  4 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.3-1
- Update to 2.19.3
- Add a BuildRequires for gstreamer

* Sat May 19 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.19.2-1
- Update to 2.19.2
- Fix file lists

* Mon May  7 2007 Ray Strode <rstrode@redhat.com> - 1:2.18.1.1-1
- update to 2.18.1.1 at the request of Andreas Røsdal

* Sun Apr  8 2007 Ray Strode <rstrode@redhat.com> - 1:2.18.0-5
- Add Obsoletes: gnome-chess (bug 234127)

* Mon Apr  2 2007 Ray Strode <rstrode@redhat.com> - 1:2.18.0-4
- Add minimum version to gnome-python2-desktop buildreq 
  (bug 234892)

* Wed Mar 28 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.18.0-3
- Split of gnome-games-extra-data as a separate package
- Correct the License tag

* Fri Mar 23 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.18.0-2
- Fix the icon in the blackjack about dialog (#233649)

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.18.0-1
- Update to 2.18.0

* Tue Feb 27 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.17.92-1
- Update to 2.17.92

* Tue Feb 13 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.17.91-1
- Update to 2.17.91

* Wed Jan 24 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.17.90.1-1
- Update to 2.17.90.1

* Mon Jan 22 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.17.90-2
- Update extra data to 2.17.90

* Mon Jan 22 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.17.90-1
- Update to 2.17.90
- Fix some directory ownership issues

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 1:2.17.5-1
- Update to 2.17.5

* Wed Dec 20 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.17.4.1-1
- Update to 2.17.4.1

* Thu Dec  7 2006 Jeremy Katz <katzj@redhat.com> - 1:2.17.3-2
- rebuild for python 2.5

* Tue Dec  5 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.17.3-1
- Update to 2.17.3

* Thu Nov 16 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.17.2-4
- Use Conflicts for gnuchess instead

* Wed Nov 15 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.17.2-3
- Add Provides/Obsoletes for gnuchess (#215110)

* Wed Nov  8 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.17.2-2
- Add Provides/Obsoletes for gnome-sudoku (#214589)

* Tue Nov  7 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.17.2-1
- Update to 2.17.2

* Sat Oct 21 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.17.1-1
- Update to 2.17.1

* Tue Sep  5 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.16.0-1.fc6
- Update to 2.16.0

* Mon Aug 21 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.92-1.fc6
- Update to 2.15.92

* Sat Aug 12 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.6-1.fc6
- Update to 2.15.6

* Thu Aug  2 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.5-1.fc6
- Update to 2.15.5
- Bump glib requirement (#197566)

* Tue Jul 25 2006 Ray Strode <rstrode@redhat.com> - 1:2.15.4-3
- install new gconf schemas. rework the way we do it to be more
  future proof (bug 193777)

* Tue Jul 25 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.4-2
- Require librsvg2 (#191576)

* Wed Jul 12 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.4-1
- Update to 2.15.4

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1:2.15.3-1.1
- rebuild

* Tue Jun 13 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.3-1
- Update to 2.15.3

* Wed May 16 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.2-1
- Update to 2.15.2

* Tue May 16 2006 Ray Strode <rstrode@redhat.com> - 1:2.15.1-2
- Apply spec file patch from 
  Hooman Mesgary <hooman@farsiweb.info> to conditionallly
  compile out some of the games (bug 192001)

* Wed May 10 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.15.1-1
- Update to 2.15.1

* Tue May 9 2006 Ray Strode <rstrode@redhat.com> - 1:2.14.1-4
- rebuild

* Mon Apr 24 2006 Matthias Clasen <mclasen@redhat.com> - 1:2.14.1-3
- Update the extra data to 2.14.0

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.1-2
- Update to 2.14.1

* Mon Mar 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.0-1
- Update to 2.14.0

* Thu Feb 23 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.8-1
- Update to 2.13.8

* Mon Feb 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.7-1
- Update to 2.13.7

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1:2.13.6-3.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1:2.13.6-3.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Sat Feb  4 2006 Matthias Clasen <mclasen@redhat.com> 1:2.13.6-3
- Remove unneeded gstreamer dependency

* Mon Jan 30 2006 Matthias Clasen <mclasen@redhat.com> 1:2.13.6-1
- Update to 2.13.6

* Mon Jan 23 2006 Christopher Aillon <caillon@redhat.com> 1:2.13.5-2
- Add patch to fix parse errors with aunt mary.

* Tue Jan 17 2006 Matthias Clasen <mclasen@redhat.com> 1:2.13.5-1
- Update to 2.13.5

* Fri Jan 06 2006 Ray Strode <rstrode@redhat.com> 1:2.13.4-2
- remove "Windows" theme from gnobots

* Tue Jan 03 2006 Matthias Clasen <mclasen@redhat.com> 1:2.13.4-1
- Update to 2.13.4

* Thu Dec 15 2005 Matthias Clasen <mclasen@redhat.com> 1:2.13.3-1
- Update to 2.13.3

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Dec 1 2005 Matthias Clasen <mclasen@redhat.com> 1:2.13.2-1
- Update to 2.13.2

* Wed Nov 2 2005 Ray Strode <rstrode@redhat.com> 1:2.12.1-4
- don't link to howl now that we aren't using it

* Mon Oct 31 2005 Ray Strode <rstrode@redhat.com> 1:2.12.1-3
- rebuild

* Mon Oct 31 2005 Ray Strode <rstrode@redhat.com> 1:2.12.1-2
- remove howl dependency
- modernize make install lines

* Thu Oct  6 2005 Matthias Clasen <mclasen@redhat.com> 1:2.12.1-1
- Update to 2.12.1

* Thu Sep  8 2005 Matthias Clasen <mclasen@redhat.com> 1:2.12.0-1
- Update to 2.12.0

* Tue Aug 16 2005 Matthias Clasen <mclasen@redhat.com> 
- New upstream version

* Fri Aug  5 2005 Matthias Clasen <mclasen@redhat.com> 1:2.11.3-1
- New upstream version

* Mon Jul 11 2005 Matthias Clasen <mclasen@redhat.com> 1:2.11.1-1
- Update to 2.11.1

* Fri May 20 2005 Ray Strode <rstrode@redhat.com> 1:2.10.0-5
- Fix gnibbles crasher, patch from 
  Richard Hoelscher <rah@rahga.com> (bug 158269).

* Thu May 19 2005 Ray Strode <rstrode@redhat.com> 1:2.10.0-4
- Change some sounds around

* Sun Apr 10 2005 Warren Togami <wtogami@redhat.com> 1:2.10.0-3
- undo previous change
- remove unnecessary ldconfig calls
- remove crack obsolete

* Sun Apr 10 2005 Ray Strode <rstrode@redhat.com> 1:2.10.0-2
- Add requires line for guile (bug 154297)

* Fri Apr  8 2005 Ray Strode <rstrode@redhat.com> 1:2.10.0-1
- Update to 2.10.0

* Wed Feb  9 2005 Matthias Clasen <mclasen@redhat.com> 1:2.9.6-1
- Update to 2.9.6
- Needs to wait for newer guile

* Tue Oct 19 2004 Christopher Aillon <caillon@redhat.com> 1:2.8.0-4
- Remove gnome-stones for now

* Thu Oct 14 2004 Marco Pesenti Gritti <mpg@redhat.com> 1:2.8.0-3
- 135591 Ataxx crashes on launch

* Thu Sep 30 2004 GNOME <jrb@redhat.com> - 1:2.8.0-2
- fix crasher, #134256

* Wed Sep 22 2004 Christopher Aillon <caillon@redhat.com> 2.8.0-1
- Update to 2.8.0 and gnome-games-extra-data 2.8.0

* Mon Aug 23 2004 Christopher Aillon <caillon@redhat.com> 2.7.7-1
- Update to 2.7.7 including gnome-games-extra-data-2.7.0

* Wed Aug 04 2004 Christopher Aillon <caillon@redhat.com> 2.7.6-1
- Update to 2.7.6

* Tue Aug 3 2004 Matthias Clasen <mclasen@redhat.com> 2.7.5-2
- Rebuilt

* Sat Jul 31 2004 Christopher Aillon <caillon@redhat.com> 2.7.5-1
- Bump to 2.7.5

* Wed Jun 30 2004 Christopher Aillon <caillon@redhat.com> 2.6.2-1
- Update to 2.6.2

* Wed Jun 16 2004 Christopher Aillon <caillon@redhat.com>
- Update to 2.6.1

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri May 21 2004 Matthias Clasen <mclasen@redhat.com> 2.6.0.1-3 
- rebuild

* Wed Apr 14 2004 Warren Togami <wtogami@redhat.com> 2.6.0.1-2
- #111114 BR perl-XML-Parser scrollkeeper librsvg2-devel gettext

* Fri Apr  2 2004 Mark McLoughlin <markmc@redhat.com> 2.6.0.1-1
- Update to 2.6.0.1

* Wed Mar 10 2004 Alex Larsson <alexl@redhat.com> 1:2.5.8-1
- update to 2.5.8

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Feb 26 2004 Alexander Larsson <alexl@redhat.com> 1:2.5.7-1
- update to 2.5.7

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jan 27 2004 Jonathan Blandford <jrb@redhat.com> 1:2.5.5-1
- new version

* Tue Oct 21 2003 Jeremy Katz <katzj@redhat.com> 1:2.4.0-3
- add patch so that gtali doesn't crash (#106524)

* Fri Oct  3 2003 Alexander Larsson <alexl@redhat.com> 1:2.4.0-2
- 2.4.0

* Mon Aug 25 2003 Alexander Larsson <alexl@redhat.com> 1:2.3.8-1
- update for gnome 2.3
- don't build aisleriot on ia64 due to some strange guile lib issue

* Mon Jul 28 2003 Havoc Pennington <hp@redhat.com> 1:2.2.1-2
- rebuild

* Mon Jul  7 2003 Havoc Pennington <hp@redhat.com> 1:2.2.1-1
- 2.2.1
- remove "applyschemas" patch fixed upstream
- remove "stonescrash" patch also fixed upstream

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Feb 24 2003 Elliot Lee <sopwith@redhat.com>
- debuginfo rebuild

* Sun Feb 23 2003 Jeremy Katz <katzj@redhat.com> 1:2.2.0-2
- apply the gnect schemas (#84905)
- gnome-stones shouldn't crash on startup (#84904)

* Wed Feb  5 2003 Havoc Pennington <hp@redhat.com> 1:2.2.0-1
- 2.2.0

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Thu Jan  9 2003 Havoc Pennington <hp@redhat.com>
- 2.1.5

* Wed Dec  4 2002 Havoc Pennington <hp@redhat.com>
- munge empty string default value out of gtali.schemas
- increment version numbers on requirements

* Tue Dec  3 2002 Bill Nottingham <notting@redhat.com> 1:2.1.3-2
- rebuild against new guile

* Mon Dec  2 2002 Tim Powers <timp@redhat.com> 1:2.1.3-1
- update to 2.1.3

* Tue Aug 13 2002 Havoc Pennington <hp@redhat.com>
- add some OnlyShowIn

* Mon Aug 12 2002 Havoc Pennington <hp@redhat.com>
- 2.0.3 from gnome 2.0.1

* Tue Aug  6 2002 Havoc Pennington <hp@redhat.com>
- 2.0.2

* Tue Jul 23 2002 Havoc Pennington <hp@redhat.com>
- gnect doesn't like being setgid games
- obsolete gnome-games-devel

* Fri Jul 12 2002 Havoc Pennington <hp@redhat.com>
- add gnect

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun Jun 16 2002 Havoc Pennington <hp@redhat.com>
- 2.0.0
- remove noreplace from the .soundlist files
- add missing schemas
- get rid of gnometris again
- use desktop-file-install

* Fri Jun 07 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Wed Jun  5 2002 Havoc Pennington <hp@redhat.com>
- 1.93.0
- remove empty NEWS/README
- fix ldconfig in post

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- 1.92.0

* Fri May  3 2002 Havoc Pennington <hp@redhat.com>
- 1.91.0

* Fri Apr 19 2002 Havoc Pennington <hp@redhat.com>
- GNOME 2 version
- spec file cleanups
- no devel package
- don't run auto*, just use the "rm from buildroot" approach to lose xbill

* Tue Apr 09 2002 Phil Knirsch <pknirsch@redhat.com>
- Bumped version number for rebuild and relink agains new guile lib

* Tue Aug 14 2001 Jonathan Blandford <jrb@redhat.com>
- Add BuildRequires on ncurses-devel

* Mon Jul 23 2001 Jonathan Blandford <jrb@redhat.com>
- Add BuildRequires

* Sun Jun 24 2001 Elliot Lee <sopwith@redhat.com>
- Bump release + rebuild.

* Fri Apr 20 2001  <jrb@redhat.com>
- New version (1.4.0)

* Tue Apr 17 2001 Jonathan Blandford <jrb@redhat.com>
- New Version.

* Tue Feb 27 2001 Trond Eivind Glomsrød <teg@redhat.com>
- use %%{_tmppath}
- langify

* Mon Aug 21 2000 Nalin Dahyabhai <nalin@redhat.com>
- run ldconfig in post and postun (#16589)
- don't put the post and postun scripts in the middle of the files list --
  that tends to break things (oops)

* Fri Aug 11 2000 Jonathan Blandford <jrb@redhat.com>
- Up Epoch and release

* Fri Aug 04 2000 Havoc Pennington <hp@redhat.com>
- Remove .desktop for gturing

* Mon Jul 17 2000 Jonathan Blandford <jrb@redhat.com>
- Mark high-score files as %config(noreplace).

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Tue Jul 11 2000 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new environment

* Sat Jul 8 2000 Havoc Pennington <hp@redhat.com>
- Remove Docdir

* Tue Jul 03 2000 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new environment

* Thu Jun 15 2000 Owen Taylor <otaylor@redhat.com>
- 1.2.0
- remove gnometris, xbill from subdirs since we don't install
  them and they cause problems with new C compiler
- update autoconf stuff
- remove gturing, add gnotski to the file list

* Thu May 11 2000 Matt Wilson <msw@redhat.com>
- 1.1.90

* Thu Feb 10 2000 Preston Brown <pbrown@redhat.com>
- mark sound event files as config files

* Tue Sep 21 1999 Michael Fulbright <drmike@redhat.com>
- fixed gnotravex to not loop infinitely

* Mon Sep 20 1999 Elliot Lee <sopwith@redhat.com>
- Update to 1.0.40

* Sat Apr 10 1999 Jonathan Blandford <jrb@redhat.com>
- added new sol games and a fix for the old ones.

* Mon Mar 29 1999 Michael Fulbright <drmike@redhat.com>
- removed more offending t*tris stuff

* Thu Mar 18 1999 Michael Fulbright <drmike@redhat.com>
- version 1.0.2
- made gnibbles have correct attr since its setgid
- strip binaries

* Sun Mar 14 1999 Michael Fulbright <drmike@redhat.com>
- added score files to file list

* Thu Mar 04 1999 Michael Fulbright <drmike@redhat.com>
- Version 1.0.1

* Fri Feb 19 1999 Michael Fulbright <drmike@redhat.com>
- removed *tris games

* Mon Feb 15 1999 Michael Fulbright <drmike@redhat.com>
- version 0.99.8
- added sound event lists to file list
- touched up file list some more

* Wed Feb 03 1999 Michael Fulbright <drmike@redhat.com>
- added gnibbles data to file list

* Wed Feb 03 1999 Michael Fulbright <drmike@redhat.com>
- updated to 0.99.7

* Wed Feb 03 1999 Michael Fulbright <drmike@redhat.com>
- updated to 0.99.5

* Mon Jan 18 1999 Michael Fulbright <drmike@redhat.com>
- updated to 0.99.3

* Wed Jan 06 1999 Michael Fulbright <drmike@redhat.com>
- updated to 0.99.1

* Thu Dec 16 1998 Michael Fulbright <drmike@redhat.com>
- updated to 0.99.0 in prep for GNOME 1.0

* Sat Nov 21 1998 Michael Fulbright <drmike@redhat.com>
- updated for 0.30 tree

* Fri Nov 20 1998 Pablo Saratxaga <srtxg@chanae.alphanet.ch>
- use --localstatedir=/var/lib in config state (score files for games
  for exemple will go there).

* Mon Mar 16 1998 Marc Ewing <marc@redhat.com>
- Integrate into gnome-games CVS source tree

