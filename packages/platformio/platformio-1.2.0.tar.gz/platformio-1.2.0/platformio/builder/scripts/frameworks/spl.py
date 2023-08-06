# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

"""
SPL

The ST Standard Peripheral Library provides a set of functions for
handling the peripherals on the STM32 Cortex-M3 family.
The idea is to save the user (the new user, in particular) having to deal
directly with the registers.

http://www.st.com/web/en/catalog/tools/FM147/CL1794/SC961/SS1743?sc=stm32embeddedsoftware
"""

from os.path import join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

env.Replace(
    PLATFORMFW_DIR=join("$PIOPACKAGES_DIR", "framework-spl")
)

env.VariantDir(
    join("$BUILD_DIR", "FrameworkSPLInc"),
    join("$PLATFORMFW_DIR", "${BOARD_OPTIONS['build']['core']}",
         "variants", "${BOARD_OPTIONS['build']['variant']}", "inc")
)

env.Append(
    CPPPATH=[
        join("$BUILD_DIR", "FrameworkSPLInc"),
        join("$BUILD_DIR", "FrameworkSPL")
    ]
)

envsafe = env.Clone()

envsafe.Append(
    CPPPATH=[
        join("$BUILD_DIR", "src")
    ],

    CPPDEFINES=[
        "USE_STDPERIPH_DRIVER"
    ]
)

#
# Target: Build SPL Library
#

extra_flags = env.get("BOARD_OPTIONS", {}).get("build", {}).get("extra_flags")
ignore_files = []
if "STM32F40_41xxx" in extra_flags:
    ignore_files += ["stm32f4xx_fmc.c"]
elif "STM32F303xC" in extra_flags:
    ignore_files += ["stm32f30x_hrtim.c"]
elif "STM32L1XX_MD" in extra_flags:
    ignore_files += ["stm32l1xx_flash_ramfunc.c"]

libs = []
libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkSPL"),
    join("$PLATFORMFW_DIR", "${BOARD_OPTIONS['build']['core']}", "variants",
         "${BOARD_OPTIONS['build']['variant']}", "src"),
    ignore_files
))

env.Append(LIBS=libs)
