from conans import ConanFile, tools, AutoToolsBuildEnvironment
import functools
import subprocess

def quick_run(*args):
    p = subprocess.run(args, stdout=subprocess.PIPE, universal_newlines=True)
    return p.stdout.strip()

class PbcConan(ConanFile):
    name = "pbc"
    version = "0.5.14"

    # Optional metadata
    license = "LGPL-3.0"
    author = "Kareem Shehata <kareem@shehata.ca>"
    url = "https://github.com/kshehata/conan-pbc"
    description = "The PBC (Pairing-Based Crypto) library is a C library providing low-level routines for pairing-based cryptosystems."
    topics = ("pbc", "crypto", "cryptography", "security", "pairings" "cryptographic")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = "gmp/6.2.1"

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(
            "https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz",
            sha256="772527404117587560080241cedaf441e5cac3269009cdde4c588a1dce4c23d2",
            strip_root=True,
        )
        # Have to update config.sub in order to build for iOS
        tools.download(
            "https://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD",
            "config.sub", overwrite=True,
        )

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--with-pic={}".format(yes_no(self.options.get_safe("fPIC", True))),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]

        # No idea why this is necessary, but if you don't set CC this way, then
        # configure complains that it can't find gmp.
        if self.settings.os == "iOS":
            if self.settings.arch == "x86_64":
                platform = "iphonesimulator"
                target = "x86_64-apple-darwin"
            else:
                platform = "iphoneos"
                target = "arm64-apple-darwin"
            sdk_path = quick_run("xcrun", "-sdk", platform, "-show-sdk-path")
            cc = quick_run("xcrun", "-sdk", platform, "-find", "cc")
            min_ios = "-miphoneos-version-min={}".format(self.settings.os.version)
            configure_args.append("CC={} -isysroot {} -target {} {}".format(
                cc, sdk_path, target, min_ios))

        autotools.configure(args=configure_args)
        return autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = ["pbc"]
