import sys as _sys

if _sys.platform.startswith("darwin"):
    from dn.usb.macosx import is_kernel_driver_active, detach_kernel_driver
    from dn.usb.macosx import attach_kernel_driver
elif _sys.platform.startswith('linux'):
    from dn.usb.linux import is_kernel_driver_active, detach_kernel_driver
    from dn.usb.linux import attach_kernel_driver
else:
    raise Exception("Sorry. Only mac and linux are supported")
