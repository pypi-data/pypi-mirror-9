#!/bin/bash
# create SamSifter packages for distribution

# svn copy https://www.biohazardous.de/svn/master_project/trunk https://www.biohazardous.de/svn/master_project/tags/release-0.1.2 -m "tagging 0.1.2 release"

# build the documentation
python3 setup.py build_sphinx

# source distributions
python3 setup.py sdist --formats=gztar,zip
#python3 setup.py sdist --formats=gztar,zip upload

# Windows installers (experimental)
python3 setup.py bdist_wininst --plat-name=win32
#python3 setup.py bdist_wininst --plat-name=win-amd64

md5sum dist/* > dist/md5sums.txt

exit
