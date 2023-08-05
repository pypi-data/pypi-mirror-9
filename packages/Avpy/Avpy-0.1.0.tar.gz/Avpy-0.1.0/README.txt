====
Avpy
====

Avpy is a ctypes binding for libav and ffmpeg (see www.libav.org or www.ffmpeg.org). 

Typical usage often looks like this:

>>> from avpy import formats, codecInfo, Media
>>> print formats()
>>> print codecInfo('mp3', decode=True)
>>> m = Media('test.avi')
>>> print m.info()

More examples can be found in the examples folder. Documentation is available 
online: https://avpy.readthedocs.org/ 

This software is licensed under the LGPL v.2.1+. Examples (and tools)
are licensed under the Apache License 2.0.

Read LICENSE.txt for details or:

- http://choosealicense.com/licenses/lgpl-2.1
- http://choosealicense.com/licenses/apache-2.0

Features:

- libav: 
    - version 0.8: done
    - version 9: done
    - version 10: done
    - version 11: done
- ffmpeg:
    - version 1.2: done
- OS: 
    - Linux - BSD: done
    - MacOS: please report!
    - Windows: please report!
- avpy:
    - media info: done
    - basic video decoding: done
    - basic audio decoding: done
    - basic encoding: done
    - subtitle support: done
- doc:
    - sphinx doc: done
- examples:
    - dump image/wav/subtitle: done
    - alsaaudio: done
    - Pygame: done
    - PIL, pillow: done
    - PySDL2 video: done
    - encoding: done
- misc:
    - Python2.6, 2.7: done
    - Python3: done
    - PyPy: done

Install
=======

Requirements
------------

libav

for ubuntu users, please run the following command:

sudo apt-get install ffmpeg

Install from source:
--------------------

- Clone this repository
- python setup.py sdist
- pip install dist/Avpy-*.tar.gz

Please read doc/DEV.txt (virtualenvs) or doc/Windows.txt for additional information.

Contact
=======

sydhds __at__ gmail __dot__ com

