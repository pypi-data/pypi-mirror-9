#####################
Mobile Map Downloader
#####################

**Mobile Map Downloader** is a command line program to download maps from the
Internet and install them on a mobile device, such as a smart phone. 

The program is intended to run on a (personal) computer, that has a fast and
cheap Internet connection, and a large hard disk. The downloaded maps are
stored on the personal computer. Only the maps that are used for the current
activity need to be installed on the mobile device. When different maps are
required for an other activity they can be quickly installed from the personal
computer's hard disk, without lengthy downloads. 

The software is currently in **beta state**. It can be productively used by
adventurous people, or semi experts. Expect it to lack some functionality, to
crash often, and to sometimes do unwanted things.

Currently the offline map programs **OsmAnd** and **Oruxmaps** are supported: 
    
* http://osmand.net/
* http://www.oruxmaps.com/index_en.html

Maps can be installed from **Osmand** and from **Openandromaps**, which means 
there is currently only one source of maps for each program:

* http://download.osmand.net/rawindexes/
* http://www.openandromaps.org/downloads

If you find any **errors**, or if you have good ideas for the program,
please put them into the project's **issue tracker**:

   https://github.com/eike-welk/mobile_map_downloader/issues 


Installation
=======================================

The program has only been tested on **Linux**. It should run on **Mac OS X** and **Windows** with only minor modifications, however installation on these operating systems is probably more complicated.

On **Linux**, open a terminal, get administrator/root privileges and type::
    
    pip install mobile-map-downloader --pre -U

Alternatively you can install the program with **Virtualenv**. With Virtualenv
you don't need root privileges, and can delete the program from your computer
without a trace::
    
    virtualenv virtualenv/  #can use any name for the directory
    cd virtualenv
    source bin/activate
    pip install mobile-map-downloader --pre -U

Broken ``pip`` in openSUSE 13.2
---------------------------------------

The Python installation program ``pip`` is broken in openSUSE 13.2, 
and possibly other Linux distributions: 
The present ``pip`` is for Python 3, while the system Python
is Python 2.7.8. The programs ``pip2`` or ``pip2.7`` are missing.

Therefore ``pip`` can't install any programs for the system Python on 
openSUSE 13.2. 

As a workaround a new ``pip`` can be easily installed from the program's
website: Download the script 
`get-pip.py <https://bootstrap.pypa.io/get-pip.py>`_
and run it with the system's regular Python interpreter. 
(This requires root privileges.)::

    python get-pip.py

This will create a working ``pip`` on your computer, which can then install ``mobile-map-downloader``. The process is described in more detail in Pip's documentation:

    https://pip.pypa.io/en/latest/installing.html


Usage
=======================================

List the maps of France, that the program can download::

    dlmap lss "*France*"

Patterns with wildcards should be quoted, because the shell might fill them in. 

Install maps of France for OsmAnd, on a certain device::

    dlmap -m /var/run/media/eike/1A042-B123/ install "osmand/France*"
 
The program has a built in help facility, detailed information about its
changing set of features has to be taken from it::

    dlmap -h

Each subcommand has its own help message::

    dlmap install -h


Development
=======================================

The program is written in the **Python** programming language, version **2.7**.
Contributions of code are very welcome. The program has currently only been
tested on **Linux**. It uses however no Linux specific functionality, so
porting to other operating systems should be easy. 

Development is coordinated on Github:

    https://github.com/eike-welk/mobile_map_downloader

The **issue tracker** for errors and good ideas is here:

   https://github.com/eike-welk/mobile_map_downloader/issues 

The program's page on PyPI, the Python Package Index, is:

    https://pypi.python.org/pypi/mobile-map-downloader/

