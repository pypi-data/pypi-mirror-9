from setuptools import setup
from os.path import join, dirname, abspath

import mob_map_dl.common


def relative(*path_fragments):
    "Create a file path that is relative to the location of this file."
    return abspath(join(dirname(abspath(__file__)), *path_fragments))

def read(fname):
    """
    Read a (text) file, and return its contents. 
    
    The file name must be relative to the location of this file.
    Used to put the contents of the README file into the library's 
    long_description below.
    """
    return open(relative(fname)).read()


#Start the setup machinery, give it detailed information about this library.
setup(name="mobile-map-downloader",
      version=mob_map_dl.common.VERSION,
      description="Download maps for mobile devices over broadband, "
                  "with a personal computer.",
      long_description=read("README.rst"),
      classifiers = [
        "Development Status :: 4 - Beta",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",],
      keywords="map, GPS, mobile device, download",
      author="Eike Welk",
      author_email="eike.welk@gmx.net",
      url="https://github.com/eike-welk/mobile_map_downloader",
      license="GNU General Public License v3 (GPLv3)",
      packages=["mob_map_dl"],
      scripts = ["dlmap"],
      install_requires=["lxml", "python-dateutil"],
#      zip_safe=False,
#      entry_points={},
#      include_package_data=True,
#      data_files=[("directory", ["directory/data_file.foo"])],
    )
