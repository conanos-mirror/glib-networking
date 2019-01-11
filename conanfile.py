from conans import ConanFile, CMake, tools, Meson
from conanos.build import config_scheme
import os, shutil


class GlibnetworkingConan(ConanFile):
    name = "glib-networking"
    version = "2.59.1"
    description = "The GLib Networking package contains Network related gio modules for GLib."
    url = "https://github.com/conanos/glib-networking"
    homepage = "https://github.com/GNOME/glib-networking"
    license = "LGPL-2+"
    patch = "windows-export-symbol.patch"
    win_def = "glib-networking.def"
    exports = ["COPYING", patch, win_def]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    #requires = ("glib/2.58.0@conanos/dev","gnutls/3.5.18@conanos/dev", 
    #            "libffi/3.3-rc0@conanos/dev",#required by gio
                ####required by gnutls
    #            "nettle/3.4@conanos/dev", 
    #            "libtasn1/4.13@conanos/dev",
    #            "gmp/6.1.2@conanos/dev"
    #            )
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)


    def requirements(self):
        self.requires.add("glib/2.58.1@conanos/stable")
        self.requires.add("libffi/3.299999@conanos/stable")
        self.requires.add("zlib/1.2.11@conanos/stable")
        self.requires.add("nettle/3.4.1@conanos/stable")
        self.requires.add("gmp/6.1.2-5@conanos/stable")
        self.requires.add("gnutls/3.5.19@conanos/stable")

    def source(self):
        url_ = 'https://github.com/GNOME/glib-networking/archive/{version}.tar.gz'.format(version=self.version)
        tools.get(url_)
        if self.settings.os == 'Windows':
            tools.patch(patch_file=self.patch)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        if self.settings.os == 'Windows':
            shutil.copy2(os.path.join(self.source_folder,self.win_def), os.path.join(self.source_folder,self._source_subfolder,self.win_def))

        #maj_ver = '.'.join(self.version.split('.')[0:2])
        #tarball_name = '{name}-{version}.tar'.format(name=self.name, version=self.version)
        #archive_name = '%s.xz' % tarball_name
        #url_ = 'http://ftp.gnome.org/pub/gnome/sources/glib-networking/{0}/{1}'.format(maj_ver,archive_name)
        #tools.download(url_, archive_name)
        #
        #if self.settings.os == 'Windows':
        #    self.run('7z x %s' % archive_name)
        #    self.run('7z x %s' % tarball_name)
        #    os.unlink(tarball_name)
        #else:
        #    self.run('tar -xJf %s' % archive_name)
        #os.rename('%s-%s' %( self.name, self.version), self.source_subfolder)
        #os.unlink(archive_name)


    def build(self):
        #with tools.chdir(self.source_subfolder):
        #    with tools.environment_append({
        #        'LD_LIBRARY_PATH' : "%s/lib"%(self.deps_cpp_info["libffi"].rootpath)
        #        }):
        #        
        #        meson = Meson(self)
        #        _defs = { 'prefix':'%s/builddir/install'%(os.getcwd()), 'libdir':'lib',
        #                  'libproxy_support' : 'false', 'gnome_proxy_support' : 'false',
        #                  'pkcs11_support' : 'false', 'installed_tests' : 'false',
        #                  'static_modules' : 'true' if not self.options.shared else 'false'
        #        }
        #        meson.configure(
        #            defs=_defs,
        #            source_dir = '%s'%(os.getcwd()),
        #            build_dir= '%s/builddir'%(os.getcwd()),
        #            pkg_config_paths=['%s/lib/pkgconfig'%(self.deps_cpp_info["glib"].rootpath),
        #                              '%s/lib/pkgconfig'%(self.deps_cpp_info["gnutls"].rootpath),
        #                              '%s/lib/pkgconfig'%(self.deps_cpp_info["libffi"].rootpath),
        #                              '%s/lib/pkgconfig'%(self.deps_cpp_info["nettle"].rootpath),
        #                              '%s/lib/pkgconfig'%(self.deps_cpp_info["libtasn1"].rootpath),
        #                              '%s/lib/pkgconfig'%(self.deps_cpp_info["gmp"].rootpath),
        #                              ]
        #            )
        #        meson.build(args=['-j2'])
        #        self.run('ninja -C {0} install'.format(meson.build_dir))
        pkg_config_paths=[ os.path.join(self.deps_cpp_info[i].rootpath, "lib", "pkgconfig") 
                            for i in ["glib","libffi","zlib","nettle","gmp","gnutls"] ]
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        binpath = [ os.path.join(self.deps_cpp_info[i].rootpath, "bin") for i in ["glib","libffi"] ]
        include = [ os.path.join(self.deps_cpp_info["gnutls"].rootpath, "include") ]
        libpath = [ os.path.join(self.deps_cpp_info[i].rootpath, "lib") for i in ["glib","libffi","zlib","nettle","gmp","gnutls"] ]
        defs = {'prefix' : prefix}
        if self.settings.os == "Linux":
            defs.update({'libdir':'lib'})
        meson = Meson(self)
        if self.settings.os == "Windows":
            with tools.environment_append({
                'PATH'    : os.pathsep.join(binpath + [os.getenv('PATH')]),
                'INCLUDE' : os.pathsep.join(include + [os.getenv('INCLUDE')]),
                'LIB' : os.pathsep.join(libpath + [os.getenv('LIB')]),
                }):
                meson.configure(defs=defs,source_dir=self._source_subfolder, build_dir=self._build_subfolder,pkg_config_paths=pkg_config_paths)
                meson.build()
                self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)