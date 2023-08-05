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

__all__ = ["export_bibtex"]


import sys, datetime
from StringIO import StringIO
from bibreview.abbrev import *
from bibreview.model  import * 
from bibreview.model  import _author_short

PUB_TYPES = {
  u"article"    : u"Article",
  u"conference" : u"InProceedings",
  u"book"       : u"Book",
  u"in_book"    : u"InBook",
  u"phd"        : u"PhdThesis",
  u"website"    : u"Misc",
  u""           : u"Misc",
  }

def escape(s): return s.replace(u"{", u"").replace(u"}", u"").replace(u"&", u"\\&")

def format_authors(s):
  authors = s.split(",")
  if len(authors) == 1:
    return u"{%s}" % s
  authors = [_author_short(author, ", ", 1) for author in authors]
  return escape(u" and ".join(authors))

def export_bibtex(base):
  s = StringIO()
  for reference in base.references:
    type = PUB_TYPES.get(reference.get_value_for_category("pub_type")) or PUB_TYPES[u""]
    date = reference.pub_date or reference.epub_date
    if date: year = date.year
    else:    year = u""
    s.write("@%s{ %s,\n" % (type, reference.gen_key()))
    if year: s.write("Year = {{%s}},\n" % year)
    if reference.journal:
      if   type == "InProceedings":
        s.write("Title = {{%s}},\n"     % escape(reference.title))
        s.write("BookTitle = {{%s}},\n" % escape(ABBREVS.get(reference.journal.upper()) or reference.journal))
      elif type == "InBook":
        s.write("Title = {{%s}},\n"   % escape(reference.journal))
        s.write("Chapter = {{%s}},\n" % escape(reference.title))
      else:
        s.write("Title = {{%s}},\n"   % escape(reference.title))
        s.write("Journal = {{%s}},\n" % escape(ABBREVS.get(reference.journal.upper()) or reference.journal))
    else:
      s.write("Title = {{%s}},\n"   % escape(reference.title))
    volume = reference.get_volume()
    issue  = reference.get_issue ()
    pages  = reference.get_pages ()
    if volume: s.write("Volume = {{%s}},\n" % escape(volume))
    if issue : s.write("Number = {{%s}},\n" % escape(issue))
    if pages : s.write("Pages = {{%s}},\n" % escape(pages))
    if reference.abstract:  s.write("Abstract = {{%s}},\n" % escape(reference.abstract))
    if reference.editor:    s.write("Editor = {{%s}},\n" % escape(reference.editor))
    if reference.publisher: s.write("Publisher = {{%s}},\n" % escape(reference.publisher))
    if reference.address:   s.write("Address = {{%s}},\n" % escape(reference.address))
    if reference.doi:       s.write("DOI = {{%s}},\n" % escape(reference.doi))
    if reference.pmid:      s.write("PMID = {{%s}},\n" % escape(reference.pmid))
    if reference.url:       s.write("Url = {{%s}},\n" % escape(reference.url))
    if reference.keywords:  s.write("Keyword = {{%s}},\n" % escape(reference.keywords))
    #if reference.authors:   s.write("Author = {%s},\n" % escape(reference.authors.replace(u"\n", u" and ")))
    if reference.authors:   s.write("Author = {%s},\n" % format_authors(reference.authors_short))
    
    s.write("}\n")
  return s.getvalue().replace(u'\u2019', u"'").replace(u'\u2018', u"'").replace(u'\u2013', u"-")


def export_bibtex_file(base, filename):
  s = export_bibtex(base)
  open(filename, "w").write(s.encode("latin1", "replace"))

COMMAND_LINE_FUNCS["--export-bibtex"] = export_bibtex_file

