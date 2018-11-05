from conans import ConanFile, CMake, tools, Meson
import os

class GlibnetworkingConan(ConanFile):
    name = "glib-networking"
    version = "2.58.0"
    description = "The GLib Networking package contains Network related gio modules for GLib."
    url = "https://github.com/conanos/glib-networking"
    homepage = "http://www.linuxfromscratch.org/blfs/view/svn/basicnet/glib-networking.html"
    license = "LGPLv2Plus"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = ("glib/2.58.0@conanos/dev","gnutls/3.5.18@conanos/dev", 
                "libffi/3.3-rc0@conanos/dev",
                "nettle/3.4@conanos/dev", 
                "libtasn1/4.13@conanos/dev",
                "gmp/6.1.2@conanos/dev"
                )

    #requires = ("libffi/3.99999@user/channel","glib/2.54.3@bincrafters/stable","gnutls/3.5.18@user/channel",
    #"nettle/3.4@user/channel","libtasn1/4.13@user/channel")

    source_subfolder = "source_subfolder"

    def source(self):
        maj_ver = '.'.join(self.version.split('.')[0:2])
        tarball_name = '{name}-{version}.tar'.format(name=self.name, version=self.version)
        archive_name = '%s.xz' % tarball_name
        url_ = 'http://ftp.gnome.org/pub/gnome/sources/glib-networking/{0}/{1}'.format(maj_ver,archive_name)
        tools.download(url_, archive_name)
        
        if self.settings.os == 'Windows':
            self.run('7z x %s' % archive_name)
            self.run('7z x %s' % tarball_name)
            os.unlink(tarball_name)
        else:
            self.run('tar -xJf %s' % archive_name)
        os.rename('%s-%s' %( self.name, self.version), self.source_subfolder)
        os.unlink(archive_name)


    def build(self):
        #vars = {'PKG_CONFIG_PATH': "%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig"
        #                           ":%s/lib/pkgconfig:%s/lib/pkgconfig"
        #                           %(self.deps_cpp_info["libffi"].rootpath,self.deps_cpp_info["glib"].rootpath,
        #                             self.deps_cpp_info["gnutls"].rootpath,self.deps_cpp_info["nettle"].rootpath,
        #                             self.deps_cpp_info["libtasn1"].rootpath),
        #        'LD_LIBRARY_PATH' : "%s/lib:%s/lib"%(self.deps_cpp_info["libffi"].rootpath,self.deps_cpp_info["glib"].rootpath),
        #        }
        #
        #with tools.environment_append(vars):
        #    self.run("autoreconf -f -i")
        #    self.run('GIO_QUERYMODULES=%s/bin/gio-querymodules ./configure --prefix %s/build --libdir %s/build/lib'
        #        ' --enable-introspection --without-ca-certificates --enable-more-warnings'
        #        %(self.deps_cpp_info["glib"].rootpath, os.getcwd(), os.getcwd()))
        #    self.run("make -j4")
        #    self.run("make install")


        with tools.chdir(self.source_subfolder):
            with tools.environment_append({
                'LD_LIBRARY_PATH' : "%s/lib"%(self.deps_cpp_info["libffi"].rootpath)
                }):
                
                meson = Meson(self)
                _defs = { 'prefix':'%s/builddir/install'%(os.getcwd()), 'libdir':'lib',
                          'libproxy_support' : 'false', 'gnome_proxy_support' : 'false',
                          'pkcs11_support' : 'false', 'installed_tests' : 'false',
                          'static_modules' : 'true' if not self.options.shared else 'false'
                }
                meson.configure(
                    defs=_defs,
                    source_dir = '%s'%(os.getcwd()),
                    build_dir= '%s/builddir'%(os.getcwd()),
                    pkg_config_paths=['%s/lib/pkgconfig'%(self.deps_cpp_info["glib"].rootpath),
                                      '%s/lib/pkgconfig'%(self.deps_cpp_info["gnutls"].rootpath),
                                      '%s/lib/pkgconfig'%(self.deps_cpp_info["libffi"].rootpath),
                                      '%s/lib/pkgconfig'%(self.deps_cpp_info["nettle"].rootpath),
                                      '%s/lib/pkgconfig'%(self.deps_cpp_info["libtasn1"].rootpath),
                                      '%s/lib/pkgconfig'%(self.deps_cpp_info["gmp"].rootpath),
                                      ]
                    )
                meson.build(args=['-j2'])
                self.run('ninja -C {0} install'.format(meson.build_dir))


    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir/install"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)