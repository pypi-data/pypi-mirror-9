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

__all__ = ["parse_bibreview", "parse_bibreview_file"]


import sys, datetime, re
import xml.sax as sax, xml.sax.handler as handler

if sys.version[0] == "2":
  from StringIO import StringIO
else:
  from io import StringIO

from bibreview.model  import *

_SPLIT_REGEXP = re.compile(" |:|\\.|-", re.UNICODE)

class Handler(handler.ContentHandler):
  def __init__(self):
    self.tags   = [u""]
    self.current_content = u""
    
  def reset(self, base):
    self.base  = base
    self.btags = [self.base]
  
  def startElement(self, name, attrs):
    self.tags.append(u"%s %s" % (self.tags[-1], name))
    self.current_content = u""
    
    if   name == u"reference":
      self.reference = Reference()
      for attr, value in dict(attrs).items():
        if   attr == u"tags":
          if value:
            for tag_name in value.split(u","):
              self.reference.add_tag(self.base.root_tag._name_2_tag[tag_name], 0)
        elif attr == u"pub_date"   : self.reference.pub_date    = datetime.date(*(int(i) for i in value.split("-")))
        elif attr == u"epub_date"  : self.reference.epub_date   = datetime.date(*(int(i) for i in value.split("-")))
        elif attr == u"insert_date": self.reference.insert_date = datetime.date(*(int(i) for i in value.split("-")))
        else: setattr(self.reference, attr, value)
        
    elif name == u"tag":
      if u"category_value" in attrs:
        value = attrs.get(u"category_value")
        try:    value = int(value)
        except: pass
      else: value = None
      tag = Tag(self.btags[-1], attrs[u"name"], attrs.get(u"category") or u"", value, int(attrs.get(u"exclusive", 0)))
      self.btags.append(tag)
      
    elif name == u"base":
      self.base.name               = attrs.get(u"name")
      self.base.review_mode        = int(attrs.get(u"review_mode") or 0)
      self.base.auto_export_bibtex = int(attrs.get(u"auto_export_bibtex") or 0)
      self.base.sort_criteria      = attrs.get(u"sort_criteria")
      
    elif name == u"review_status":
      status = attrs.get(u"status")
      if   status == u"None": status = None
      elif status == u"c":    pass
      else:                   status = int(status)
      self.reference.review_history.append((datetime.datetime(*map(int, _SPLIT_REGEXP.split(attrs.get(u"date")))), attrs.get(u"user"), status))
      
  def endElement(self, name):
    if self.current_content: self.characters2(self.current_content)
    
    if   name == u"reference":
      self.reference.set_authors(self.reference.authors.strip())
      self.base.add_reference(self.reference)
      
    elif name == u"tag": del self.btags[-1]
    
    del self.tags[-1]
    
  def characters(self, content): self.current_content += content
  
  def characters2(self, content):
    tags = self.tags[-1]
    if   tags.endswith(u"authors"):                       self.reference.authors  += content
    elif tags.endswith(u"abstract"):                      self.reference.abstract += content
    elif tags.endswith(u"reference comment"):             self.reference.comment  += content
    elif tags.endswith(u"base comment"):                  self.base.comment       += content
    
    

handler = Handler()
parser  = sax.make_parser()
parser.setContentHandler(handler)

def parse_bibreview_file(filename):
  handler.reset(Base(create_tags = 0))
  parser.parse(open(filename))
  handler.base.filename = filename
  handler.base.sort()
  return handler.base

def parse_bibreview(xml):
  handler.reset(Base(create_tags = 0))
  if sys.version[0] == "2":
    xml = StringIO(xml.encode("utf8"))
  else:
    xml = StringIO(xml)
  parser.parse(xml)
  handler.base.sort()
  return handler.base
