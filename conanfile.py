from conans import ConanFile, CMake, tools
import os

class ProtobufConan(ConanFile):
    name = "protobufc"
    version = "1.3.1"
    author = "Ralph-Gordon Paul (gordon@rgpaul.com)"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "android_ndk": "ANY", "android_stl_type":["c++_static", "c++_shared"]}
    default_options = "shared=False", "android_ndk=None", "android_stl_type=c++_static"
    description = "Protocol Buffers implementation in C"
    url = "https://github.com/Manromen/conan-protobuf-c-scripts"
    exports_sources = "cmake-modules/*"
    generators = "cmake_paths"

    # download sources
    def source(self):
        url = "https://github.com/protobuf-c/protobuf-c/archive/v%s.zip" % self.version
        tools.get(url)

        tools.replace_in_file("%s/protobuf-c-%s/build-cmake/CMakeLists.txt" % (self.source_folder, self.version),
            "PROJECT(protobuf-c)",
            """PROJECT(protobuf-c)
            set(CMAKE_CXX_STANDARD 11)
            set(CMAKE_CXX_STANDARD_REQUIRED ON)
            set(CMAKE_CXX_EXTENSIONS OFF)
            set(CMAKE_C_STANDARD 11)
            set(CMAKE_C_STANDARD_REQUIRED ON)
            include(${CMAKE_BINARY_DIR}/conan_paths.cmake) """)

    # compile using cmake
    def build(self):

        cmake = CMake(self)
        cmake.verbose = True

        src_folder = "%s/protobuf-c-%s/build-cmake" % (self.source_folder, self.version)

        if self.settings.os == "Android":
            cmake.definitions["CMAKE_SYSTEM_VERSION"] = self.settings.os.api_level
            cmake.definitions["CMAKE_ANDROID_NDK"] = os.environ["ANDROID_NDK_PATH"]
            cmake.definitions["CMAKE_ANDROID_NDK_TOOLCHAIN_VERSION"] = self.settings.compiler
            cmake.definitions["CMAKE_ANDROID_STL_TYPE"] = self.options.android_stl_type

        if self.settings.os == "iOS":
            ios_toolchain = "cmake-modules/Toolchains/ios.toolchain.cmake"
            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = ios_toolchain
            if self.settings.arch == "x86" or self.settings.arch == "x86_64":
                cmake.definitions["IOS_PLATFORM"] = "SIMULATOR"
            else:
                cmake.definitions["IOS_PLATFORM"] = "OS"

        if self.settings.os == "Macos":
            cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = tools.to_apple_arch(self.settings.arch)

        cmake.configure(source_folder=src_folder)
        cmake.build()
        cmake.install()

        lib_dir = os.path.join(self.package_folder,"lib")

        if self.settings.os == "iOS":
            # delete shared artifacts for static builds and the static library for shared builds
            if self.options.shared == False:
                for f in os.listdir(lib_dir):
                    if f.endswith(".a") and os.path.isfile(os.path.join(lib_dir,f)) and not os.path.islink(os.path.join(lib_dir,f)):
                        self.run("xcrun ranlib %s" % os.path.join(lib_dir,f))
                        # thin the library (remove all other archs)
                        self.run("lipo -extract %s %s -output %s" % (tools.to_apple_arch(self.settings.arch), os.path.join(lib_dir,f), os.path.join(lib_dir,f)))
            else:
                # thin the library (remove all other archs)
                for f in os.listdir(lib_dir):
                    if f.endswith(".dylib") and os.path.isfile(os.path.join(lib_dir,f)) and not os.path.islink(os.path.join(lib_dir,f)):
                        self.run("lipo -extract %s %s -output %s" % (tools.to_apple_arch(self.settings.arch), os.path.join(lib_dir,f), os.path.join(lib_dir,f)))

    def requirements(self):
        self.requires("protobufcpp/3.6.1@%s/%s" % (self.user, self.channel))
        
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ['include']

    def config_options(self):
        # remove android specific option for all other platforms
        if self.settings.os != "Android":
            del self.options.android_ndk
            del self.options.android_stl_type
