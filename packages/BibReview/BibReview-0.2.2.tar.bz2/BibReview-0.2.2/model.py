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


__all__ = ["Base", "Tag", "Groups", "Group", "Reference", "COMMAND_LINE_FUNCS", "vol_n_p"]


import datetime, unicodedata
import bibreview.globdef as globdef
from bibreview.abbrev import *
from xml.sax.saxutils import escape as xml_escape, unescape as xml_unescape, quoteattr as xml_escape_attr

class Base(object):
  def __init__(self, create_tags = 1):
    self.name          = u""
    self.filename      = u""
    self.comment       = u""
    self.root_tag      = None
    if create_tags: RootTag(self)
    self.references    = []
    self.selections    = []
    self.review_mode   = 0
    self.sort_criteria = u"authors"
    self._search       = u""
    self._search_tags  = frozenset()
    self.auto_export_bibtex = 0
    
  def __repr__   (self): return unicode(self).encode("utf8")
  def __unicode__(self): return u"%s %s (%s / %s)" % (_(u"Base"), self.name, len(self.selections), len(self.references))
  
  def __xml__(self, references = None):
    s = u"""<?xml version="1.0" encoding="utf-8"?>
<base name=%s sort_criteria=%s review_mode="%s" auto_export_bibtex="%s">""" % (xml_escape_attr(self.name), xml_escape_attr(self.sort_criteria), int(self.review_mode), int(self.auto_export_bibtex))
    if self.comment: s += u"\n<comment>%s</comment>" % xml_escape(self.comment)
    s += u"\n%s" % self.root_tag.__xml__()
    s += u"\n%s\n</base>" % u"\n".join(reference.__xml__() for reference in (references or self.references))
    return s
  
  def add_reference(self, reference):
    reference._base = self
    self.references.append(reference)
    self.selections.append(reference)
    
  def remove_reference(self, reference):
    reference._base = None
    self.references.remove(reference)
    self.selections.remove(reference)
    for tag in set(reference.tags): tag.references.discard(reference)
    
  def set_sort_criteria(self, sort_criteria):
    self.sort_criteria = sort_criteria
    self.sort()
    
  def sort(self):
    if   self.sort_criteria == u"authors":
      self.selections.sort(key = lambda reference: ((reference.authors.lower() or u"").split(u"\n")[0], reference.get_pub_or_epub_date()))
    elif self.sort_criteria == u"pub_date":
      self.selections.sort(key = lambda reference: (reference.get_pub_or_epub_date(), reference.authors))
    elif self.sort_criteria == u"epub_date":
      self.selections.sort(key = lambda reference: (reference.get_epub_or_pub_date(), reference.authors))
    elif self.sort_criteria == u"insert_date":
      self.selections.sort(key = lambda reference: (reference.insert_date, reference.authors))
    elif self.sort_criteria == u"review_date":
      self.selections.sort(key = lambda reference: ((reference.review_history and reference.review_history[-1][0]) or datetime.datetime.now()))
    elif self.sort_criteria == u"title":
      self.selections.sort(key = lambda reference: reference.title.lower())
    elif self.sort_criteria == u"journal":
      self.selections.sort(key = lambda reference: (reference.journal.lower(), reference.get_pub_or_epub_date()))
    elif self.sort_criteria == u"review":
      self.selections.sort(key = lambda reference: reference.get_value_for_category(u"review"))
      def key(reference):
        status = reference.get_value_for_category(u"review")
        if status == u"c":
          return u"c%s" % getattr(reference, "conflict_type", "")
        return status
      self.selections.sort(key = key)
    elif self.sort_criteria == u"lexical":
      import bibreview.princomp as princomp
      princomp.assign_lexical_proximity(self.selections)
      self.selections.sort(key = lambda reference: reference.lexical_coord)
    elif self.sort_criteria == u"neural":
      import bibreview.neural_network as neural_network
      neural_network.classify_with_neural_network(self.selections)
      self.selections.sort(key = lambda reference: reference.neural_score)
    elif self.sort_criteria == u"bayes":
      import bibreview.bayesian_classifier as bayesian_classifier
      bayesian_classifier.classify_with_bayesian_classifer(self.selections)
      self.selections.sort(key = lambda reference: reference.bayesian_score)
      
  def search(self, search):
    if not isinstance(search, unicode): search = search.decode("utf8")
    self._search = search
    if self._search_tags:
      self.selections = [reference for reference in self.references if reference.has_tags(self._search_tags)]
    else: self.selections = list(self.references)
    
    if search:
      search = search.lower()
      if u'"' in search:
        splitted = search.split(u'"')
        searches = splitted[1::2]
        for i in splitted[0::2]:
          for j in i.split(): searches.append(j)
      else: searches = search.split()
      for word in searches:
        self.selections = [reference for reference in self.selections if reference.match(word)]
    self.sort()
    
  def analyze_authors(base, first = 0, last = 0, counter = None, multiply = 1):
    from collections import Counter
    if counter is None: counter = Counter()
    for reference in base.selections:
      authors = remove_accents(reference.authors_short).split(", ")
      if   first: counter.update({ authors[ 0] : multiply })
      elif last:  counter.update({ authors[-1] : multiply })
      else:
        for author in authors: counter.update({ author : multiply })
    return counter

  def group_references_by_author(self):
    def get_authors(reference):
      return remove_accents(reference.authors_short).split(", ")
    return self.group_references_by(_(u"author"), get_authors)
  
  def group_references_by_first_author(self):
    def get_first_author(reference):
      return remove_accents(reference.authors_short).split(", ")[:1]
    return self.group_references_by(_(u"first author"), get_first_author)
  
  def group_references_by_last_author(self):
    def get_last_author(reference):
      return remove_accents(reference.authors_short).split(", ")[-1:]
    return self.group_references_by(_(u"last author"), get_last_author)
  
#  def group_references_by_journal(self): return self.group_references_by(_(u"Journal"), lambda reference: reference.journal)
#  def group_references_by_journal(self): return self.group_references_by(_(u"Journal"), lambda reference: reference.journal)
  
  def group_references_by_journal(self):
    def get_journal(reference):
      return [ABBREVS.get(reference.journal.upper()) or reference.journal.title() or u"None"]
    return self.group_references_by(_(u"Journal"), get_journal)
  
  def group_references_by(self, criteria, attr_func):
    from collections import defaultdict
    counter = defaultdict(list)
    groups  = Groups(self, criteria)
    
    for reference in self.selections:
      for i in attr_func(reference):
        counter[i].append(reference)
        
    total = 0
    for (value, references) in sorted(counter.items(), reverse = 1, key = lambda item: len(item[1])):
      total += len(references)
      Group(groups, value, references, total)
    return groups

  def get_text_export(self):
    return TextExport(u"\n".join(ref.export_as_text() for ref in self.selections))

class TextExport(object):
  def __init__(self, text): self.text = text

class Groups(object):
  def __init__(self, base, criteria):
    self.base     = base
    self.criteria = criteria
    self.children = []
    
  def __repr__   (self): return unicode(self).encode("utf8")
  def __unicode__(self):
    return xml_escape(u"%s %s %s" % (self.base, _(u"grouped by"), self.criteria))
  
  def get_text_export(self):
    return TextExport(u"\n".join(group.export_as_text() for group in self.children))
    
    
class Group(object):
  def __init__(self, groups, criteria, children, cumulated_length):
    self._groups          = groups
    self.criteria         = criteria
    self.children         = children
    self.cumulated_length = cumulated_length
    groups.children.append(self)
    
  def __repr__   (self): return unicode(self).encode("utf8")
  def __unicode__(self):
    return xml_escape(u"%s (%s, %s cum)" % (self.criteria, len(self.children), self.cumulated_length))
    
  def export_as_text(self): return unicode(self)
  

class Tag(object):
  def __init__(self, parent, name = u"", category = u"", category_value = None, exclusive = 0):
    if isinstance(parent, Base):
      self._name_2_tag     = {}
      self._category_2_tag = {}
      self._parent         = None
      self._base           = parent
      parent.root_tag      = self
    else:
      parent.children.append(self)
      self._parent         = parent
      self._base           = parent._base
      
    self.name            = name
    self.children        = []
    self.references      = set()
    self._exclusive      = exclusive
    self._category       = category
    self._category_value = category_value
    
    root = self.get_root()
    root._name_2_tag[name] = self
    if category:                   root._category_2_tag[category] = self
    if not category_value is None: root._category_2_tag[self.get_category()._category, category_value] = self
    
  def __repr__   (self): return unicode(self).encode("utf8")
  def __unicode__(self):
    if self._category or not self._parent: return self.name
    n = 0
    for tag in self.self_and_descendants(): n += len(tag.references)
    return u"%s (%s)"% (self.name, n)

  def __xml__(self):
    s = u"<tag name=%s" % xml_escape_attr(self.name)
    if self._category:                   s += u' category="%s"'       % self._category
    if not self._category_value is None: s += u' category_value="%s"' % self._category_value
    if self._exclusive:                  s += u' exclusive="%s"' % int(self._exclusive)
    if self.children:                    s += u">\n%s\n</tag>" % "\n".join(tag.__xml__() for tag in self.children)
    else: s += u"/>"
    return s

  def set_name(self, name):
    root = self.get_root()
    del root._name_2_tag[self.name]
    self.name = name
    root._name_2_tag[name] = self
    
  def add_child(self, tag):
    self.children.append(tag)
    
  def remove_child(self, tag):
    if tag._category or tag._category_value: return
    for tag_descendant in tag.self_and_descendants():
      for reference in set(tag_descendant.references):
        reference.remove_tag(tag_descendant)
        
    self.children.remove(tag)
    
  def get_root(self):
    if not self._parent: return self
    return self._parent.get_root()
  
  def descendants(self):
    for child in self.children:
      yield child
      for tag in child.descendants():
        yield tag
        
  def self_and_descendants(self):
    yield self
    for term in self.descendants(): yield term
    
  def get_category(self):
    if self._category: return self
    if not self._parent: return None
    return self._parent.get_category()
    
  def get_category_name(self):
    if self._category: return self._category
    if not self._parent: return u""
    return self._parent.get_category_name()
  
  def get_category_value(self):
    if not self._category_value is None: return self
    if not self._parent: return None
    return self._parent.get_category_value()
    
  def get_all_references(self):
    if not self.children: return self.references
    references = set(self.references)
    for descendant in self.descendants(): references.update(descendant.references)
    return references
  
  def copy(self):
    copy = Tag(None, self.name)
    copy.children = [tag.copy for tag in self.children]
    return copy
  
  def match(self, search):
    if search in self.name.lower(): return True
    if self._parent: return self._parent.match(search)
    return False
  
  def get_search_tag(self): return self in self._base._search_tags
  def set_search_tag(self, b):
    if b: self._base._search_tags = self._base._search_tags | frozenset([self])
    else: self._base._search_tags = self._base._search_tags - frozenset([self])
    self._base.search(self._base._search)
    
def RootTag(base):
  root = Tag(base, _(u"Tags"))
  
  review = Tag(root, _(u"Review status"), u"review", exclusive = 1)
  Tag(review, _(u"Accepted"), category_value = 1)
  Tag(review, _(u"Pending" ), category_value = 0)
  Tag(review, _(u"Conflict"), category_value = u"c")
  rejected = Tag(review, _(u"Rejected"), category_value = -1)
  Tag(rejected, _(u"Rejected by text"), category_value = -2)
  Tag(rejected, _(u"Rejected by abstract"), category_value = -3)
  Tag(rejected, _(u"Rejected by title"), category_value = -4)
  
  pub_type = Tag(root, _(u"Publication type"), u"pub_type", exclusive = 1)
  Tag(pub_type, _(u"Article")     , category_value = u"article")
  Tag(pub_type, _(u"Conference")  , category_value = u"conference")
  Tag(pub_type, _(u"Book")        , category_value = u"book")
  Tag(pub_type, _(u"Book chapter"), category_value = u"in_book")
  Tag(pub_type, _(u"PhD thesis")  , category_value = u"phd")
  Tag(pub_type, _(u"Website")     , category_value = u"website")
  
  return root


def vol_n_p(volume, issue, pages):
  if issue: volume = u"%s(%s)" % (volume, issue)
  if pages:
    if volume: volume = u"%s:%s"  % (volume, pages)
    else:      volume = pages
  return volume

REFERENCE_LONG_ATTRS    = set(["abstract", "comment", "authors"])
REFERENCE_SPECIAL_ATTRS = set(["_base", "tags", "authors_short", "review_history"]) | REFERENCE_LONG_ATTRS

class Reference(object):
  def __init__(self, tags = None):
    self.key            = u""
    self.pmid           = u""
    self.doi            = u""
    self.url            = u""
    self.title          = u""
    self.authors        = self.authors_short = u""
    self.pub_date       = None
    self.epub_date      = None
    self.insert_date    = datetime.date.today()
    self.journal        = u""
    self.editor         = u""
    self.publisher      = u""
    self.address        = u""
    self.vol_n_p        = u""
    self.abstract       = u""
    self.comment        = u""
    self.path           = u""
    self.keywords       = u""
    self.tags           = tags or set()
    self.review_history = []
    self._base          = None
    
    self.authors  = self.authors_short = u""
    self.abstract = u""
    self.comment  = u""
  def __repr__   (self): return unicode(self).encode("utf8")
  def __unicode__(self):
    return u"%s\n<b>%s</b>\n%s" % (xml_escape(self.journal_ref()), xml_escape(self.title), xml_escape(self.authors_short))
    
  def export_as_text(self): return u"%s. %s. %s." % (self.authors_short, self.title, self.journal_ref())
  
  def __xml__(self):
    return u'<reference tags=%s %s>\n%s\n<review_history>%s</review_history></reference>' % (
      xml_escape_attr(u",".join(tag.name for tag in self.tags)),
      u" ".join(u"%s=%s" % (attr, xml_escape_attr(unicode(value))) for (attr, value) in self.__dict__.iteritems() if value and (not attr in REFERENCE_SPECIAL_ATTRS)),
      u"" .join(u"<%s>%s</%s>\n" % (attr, xml_escape(getattr(self, attr)), attr) for attr in REFERENCE_LONG_ATTRS if getattr(self, attr)),
      u"\n".join(u"""<review_status date="%s" user="%s" status="%s"/>""" % (date, user, status) for (date, user, status) in self.review_history))

  def gen_key(self):
    if not self.key:
      keys = set(r.key for r in self._base.references)
      self.key = self.authors.split(u"\n", 1)[0]
      if u"," in self.key: self.key = self.key.split(u",", 1)[0]
      else:                self.key = self.key.split(None, 1)[0]
      date = self.pub_date or self.epub_date
      if date: self.key = u"%s%s" % (self.key, date.year)
    return self.key
  def journal_ref(self):
    if   self.pub_date : year = str(self.pub_date.year)
    elif self.epub_date: year = u"%s (epub)" % self.epub_date.year
    else:                year = u"-"
    if self.vol_n_p: vol_n_p = u";%s" % self.vol_n_p
    else:            vol_n_p = u""
    return (u"%s %s%s" % (ABBREVS.get(self.journal.upper()) or self.journal, year, vol_n_p)).lstrip()

  def get_volume(self): return self.vol_n_p.split(u"(")[0].split(u";")[0].split(u":")[0]
  def get_issue (self):
    if not "(" in self.vol_n_p: return u""
    return self.vol_n_p.split(u"(")[-1].split(u")")[0]
  def get_pages (self):
    if not ":" in self.vol_n_p: return u""
    return self.vol_n_p.split(u":")[-1]
  
  def get_pub_or_epub_date(self): return self.pub_date or self.epub_date or datetime.date.today()
  def get_epub_or_pub_date(self): return self.epub_date or self.pub_date or datetime.date.today()
  
  def set_authors(self, authors):
    self.authors = authors
    self.authors_short = u", ".join([_author_short(author) for author in self.authors.split(u"\n")])
    
  def add_tag(self, tag, track = 1):
    category = tag.get_category()
    
    if category and category._exclusive:
      for other in list(self.tags):
        if other.get_category_name() == category._category:
          self.remove_tag(other)
          
    self.tags.add(tag)
    tag.references.add(self)
    
    if track and (tag.get_category_name() == "review"):
      if track == 1: track = globdef.CONFIG.user_name
      self.review_history = self.review_history + [(datetime.datetime.now(), track, self.get_value_for_category(u"review"))]
      
  def remove_tag(self, tag):
    self.tags.discard(tag)
    tag.references.discard(self)
    
  def has_tag(self, tag):
    for tag_descendant in tag.self_and_descendants():
      if tag_descendant in self.tags: return True
      
  def has_tags(self, tags):
    for tag in tags:
      for tag_descendant in tag.self_and_descendants():
        if tag_descendant in self.tags: break
      else: return False
    return True
  
  def get_tag_for_category(self, category):
    for tag in self.tags:
      if tag.get_category()._category == category: return tag
      
  def get_tag_value_for_category(self, category):
    for tag in self.tags:
      cat = tag.get_category()
      if cat and (cat._category == category):
        return tag.get_category_value()
      
  def get_value_for_category(self, category):
    tag = self.get_tag_value_for_category(category)
    if not tag is None: return tag._category_value
    
  def set_value_for_category(self, category, value, track = 1):
    self.add_tag(self._base.root_tag._category_2_tag[category, value], track)
    
  def __eq__(self, other):
    if  self.doi  and (self.doi  == other.doi ): return True
    if  self.pmid and (self.pmid == other.pmid): return True
    if (self.title.upper() == other.title.upper()) and (self.journal.upper() == other.journal.upper()):
      if (not self.pub_date) and (not other.pub_date): return True
      if (self.pub_date) and (other.pub_date) and (self.pub_date.year == other.pub_date.year): return True
    return False

  def __hash__(self): return id(self)
  
  def match(self, search):
    if (search in self.title.lower()) or (remove_accents(search) in remove_accents(self.authors.lower())) or (search in self.journal.lower()) or (search in self.doi.lower()) or (search in self.pmid.lower()) or (search in self.url.lower()) or (search in self.path.lower()) or (search in self.abstract.lower()) or (search in self.comment.lower()) or (search in self.keywords.lower()): return True
    for tag in self.tags:
      if tag.match(search): return True
      
def remove_accents(s): return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")

def _author_short(author, sep = " "):
  if u"," in author:
    last_name, first_names = author.split(",", 1)
    initials               = [first_name[0].upper() for first_name in first_names.replace(u"-", u"").split()]
    
    return u"%s%s%s" % (last_name, sep, "".join(initials))
  splitted = author.rsplit(None, 1)
  #if (not splitted) or (splitted[-1] == splitted[-1].upper()):
  if (len(splitted) == 2) and (splitted[-1] == splitted[-1].upper()):
    splitted[-1] = splitted[-1].replace(u"-", u"")
    return sep.join(splitted)
  return author


def _split_author(author):
  if u"," in author:
    last_name, first_names = author.split(u",", 1)
    return last_name, first_names.strip()
  splitted = author.rsplit(None, 1)
  if (len(splitted) == 2) and (splitted[-1] == splitted[-1].upper()): return splitted
  return [author, u""]
  
def _author_short(author, sep = " ", separate_initials = 0):
  last_name, first_names = _split_author(author)
  if first_names != first_names.upper():
    first_names = u"".join([first_name[0].upper() for first_name in first_names.replace(u"-", u" ").split()])
  else:  
    first_names = first_names.replace(u"-", u"").replace(u".", u"")
  if separate_initials: first_names = " ".join(first_names)
  if first_names: return u"%s%s%s" % (last_name, sep, first_names)
  return last_name


class _ReferencesHash(dict):
  def __init__(self, references):
    dict.__init__(self)
    for reference in references:
      if reference.doi : self[reference.doi ] = reference
      if reference.pmid: self[reference.pmid] = reference
      self[self._hash_for(reference)] = reference
      
  def _hash_for(self, reference):
    if   reference.pub_date : year = reference.pub_date .year
    elif reference.epub_date: year = reference.epub_date.year
    else:                     year = 0
    author = unicodedata.normalize('NFKD', reference.authors_short.split(u",")[0]).encode("ascii", "ignore")
    return (u"%s  %s  %s" % (reference.title.replace(u'`', u"").replace(u'"', u"").replace(u"'", u"").replace(u":", u"").replace(u"-", u"").replace(u"  ", u" "), author, year)).lower()
  
  def get_same(self, reference):
    if reference.doi  and (reference.doi  in self): return self[reference.doi ]
    if reference.pmid and (reference.pmid in self): return self[reference.pmid]
    return self.get(self._hash_for(reference))
    
    
def set_base_review_status(base1, status):
  status = int(status)
  for ref in list(base1.references): ref.set_value_for_category(u"review", status)
  return base1

def copy_reference_review_status(ref1, ref2):
  ref1.review_history = ref1.review_history + ref2.review_history
  ref1.review_history.sort(key = lambda x: x[0])
  value = ref2.get_value_for_category(u"review")
  if (not value is None) and (value != ref1.get_value_for_category(u"review")): ref1.set_value_for_category(u"review", value, track = "Copy")
  
def copy_base_review_status(base1, base2):
  h2 = _ReferencesHash(base2.references)
  
  for ref1 in list(base1.references):
    ref2 = h2.get_same(ref1)
    if ref2: copy_reference_review_status(ref1, ref2)
    
  return base1

def union_reference_review_status(ref1, ref2):
  if ref2:
    ref1.review_history = ref1.review_history + ref2.review_history
    ref1.review_history.sort(key = lambda x: x[0])
    if ref1.review_history: ref1.set_value_for_category(u"review", ref1.review_history[-1][2], track = 0)
    

def _build_review_matrix():
  m = {}
  for x in [-4, -3, -2, -1]:
    for y in [-4, -3, -2, -1]:
      m[x, y] = max(x, y)
  for x in [-4, -3, -2, -1]:
    for y in [None, 0, 1]:
      m[x, y] = "c"
      m[y, x] = "c"
  m[1, 0] = "c"
  m[0, 1] = "c"
  m[None, 0] = "c"
  m[0, None] = "c"
  m[1, None] = "c"
  m[None, 1] = "c"
  for x in [-4, -3, -2, -1, 0, None, "c", 1]:
    m[x, "c"] = "c"
    m["c", x] = "c"
  for x in [-4, -3, -2, -1, 0, None, "c", 1]:
    m[x, x] = x
  assert len(m) == 64
  return m
_MERGE_REVIEW_STATUS_MATRIX = _build_review_matrix()

def _build_review_matrix_worse():
  m = {}
  for x in [-4, -3, -2, -1]:
    for y in [-4, -3, -2, -1]:
      m[x, y] = min(x, y)
  for x in [-4, -3, -2, -1]:
    for y in [None, 0, 1]:
      m[x, y] = "c"
      m[y, x] = "c"
  m[1, 0] = "c"
  m[0, 1] = "c"
  m[None, 0] = "c"
  m[0, None] = "c"
  m[1, None] = "c"
  m[None, 1] = "c"
  for x in [-4, -3, -2, -1, 0, None, "c", 1]:
    m[x, "c"] = "c"
    m["c", x] = "c"
  for x in [-4, -3, -2, -1, 0, None, "c", 1]:
    m[x, x] = x
  assert len(m) == 64
  return m
_MERGE_REVIEW_STATUS_MATRIX_WORSE = _build_review_matrix_worse()

def compute_cohen_kappa(base1, base2):
  h2 = _ReferencesHash(base2.references)
  d  = { (i, j) : 0 for i in ["a", "p", "r"] for j in ["a", "p", "r"] }
      
  def get_status(ref):
    status = ref.get_value_for_category(u"review")
    if status <  0: return "r"
    if status == 0: return "p"
    if status >  0: return "a"
    return "p"

  nb = 0
  d1 = { "a" : 0, "p" : 0, "r" : 0 }
  d2 = { "a" : 0, "p" : 0, "r" : 0 }
  for ref1 in list(base1.references):
    ref2 = h2.get_same(ref1)
    if ref2:
      nb += 1
      d1[get_status(ref1)] += 1
      d2[get_status(ref2)] += 1
      d [get_status(ref1), get_status(ref2)] += 1
      
  pr_a = (d["a", "a"] + d["p", "p"] + d["r", "r"]) / float(nb)
  pr_e = ((d1["a"] / float(nb)) * (d2["a"] / float(nb))) + ((d1["p"] / float(nb)) * (d2["p"] / float(nb))) + ((d1["r"] / float(nb)) * (d2["r"] / float(nb)))
  kappa= (pr_a - pr_e) / (1 - pr_e)
  print(d)
  print(pr_a)
  print(pr_e)
  print(kappa)
  return kappa
  
  

def compute_cohen_kappa(base1, base2):
  h2 = _ReferencesHash(base2.references)
  d  = { (i, j) : 0 for i in ["a", "r"] for j in ["a", "r"] }
      
  def get_status(ref):
    status = ref.get_value_for_category(u"review")
    if status <  0: return "r"
    if status == 0: return "a"
    if status >  0: return "a"
    return "a"

  nb = 0
  d1 = { "a" : 0, "r" : 0 }
  d2 = { "a" : 0, "r" : 0 }
  for ref1 in list(base1.references):
    ref2 = h2.get_same(ref1)
    if ref2:
      nb += 1
      d1[get_status(ref1)] += 1
      d2[get_status(ref2)] += 1
      d [get_status(ref1), get_status(ref2)] += 1
      
  pr_a = (d["a", "a"] + d["r", "r"]) / float(nb)
  pr_e = ((d1["a"] / float(nb)) * (d2["a"] / float(nb))) + ((d1["r"] / float(nb)) * (d2["r"] / float(nb)))
  kappa= (pr_a - pr_e) / (1 - pr_e)
  print(d)
  print(pr_a)
  print(pr_e)
  print(kappa)
  return kappa


def compute_cohen_kappa(base1, base2):
  h2 = _ReferencesHash(base2.references)
  d  = { (i, j) : 0 for i in ["a", "p", "r"] for j in ["a", "p", "r"] }
      
  def get_status(ref):
    status = ref.get_value_for_category(u"review")
    if status <  0: return "r"
    if status == 0: return "p"
    if status >  0: return "a"
    return "p"

  nb = 0
  d1 = { "a" : 0, "p" : 0, "r" : 0 }
  d2 = { "a" : 0, "p" : 0, "r" : 0 }
  for ref1 in list(base1.references):
    ref2 = h2.get_same(ref1)
    if ref2:
      nb += 1
      d1[get_status(ref1)] += 1
      d2[get_status(ref2)] += 1
      d [get_status(ref1), get_status(ref2)] += 1
      
  pr_a = (d["a", "a"] + d["p", "p"] + d["r", "r"]) / float(nb)
  pr_e = ((d1["a"] / float(nb)) * (d2["a"] / float(nb))) + ((d1["p"] / float(nb)) * (d2["p"] / float(nb))) + ((d1["r"] / float(nb)) * (d2["r"] / float(nb)))
  kappa= (pr_a - pr_e) / (1 - pr_e)
  print(d)
  print(pr_a)
  print(pr_e)
  print(kappa)
  return kappa
  
        
def compute_cohen_kappa(base1, base2):
  h2 = _ReferencesHash(base2.references)
  d  = { (i, j) : 0 for i in ["a", "r"] for j in ["a", "r"] }
      
  def get_status(ref):
    status = ref.get_value_for_category(u"review")
    if status == -4: return "r"
    return "a"

  nb = 0
  d1 = { "a" : 0, "r" : 0 }
  d2 = { "a" : 0, "r" : 0 }
  for ref1 in list(base1.references):
    ref2 = h2.get_same(ref1)
    if ref2:
      nb += 1
      d1[get_status(ref1)] += 1
      d2[get_status(ref2)] += 1
      d [get_status(ref1), get_status(ref2)] += 1
      
  pr_a = (d["a", "a"] + d["r", "r"]) / float(nb)
  pr_e = ((d1["a"] / float(nb)) * (d2["a"] / float(nb))) + ((d1["r"] / float(nb)) * (d2["r"] / float(nb)))
  kappa= (pr_a - pr_e) / (1 - pr_e)
  
  print(d)
  print(pr_a)
  print(pr_e)
  print(kappa)
  return kappa
  
        
def merge_reference_review_status(ref1, ref2):
  if ref2 is None:
    ref1.set_value_for_category(u"review", "c", track = _("Merge"))
  else:
    status = _MERGE_REVIEW_STATUS_MATRIX[ref1.get_value_for_category(u"review"), ref2.get_value_for_category(u"review")]
    ref1.review_history = ref1.review_history + ref2.review_history
    ref1.review_history.sort(key = lambda x: x[0])
    if ref1.get_value_for_category(u"review") != status:
      ref1.set_value_for_category(u"review", status, track = _("Merge"))
      
      if status == u"c":
        user_status = {}
        for (date, user, status) in ref1.review_history:
          if status in [-4, -3, -2]: status = -1
          user_status[user] = status
        statuses = set(user_status.values())
        statuses.discard(u"c")
        ref1.conflict_type = "".join("%s" % i for i in sorted(statuses))
        
def merge_reference_review_status_worse(ref1, ref2):
  if ref2 is None:
    ref1.set_value_for_category(u"review", "c", track = _("Merge"))
  else:
    status = _MERGE_REVIEW_STATUS_MATRIX_WORSE[ref1.get_value_for_category(u"review"), ref2.get_value_for_category(u"review")]
    ref1.review_history = ref1.review_history + ref2.review_history
    ref1.review_history.sort(key = lambda x: x[0])
    if ref1.get_value_for_category(u"review") != status:
      ref1.set_value_for_category(u"review", status, track = _("Merge"))
      
      if status == u"c":
        user_status = {}
        for (date, user, status) in ref1.review_history:
          if status in [-4, -3, -2]: status = -1
          user_status[user] = status
        statuses = set(user_status.values())
        statuses.discard(u"c")
        ref1.conflict_type = "".join("%s" % i for i in sorted(statuses))
        
def merge_base_review_status(base1, base2):
  h2 = _ReferencesHash(base2.references)
  
  for ref1 in list(base1.references):
    ref2 = h2.get_same(ref1)
    if ref2: merge_reference_review_status(ref1, ref2)
    else:    ref1.set_value_for_category(u"review", "c", track = _("Merge"))
  return base1
  
def merge_reference(ref1, ref2, tag_maps, combine_reference_review_status):
  for attr, value2 in ref2.__dict__.iteritems():
    if   attr == "comment":
      if not value2 in ref1.comment: ref1.comment = u"\n".join(filter(None, [ref1.comment, value2]))
      
    elif attr == "tags":
      for tag2 in ref2.tags:
        if tag2.get_category() and (tag2.get_category()._category == u"review"): continue
        if not tag2 in ref1.tags: ref1.add_tag(tag_maps[tag2])
        
    elif attr == "keywords":
      if ref1.keywords != ref2.keywords:
        keywords1 = [keyword.strip() for keyword in ref1.keywords.split(u";")]
        keywords2 = [keyword.strip() for keyword in ref2.keywords.split(u";")]
        for dup in set(keywords2) & set(keywords1): keywords2.remove(dup)
        ref1.keywords = u" ; ".join(keywords1 + keywords2)
        
    elif attr == "review_history": pass # Done when combining review status
    
    else:
      if not(getattr(ref1, attr, None)): setattr(ref1, attr, value2)
      
  combine_reference_review_status(ref1, ref2)
    
def union_base(base1, base2, combine_reference_review_status):
  h1 = _ReferencesHash(base1.references)
  h2 = _ReferencesHash(base2.references)
  
  if not base2.comment in base1.comment: base1.comment = u"\n".join(filter(None, [base1.comment, base2.comment]))
  
  tag_maps = {}
  for tag2 in base2.root_tag.descendants():
    if tag2._parent is None:
      tag1    = base1.root_tag
    else:
      if   tag2._category:
        tag1 = base1.root_tag._category_2_tag[tag2._category]
      elif tag2._category_value is not None:
        tag1 = base1.root_tag._category_2_tag[tag2.get_category()._category, tag2._category_value]
      else:
        tag1 = base1.root_tag._name_2_tag.get(tag2.name)
      if not tag1:
        parent1 = tag_maps.get(tag2._parent) or base1.root_tag
        tag1    = Tag(parent1, tag2.name, tag2._category, tag2._category_value, tag2._exclusive)
    tag_maps[tag2] = tag1
    
    
  for ref2 in base2.references:
    ref1 = h1.get_same(ref2)
    
    if ref1:
      merge_reference(ref1, ref2, tag_maps, combine_reference_review_status)
    else:
      ref1 = Reference()
      for attr in ref2.__dict__:
        if not attr in REFERENCE_SPECIAL_ATTRS: setattr(ref1, attr, getattr(ref2, attr))
      ref1.abstract       = ref2.abstract
      ref1.comment        = ref2.comment
      ref1.set_authors(ref2.authors)
      ref1.tags           = set(tag_maps[tag2] for tag2 in ref2.tags)
      for tag1 in ref1.tags: tag1.references.add(ref1)
      ref1.review_history = list(ref2.review_history)
      base1.add_reference(ref1)
      combine_reference_review_status(ref1, None)
      
  for ref1 in base1.references:
    ref2 = h2.get_same(ref1)
      
    if not ref2:
      combine_reference_review_status(ref1, None)
      
  return base1

def intersection_base(base1, base2):
  h2 = _ReferencesHash(base2.references)
  
  for ref1 in list(base1.references):
    if not h2.get_same(ref1):
      base1.remove_reference(ref1)
      
  return base1

def compare_base(base1, base2):
  h1 = _ReferencesHash(base1.references)
  h2 = _ReferencesHash(base2.references)

  #print len(base1.references)
  #print len([r for r in base1.references if r.doi])
  #print len([r for r in base1.references if r.pmid])
  #print
  #print len(base2.references)
  #print len([r for r in base2.references if r.doi])
  #print len([r for r in base2.references if r.pmid])
  
  common = only1 = only2 = 0
  for ref2 in base2.references:
    if h1.get_same(ref2): common += 1
    else: only2 += 1
  for ref1 in base1.references:
    if not h2.get_same(ref1): only1 += 1
    
  print(u"│ %5i │ │   %5i │             %s" % (len(base1.references), only1, base1.filename))
  print(u"│       │ │ ┌───────┼─┐ ┌───────┐")
  print(u"│       │ │ │ %5i │ │ │       │" % common)
  print(u"└───────┘ └─┼───────┘ │ │       │")
  print(u"            │ %5i   │ │ %5i │ %s" % (only2, len(base2.references), base2.filename))
  return None

def substract_base(base1, base2):
  h2 = _ReferencesHash(base2.references)
  for ref1 in list(base1.references):
    if h2.get_same(ref1): base1.remove_reference(ref1)
  return base1
  
def remove_references_pred(base, pred):
  for reference in list(base.references):
    if pred(reference): base.remove_reference(reference)
  return base


def set_review_mode(base):
  base.review_mode = 1
  return base

def analyse_author_frequency(base):
  groups = base.group_references_by_author()
  for group in groups.children:
    print(group)

COMMAND_LINE_FUNCS = {
  "--review-mode"             : set_review_mode,
  "--compare"                 : compare_base,
  "--substract"               : substract_base,
  "--intersection"            : intersection_base,
  "--union"                   : lambda base1, base2: union_base(base1, base2, union_reference_review_status),
  "--merge"                   : lambda base1, base2: union_base(base1, base2, merge_reference_review_status),
  "--merge-worse"             : lambda base1, base2: union_base(base1, base2, merge_reference_review_status_worse),
#  "--merge-review-status"     : merge_base_review_status,
  "--copy-review-status"      : copy_base_review_status,
  "--set-review-status"       : set_base_review_status,
  "--remove-without-author"   : lambda base: remove_references_pred(base, lambda ref: not ref.authors .strip()),
  "--remove-without-abstract" : lambda base: remove_references_pred(base, lambda ref: not ref.abstract.strip()),
  "--remove-without-keyword"  : lambda base: remove_references_pred(base, lambda ref: not ref.keywords.strip()),
  "--remove-with-keyword"     : lambda base: remove_references_pred(base, lambda ref:     ref.keywords.strip()),
  "--kappa"                   : compute_cohen_kappa,
  "--keep-accepted"           : lambda base: remove_references_pred(base, lambda ref: ref.get_value_for_category(u"review") != 1),
  "--analyse-author-frequency": analyse_author_frequency,
 }
