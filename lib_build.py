import sys
import os
import shutil

from SCons.Script import DefaultEnvironment
env = DefaultEnvironment()
env.Import("env")

devices = {
     # libopencm3 macros
    "STM32F0": "ARM_CM0",
    "STM32F1": "ARM_CM3",
    "STM32F2": "ARM_CM3",
    "STM32F3": "ARM_CM4F",
    "STM32F4": "ARM_CM4F",
    "STM32F7": "ARM_CM7/r0p1",
    "STM32L0": "ARM_CM0",
    "STM32L1": "ARM_CM3",
    "STM32L4": "ARM_CM4F",
    "STM32G0": "ARM_CM0",
    "STM32G4": "ARM_CM4F",
    "STM32H7": "ARM_CM4F",
    "GD32F1X0": "ARM_CM3",
    "EFM32TG": "ARM_CM3",
    "EFM32G": "ARM_CM3",
    "EFM32LG": "ARM_CM3",
    "EFM32GG": "ARM_CM3",
    "EFM32HG": "ARM_CM0",
    "EFM32WG": "ARM_CM4F",
    "EZR32WG": "ARM_CM4F",
    "LPC13XX": "ARM_CM3",
    "LPC17XX": "ARM_CM3",
    "LPC43XX_M4": "ARM_CM4F",
    "LPC43XX_M0": "ARM_CM0",
    "SAM3A": "ARM_CM3",
    "SAM3N": "ARM_CM3",
    "SAM3S": "ARM_CM3",
    "SAM3U": "ARM_CM3",
    "SAM3X": "ARM_CM3",
    "SAM4L": "ARM_CM4F",
    "SAMD": "ARM_CM0",
    "VF6XX": "ARM_CM4F",
    "PAC55XX": "ARM_CM4F",
    "LM3S": "ARM_CM3",
    "LM4F": "ARM_CM4F",
    "MSP432E4": "ARM_CM4F",
    "SWM050": "ARM_CM0",

    # Arduino/STM32Cube macros
    "STM32F0xx": "ARM_CM0",
    "STM32F1xx": "ARM_CM3",
    "STM32F2xx": "ARM_CM3",
    "STM32F3xx": "ARM_CM4F",
    "STM32F4xx": "ARM_CM4F",
    "STM32F7xx": "ARM_CM7/r0p1",
    "STM32G0xx": "ARM_CM0",
    "STM32G4xx": "ARM_CM4F",
    "STM32H7xx": "ARM_CM4F",
    "STM32L0xx": "ARM_CM0",
    "STM32L1xx": "ARM_CM3",
    "STM32L4xx": "ARM_CM4F",
    "STM32L5xx": "ARM_CM33/non_secure",
    "STM32WBxx": "ARM_CM4F",
    "STM32WLxx": "ARM_CM4F",

    # Raspberry Pi Pico macros
    "cortex-m0plus": "ARM_CM0"
}

platform = env.PioPlatform()
KERNEL_PATH = platform.get_package_dir("framework-freertos-kernel")
port = []

cpu = env.BoardConfig().get("build").get("cpu")
if cpu in devices:
    port.append(cpu)

# throw an exception if no macros match
if len(port) == 0:
    sys.stderr.write("ERROR: No device defined for FreeRTOS \n")
    device_keys = devices.keys()
    s = ' ,'.join(device_keys)
    sys.stderr.write(str(s) + '\n')
    env.Exit(1)

# Throw an exception if more than one device is defined
elif len(port) > 1:
    sys.stderr.write("ERROR: Multiple devices defined: %s \n Using %s as default device. \n" % (" ".join(port), port[0]))
    env.Exit(1)
else:
    ## Create FreeRTOS in a new construction environment
    libs = []
    sys.stdout.write("FreeRTOS-Kernel: building for %s \n" % devices[port[0]])
    env.Append(CPPPATH=[os.path.join(KERNEL_PATH,"FreeRTOS-Kernel","include","")])
    env.Append(CPPPATH=[os.path.join(KERNEL_PATH,"FreeRTOS-Kernel","portable","GCC", devices[port[0]],"")])
    env.Append(CPPPATH=env.get("PROJECT_INCLUDE_DIR", []))
    print(env['CPPPATH'])
    rtosENV = env.Clone()
    ## TODO: Automatically select heap management
    rtosENV.Append(SRC_FILTER = [
        os.path.join("+<FreeRTOS-Kernel",">"),
        os.path.join("-<FreeRTOS-Kernel","portable", ">"),
        # os.path.join("+<FreeRTOS-Kernel","portable","MemMang","heap_3.c>"),
        os.path.join("+<FreeRTOS-Kernel","portable","GCC",devices[port[0]], ">")
    ])
    ## TODO: Improve File collection
    libs.append(
        rtosENV.StaticLibrary(target='FreeRTOS', source=[
            os.path.join(KERNEL_PATH, "FreeRTOS-Kernel", "croutine.c"),
            os.path.join(KERNEL_PATH, "FreeRTOS-Kernel", "event_groups.c"),
            os.path.join(KERNEL_PATH, "FreeRTOS-Kernel", "list.c"),
            os.path.join(KERNEL_PATH, "FreeRTOS-Kernel", "queue.c"),
            os.path.join(KERNEL_PATH, "FreeRTOS-Kernel", "stream_buffer.c"),
            os.path.join(KERNEL_PATH, "FreeRTOS-Kernel", "tasks.c"),
            os.path.join(KERNEL_PATH, "FreeRTOS-Kernel", "timers.c"),
            os.path.join(KERNEL_PATH, "FreeRTOS-Kernel", "portable","MemMang", "heap_3.c"),
            os.path.join(KERNEL_PATH, "FreeRTOS-Kernel", "portable","GCC",devices[port[0]], "port.c"),

        ]))

    env.Prepend(LIBS=libs)
    
