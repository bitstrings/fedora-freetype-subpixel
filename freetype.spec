%{!?with_xfree86:%define with_xfree86 1}

Summary: A free and portable font rendering engine
Name: freetype
Version: 2.10.1
Release: 200%{?dist}
License: (FTL or GPLv2+) and BSD and MIT and Public Domain and zlib with acknowledgement
URL: http://www.freetype.org
Source:  https://download.savannah.gnu.org/releases/freetype/freetype-%{version}.tar.bz2
Source1: https://download.savannah.gnu.org/releases/freetype/freetype-doc-%{version}.tar.bz2
Source2: https://download.savannah.gnu.org/releases/freetype/ft2demos-%{version}.tar.bz2
Source3: ftconfig.h
Source4: %{name}.sh

# Enable subpixel rendering (ClearType)
Patch0:  freetype-2.3.0-enable-spr.patch
# Enable otvalid and gxvalid modules
Patch1:  freetype-2.2.1-enable-valid.patch
# Enable additional demos
Patch2:  freetype-2.5.2-more-demos.patch

Patch3:  freetype-2.6.5-libtool.patch

Patch4:  freetype-2.8-multilib.patch

Patch5:  freetype-ftlcdfil.patch

BuildRequires:  gcc
BuildRequires: libX11-devel
BuildRequires: libpng-devel
BuildRequires: zlib-devel
BuildRequires: bzip2-devel

Provides: %{name}-bytecode
Provides: %{name}-subpixel
Obsoletes: freetype-freeworld < 2.9.1-2

%description
The FreeType engine is a free and portable font rendering
engine, developed to provide advanced font support for a variety of
platforms and environments. FreeType is a library which can open and
manages font files as well as efficiently load, hint and render
individual glyphs. FreeType is not a font server or a complete
text-rendering library.


%package demos
Summary: A collection of FreeType demos
Requires: %{name} = %{version}-%{release}

%description demos
The FreeType engine is a free and portable font rendering
engine, developed to provide advanced font support for a variety of
platforms and environments.  The demos package includes a set of useful
small utilities showing various capabilities of the FreeType library.


%package devel
Summary: FreeType development libraries and header files
Requires: %{name} = %{version}-%{release}
Requires: pkgconf%{?_isa}

%description devel
The freetype-devel package includes the static libraries and header files
for the FreeType font rendering engine.

Install freetype-devel if you want to develop programs which will use
FreeType.


%prep
%setup -q -b 1 -a 2

%patch0  -p1 -b .enable-spr
%patch1  -p1 -b .enable-valid

pushd ft2demos-%{version}
%patch2  -p1 -b .more-demos
popd

%patch3 -p1 -b .libtool
%patch4 -p1 -b .multilib
%patch5 -p1

%build

%configure --disable-static \
           --with-zlib=yes \
           --with-bzip2=yes \
           --with-png=yes \
           --enable-freetype-config \
           --with-harfbuzz=no
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' builds/unix/libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' builds/unix/libtool
make %{?_smp_mflags}

%if %{with_xfree86}
# Build demos
pushd ft2demos-%{version}
make TOP_DIR=".."
popd
%endif

# Convert FTL.txt and example3.cpp to UTF-8
pushd docs
iconv -f latin1 -t utf-8 < FTL.TXT > FTL.TXT.tmp && \
touch -r FTL.TXT FTL.TXT.tmp && \
mv FTL.TXT.tmp FTL.TXT

iconv -f iso-8859-1 -t utf-8 < "tutorial/example3.cpp" > "tutorial/example3.cpp.utf8"
touch -r tutorial/example3.cpp tutorial/example3.cpp.utf8 && \
mv tutorial/example3.cpp.utf8 tutorial/example3.cpp
popd


%install

%make_install gnulocaledir=$RPM_BUILD_ROOT%{_datadir}/locale

{
  for ftdemo in ftbench ftchkwd ftmemchk ftpatchk fttimer ftdump ftlint ftmemchk ftvalid ; do
      builds/unix/libtool --mode=install install -m 755 ft2demos-%{version}/bin/$ftdemo $RPM_BUILD_ROOT/%{_bindir}
  done
}
%if %{with_xfree86}
{
  for ftdemo in ftdiff ftgamma ftgrid ftmulti ftstring fttimer ftview ; do
      builds/unix/libtool --mode=install install -m 755 ft2demos-%{version}/bin/$ftdemo $RPM_BUILD_ROOT/%{_bindir}
  done
}
%endif

# fix multilib issues
%define wordsize %{__isa_bits}

mv $RPM_BUILD_ROOT%{_includedir}/freetype2/freetype/config/ftconfig.h \
   $RPM_BUILD_ROOT%{_includedir}/freetype2/freetype/config/ftconfig-%{wordsize}.h
install -p -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_includedir}/freetype2/freetype/config/ftconfig.h
install -Dm 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/profile.d/%{name}.sh

# Don't package static .a or .la files
rm -f $RPM_BUILD_ROOT%{_libdir}/*.{a,la}


%triggerpostun -- freetype < 2.0.5-3
{
  # ttmkfdir updated - as of 2.0.5-3, on upgrades we need xfs to regenerate
  # things to get the iso10646-1 encoding listed.
  for I in %{_datadir}/fonts/*/TrueType /usr/share/X11/fonts/TTF; do
      [ -d $I ] && [ -f $I/fonts.scale ] && [ -f $I/fonts.dir ] && touch $I/fonts.scale
  done
  exit 0
}

%ldconfig_scriptlets

%files
%{!?_licensedir:%global license %%doc}
%license docs/LICENSE.TXT docs/FTL.TXT docs/GPLv2.TXT
%{_libdir}/libfreetype.so.*
%doc README
%config %{_sysconfdir}/profile.d/%{name}.sh

%files demos
%{_bindir}/ftbench
%{_bindir}/ftchkwd
%{_bindir}/ftmemchk
%{_bindir}/ftpatchk
%{_bindir}/fttimer
%{_bindir}/ftdump
%{_bindir}/ftlint
%{_bindir}/ftvalid
%if %{with_xfree86}
%{_bindir}/ftdiff
%{_bindir}/ftgamma
%{_bindir}/ftgrid
%{_bindir}/ftmulti
%{_bindir}/ftstring
%{_bindir}/ftview
%endif
%doc ChangeLog README

%files devel
%doc docs/CHANGES docs/formats.txt docs/ft2faq.html
%dir %{_includedir}/freetype2
%{_datadir}/aclocal/freetype2.m4
%{_includedir}/freetype2/*
%{_libdir}/libfreetype.so
%{_bindir}/freetype-config
%{_libdir}/pkgconfig/freetype2.pc
%doc docs/design
%doc docs/glyphs
%doc docs/reference
%doc docs/tutorial
%{_mandir}/man1/*

%changelog
