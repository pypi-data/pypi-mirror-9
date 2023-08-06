.. _devices:

Devices
=======

Nexus10
-------

Nexus10 is a 10 inch tablet device, which has dual-core A15.

To be able to use Nexus10 in WA, the following must be true:

    - USB Debugging Mode is enabled.
    - Generate USB debugging authorisation for the host machine

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.

core_names : list_of_strs (mandatory)
    This is a list of all cpu cores on the device with each
    element being the core type, e.g. ``['a7', 'a7', 'a15']``. The
    order of the cores must match the order they are listed in
    ``'/sys/devices/system/cpu'``. So in this case, ``'cpu0'`` must
    be an A7 core, and ``'cpu2'`` an A15.'

    default: ``['A15', 'A15']``

core_clusters : list_of_ints (mandatory)
    This is a list indicating the cluster affinity of the CPU cores,
    each element correponding to the cluster ID of the core coresponding
    to it's index. E.g. ``[0, 0, 1]`` indicates that cpu0 and cpu1 are on
    cluster 0, while cpu2 is on cluster 1.

    default: ``[0, 0]``

scheduler : str  
    Specifies the type of multi-core scheduling model utilized in the device. The value
    must be one of the following:

    :unknown: A generic Device interface is used to interact with the underlying device
              and the underlying scheduling model is unkown.
    :smp: A standard single-core or Symmetric Multi-Processing system.
    :hmp: ARM Heterogeneous Multi-Processing system.
    :iks: Linaro In-Kernel Switcher.
    :ea: ARM Energy-Aware scheduler.
    :other: Any other system not covered by the above.

            .. note:: most currently-available systems would fall under ``smp`` rather than
                      this value. ``other`` is there to future-proof against new schemes
                      not yet covered by WA.

    allowed values: ``'unknown'``, ``'smp'``, ``'hmp'``, ``'iks'``, ``'ea'``, ``'other'``

    default: ``'unknown'``

iks_switch_frequency : int  
    This is the switching frequency, in kilohertz, of IKS devices. This parameter *MUST NOT*
    be set for non-IKS device (i.e. ``scheduler != 'iks'``). If left unset for IKS devices,
    it will default to ``800000``, i.e. 800MHz.

adb_name : str  
    The unique ID of the device as output by "adb devices".

android_prompt : regex  
    The format  of matching the shell prompt in Android.

    default: ``r'^.*(shell|root)@.*:/ [#$] '``

working_directory : str  
    Directory that will be used WA on the device for output files etc.

    default: ``'/sdcard/wa-working'``

binaries_directory : str  
    Location of binaries on the device.

    default: ``'/system/bin'``

package_data_directory : str  
    Location of of data for an installed package (APK).

    default: ``'/data/data'``

external_storage_directory : str  
    Mount point for external storage.

    default: ``'/sdcard'``

connection : str  
    Specified the nature of adb connection.

    allowed values: ``'usb'``, ``'ethernet'``

    default: ``'usb'``

logcat_poll_period : int  
    If specified and is not ``0``, logcat will be polled every
    ``logcat_poll_period`` seconds, and buffered on the host. This
    can be used if a lot of output is expected in logcat and the fixed
    logcat buffer on the device is not big enough. The trade off is that
    this introduces some minor runtime overhead. Not set by default.

enable_screen_check : boolean  
    Specified whether the device should make sure that the screen is on
    during initialization.


Nexus5
------

Adapter for Nexus 5.

To be able to use Nexus5 in WA, the following must be true:

    - USB Debugging Mode is enabled.
    - Generate USB debugging authorisation for the host machine

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.

core_names : list_of_strs (mandatory)
    This is a list of all cpu cores on the device with each
    element being the core type, e.g. ``['a7', 'a7', 'a15']``. The
    order of the cores must match the order they are listed in
    ``'/sys/devices/system/cpu'``. So in this case, ``'cpu0'`` must
    be an A7 core, and ``'cpu2'`` an A15.'

    default: ``['krait400', 'krait400', 'krait400', 'krait400']``

core_clusters : list_of_ints (mandatory)
    This is a list indicating the cluster affinity of the CPU cores,
    each element correponding to the cluster ID of the core coresponding
    to it's index. E.g. ``[0, 0, 1]`` indicates that cpu0 and cpu1 are on
    cluster 0, while cpu2 is on cluster 1.

    default: ``[0, 0, 0, 0]``

scheduler : str  
    Specifies the type of multi-core scheduling model utilized in the device. The value
    must be one of the following:

    :unknown: A generic Device interface is used to interact with the underlying device
              and the underlying scheduling model is unkown.
    :smp: A standard single-core or Symmetric Multi-Processing system.
    :hmp: ARM Heterogeneous Multi-Processing system.
    :iks: Linaro In-Kernel Switcher.
    :ea: ARM Energy-Aware scheduler.
    :other: Any other system not covered by the above.

            .. note:: most currently-available systems would fall under ``smp`` rather than
                      this value. ``other`` is there to future-proof against new schemes
                      not yet covered by WA.

    allowed values: ``'unknown'``, ``'smp'``, ``'hmp'``, ``'iks'``, ``'ea'``, ``'other'``

    default: ``'unknown'``

iks_switch_frequency : int  
    This is the switching frequency, in kilohertz, of IKS devices. This parameter *MUST NOT*
    be set for non-IKS device (i.e. ``scheduler != 'iks'``). If left unset for IKS devices,
    it will default to ``800000``, i.e. 800MHz.

adb_name : str  
    The unique ID of the device as output by "adb devices".

android_prompt : regex  
    The format  of matching the shell prompt in Android.

    default: ``r'^.*(shell|root)@.*:/ [#$] '``

working_directory : str  
    Directory that will be used WA on the device for output files etc.

    default: ``'/sdcard/wa-working'``

binaries_directory : str  
    Location of binaries on the device.

    default: ``'/system/bin'``

package_data_directory : str  
    Location of of data for an installed package (APK).

    default: ``'/data/data'``

external_storage_directory : str  
    Mount point for external storage.

    default: ``'/sdcard'``

connection : str  
    Specified the nature of adb connection.

    allowed values: ``'usb'``, ``'ethernet'``

    default: ``'usb'``

logcat_poll_period : int  
    If specified and is not ``0``, logcat will be polled every
    ``logcat_poll_period`` seconds, and buffered on the host. This
    can be used if a lot of output is expected in logcat and the fixed
    logcat buffer on the device is not big enough. The trade off is that
    this introduces some minor runtime overhead. Not set by default.

enable_screen_check : boolean  
    Specified whether the device should make sure that the screen is on
    during initialization.


Note3
-----

Adapter for Galaxy Note 3.

To be able to use Note3 in WA, the following must be true:

    - USB Debugging Mode is enabled.
    - Generate USB debugging authorisation for the host machine

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.

core_names : list_of_strs (mandatory)
    This is a list of all cpu cores on the device with each
    element being the core type, e.g. ``['a7', 'a7', 'a15']``. The
    order of the cores must match the order they are listed in
    ``'/sys/devices/system/cpu'``. So in this case, ``'cpu0'`` must
    be an A7 core, and ``'cpu2'`` an A15.'

    default: ``['A15', 'A15', 'A15', 'A15']``

core_clusters : list_of_ints (mandatory)
    This is a list indicating the cluster affinity of the CPU cores,
    each element correponding to the cluster ID of the core coresponding
    to it's index. E.g. ``[0, 0, 1]`` indicates that cpu0 and cpu1 are on
    cluster 0, while cpu2 is on cluster 1.

    default: ``[0, 0, 0, 0]``

scheduler : str  
    Specifies the type of multi-core scheduling model utilized in the device. The value
    must be one of the following:

    :unknown: A generic Device interface is used to interact with the underlying device
              and the underlying scheduling model is unkown.
    :smp: A standard single-core or Symmetric Multi-Processing system.
    :hmp: ARM Heterogeneous Multi-Processing system.
    :iks: Linaro In-Kernel Switcher.
    :ea: ARM Energy-Aware scheduler.
    :other: Any other system not covered by the above.

            .. note:: most currently-available systems would fall under ``smp`` rather than
                      this value. ``other`` is there to future-proof against new schemes
                      not yet covered by WA.

    allowed values: ``'unknown'``, ``'smp'``, ``'hmp'``, ``'iks'``, ``'ea'``, ``'other'``

    default: ``'unknown'``

iks_switch_frequency : int  
    This is the switching frequency, in kilohertz, of IKS devices. This parameter *MUST NOT*
    be set for non-IKS device (i.e. ``scheduler != 'iks'``). If left unset for IKS devices,
    it will default to ``800000``, i.e. 800MHz.

adb_name : str  
    The unique ID of the device as output by "adb devices".

android_prompt : regex  
    The format  of matching the shell prompt in Android.

    default: ``r'^.*(shell|root)@.*:/ [#$] '``

working_directory : str  
    Directory that will be used WA on the device for output files etc.

    default: ``'/storage/sdcard0/wa-working'``

binaries_directory : str  
    Location of binaries on the device.

    default: ``'/system/bin'``

package_data_directory : str  
    Location of of data for an installed package (APK).

    default: ``'/data/data'``

external_storage_directory : str  
    Mount point for external storage.

    default: ``'/sdcard'``

connection : str  
    Specified the nature of adb connection.

    allowed values: ``'usb'``, ``'ethernet'``

    default: ``'usb'``

logcat_poll_period : int  
    If specified and is not ``0``, logcat will be polled every
    ``logcat_poll_period`` seconds, and buffered on the host. This
    can be used if a lot of output is expected in logcat and the fixed
    logcat buffer on the device is not big enough. The trade off is that
    this introduces some minor runtime overhead. Not set by default.

enable_screen_check : boolean  
    Specified whether the device should make sure that the screen is on
    during initialization.


TC2
---

TC2 is a development board, which has three A7 cores and two A15 cores.

TC2 has a number of boot parameters which are:

    :root_mount: Defaults to '/media/VEMSD'
    :boot_firmware: It has only two boot firmware options, which are
                    uefi and bootmon. Defaults to 'uefi'.
    :fs_medium: Defaults to 'usb'.
    :device_working_directory: The direcitory that WA will be using to copy
                               files to. Defaults to 'data/local/usecase'
    :serial_device: The serial device which TC2 is connected to. Defaults to
                    '/dev/ttyS0'.
    :serial_baud: Defaults to 38400.
    :serial_max_timeout: Serial timeout value in seconds. Defaults to 600.
    :serial_log: Defaults to standard output.
    :init_timeout: The timeout in seconds to init the device. Defaults set
                   to 30.
    :always_delete_uefi_entry: If true, it will delete the ufi entry.
                               Defaults to True.
    :psci_enable: Enabling the psci. Defaults to True.
    :host_working_directory: The host working directory. Defaults to None.
    :disable_boot_configuration: Disables boot configuration through images.txt and board.txt. When
                                 this is ``True``, those two files will not be overwritten in VEMSD.
                                 This option may be necessary if the firmware version in the ``TC2``
                                 is not compatible with the templates in WA. Please note that enabling
                                 this will prevent you form being able to set ``boot_firmware`` and
                                 ``mode`` parameters. Defaults to ``False``.

TC2 can also have a number of different booting mode, which are:

    :mp_a7_only: Only the A7 cluster.
    :mp_a7_bootcluster: Both A7 and A15 clusters, but it boots on A7
                        cluster.
    :mp_a15_only: Only the A15 cluster.
    :mp_a15_bootcluster: Both A7 and A15 clusters, but it boots on A15
                         clusters.
    :iks_cpu: Only A7 cluster with only 2 cpus.
    :iks_a15: Only A15 cluster.
    :iks_a7: Same as iks_cpu
    :iks_ns_a15: Both A7 and A15 clusters.
    :iks_ns_a7: Both A7 and A15 clusters.

The difference between mp and iks is the scheduling policy.

TC2 takes the following runtime parameters

    :a7_cores: Number of active A7 cores.
    :a15_cores: Number of active A15 cores.
    :a7_governor: CPUFreq governor for the A7 cluster.
    :a15_governor: CPUFreq governor for the A15 cluster.
    :a7_min_frequency: Minimum CPU frequency for the A7 cluster.
    :a15_min_frequency: Minimum CPU frequency for the A15 cluster.
    :a7_max_frequency: Maximum CPU frequency for the A7 cluster.
    :a15_max_frequency: Maximum CPU frequency for the A7 cluster.
    :irq_affinity: lambda x: Which cluster will receive IRQs.
    :cpuidle: Whether idle states should be enabled.
    :sysfile_values: A dict mapping a complete file path to the value that
                     should be echo'd into it. By default, the file will be
                     subsequently read to verify that the value was written
                     into it with DeviceError raised otherwise. For write-only
                     files, this check can be disabled by appending a ``!`` to
                     the end of the file path.

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.

core_names : list_of_strs  
    This parameter will be ignored for TC2

core_clusters : list_of_ints  
    This parameter will be ignored for TC2

scheduler : str  
    Specifies the type of multi-core scheduling model utilized in the device. The value
    must be one of the following:

    :unknown: A generic Device interface is used to interact with the underlying device
              and the underlying scheduling model is unkown.
    :smp: A standard single-core or Symmetric Multi-Processing system.
    :hmp: ARM Heterogeneous Multi-Processing system.
    :iks: Linaro In-Kernel Switcher.
    :ea: ARM Energy-Aware scheduler.
    :other: Any other system not covered by the above.

            .. note:: most currently-available systems would fall under ``smp`` rather than
                      this value. ``other`` is there to future-proof against new schemes
                      not yet covered by WA.

    allowed values: ``'unknown'``, ``'smp'``, ``'hmp'``, ``'iks'``, ``'ea'``, ``'other'``

    default: ``'hmp'``

iks_switch_frequency : int  
    This is the switching frequency, in kilohertz, of IKS devices. This parameter *MUST NOT*
    be set for non-IKS device (i.e. ``scheduler != 'iks'``). If left unset for IKS devices,
    it will default to ``800000``, i.e. 800MHz.

adb_name : str  
    The unique ID of the device as output by "adb devices".

android_prompt : regex  
    The format  of matching the shell prompt in Android.

    default: ``r'^.*(shell|root)@.*:/ [#$] '``

working_directory : str  
    Directory that will be used WA on the device for output files etc.

    default: ``'/sdcard/wa-working'``

binaries_directory : str  
    Location of binaries on the device.

    default: ``'/system/bin'``

package_data_directory : str  
    Location of of data for an installed package (APK).

    default: ``'/data/data'``

external_storage_directory : str  
    Mount point for external storage.

    default: ``'/sdcard'``

connection : str  
    Specified the nature of adb connection.

    allowed values: ``'usb'``, ``'ethernet'``

    default: ``'usb'``

logcat_poll_period : int  
    If specified and is not ``0``, logcat will be polled every
    ``logcat_poll_period`` seconds, and buffered on the host. This
    can be used if a lot of output is expected in logcat and the fixed
    logcat buffer on the device is not big enough. The trade off is that
    this introduces some minor runtime overhead. Not set by default.

enable_screen_check : boolean  
    Specified whether the device should make sure that the screen is on
    during initialization.


generic_android
---------------

Generic Android device. Use this if you do not have a device file for
your device.

This implements the minimum functionality that should be supported by
all android devices.

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.

core_names : list_of_strs (mandatory)
    This is a list of all cpu cores on the device with each
    element being the core type, e.g. ``['a7', 'a7', 'a15']``. The
    order of the cores must match the order they are listed in
    ``'/sys/devices/system/cpu'``. So in this case, ``'cpu0'`` must
    be an A7 core, and ``'cpu2'`` an A15.'

core_clusters : list_of_ints (mandatory)
    This is a list indicating the cluster affinity of the CPU cores,
    each element correponding to the cluster ID of the core coresponding
    to it's index. E.g. ``[0, 0, 1]`` indicates that cpu0 and cpu1 are on
    cluster 0, while cpu2 is on cluster 1.

scheduler : str  
    Specifies the type of multi-core scheduling model utilized in the device. The value
    must be one of the following:

    :unknown: A generic Device interface is used to interact with the underlying device
              and the underlying scheduling model is unkown.
    :smp: A standard single-core or Symmetric Multi-Processing system.
    :hmp: ARM Heterogeneous Multi-Processing system.
    :iks: Linaro In-Kernel Switcher.
    :ea: ARM Energy-Aware scheduler.
    :other: Any other system not covered by the above.

            .. note:: most currently-available systems would fall under ``smp`` rather than
                      this value. ``other`` is there to future-proof against new schemes
                      not yet covered by WA.

    allowed values: ``'unknown'``, ``'smp'``, ``'hmp'``, ``'iks'``, ``'ea'``, ``'other'``

    default: ``'unknown'``

iks_switch_frequency : int  
    This is the switching frequency, in kilohertz, of IKS devices. This parameter *MUST NOT*
    be set for non-IKS device (i.e. ``scheduler != 'iks'``). If left unset for IKS devices,
    it will default to ``800000``, i.e. 800MHz.

adb_name : str  
    The unique ID of the device as output by "adb devices".

android_prompt : regex  
    The format  of matching the shell prompt in Android.

    default: ``r'^.*(shell|root)@.*:/ [#$] '``

working_directory : str  
    Directory that will be used WA on the device for output files etc.

    default: ``'/sdcard/wa-working'``

binaries_directory : str  
    Location of binaries on the device.

    default: ``'/system/bin'``

package_data_directory : str  
    Location of of data for an installed package (APK).

    default: ``'/data/data'``

external_storage_directory : str  
    Mount point for external storage.

    default: ``'/sdcard'``

connection : str  
    Specified the nature of adb connection.

    allowed values: ``'usb'``, ``'ethernet'``

    default: ``'usb'``

logcat_poll_period : int  
    If specified and is not ``0``, logcat will be polled every
    ``logcat_poll_period`` seconds, and buffered on the host. This
    can be used if a lot of output is expected in logcat and the fixed
    logcat buffer on the device is not big enough. The trade off is that
    this introduces some minor runtime overhead. Not set by default.

enable_screen_check : boolean  
    Specified whether the device should make sure that the screen is on
    during initialization.


generic_linux
-------------

Generic Linux device. Use this if you do not have a device file for
your device.

This implements the minimum functionality that should be supported by
all Linux devices.

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.

core_names : list_of_strs (mandatory)
    This is a list of all cpu cores on the device with each
    element being the core type, e.g. ``['a7', 'a7', 'a15']``. The
    order of the cores must match the order they are listed in
    ``'/sys/devices/system/cpu'``. So in this case, ``'cpu0'`` must
    be an A7 core, and ``'cpu2'`` an A15.'

core_clusters : list_of_ints (mandatory)
    This is a list indicating the cluster affinity of the CPU cores,
    each element correponding to the cluster ID of the core coresponding
    to it's index. E.g. ``[0, 0, 1]`` indicates that cpu0 and cpu1 are on
    cluster 0, while cpu2 is on cluster 1.

scheduler : str  
    Specifies the type of multi-core scheduling model utilized in the device. The value
    must be one of the following:

    :unknown: A generic Device interface is used to interact with the underlying device
              and the underlying scheduling model is unkown.
    :smp: A standard single-core or Symmetric Multi-Processing system.
    :hmp: ARM Heterogeneous Multi-Processing system.
    :iks: Linaro In-Kernel Switcher.
    :ea: ARM Energy-Aware scheduler.
    :other: Any other system not covered by the above.

            .. note:: most currently-available systems would fall under ``smp`` rather than
                      this value. ``other`` is there to future-proof against new schemes
                      not yet covered by WA.

    allowed values: ``'unknown'``, ``'smp'``, ``'hmp'``, ``'iks'``, ``'ea'``, ``'other'``

    default: ``'unknown'``

iks_switch_frequency : int  
    This is the switching frequency, in kilohertz, of IKS devices. This parameter *MUST NOT*
    be set for non-IKS device (i.e. ``scheduler != 'iks'``). If left unset for IKS devices,
    it will default to ``800000``, i.e. 800MHz.

host : str (mandatory)
    Host name or IP address for the device.

username : str (mandatory)
    User name for the account on the device.

password : str  
    Password for the account on the device (for password-based auth).

keyfile : str  
    Keyfile to be used for key-based authentication.

port : int  
    SSH port number on the device.

use_telnet : boolean  
    Optionally, telnet may be used instead of ssh, though this is discouraged.

working_directory : str  
    Working directory to be used by WA. This must be in a location where the specified user
    has write permissions. This will default to /home/<username>/wa (or to /root/wa, if
    username is 'root').

binaries_directory : str  
    Location of executable binaries on this device (must be in PATH).

    default: ``'/usr/local/bin'``

property_files : list_of_strs  
    A list of paths to files containing static OS properties. These will be pulled into the
    __meta directory in output for each run in order to provide information about the platfrom.
    These paths do not have to exist and will be ignored if the path is not present on a
    particular device.

    default: ``['/proc/version', '/etc/debian_version', '/etc/lsb-release', '/etc/arch-release']``


juno
----

ARM Juno next generation big.LITTLE development platform.

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.

core_names : list_of_strs (mandatory)
    This is a list of all cpu cores on the device with each
    element being the core type, e.g. ``['a7', 'a7', 'a15']``. The
    order of the cores must match the order they are listed in
    ``'/sys/devices/system/cpu'``. So in this case, ``'cpu0'`` must
    be an A7 core, and ``'cpu2'`` an A15.'

    default: ``['a53', 'a53', 'a53', 'a53', 'a57', 'a57']``

core_clusters : list_of_ints (mandatory)
    This is a list indicating the cluster affinity of the CPU cores,
    each element correponding to the cluster ID of the core coresponding
    to it's index. E.g. ``[0, 0, 1]`` indicates that cpu0 and cpu1 are on
    cluster 0, while cpu2 is on cluster 1.

    default: ``[0, 0, 0, 0, 1, 1]``

scheduler : str  
    Specifies the type of multi-core scheduling model utilized in the device. The value
    must be one of the following:

    :unknown: A generic Device interface is used to interact with the underlying device
              and the underlying scheduling model is unkown.
    :smp: A standard single-core or Symmetric Multi-Processing system.
    :hmp: ARM Heterogeneous Multi-Processing system.
    :iks: Linaro In-Kernel Switcher.
    :ea: ARM Energy-Aware scheduler.
    :other: Any other system not covered by the above.

            .. note:: most currently-available systems would fall under ``smp`` rather than
                      this value. ``other`` is there to future-proof against new schemes
                      not yet covered by WA.

    allowed values: ``'unknown'``, ``'smp'``, ``'hmp'``, ``'iks'``, ``'ea'``, ``'other'``

    default: ``'hmp'``

iks_switch_frequency : int  
    This is the switching frequency, in kilohertz, of IKS devices. This parameter *MUST NOT*
    be set for non-IKS device (i.e. ``scheduler != 'iks'``). If left unset for IKS devices,
    it will default to ``800000``, i.e. 800MHz.

adb_name : str  
    The unique ID of the device as output by "adb devices".

android_prompt : regex  
    The format  of matching the shell prompt in Android.

    default: ``r'^.*(shell|root)@.*:/ [#$] '``

working_directory : str  
    Directory that will be used WA on the device for output files etc.

    default: ``'/sdcard/wa-working'``

binaries_directory : str  
    Location of binaries on the device.

    default: ``'/system/bin'``

package_data_directory : str  
    Location of of data for an installed package (APK).

    default: ``'/data/data'``

external_storage_directory : str  
    Mount point for external storage.

    default: ``'/sdcard'``

connection : str  
    Specified the nature of adb connection.

    allowed values: ``'usb'``, ``'ethernet'``

    default: ``'usb'``

logcat_poll_period : int  
    If specified and is not ``0``, logcat will be polled every
    ``logcat_poll_period`` seconds, and buffered on the host. This
    can be used if a lot of output is expected in logcat and the fixed
    logcat buffer on the device is not big enough. The trade off is that
    this introduces some minor runtime overhead. Not set by default.

enable_screen_check : boolean  
    Specified whether the device should make sure that the screen is on
    during initialization.

retries : int  
    Specifies the number of times the device will attempt to recover
    (normally, with a hard reset) if it detects that something went wrong.

    default: ``2``

uefi_entry : str  
    The name of the entry to use (will be created if does not exist).

    default: ``'WA'``

microsd_mount_point : str  
    Location at which the device's MicroSD card will be mounted.

    default: ``'/media/JUNO'``

port : str  
    Serial port on which the device is connected.

    default: ``'/dev/ttyS0'``

baudrate : int  
    Serial connection baud.

    default: ``115200``

timeout : int  
    Serial connection timeout.

    default: ``300``


odroidxu3
---------

HardKernel Odroid XU3 development board.

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.

core_names : list_of_strs (mandatory)
    This is a list of all cpu cores on the device with each
    element being the core type, e.g. ``['a7', 'a7', 'a15']``. The
    order of the cores must match the order they are listed in
    ``'/sys/devices/system/cpu'``. So in this case, ``'cpu0'`` must
    be an A7 core, and ``'cpu2'`` an A15.'

    default: ``['a7', 'a7', 'a7', 'a7', 'a15', 'a15', 'a15', 'a15']``

core_clusters : list_of_ints (mandatory)
    This is a list indicating the cluster affinity of the CPU cores,
    each element correponding to the cluster ID of the core coresponding
    to it's index. E.g. ``[0, 0, 1]`` indicates that cpu0 and cpu1 are on
    cluster 0, while cpu2 is on cluster 1.

    default: ``[0, 0, 0, 0, 1, 1, 1, 1]``

scheduler : str  
    Specifies the type of multi-core scheduling model utilized in the device. The value
    must be one of the following:

    :unknown: A generic Device interface is used to interact with the underlying device
              and the underlying scheduling model is unkown.
    :smp: A standard single-core or Symmetric Multi-Processing system.
    :hmp: ARM Heterogeneous Multi-Processing system.
    :iks: Linaro In-Kernel Switcher.
    :ea: ARM Energy-Aware scheduler.
    :other: Any other system not covered by the above.

            .. note:: most currently-available systems would fall under ``smp`` rather than
                      this value. ``other`` is there to future-proof against new schemes
                      not yet covered by WA.

    allowed values: ``'unknown'``, ``'smp'``, ``'hmp'``, ``'iks'``, ``'ea'``, ``'other'``

    default: ``'unknown'``

iks_switch_frequency : int  
    This is the switching frequency, in kilohertz, of IKS devices. This parameter *MUST NOT*
    be set for non-IKS device (i.e. ``scheduler != 'iks'``). If left unset for IKS devices,
    it will default to ``800000``, i.e. 800MHz.

adb_name : str  
    The unique ID of the device as output by "adb devices".

    default: ``'BABABEEFBABABEEF'``

android_prompt : regex  
    The format  of matching the shell prompt in Android.

    default: ``r'^.*(shell|root)@.*:/ [#$] '``

working_directory : str  
    Directory that will be used WA on the device for output files etc.

    default: ``'/data/local/wa-working'``

binaries_directory : str  
    Location of binaries on the device.

    default: ``'/system/bin'``

package_data_directory : str  
    Location of of data for an installed package (APK).

    default: ``'/data/data'``

external_storage_directory : str  
    Mount point for external storage.

    default: ``'/sdcard'``

connection : str  
    Specified the nature of adb connection.

    allowed values: ``'usb'``, ``'ethernet'``

    default: ``'usb'``

logcat_poll_period : int  
    If specified and is not ``0``, logcat will be polled every
    ``logcat_poll_period`` seconds, and buffered on the host. This
    can be used if a lot of output is expected in logcat and the fixed
    logcat buffer on the device is not big enough. The trade off is that
    this introduces some minor runtime overhead. Not set by default.

enable_screen_check : boolean  
    Specified whether the device should make sure that the screen is on
    during initialization.

port : str  
    Serial port on which the device is connected

    default: ``'/dev/ttyUSB0'``

baudrate : int  
    Serial connection baud rate

    default: ``115200``


odroidxu3_linux
---------------

HardKernel Odroid XU3 development board (Ubuntu image).

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.

core_names : list_of_strs (mandatory)
    This is a list of all cpu cores on the device with each
    element being the core type, e.g. ``['a7', 'a7', 'a15']``. The
    order of the cores must match the order they are listed in
    ``'/sys/devices/system/cpu'``. So in this case, ``'cpu0'`` must
    be an A7 core, and ``'cpu2'`` an A15.'

    default: ``['a7', 'a7', 'a7', 'a7', 'a15', 'a15', 'a15', 'a15']``

core_clusters : list_of_ints (mandatory)
    This is a list indicating the cluster affinity of the CPU cores,
    each element correponding to the cluster ID of the core coresponding
    to it's index. E.g. ``[0, 0, 1]`` indicates that cpu0 and cpu1 are on
    cluster 0, while cpu2 is on cluster 1.

    default: ``[0, 0, 0, 0, 1, 1, 1, 1]``

scheduler : str  
    Specifies the type of multi-core scheduling model utilized in the device. The value
    must be one of the following:

    :unknown: A generic Device interface is used to interact with the underlying device
              and the underlying scheduling model is unkown.
    :smp: A standard single-core or Symmetric Multi-Processing system.
    :hmp: ARM Heterogeneous Multi-Processing system.
    :iks: Linaro In-Kernel Switcher.
    :ea: ARM Energy-Aware scheduler.
    :other: Any other system not covered by the above.

            .. note:: most currently-available systems would fall under ``smp`` rather than
                      this value. ``other`` is there to future-proof against new schemes
                      not yet covered by WA.

    allowed values: ``'unknown'``, ``'smp'``, ``'hmp'``, ``'iks'``, ``'ea'``, ``'other'``

    default: ``'unknown'``

iks_switch_frequency : int  
    This is the switching frequency, in kilohertz, of IKS devices. This parameter *MUST NOT*
    be set for non-IKS device (i.e. ``scheduler != 'iks'``). If left unset for IKS devices,
    it will default to ``800000``, i.e. 800MHz.

host : str (mandatory)
    Host name or IP address for the device.

username : str (mandatory)
    User name for the account on the device.

password : str  
    Password for the account on the device (for password-based auth).

keyfile : str  
    Keyfile to be used for key-based authentication.

port : int  
    SSH port number on the device.

use_telnet : boolean  
    Optionally, telnet may be used instead of ssh, though this is discouraged.

working_directory : str  
    Working directory to be used by WA. This must be in a location where the specified user
    has write permissions. This will default to /home/<username>/wa (or to /root/wa, if
    username is 'root').

binaries_directory : str  
    Location of executable binaries on this device (must be in PATH).

    default: ``'/usr/local/bin'``

property_files : list_of_strs  
    A list of paths to files containing static OS properties. These will be pulled into the
    __meta directory in output for each run in order to provide information about the platfrom.
    These paths do not have to exist and will be ignored if the path is not present on a
    particular device.

    default: ``['/proc/version', '/etc/debian_version', '/etc/lsb-release', '/etc/arch-release']``


