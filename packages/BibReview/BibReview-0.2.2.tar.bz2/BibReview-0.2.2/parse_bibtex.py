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

__all__ = ["parse_bibtex"]


import sys, datetime, re
from bibreview.abbrev import *
from bibreview.model  import *

MONTH_NAMES = { "spr" : 3, "sum" : 6, "aut" : 9, "win" : 12, "jan" :  1, "feb" :  2, "mar" :  3, "apr" :  4, "may" :  5, "jun" :  6, "jul" :  7, "aug" :  8, "sep" :  9, "oct" : 10, "nov" : 11, "dec" : 12 }

SPACE_REGEXP  = re.compile(u"\\s+")
SPACE2_REGEXP = re.compile(u"[ \\t]+")
SPACE3_REGEXP = re.compile(u"\n[ \\t]+")

def parse_bibtex(base, s):
  s     = s.replace(u"{", u"\n{").replace(u"}", u"\n}")
  root  = []
  stack = [root]
  for line in s.split(u"\n"):
    if   line.startswith(u"{"):
      line = line[1:]
      l = []
      stack[-1].append(l)
      stack.append(l)
    elif line.startswith(u"}"):
      line = line[1:]
      del stack[-1]
    if line: stack[-1].append(line + "\n")

  i = 0
  while i < len(root):
    if root[i].startswith(u"@"):
      add_reference(base, root[i + 1])
      i += 1
    i += 1
  
  base.sort()
  return base

def add_reference(base, l):
  reference = Reference()
  volume    = issue = pages = u""
  year      = month = day = 1
  i         = 0
  while i < len(l):
    attr = SPACE_REGEXP.sub(u"", l[i])
    if attr.endswith(u"="):
      i += 1
      if   attr == u"Title=":    reference.title    = strip_spaces(flatten_list(l[i]))
      elif attr == u"Journal=":  reference.journal  = strip_spaces(flatten_list(l[i]))
      elif attr == u"DOI=":      reference.doi      = strip_spaces(flatten_list(l[i]))
      elif attr == u"Volume=":   volume             = strip_spaces(flatten_list(l[i]))
      elif attr == u"Pages=":    pages              = strip_spaces(flatten_list(l[i]))
      elif attr == u"Number=":   issue              = strip_spaces(flatten_list(l[i]))
      elif attr == u"Abstract=": reference.abstract = strip_spaces_multiline(flatten_list(l[i]))
      elif attr == u"Year=":     year = int(flatten_list(l[i]))
      elif attr == u"Month=":
        s = flatten_list(l[i]).split()
        try: month = MONTH_NAMES.get(s[0][:3].lower()) or int(s[0])
        except: month = 1
        if len(s) > 1: day = int(s[1])
      elif attr == u"Author=":
        s = strip_spaces(flatten_list(l[i]))
        s = u"\n".join(i.strip() for i in s.split(u" and "))
        #s = s.replace(u". ", u".")
        reference.set_authors(s)
    i += 1
    
  if reference.journal: reference.journal = u"%s%s" % (reference.journal[0].upper(), reference.journal[1:].lower())
  reference.vol_n_p = vol_n_p(volume, issue, pages)
  if year != 1: reference.pub_date = datetime.date(year, month, day)
  base.add_reference(reference)
  #print
  #print reference
  #print
  #print reference.abstract
  return reference

def strip_spaces(s):
  return SPACE_REGEXP.sub(u" ", s).strip()

def strip_spaces_multiline(s):
  s = "".join(((line.endswith(u".") and "%s\n" % line) or line) for line in s.split(u"\n"))
  s = SPACE2_REGEXP.sub(u" ", s).strip()
  s = SPACE3_REGEXP.sub(u"\n", s)
  return s

def flatten_list(l):
  return u"".join(((isinstance(i, list) and flatten_list(i)) or i) for i in l)

COMMAND_LINE_FUNCS["--import-bibtex"] = lambda arg: parse_bibtex(Base(), open(arg).read().decode("utf8"))

