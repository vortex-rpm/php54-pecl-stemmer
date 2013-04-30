%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}
%{!?pecl_phpdir: %{expand: %%global pecl_phpdir  %(%{__pecl} config-get php_dir  2> /dev/null || echo undefined)}}
%{?!pecl_xmldir: %{expand: %%global pecl_xmldir %{pecl_phpdir}/.pkgxml}}

%{!?php_extdir: %{expand: %%global php_extdir %(php-config --extension-dir)}}
%global php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)

%global php_base php54
%global pecl_name stemmer
%global real_name stemmer

%global commit 0f32673f89e72049a6c43a4d5966a88b81aff039

Summary: Stemming capability for a variety of languages using Dr. M.F. Porter's Snowball API
Name: %{php_base}-pecl-stemmer
Version: 0
Release: 1.%{commit}.vortex%{?dist}
License: BSD
Group: Development/Languages
Vendor: Vortex RPM
URL: https://github.com/hthetiot/php-%{real_name}

Source: %{real_name}-%{commit}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: %{php_base}-devel, %{php_base}-cli, %{php_base}-pear
Requires(post): %{__pecl}
Requires(postun): %{__pecl}

%if %{?php_zend_api}0
Requires: php(zend-abi) = %{php_zend_api}
Requires: php(api) = %{php_core_api}
%else
Requires: %{php_base}-api = %{php_apiver}
%endif

%description
This stem extension for PHP provides stemming capability for a variety of
languages using Dr. M.F. Porter's Snowball API.

It has a much simpler API than the stem extension found in pecl.

%prep 
%setup -c -n php-%{real_name}-master -q


%build
phpize
%configure
%{__make} -C libstemmer_c
%{__make} %{?_smp_mflags}


%install
%{__rm} -rf %{buildroot}
%{__make} install INSTALL_ROOT=%{buildroot}

# Drop in the bit of configuration
%{__mkdir_p} %{buildroot}%{_sysconfdir}/php.d
%{__cat} > %{buildroot}%{_sysconfdir}/php.d/%{pecl_name}.ini << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so

EOF

# Install XML package description
# use 'name' rather than 'pecl_name' to avoid conflict with pear extensions
%{__mkdir_p} %{buildroot}%{pecl_xmldir}
%{__install} -m 644 ../package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml


%clean
%{__rm} -rf %{buildroot}


%post
%{__pecl} install --nodeps --soft --force --register-only --nobuild %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ]; then
%{__pecl} uninstall --nodeps --ignore-errors --register-only %{pecl_name} >/dev/null || :
fi


%files
%defattr(-, root, root, -)
%doc %{pecl_name}-%{version}/README %{pecl_name}-%{version}/LICENSE
%config(noreplace) %{_sysconfdir}/php.d/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{pecl_name}.xml


%changelog
* Tue Apr 30 2013 Ilya Otyutskiy <ilya.otyutskiy@icloud.com> - 0-1.0f32673f89e72049a6c43a4d5966a88b81aff039.vortex
- Initial packaging.
