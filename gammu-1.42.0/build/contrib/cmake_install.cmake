# Install script for directory: /home/vincent/Gofood/gammu-1.42.0/contrib

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

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xsymbianx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/gammu" TYPE FILE FILES
    "/home/vincent/Gofood/gammu-1.42.0/contrib/symbian/gnapplet.ini"
    "/home/vincent/Gofood/gammu-1.42.0/contrib/symbian/gnapplet.sis"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xsymbianx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/gammu" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/s60/gammu-s60-remote.sis")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmediax" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/media" TYPE FILE FILES
    "/home/vincent/Gofood/gammu-1.42.0/contrib/media/aliens.nlm"
    "/home/vincent/Gofood/gammu-1.42.0/contrib/media/axelf.txt"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/class_gammu" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/class_gammu/class.gammu.php")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/class_gammu" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/class_gammu/class.sms.gammu.php")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/class_gammu" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/class_gammu/README")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/smsd-mysql-admin" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/smsd-mysql-admin/admin.php")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/smsd-mysql-linked" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/smsd-mysql-linked/linked.php")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/smsd-mysql-linked" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/smsd-mysql-linked/linked.sql")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/smsd-mysql-intergammu" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/smsd-mysql-intergammu/config.php")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/smsd-mysql-intergammu/funcoes" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/smsd-mysql-intergammu/funcoes/func.gammu.php")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/smsd-mysql-intergammu/funcoes" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/smsd-mysql-intergammu/funcoes/func.sql.php")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/smsd-mysql-intergammu" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/smsd-mysql-intergammu/index.php")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/smsd-mysql-intergammu" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/smsd-mysql-intergammu/intergammu.txt")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/smsd-mysql-intergammu/proc" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/smsd-mysql-intergammu/proc/admin.php")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/smsd-mysql-intergammu" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/smsd-mysql-intergammu/proclast.sql")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xexamplesx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/examples/php/smsd-mysql-list" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/php/smsd-mysql-list/sms.php")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xbashx" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/usr/share/bash-completion/completions/gammu")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/usr/share/bash-completion/completions" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/contrib/bash-completion/gammu")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xsystemdx" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/lib/systemd/system/gammu-smsd.service")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/lib/systemd/system" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/build/contrib/init/gammu-smsd.service")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/home/vincent/Gofood/gammu-1.42.0/build/contrib/smscgi/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/contrib/convert/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/contrib/sqlreply/cmake_install.cmake")
  include("/home/vincent/Gofood/gammu-1.42.0/build/contrib/coveragehelper/cmake_install.cmake")

endif()

