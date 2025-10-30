# Install script for directory: /home/vincent/Gofood/gammu-1.42.0

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xpkgconfigx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" TYPE FILE FILES
    "/home/vincent/Gofood/gammu-1.42.0/build/cfg/gammu.pc"
    "/home/vincent/Gofood/gammu-1.42.0/build/cfg/gammu-smsd.pc"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xdocsx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu" TYPE FILE FILES
    "/home/vincent/Gofood/gammu-1.42.0/README.rst"
    "/home/vincent/Gofood/gammu-1.42.0/ChangeLog"
    "/home/vincent/Gofood/gammu-1.42.0/COPYING"
    )
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/home/vincent/Gofood/gammu-1.42.0/build/include/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/libgammu/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/helper/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/tests/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/smsd/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/gammu/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/gammu-detect/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/locale/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/utils/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/docs/config/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/docs/manual/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/docs/examples/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/docs/sql/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/docs/man/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/contrib/cmake_install.cmake")

endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/home/vincent/Gofood/gammu-1.42.0/build/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
