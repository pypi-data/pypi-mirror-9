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

__all__ = ["parse_pubmed", "parse_pubmeds", "query_pubmed"]


import sys, datetime, urllib, urllib2, re, xml.sax as sax, xml.sax.handler as handler
from StringIO    import StringIO
from collections import defaultdict
from bibreview.abbrev import *
from bibreview.model  import *

MONTH_NAMES = { "jan" :  1, "feb" :  2, "mar" :  3, "apr" :  4, "may" :  5, "jun" :  6, "jul" :  7, "aug" :  8, "sep" :  9, "oct" : 10, "nov" : 11, "dec" : 12 }

class Handler(handler.ContentHandler):
  def __init__(self):
    self.tags   = [u""]
    self.attrss = []
    self.current_content = u""
    
  def reset(self, base): self.base = base

  def get_date(self, *names):
    for name in names:
      if self.years[name] != "":
        try: return datetime.date(int(self.years[name]), MONTH_NAMES.get(self.months[name][:3].lower()) or int(self.months[name] or 1), int(self.days[name] or 1))
        except:
          try: return datetime.date(int(self.years[name]))
          except:
             pass
          
  def parse_date(self, s, name):
    s = s.split()
    self.years[name] = s[0]
    if len(s) >= 2: self.months[name] = s[1]
    if len(s) >= 3: self.days[name] = s[2]
    
  def startElement(self, name, attrs):
    self.tags.append(u"%s %s" % (self.tags[-1], name))
    self.attrss.append(attrs)
    self.current_content = u""
    
    if   name == u"Author": self.last_name = self.first_name = self.initials = u""
    
    elif name == u"AbstractText":
      self.abstract_part = attrs.get(u"Label") or u""
      if self.abstract_part: self.abstract_part = u"%s%s: " % (self.abstract_part[0], self.abstract_part[1:].lower())
      
    elif name == u"PubmedArticle":
      self.reference  = Reference()
      self.years      = defaultdict(lambda : "")
      self.months     = defaultdict(lambda : "")
      self.days       = defaultdict(lambda : "")
      self.keywords   = []
      self.issue      = self.pages = u""
      self.pub_status = u""
      self.last_name  = self.first_name = self.initials = u""
      
    elif name == u"Article": self.pub_model = attrs.get(u"PubModel")
      
    elif name == u"ArticleDate"  : self.date_type        = attrs.get(u"DateType")
    elif name == u"PubMedPubDate": self.current_pub_date = attrs.get(u"PubStatus")
    
  def endElement(self, name):
    if self.current_content: self.characters2(self.current_content)
    
    if   self.tags[-1].endswith(u"Article AuthorList Author"):
      if self.first_name: self.reference.authors = text_join(self.reference.authors, u"%s, %s" % (self.last_name, self.first_name))
      else:               self.reference.authors = text_join(self.reference.authors, u"%s %s"  % (self.last_name, self.initials.replace(u" ", u"")))
      
    elif name == u"PubmedArticle":
      if self.reference.title.endswith(u"."): self.reference.title = self.reference.title[:-1]
      self.reference.set_authors(self.reference.authors)
      if   self.pub_status == u"aheadofprint":
        self.reference.epub_date = self.get_date("pub", "epublish", "aheadofprint", "Internet", "Electronic")
      elif self.pub_status == u"epublish":
        self.reference.pub_date = self.reference.epub_date = self.get_date("pub", "Internet", "epublish", "aheadofprint")
      elif self.pub_status == u"ppublish":
        self.reference.pub_date  = self.get_date("pub", "Print")
        self.reference.epub_date = self.get_date("epublish", "aheadofprint", "Internet", "Electronic") or self.reference.pub_date
      self.reference.abstract  = self.reference.abstract.replace(u'\n"\n', u' " ').replace(u'\n<\n', u' < ').replace(u'\n>\n', u' > ')
      self.reference.keywords  = u" ; ".join(self.keywords)
      if self.reference.journal == u"Journal of the American Medical Informatics Association : JAMIA": self.reference.journal = "Journal of the american medical informatics association" # Pubmed uses a non standard name ???
      #if (ABBREVS.get(self.reference.journal.upper()) or self.reference.journal).endswith("proc"):
      #  self.reference.add_tag(self.base.root_tag._category_2_tag[u"pub_type", "conference"])
      #else:
      #  self.reference.add_tag(self.base.root_tag._category_2_tag[u"pub_type", "article"])
      if self.issue: self.reference.vol_n_p += u"(%s)" % self.issue
      if self.pages: self.reference.vol_n_p += u":%s"  % self.pages
      if (not self.reference.url) and self.reference.pmid: self.reference.url = u"http://www.ncbi.nlm.nih.gov/pubmed/%s" % self.reference.pmid
      self.base.add_reference(self.reference)
      
    del self.tags  [-1]
    del self.attrss[-1]
    
  def characters(self, content): self.current_content += content
    
  def characters2(self, content):
    tags = self.tags[-1]
    if u" Article " in tags: # Optimisation !
      if   tags.endswith(u"Article AuthorList Author LastName"):                            self.last_name          = content.strip()
      elif tags.endswith(u"Article AuthorList Author ForeName"):                            self.first_name         = content.strip()
      elif tags.endswith(u"Article AuthorList Author Initials"):                            self.initials           = content.strip()
      elif tags.endswith(u"Article Abstract AbstractText"):                                 self.reference.abstract = text_join(self.reference.abstract, (u"%s%s" % (self.abstract_part, content.strip()))); self.abstract_part = u""
      elif tags.endswith(u"Article ELocationID") and (self.attrss[-1]["EIdType"] == "doi"): self.reference.doi      = content.strip()
      elif tags.endswith(u"Article ArticleTitle"):                                          self.reference.title    = content.strip()
      elif tags.endswith(u"Article ArticleDate Year"):                                      self.years [self.date_type] = content.strip()
      elif tags.endswith(u"Article ArticleDate Month"):                                     self.months[self.date_type] = content.strip()
      elif tags.endswith(u"Article ArticleDate Day"):                                       self.days  [self.date_type] = content.strip()
      elif tags.endswith(u"Article Journal JournalIssue PubDate Year"):                     self.years ["pub"] = content.strip()
      elif tags.endswith(u"Article Journal JournalIssue PubDate Month"):                    self.months["pub"] = content.strip()
      elif tags.endswith(u"Article Journal JournalIssue PubDate Day"):                      self.days  ["pub"] = content.strip()
      elif tags.endswith(u"Article Journal JournalIssue PubDate MedlineDate"):              self.parse_date(content.strip(), "pub")
      elif tags.endswith(u"Article Journal Title"):                                         self.reference.journal = content.strip()
      elif tags.endswith(u"Article Journal JournalIssue Volume"):                           self.reference.vol_n_p = content.strip()
      elif tags.endswith(u"Article Journal JournalIssue Issue"):                            self.issue             = content.strip()
      elif tags.endswith(u"Article Pagination MedlinePgn"):                                 self.pages             = content.strip()
      elif tags.endswith(u"Article PublicationTypeList PublicationType"):
        pub_type = content.strip().lower()
        if   pub_type == u"congresses":      self.reference.add_tag(self.base.root_tag._category_2_tag[u"pub_type", "conference"])
        elif pub_type == u"journal article": self.reference.add_tag(self.base.root_tag._category_2_tag[u"pub_type", "article"])
        
    elif tags.endswith(u"PubmedData History PubMedPubDate Year"):                           self.years [self.current_pub_date] = content.strip()
    elif tags.endswith(u"PubmedData History PubMedPubDate Month"):                          self.months[self.current_pub_date] = content.strip()
    elif tags.endswith(u"PubmedData History PubMedPubDate Day"):                            self.days  [self.current_pub_date] = content.strip()
    elif tags.endswith(u"MeshHeadingList MeshHeading DescriptorName"):                      self.keywords.append(content.strip())
    elif tags.endswith(u"MeshHeadingList MeshHeading QualifierName"):                       self.keywords[-1]    = u"%s/%s" % (self.keywords[-1], content.strip())
    elif tags.endswith(u"MedlineCitation PMID"):                                            self.reference.pmid  = content.strip()
    elif tags.endswith(u"PubmedData PublicationStatus"):                                    self.pub_status      = content.strip()
    
    
def text_join(text, part):
  if text: return u"%s\n%s" % (text, part)
  return part

handler = Handler()
parser  = sax.make_parser()
parser.setContentHandler(handler)

ID_REGEXP  = re.compile(u"<Id>\\s*(.*)\\s*</Id>", re.UNICODE)
DTD_REGEXP = re.compile(u"<!DOCTYPE.*?>")

MAX_NUMBER_OF_PMIDS = 200

def parse_pubmed(base, xml):
  handler.reset(base)
  parser.parse(StringIO(DTD_REGEXP.sub("", xml)))
  base.sort()
  return base

def query_pubmed(base, query):
  handler.reset(base)
  if isinstance(query, basestring):
    #reply = urllib2.urlopen(u"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s&retmax=99999999" % urllib.quote_plus(query)).read().decode("utf8")
    data = urllib.urlencode({"db" : "pubmed", "retmax" : "99999999", "term" : query})
    reply = urllib2.urlopen(u"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", data).read().decode("utf8")
    pmids = ID_REGEXP.findall(reply)
  else:
    pmids = query
  sys.stderr.write("Pubmed query: %s references\n" % len(pmids))
  
  nb0 = len(base.references)
  for pmids_part in [pmids[i:i+MAX_NUMBER_OF_PMIDS] for i in range(0, len(pmids), MAX_NUMBER_OF_PMIDS)]:
    xml   = urllib2.urlopen(u"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=%s&retmode=xml" % u",".join(pmids_part)).read()
    xml   = DTD_REGEXP.sub("", xml)
    parser.parse(StringIO(xml))
    sys.stderr.write("%s / %s references retrieved...\n" % (len(base.references) - nb0, len(pmids)))
  base.sort()
  return base


COMMAND_LINE_FUNCS["--import-pubmed"] = lambda arg: parse_pubmed(Base(), open(arg).read())
COMMAND_LINE_FUNCS["--query-pubmed" ] = lambda arg: query_pubmed(Base(), arg)
