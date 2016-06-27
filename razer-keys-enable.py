#!/usr/bin/python
# -*- coding: utf-8 -*-
# Razer Keys Enable 
# Copyright © 2012 Michael Fincham <michael@finch.am>
# Copyright © 2012 Jelle Licht <jlicht@fsfe.org>
#
# Razer Keys Enable is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.
#
# Razer Keys Enable is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Razer Keys Enable. If not, see <http://www.gnu.org/licenses/>.

# Enables the M1-5 and FN keys to send scancodes on the Razer
# BlackWidow,BlackWidow Ultimate, Lachesis and Anansi keyboards.
#
# Requires the PyUSB library.

import sys
import usb

USB_VENDOR = 0x1532  # Razer
USB_PRODUCT = 0x010d  # BlackWidow / BlackWidow Ultimate

# These values are from the USB HID 1.11 spec section 7.2.
# <http://www.usb.org/developers/devclass_docs/HID1_11.pdf>
USB_REQUEST_TYPE = 0x21  # Host To Device | Class | Interface
USB_REQUEST = 0x09  # SET_REPORT

# These values are from the manufacturer's driver.
USB_VALUE = 0x0300
USB_INDEX = 0x2
USB_INTERFACE = 2

# These magic bytes are also from the manufacturer's driver.
USB_BUFFER = b"\x00\x00\x00\x00\x00\x01\x00\x04\x03\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00"


def find_keyboard_device():
    for bus in usb.busses():
        for device in bus.devices:
            if device.idVendor == USB_VENDOR and \
               device.idProduct == USB_PRODUCT:
                return device


def main():

    device = find_keyboard_device()
    if device == None:
        sys.stderr.write("BlackWidow not found.\n")
        sys.exit(1)

    try:
        handle = device.open()
        interface = device.configurations[0].interfaces[0][USB_INTERFACE]
        endpoint = interface.endpoints[0]
    except:
        sys.stderr.write("Could not select configuration endpoint.\n")
        sys.exit(1)

    try:
        handle.detachKernelDriver(interface)
    except usb.USBError:
        pass  # This is usually because the enabler was run before and the kernel is still detached
    except Exception:
        sys.stderr.write("A very unusual error happened trying to detch the kernel driver.\n")
        sys.exit(1)

    try:
        handle.claimInterface(interface)
    except:
        sys.stderr.write("Unable to claim the configuration interface. Do you have the appropriate privileges?\n")
        sys.exit(1)

    result = 0

    try:
        result = handle.controlMsg(requestType=USB_REQUEST_TYPE,
                                   request=USB_REQUEST,
                                   value=USB_VALUE,
                                   index=USB_INDEX,
                                   buffer=USB_BUFFER)
    except:
        sys.stderr.write("Could not write the magic bytes to the BlackWidow.\n")

    if result == len(USB_BUFFER):
        sys.stderr.write("Configured BlackWidow.\n")

    try:
        handle.releaseInterface()
    except:
        sys.stderr.write("Unable to release interface.\n")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
