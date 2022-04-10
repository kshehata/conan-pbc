from conans import ConanFile, tools, AutoToolsBuildEnvironment

class PbcConan(ConanFile):
    name = "pbc"
    version = "0.5.14"

    # Optional metadata
    license = "LGPL-3.0"
    author = "Kareem Shehata <kareem@shehata.ca>"
    url = "TBD"
    description = "The PBC (Pairing-Based Crypto) library is a C library providing low-level routines for pairing-based cryptosystems."
    topics = ("pbc", "crypto", "cryptography", "security", "pairings" "cryptographic")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = ["pbc"]
