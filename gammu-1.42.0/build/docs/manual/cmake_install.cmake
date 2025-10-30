# Install script for directory: /home/vincent/Gofood/gammu-1.42.0/docs/manual

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

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/api.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/backup.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/bitmap.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/calendar.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/call.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/callback.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/category.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/datetime.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/debug.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/error.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/examples.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/file.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/hints.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/info.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/inifile.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/keys.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/limits.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/memory.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/message.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/misc.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/nokia.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/porting.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/ringtone.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/security.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/settings.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/smsd.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/statemachine.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/types.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/unicode.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/c" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/c/wap.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/config" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/config/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/contents.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/faq" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/faq/config.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/faq" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/faq/general.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/faq" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/faq/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/faq" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/faq/phone.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/faq" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/faq/python.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/faq" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/faq/smsd.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/formats" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/formats/backup.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/formats" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/formats/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/formats" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/formats/ini.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/formats" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/formats/smsbackup.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/gammu" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/gammu/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/glossary.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/internal" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/internal/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/internal" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/internal/new-phone.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/internal" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/internal/reply.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/internal" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/internal/state-machine.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/about.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/coding-style.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/contributing.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/directories.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/documentation.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/install.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/localization.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/motivation.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/releasing.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/roadmap.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/testing.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/project" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/project/versioning.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/carkit.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/discovering.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/gnapplet.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/m-obex.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/mtk.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/n6110.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/n6510.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/n7110.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/nokia-s40-sms.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/nokia.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/s60.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/samsung-gt.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/samsung.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/sonim.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/protocol" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/protocol/tdma_5120.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/python" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/python/data.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/python" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/python/examples.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/python" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/python/exceptions.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/python" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/python/gammu.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/python" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/python/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/python" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/python/objects.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/python" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/python/smsd.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/python" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/python/worker.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/quick" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/quick/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/backends.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/code.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/config.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/dbi.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/files.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/inject.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/manual.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/monitor.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/mysql.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/null.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/odbc.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/overview.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/pgsql.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/run.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/smsd.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/sql.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/tables.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/smsd" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/smsd/usage.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/testing" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/testing/dummy-driver.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/testing" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/testing/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/testing" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/testing/testsuite.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/utils" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/utils/gammu-config.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/utils" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/utils/gammu-detect.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/utils" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/utils/index.rst")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xmanualx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/gammu/manual/utils" TYPE FILE FILES "/home/vincent/Gofood/gammu-1.42.0/docs/manual/utils/jadmaker.rst")
endif()

