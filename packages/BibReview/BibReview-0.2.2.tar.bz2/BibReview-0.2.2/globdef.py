# -*- coding: utf-8 -*-

# BibReview
# Copyright (C) 2012 Jean-Baptiste LAMY (jibalamy at free . fr)
# BibReview is developped by Jean-Baptiste LAMY, at LIM&BIO,
# UFR SMBH, Université Paris 13, Sorbonne Paris Cité.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys, os, os.path, gettext, sys, locale

locale.setlocale(locale.LC_ALL, "")

APPDIR    = os.path.dirname(__file__)
DATADIR   = os.path.join(APPDIR, "data")
LOCALEDIR = os.path.join(APPDIR, "locale")
if not os.path.exists(LOCALEDIR):
  LOCALEDIR = os.path.join(APPDIR, "..", "locale")
  if not os.path.exists(LOCALEDIR):
    LOCALEDIR = os.path.join("/", "usr", "share", "locale")
    
try:            translator = gettext.translation("bibreview", LOCALEDIR)
except IOError: translator = gettext.translation("bibreview", LOCALEDIR, ("fr",))

translator.install(1)

if not os.path.exists(DATADIR): sys.stderr.write("BibReview's data directory cannot be found!\n")
  
VERSION = "0.2.2"


class Config(object):
  def __init__(self):
    try:
      import getpass
      self.user_name = getpass.getuser().title()
    except:
      self.user_name = u""
    self.lyx_pipe = "/tmp/lyxpipe.in"
    
  def __repr__(self): return _(u"BibReview preferences")
  
  def save(self):
    s = u""
    for attr in self.__dict__:
      if attr[0] == "_": continue
      s += "%s=%s\n" % (attr, repr(getattr(self, attr)))
    f = open(os.path.expanduser("~/.bibreview"), "w")
    f.write(s.encode("utf8"))
    f.close()
    
  def load(self):
    try:
      for line in open(os.path.expanduser("~/.bibreview")).read().decode("utf8").split("\n"):
        if line:
          attr, value = line.split(u"=")
          if   value.startswith(u"'")  or value.startswith(u'"') : value = value[1:-1]
          elif value.startswith(u"u'") or value.startswith(u'u"'): value = value[2:-1]
          else:
            if u"." in value: value = float(value)
            else:             value = int  (value)
          setattr(self, attr, value)
    except:
      if os.path.exists(os.path.expanduser("~/.bibreview")):
        sys.excepthook(*sys.exc_info())
        
CONFIG = Config()
CONFIG.load()
