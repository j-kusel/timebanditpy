timebandit
==========
polytempo composition suite for python and extensions

requires `numpy`_, `scipy`_, `Tkinter`_
_numpy: https://github.com/numpy/numpy
_scipy: https://github.com/scipy/scipy
_Tkinter: https://github.com/python/python-git/python/blob/master/Lib/lib-tk/Tkinter

current features
----------------
* calculating elapsed time across linear tempo ramps
* beat alignment between multiple instruments
* tbimg.py for generating graph paper / measure visualization
* easy load/save/merge filesystem with .tb extension
* multiple measure support
* automatic alignment / tempo fitting around anchor points

planned features
----------------
* .txt compiler / interpretive shell for line-by-line rapid score prototyping
* [pure data] external integration for audio preview / live performance 
[pure data]: https://github.com/pure-data/pure-data
* curve tension support
* MusicXML support
* Max/MSP integration / M4L device 
* App system for third-party plugins
