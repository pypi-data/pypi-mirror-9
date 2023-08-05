#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# BibReview
# Copyright (C) 2014 Jean-Baptiste LAMY

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os, os.path, sys, glob

HERE = os.path.dirname(sys.argv[0]) or "."

if len(sys.argv) <= 1: sys.argv.append("install")

import setuptools

data_files   = []
package_data = {
  "bibreview" : ["data/*.*"]
}

if os.name == "posix":
  for mo_file in glob.glob(os.path.abspath(os.path.join(HERE, "locale", "*", "LC_MESSAGES", "*.mo"))):
    lang = os.path.dirname(mo_file).split(os.sep)[-2]
    data_files.append( (os.path.join("/", "usr", "share", "locale", lang, "LC_MESSAGES"), [mo_file]) )
else:
  package_data["bibreview"].append("locale/*/*/*.mo")


  
setuptools.setup(
  name         = "BibReview",
  version      = "0.2.2",
  license      = "GPLv3+",
  description  = "BibReview is a software for managing bibliographic database. It includes avanced functions for literature reviews.",
  long_description = open(os.path.join(HERE, "README.rst")).read(),
  
  author       = "Lamy Jean-Baptiste (Jiba)",
  author_email = "<jibalamy *@* free *.* fr>",
  url          = "http://www.lesfleursdunormal.fr/static/informatique/bibreview/index_fr.html",
  classifiers  = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 2",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Environment :: X11 Applications :: GTK",
    "Intended Audience :: Science/Research",
    "Operating System :: POSIX :: Linux",
    ],
  
  requires = ["pygtk", "editobj2"],
  zip_safe = False,
  
  scripts      = ["bibreview"],
  package_dir  = {"bibreview" : "."},
  packages     = ["bibreview"],
  package_data = package_data,
  data_files   = data_files,
)
