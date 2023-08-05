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

__all__ = ["parse_reflib"]


import sys, datetime, urllib, urllib2, re, xml.sax as sax, xml.sax.handler as handler
from StringIO    import StringIO
from collections import defaultdict
from bibreview.abbrev import *
from bibreview.model  import *

MONTH_NAMES = { "jan" :  1, "feb" :  2, "mar" :  3, "apr" :  4, "may" :  5, "jun" :  6, "jul" :  7, "aug" :  8, "sep" :  9, "oct" : 10, "nov" : 11, "dec" : 12 }

class Handler(handler.ContentHandler):
  def __init__(self):
    self.tags      = [u""]
    self.attrss    = []
    self.base_tags = {}
    
  def reset(self, base): self.base = base
  
  def startElement(self, name, attrs):
    self.tags.append(u"%s %s" % (self.tags[-1], name))
    self.attrss.append(attrs)
    
    if   name == u"tag":
      self.tag_name = u""
      self.tag_uid  = 0
      
    elif name == u"doc":
      self.reference  = Reference()
      self.base.add_reference(self.reference)
      self.year       = 1
      self.month      = 1
      self.day        = 1
      self.volume     = self.issue = self.pages = u""
      self.chapter    = u""
      
    elif name == u"bib_extra": self.extra = attrs[u"key"].lower()
      
  def endElement(self, name):
    if   name == u"tag":
      if self.tag_name:
        self.base_tags[self.tag_uid] = Tag(self.base.root_tag, self.tag_name)
        
    elif name == u"doc":
      if self.year != 1: self.reference.pub_date = datetime.date(self.year, self.month, self.day)
      self.reference.vol_n_p   = vol_n_p(self.volume, self.issue, self.pages)
      if (not self.reference.url) and self.reference.pmid: self.reference.url = u"http://www.ncbi.nlm.nih.gov/pubmed/%s" % self.reference.pmid
      if self.chapter:
        if self.reference.title: self.reference.journal = self.reference.title
        self.reference.title = self.chapter
        
    del self.tags  [-1]
    del self.attrss[-1]
    
  def characters(self, content):
    if not content: return
    
    tags = self.tags[-1]
    if   tags.endswith(u"tag name"):        self.tag_name          += content.strip()
    elif tags.endswith(u"tag uid"):         self.tag_uid           = int(content)
    elif tags.endswith(u"doc key"):         self.reference.key     += content.strip()
    elif tags.endswith(u"doc bib_title"):   self.reference.title   += content.strip()
    elif tags.endswith(u"doc bib_journal"): self.reference.journal += content.strip()
    elif tags.endswith(u"doc bib_volume"):  self.volume            += content.strip()
    elif tags.endswith(u"doc bib_number"):  self.issue             += content.strip()
    elif tags.endswith(u"doc bib_pages"):   self.pages             += content.strip()
    elif tags.endswith(u"doc bib_year"):    self.year              = int(content)
    elif tags.endswith(u"doc bib_doi"):     self.reference.doi     += content.strip()
    #elif tags.endswith(u"doc bib_"):        self.reference. = content.strip()
    elif tags.endswith(u"doc notes"):       self.reference.comment += content.strip()
    elif tags.endswith(u"doc filename"):    self.reference.path    += content.strip()
    elif tags.endswith(u"doc tagged"):
      tag = self.base_tags.get(int(content))
      if tag: self.reference.add_tag(tag)
    elif tags.endswith(u"doc bib_type"):
      content = content.strip().lower()
      if   content == u"article":       self.reference.set_value_for_category(u"pub_type", u"article")
      elif content == u"inproceedings": self.reference.set_value_for_category(u"pub_type", u"conference")
      elif content == u"book":          self.reference.set_value_for_category(u"pub_type", u"book")
      elif content == u"inbook":        self.reference.set_value_for_category(u"pub_type", u"in_book")
      elif content == u"phdthesis":     self.reference.set_value_for_category(u"pub_type", u"phd")
      
    elif tags.endswith(u"doc bib_extra"):
      if   self.extra == "url":          self.reference.url       += content.strip()
      elif self.extra == "keywords":     self.reference.keywords  += u"; ".join((self.reference.keywords + u" " + content.strip()).split())
      elif self.extra == "booktitle":    self.reference.journal   += content.strip()
      elif self.extra == "address":      self.reference.address   += content.strip()
      elif self.extra == "location":     self.reference.address   += content.strip()
      elif self.extra == "abstract":     self.reference.abstract  += content.strip()
      elif self.extra == "medline-pmid": self.reference.pmid      += content.strip()
      elif self.extra == "pubmedid":     self.reference.pmid      += content.strip()
      elif self.extra == "doi":          self.reference.doi       += content.strip()
      elif self.extra == "publisher":    self.reference.publisher += content.strip()
      elif self.extra == "editor":       self.reference.editor    += content.strip()
      elif self.extra == "noteperso":    self.reference.comment   += "\n" + content.strip()
      elif self.extra == "chapter":      self.chapter             += content.strip()
      
    elif tags.endswith(u"doc bib_authors"):
      authors = content.strip()
      authors = u"\n".join(authors.split(u" and "))
      self.reference.set_authors(authors)
      
    
def text_join(text, part):
  if text: return u"%s\n%s" % (text, part)
  return part

handler = Handler()
parser  = sax.make_parser()
parser.setContentHandler(handler)

def parse_reflib(base, xml):
  handler.reset(base)
  parser.parse(StringIO(xml))
  base.sort()
  return base


COMMAND_LINE_FUNCS["--import-reflib"] = lambda arg: parse_reflib(Base(), open(arg).read())
