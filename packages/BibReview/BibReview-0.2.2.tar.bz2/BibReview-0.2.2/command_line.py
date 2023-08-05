# -*- coding: utf-8 -*-
# -*- python -*-

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


import sys, os, os.path, inspect, shlex

import bibreview, bibreview.globdef as globdef, bibreview.model as model, bibreview.parse_bibreview as parse_bibreview, bibreview.parse_pubmed, bibreview.parse_bibtex, bibreview.parse_reflib, bibreview.export_bibtex

BASES = []

def format_arg(arg):
  if arg.startswith(u"--"): return arg
  return '"%s"' % arg.replace('"', '\\"')

def run(command):
  global BASES
  
  if isinstance(command, list): argv = command
  else:                         argv = shlex.split(command)
  
  i   = 0
  gui = 1
  while i < len(argv):
    arg = argv[i]

    if   arg == "--version":
      gui = 0
      print "BibReview version %s" % globdef.VERSION
      
    elif arg == "--help":
      gui = 0
      print _("__help__")

    elif arg == "--save-as":
      gui = 0
      i += 1
      s = BASES.pop().__xml__().encode("utf8")
      open(argv[i], "w").write(s)
      
    elif arg == "--save":
      gui = 0
      s = BASES[-1].__xml__().encode("utf8")
      open(BASES.pop().filename or None, "w").write(s)

    elif arg in model.COMMAND_LINE_FUNCS:
      arg_names = inspect.getargspec(model.COMMAND_LINE_FUNCS[arg])[0]
      args      = argv[i+1 : i+len(arg_names)+1]
      for j in range(len(arg_names)):
        if arg_names[j].startswith("base"):
          if args[j] == "CURRENT": args[j] = BASES[-1]
          else:                    args[j] = parse_bibreview.parse_bibreview_file(args[j])
      r = model.COMMAND_LINE_FUNCS[arg](*args)
      if isinstance(r, model.Base):
        r.comment = _(u"Command line:\n") + argv[0] + u" " + u" ".join(map(format_arg, argv[1:]))
        BASES = [r]
      elif r is None: gui = 0
      i += len(arg_names)
      
    else:
      BASES.append(parse_bibreview.parse_bibreview_file(arg))
      
    i  += 1

  if gui:
    import gtk, bibreview.gui
    if not BASES: BASES.append(model.Base())
    for base in BASES: bibreview.gui.MainWindow(base).show_all()
    gtk.main()
    
  if BASES: return BASES[-1]
