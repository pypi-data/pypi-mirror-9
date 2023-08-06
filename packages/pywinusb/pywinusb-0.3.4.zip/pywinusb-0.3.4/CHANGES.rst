Release changes
===============

0.3.3
-----

 * Win7/64 fixes, PnP example fixed, show_hids.py now using local encodings, stdout encodings now not in library (should be part of applications), usage_pages.py UsagePage repr() fix.

0.3.2
-----

 * Python 3 filtering fix

0.3.1
-----

 * Python 2 and 3 support (tested with Python 3.2)

0.3.0
-----

 * Refactored setup api handling.

 * Many PyLint fixes.

0.2.9
-----

 * Fixed broken value array usages transactions

 * Better Setup API device paths handling

<= 0.2.8
--------

 * Fixed broken value array usages transactions

 * Fixing sending output / feature reports

 * Fixed broken input report handling

 * Stability improvements

 * Tweaked PnP example, added frame closing event handler, so the USB device is closed

 * Report reading threads and device closing optimizations

 * Fixed bugs preventing properly setting report usage variables after a HidReport().get()

 * Fixed raw_data.py example

 * Fixed bug preventing proper value array setting/getting items

 * Fixed deadlock when device unplugged

 * Added HidDevice.set_raw_data_handler(), and corresponding raw_data.py example script

 * Fixing output only mode (no input report for forced open)

 * Bringing a little bit of stability

 * Output only mode (no reading thread configured)

 * Kind of usable now

0.1.0 
-----

 * First public release

