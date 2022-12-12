import functools
import os

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.meson import Meson
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.36.0"


class PkgConfConan(ConanFile):
    name = "pkgconf"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.sr.ht/~kaniini/pkgconf"
    topics = ("pkgconf")
    license = "ISC"
    description = "package compiler and linker metadata toolkit"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_lib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_lib": False,
    }

    def layout(self):
        basic_layout(self)

    @property
    def _is_clang_cl(self):
        return self.settings.compiler == "clang" and self.settings.os == "Windows"


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if not self.options.enable_lib:
            self.options.rm_safe("fPIC")
            self.options.rm_safe("shared")
        elif self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.compiler.rm_safe("libcxx")
        self.settings.compiler.rm_safe("cppstd")

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross-building is not implemented in the recipe")

    def build_requirements(self):
        self.build_requires("meson/0.62.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @property
    def _sharedstatedir(self):
        return os.path.join(self.package_folder, "bin", "share")

    @functools.lru_cache(1)
    def _configure_meson(self):
        meson = Meson(self)
        meson.options["tests"] = False
        meson.options["sharedstatedir"] = self._sharedstatedir
        if not self.options.enable_lib:
            meson.options["default_library"] = "static"
        meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return meson

    def _patch_sources(self):
        apply_conandata_patches(self)
        if not self.options.get_safe("shared", False):
            tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"),
                                  "'-DLIBPKGCONF_EXPORT'",
                                  "'-DPKGCONFIG_IS_STATIC'")
        tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"),
            "project('pkgconf', 'c',",
            "project('pkgconf', 'c',\ndefault_options : ['c_std=gnu99'],")

    def build(self):
        self._patch_sources()
        with tools.vcvars(self) if self._is_clang_cl else tools.no_op():
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with tools.vcvars(self) if self._is_clang_cl else tools.no_op():
            meson = self._configure_meson()
            meson.install()

        if self._is_msvc:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
            if self.options.enable_lib and not self.options.shared:
                os.rename(os.path.join(self.package_folder, "lib", "libpkgconf.a"),
                          os.path.join(self.package_folder, "lib", "pkgconf.lib"),)

        if not self.options.enable_lib:
            rmdir(self, os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "include"))

        rmdir(self, os.path.join(self.package_folder, "share", "man"))
        os.rename(os.path.join(self.package_folder, "share", "aclocal"),
                  os.path.join(self.package_folder, "bin", "aclocal"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_id(self):
        if not self.info.options.enable_lib:
            del self.info.settings.compiler

    def package_info(self):
        if self.options.enable_lib:
            self.cpp_info.set_property("pkg_config_name", "libpkgconf")
            if Version(self.version) >= "1.7.4":
                self.cpp_info.includedirs.append(os.path.join("include", "pkgconf"))
            self.cpp_info.libs = ["pkgconf"]
            if not self.options.shared:
                self.cpp_info.defines = ["PKGCONFIG_IS_STATIC"]
        else:
            self.cpp_info.includedirs = []
            self.cpp_info.libdirs = []

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        exesuffix = ".exe" if self.settings.os == "Windows" else ""
        pkg_config = os.path.join(bindir, "pkgconf" + exesuffix).replace("\\", "/")
        self.output.info("Setting PKG_CONFIG env var: {}".format(pkg_config))
        self.buildenv_info.define_path("PKG_CONFIG", pkg_config)
        self.env_info.PKG_CONFIG = pkg_config # remove in conan v2?

        automake_extra_includes = tools.unix_path(os.path.join(self.package_folder , "bin", "aclocal").replace("\\", "/"))
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES env var: {}".format(automake_extra_includes))
        self.buildenv_info.prepend_path("AUTOMAKE_CONAN_INCLUDES", automake_extra_includes)
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(automake_extra_includes) # remove in conan v2?

        # TODO: to remove in conan v2 once pkg_config generator removed
        if self.options.enable_lib:
            self.cpp_info.names["pkg_config"] = "libpkgconf"
