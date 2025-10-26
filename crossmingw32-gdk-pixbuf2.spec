#
# Conditional build:
%bcond_without	gdiplus	# system GDIPLUS instead of libjpeg and libtiff
#
Summary:	An image loading and scaling library - cross MinGW32 version
Summary(pl.UTF-8):	Biblioteka ładująca i skalująca obrazki - wersja skrośna MinGW32
Name:		crossmingw32-gdk-pixbuf2
Version:	2.44.4
Release:	1
License:	LGPL v2+
Group:		Development/Libraries
Source0:	https://download.gnome.org/sources/gdk-pixbuf/2.44/gdk-pixbuf-%{version}.tar.xz
# Source0-md5:	2676fd771eeec4ecee3af4b366aa1412
URL:		https://gnome.pages.gitlab.gnome.org/gtk/gdk-pixbuf/
BuildRequires:	crossmingw32-gcc
BuildRequires:	crossmingw32-glib2 >= 2.56.0
BuildRequires:	crossmingw32-libpng >= 1.0
BuildRequires:	gettext-tools >= 0.19
# glib-genmarshal, glib-mkenums
BuildRequires:	glib2-devel >= 1:2.56.0
BuildRequires:	meson >= 0.55.3
BuildRequires:	ninja >= 1.5
BuildRequires:	pkgconfig >= 1:0.15
BuildRequires:	rpmbuild(macros) >= 2.042
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
%if %{without gdiplus}
BuildRequires:	crossmingw32-libjpeg
BuildRequires:	crossmingw32-libtiff
%endif
Requires:	crossmingw32-glib2 >= 2.56.0
Requires:	crossmingw32-libpng >= 1.0
%if %{without gdiplus}
Requires:	crossmingw32-libjpeg
Requires:	crossmingw32-libtiff
%endif
Conflicts:	crossmingw32-gtk+2 < 2.22.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		abiver	2.10.0

%define		no_install_post_strip	1
%define		_enable_debug_packages	0

%define		target			i386-mingw32
%define		target_platform 	i386-pc-mingw32

%define		_sysprefix		/usr
%define		_prefix			%{_sysprefix}/%{target}
%define		_libdir			%{_prefix}/lib
%define		_pkgconfigdir		%{_prefix}/lib/pkgconfig
%define		_docdir			%{_sysprefix}/share/doc
%define		_dlldir			/usr/share/wine/windows/system
%define		__pkgconfig_provides	%{nil}
%define		__pkgconfig_requires	%{nil}
# for meson 0.50+, keep __cc/__cxx as host compiler and pass %{target}-* in meson-cross.txt

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

%package static
Summary:	Static gdk-pixbuf library (cross MinGW32 version)
Summary(pl.UTF-8):	Statyczna biblioteka gdk-pixbuf (wersja skrośna MinGW32)
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description static
Static gdk-pixbuf library (cross MinGW32 version).

%description static -l pl.UTF-8
Statyczna biblioteka gdk-pixbuf (wersja skrośna MinGW32).

%package dll
Summary:	DLL gdk-pixbuf libraries for Windows
Summary(pl.UTF-8):	Biblioteki DLL gdk-pixbuf dla Windows
Group:		Applications/Emulators
Requires:	crossmingw32-glib2-dll >= 2.56.0
Requires:	wine
Conflicts:	crossmingw32-gtk+2-dll < 2.22.0

%description dll
DLL gdk-pixbuf libraries for Windows.

%description dll -l pl.UTF-8
Biblioteki DLL gdk-pixbuf dla Windows.

%prep
%setup -q -n gdk-pixbuf-%{version}

cat > meson-cross.txt <<'EOF'
[host_machine]
system = 'windows'
cpu_family = 'x86'
cpu = 'i386'
endian='little'
[binaries]
c = '%{target}-gcc'
ar = '%{target}-ar'
windres = '%{target}-windres'
pkg-config = 'pkg-config'
[built-in options]
%ifarch %{ix86}
; force gnu99 to disable __STRICT_ANSI__ and unblock fdopen() in mingw32
c_args = ['%(echo %{rpmcflags} | sed -e "s/ \+/ /g;s/ /', '/g")', '-std=gnu99']
%else
# arch-specific flags (like alpha's -mieee) are not valid for i386 gcc.
c_args = ['-O2', '-std=gnu99']
%endif
EOF

%build
unset PKG_CONFIG_PATH
export PKG_CONFIG_LIBDIR=%{_prefix}/lib/pkgconfig
%meson \
	--cross-file meson-cross.txt \
	-Dandroid=disabled \
	-Dbuiltin_loaders="" \
	-Ddocumentation=false \
	-Dgif=%{__enabled_disabled_not gdiplus} \
	-Dglycin=disabled \
	-Dinstalled_tests=false \
	-Dintrospection=disabled \
	-Djpeg=%{__enabled_disabled_not gdiplus} \
	-Dman=false \
	%{?with_gdiplus:-Dnative_windows_loaders=true} \
	-Dothers=enabled \
	-Dpng=enabled \
	-Dtests=false \
	-Dthumbnailer=disabled \
	-Dtiff=%{__enabled_disabled_not gdiplus}

%meson_build

%install
rm -rf $RPM_BUILD_ROOT

%meson_install

install -d $RPM_BUILD_ROOT%{_dlldir}
%{__mv} $RPM_BUILD_ROOT%{_prefix}/bin/*.dll $RPM_BUILD_ROOT%{_dlldir}

%if 0%{!?debug:1}
%{target}-strip --strip-unneeded -R.comment -R.note $RPM_BUILD_ROOT%{_dlldir}/*.dll \
	$RPM_BUILD_ROOT%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/*.dll
%{target}-strip -g -R.comment -R.note $RPM_BUILD_ROOT%{_libdir}/*.a
%endif

# shut up check-files
%{__rm} $RPM_BUILD_ROOT%{_bindir}/*.exe
%{__rm} -r $RPM_BUILD_ROOT%{_datadir}/locale
%{__rm} -r $RPM_BUILD_ROOT%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/*.dll.a

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_libdir}/libgdk_pixbuf-2.0.dll.a
%{_includedir}/gdk-pixbuf-2.0
%{_pkgconfigdir}/gdk-pixbuf-2.0.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libgdk_pixbuf-2.0.a

%files dll
%defattr(644,root,root,755)
%{_dlldir}/libgdk_pixbuf-2.0-0.dll
%dir %{_libdir}/gdk-pixbuf-2.0
%dir %{_libdir}/gdk-pixbuf-2.0/%{abiver}
%dir %{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-ani.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-icns.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-png.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-pnm.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-qtif.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-tga.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-xbm.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-xpm.dll
%if %{with gdiplus}
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-gdip-bmp.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-gdip-emf.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-gdip-gif.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-gdip-ico.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-gdip-jpeg.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-gdip-tiff.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-gdip-wmf.dll
%else
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-bmp.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-gif.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-ico.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-jpeg.dll
%{_libdir}/gdk-pixbuf-2.0/%{abiver}/loaders/libpixbufloader-tiff.dll
%endif
