#
# Conditional build:
%bcond_without	gdiplus	# use libjpeg and libtiff instead of system GDIPLUS
#
Summary:	An image loading and scaling library - cross MinGW32 version
Summary(pl.UTF-8):	Biblioteka ładująca i skalująca obrazki - wersja skrośna MinGW32
Name:		crossmingw32-gdk-pixbuf2
Version:	2.30.8
Release:	1
License:	LGPL v2+
Group:		Development/Libraries
Source0:	http://ftp.gnome.org/pub/GNOME/sources/gdk-pixbuf/2.30/gdk-pixbuf-%{version}.tar.xz
# Source0-md5:	4fed0d54432f1b69fc6e66e608bd5542
Patch0:		gdk-pixbuf2-png-nodep.patch
Patch1:		gdk-pixbuf2-gdip.patch
URL:		http://developer.gnome.org/gdk-pixbuf/
BuildRequires:	autoconf >= 2.63
BuildRequires:	automake >= 1:1.11
BuildRequires:	crossmingw32-gcc
BuildRequires:	crossmingw32-glib2 >= 2.37.6
BuildRequires:	crossmingw32-jasper
BuildRequires:	crossmingw32-libpng
BuildRequires:	gettext-devel >= 0.17
BuildRequires:	gtk-doc >= 1.20
BuildRequires:	libtool >= 2:2.2.6
BuildRequires:	pkgconfig >= 1:0.15
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
%if %{without gdiplus}
BuildRequires:	crossmingw32-libjpeg
BuildRequires:	crossmingw32-libtiff
%endif
Requires:	crossmingw32-glib2 >= 2.37.6
Conflicts:	crossmingw32-gtk+2 < 2.22.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		abiver	2.10.0

%define		no_install_post_strip	1

%define		target			i386-mingw32
%define		target_platform 	i386-pc-mingw32

%define		_sysprefix		/usr
%define		_prefix			%{_sysprefix}/%{target}
%define		_libdir			%{_prefix}/lib
%define		_pkgconfigdir		%{_prefix}/lib/pkgconfig
%define		_dlldir			/usr/share/wine/windows/system
%define		__cc			%{target}-gcc
%define		__cxx			%{target}-g++
%define		__pkgconfig_provides	%{nil}
%define		__pkgconfig_requires	%{nil}

#define         filterout_ld            (-Wl,)?-as-needed.*

%ifnarch %{ix86}
# arch-specific flags (like alpha's -mieee) are not valid for i386 gcc
%define		optflags	-O2
%endif
# -z options are invalid for mingw linker, most of -f options are Linux-specific
%define		filterout_ld	-Wl,-z,.*
%define		filterout_c	-f[-a-z0-9=]*

%description
gdk-pixbuf is an image loading and scaling library that can be
extended by loadable modules for new image formats.

This package contains the cross version for Win32.

%description -l pl.UTF-8
gdk-pixbuf to biblioteka ładująca i skalująca obrazki, której
funkcjonalność może być rozszerzana o obsługę nowych formatów poprzez
ładowane moduły.

Ten pakiet zawiera wersję skrośną dla Win32.

%package dll
Summary:	DLL gdk-pixbuf libraries for Windows
Summary(pl.UTF-8):	Biblioteki DLL gdk-pixbuf dla Windows
Group:		Applications/Emulators
Requires:	crossmingw32-glib2-dll >= 2.37.6
Requires:	wine
Conflicts:	crossmingw32-gtk+2-dll < 2.22.0

%description dll
DLL gdk-pixbuf libraries for Windows.

%description dll -l pl.UTF-8
Biblioteki DLL gdk-pixbuf dla Windows.

%prep
%setup -q -n gdk-pixbuf-%{version}
%patch0 -p1
%patch1 -p1

%build
%{__gettextize}
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
export PKG_CONFIG_LIBDIR=%{_prefix}/lib/pkgconfig
%configure \
	--target=%{target} \
	--host=%{target} \
	--disable-gtk-doc \
	--disable-man \
	--disable-silent-rules \
	--with-libjasper \
	%{!?with_gdiplus:--without-gdiplus}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_dlldir}
mv -f $RPM_BUILD_ROOT%{_prefix}/bin/*.dll $RPM_BUILD_ROOT%{_dlldir}

%if 0%{!?debug:1}
%{target}-strip --strip-unneeded -R.comment -R.note $RPM_BUILD_ROOT%{_dlldir}/*.dll \
	$RPM_BUILD_ROOT%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/*.dll
%{target}-strip -g -R.comment -R.note $RPM_BUILD_ROOT%{_libdir}/*.a
%endif

# shut up check-files
%{__rm} -r $RPM_BUILD_ROOT%{_datadir}/{gtk-doc,locale,man}
%{__rm} -r $RPM_BUILD_ROOT%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/*.{la,dll.a}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_libdir}/libgdk_pixbuf-2.0.dll.a
%{_libdir}/libgdk_pixbuf-2.0.la
%{_libdir}/gdk_pixbuf-2.0.def
%{_includedir}/gdk-pixbuf-2.0
%{_pkgconfigdir}/gdk-pixbuf-2.0.pc

%files dll
%defattr(644,root,root,755)
%{_dlldir}/libgdk_pixbuf-2.0-*.dll
%dir %{_libdir}/gdk-pixbuf-2.0
%dir %{_libdir}/gdk-pixbuf-2.0/%{abiver}
%dir %{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-*.dll
