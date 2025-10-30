# Install script for directory: /home/vincent/Gofood/gammu-1.42.0/include

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

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xheadersx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/gammu" TYPE FILE FILES
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-backup.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-bitmap.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-calendar.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-call.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-callback.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-category.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-datetime.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-debug.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-error.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-file.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-info.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-inifile.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-keys.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-limits.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-memory.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-message.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-misc.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-nokia.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-ringtone.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-security.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-settings.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-smsd.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-statemachine.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-types.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-unicode.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu-wap.h"
    "/home/vincent/Gofood/gammu-1.42.0/include/gammu.h"
    "/home/vincent/Gofood/gammu-1.42.0/build/include/gammu-config.h"
    )
endif()

