import sys as _sys

if _sys.platform.startswith("darwin"):
    from dn.lusb.macosx import is_kernel_driver_active, detach_kernel_driver
    from dn.lusb.macosx import attach_kernel_driver
elif _sys.platform.startswith('linux'):
    from dn.lusb.linux import is_kernel_driver_active, detach_kernel_driver
    from dn.lusb.linux import attach_kernel_driver
else:
    raise Exception("Sorry. Only mac and linux are supported")
