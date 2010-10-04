Summary:	An image loading and scaling library - cross MinGW32 version
Summary(pl.UTF-8):	Biblioteka ładująca i skalująca obrazki - wersja skrośna MinGW32
Name:		crossmingw32-gdk-pixbuf2
Version:	2.22.0
Release:	1
License:	LGPL v2+
Group:		Development/Libraries
Source0:	http://ftp.gnome.org/pub/GNOME/sources/gdk-pixbuf/2.22/gdk-pixbuf-%{version}.tar.bz2
# Source0-md5:	0447e70f7bada542182d12e6459442b0
URL:		http://www.gtk.org/
BuildRequires:	crossmingw32-gcc
BuildRequires:	crossmingw32-glib2 >= 2.26.0
BuildRequires:	crossmingw32-jasper
BuildRequires:	crossmingw32-libpng
# libjpeg + libtiff because gdiplus loader is "known to be broken"
BuildRequires:	crossmingw32-libjpeg
BuildRequires:	crossmingw32-libtiff
BuildRequires:	gtk-doc >= 1.11
BuildRequires:	pkgconfig >= 1:0.15
Requires:	crossmingw32-glib2 >= 2.26.0
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

#define         filterout_ld            (-Wl,)?-as-needed.*

%ifnarch %{ix86}
# arch-specific flags (like alpha's -mieee) are not valid for i386 gcc
%define		optflags	-O2
%endif
# -z options are invalid for mingw linker
%define		filterout_ld	-Wl,-z,.*

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
Requires:	crossmingw32-glib2-dll >= 2.26.0
Requires:	wine
Conflicts:	crossmingw32-gtk+2-dll < 2.22.0

%description dll
DLL gdk-pixbuf libraries for Windows.

%description dll -l pl.UTF-8
Biblioteki DLL gdk-pixbuf dla Windows.

%prep
%setup -q -n gdk-pixbuf-%{version}

%build
export PKG_CONFIG_LIBDIR=%{_prefix}/lib/pkgconfig
%configure \
	--target=%{target} \
	--host=%{target} \
	--disable-gtk-doc \
	--disable-man \
	--with-libjasper

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
