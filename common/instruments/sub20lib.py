import os
from ctypes import c_char_p, c_int, c_void_p, c_char, sizeof, POINTER, byref, cdll, Union, Structure
from sys import getwindowsversion


class Sub20Lib:
    sub20dll = cdll.LoadLibrary("C:/Windows/System32/sub20.dll")

    sub_find_devices = sub20dll.sub_find_devices
    sub_find_devices.argtypes = [c_void_p]
    sub_find_devices.restype = c_void_p

    sub_open = sub20dll.sub_open
    sub_open.argtypes = [c_void_p]
    sub_open.restype = c_void_p

    sub_close = sub20dll.sub_close
    sub_close.argtypes = [c_void_p]

    sub_reset = sub20dll.sub_reset
    sub_reset.argtypes = [c_void_p]

    sub_get_product_id = sub20dll.sub_get_product_id
    sub_get_product_id.argtypes = [c_void_p, c_char_p, c_int]

    sub_get_serial_number = sub20dll.sub_get_serial_number
    sub_get_serial_number.argtypes = [c_void_p, c_char_p, c_int]

    '''
    sub_strerror = sub20dll.sub_strerror
    sub_strerror.argtypes = [c_int]
    sub_strerror.restype = c_char_p
    '''

    sub_i2c_scan = sub20dll.sub_i2c_scan
    sub_i2c_scan.argtypes = [c_void_p, POINTER(c_int), c_char_p]

    sub_i2c_read = sub20dll.sub_i2c_read
    sub_i2c_read.argtypes = [c_void_p, c_int, c_int, c_int, c_char_p, c_int]

    sub_i2c_write = sub20dll.sub_i2c_write
    sub_i2c_write.argtypes = [c_void_p, c_int, c_int, c_int, c_char_p, c_int]
