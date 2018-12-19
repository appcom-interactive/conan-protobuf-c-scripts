# Conan protobuf-c

This repository contains the conan receipe that is used to build the protobufc packages at [rgpaul bintray](https://bintray.com/manromen/rgpaul).

For Infos about the library please visit the [github](https://github.com/protobuf-c/protobuf-c) page.
The license of the library can be found on [github](https://github.com/protobuf-c/protobuf-c/blob/master/LICENSE).
This repository is licensed under the [MIT License](LICENSE).

## macOS

To create a package for macOS you can run the conan command like this:

`conan create . protobufc/1.3.1@rgpaul/stable -s os=Macos -s os.version=10.14 -s arch=x86_64 -s build_type=Release -o shared=False`

### Requirements

* [CMake](https://cmake.org/)
* [Conan](https://conan.io/)
* [Xcode](https://developer.apple.com/xcode/)
