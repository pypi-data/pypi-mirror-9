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


import sys, os, os.path, re, gobject, gtk, glib, bibreview.globdef as globdef
from xml.sax.saxutils import escape as xml_escape, unescape as xml_unescape, quoteattr as xml_escape_attr
import editobj2, editobj2.introsp as introsp, editobj2.field as field, editobj2.editor as editor, editobj2.observe as observe, editobj2.undoredo as undoredo, editobj2.field_gtk as field_gtk, editobj2.editor_gtk as editor_gtk, editobj2.observe as observe
import bibreview
from bibreview.model           import *
from bibreview.parse_bibreview import *

editobj2.GUI = "Gtk"
editobj2.TRANSLATOR = _
editor_gtk.USE_MARKUP_FOR_LABEL = 1


class GtkTagField(field_gtk.GtkField, gtk.ScrolledWindow):
  def __init__(self, gui, master, obj, attr, undo_stack):
    gtk.ScrolledWindow.__init__(self)
    super(GtkTagField, self).__init__(gui, master, obj, attr, undo_stack)
    self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.set_shadow_type(gtk.SHADOW_IN)
    self.set_size_request(-1, 250)
    
    if isinstance(obj, introsp.ObjectPack): self.base = obj.objects[0]._base
    else:                                   self.base = obj._base
    
    self.tree = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_BOOLEAN)
    self.tag_2_path = {}
    self.path_2_tag = {}
    
    for tag in self.base.root_tag.descendants():
      path = self.tag_2_path.get(tag._parent)
      if path is None: iter = None
      else:            iter = self.tree.get_iter(path)
      path = self.tree.get_path(self.tree.append(iter, (unicode(tag), False)))
      if isinstance(path, tuple): path = ":".join(str(i) for i in path)
      self.tag_2_path[tag ] = path
      self.path_2_tag[path] = tag
      
    self.tree_view = gtk.TreeView(self.tree)
    self.tree_view.set_headers_visible(0)

    def add_colum(renderer, attr, i):
      column = gtk.TreeViewColumn(None)
      column.pack_start(renderer)
      column.add_attribute(renderer, attr, i)
      self.tree_view.append_column(column)
      return renderer
    add_colum(gtk.CellRendererToggle(), "active", 1).connect("toggled", self.on_cell_toggled, self.tree)
    add_colum(gtk.CellRendererText  (), "text"  , 0)
    
    self.add(self.tree_view)
    
    self.update()
    
  def get_value(self):
    if isinstance(self.o, introsp.ObjectPack):
      tags = set(self.o.objects[0].tags)
      for o in self.o.objects[1:]: tags.intersection_update(o.tags)
      return tags
    return self.o.tags
  
  def set_value(self, tags):
    old_tags     = set(self.get_value())
    added_tags   = tags - old_tags
    removed_tags = old_tags - tags
    
    def do_it  (added_tags = added_tags, removed_tags = removed_tags):
      for tag in removed_tags:
        if isinstance(self.o, introsp.ObjectPack):
          for o in self.o.objects: o.remove_tag(tag)
        else: self.o.remove_tag(tag)
      for tag in added_tags:
        if isinstance(self.o, introsp.ObjectPack):
          for o in self.o.objects: o.add_tag(tag)
        else: self.o.add_tag(tag)
      observe.assert_changed(self.o)
      self.update()
    def undo_it(): do_it(removed_tags, added_tags)
    a = undoredo.UndoableOperation(do_it, undo_it, _("change of tags"), self.undo_stack)
    
  def on_cell_toggled(self, widget, path, model):
    tags = set(self.get_value())
    if model[path][1]: tags.discard(self.path_2_tag[path])
    else:              tags.add    (self.path_2_tag[path])
    self.set_value(tags)
    self.update(auto_expand = 0)
    
  def update(self, auto_expand = 1, *args):
    tags = self.get_value()
    
    if auto_expand:
      self.tree_view.collapse_all()
      if self.base.review_mode:
        for tag in self.base.root_tag.descendants():
          if tag._category == u"review":
            for tag2 in tag.self_and_descendants():
              if tag2.children: self.tree_view.expand_to_path(self.tag_2_path[tag2])
            break
          
    for tag in self.base.root_tag.descendants():
      value = tag in tags
      row = self.tree[self.tag_2_path[tag]]
      row[0] = unicode(tag)
      row[1] = value
      if auto_expand and value:
        parent_path = self.tag_2_path.get(tag._parent)
        if parent_path: self.tree_view.expand_to_path(parent_path)



stops = [u"Material", u"Methods", u"Results", u"Conclusion", u"However", u"Moreover", u"This article", u"The article", u"This paper", u"The paper", u"We present", u"We describe", u"We then", u"Our method", u"The evaluation", u"In this ", u"In conclusion", u"Therefore", u"The aim", u"The objective", u"Our objective"]
STOP_REGEXP1 = re.compile(u"(?<=\\.) (?=[ A-Z]+:)", re.UNICODE)
STOP_REGEXP2 = re.compile(u"(?<=\\.) (?=%s)" % u"|".join(u"(?:%s)" % stop for stop in stops), re.UNICODE)
DOT          = re.compile(u"(?<!i\\.e)(?<!e\\.g)(?<=\\.|,|:|;) ", re.UNICODE)

class GtkLongTextField(field_gtk.GtkTextField):
  def __init__(self, gui, master, o, attr, undo_stack):
    field_gtk.GtkTextField.__init__(self, gui, master, o, attr, undo_stack)
    self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_NEVER)
    self.set_size_request(-1, -1)
    self.text.set_left_margin (12)
    self.text.set_right_margin(12)
    
class GtkCommentField(GtkLongTextField):
  def __init__(self, gui, master, o, attr, undo_stack):
    GtkLongTextField.__init__(self, gui, master, o, attr, undo_stack)
    self.text.set_justification(gtk.JUSTIFY_FILL)
    self.text.set_pixels_above_lines(15)
    self.text.set_indent(25)
    
class GtkAbstractField(GtkCommentField):
  def get_value(self):
    s = GtkCommentField.get_value(self)
    if s.count(u"\n") > 2: return s
    s = STOP_REGEXP1.sub(u"\n", s)
    if s.count(u"\n") > 2: return s
    return STOP_REGEXP2.sub(u"\n", s)
  
  def update(self):
    buf = self.text.get_buffer()
    buf.set_text(u"")
    bold = buf.create_tag(weight = 700)
    paras = self.get_value().split(u"\n")
    for para in paras:
      splitted = DOT.split(para, maxsplit = 1)
      if len(splitted) == 2:
        buf.insert_with_tags(buf.get_end_iter(), splitted[0], bold)
        buf.insert          (buf.get_end_iter(), u" %s" % splitted[1])
      else:
        buf.insert          (buf.get_end_iter(), u"%s" % para)
      if not para is paras[-1]:
        buf.insert          (buf.get_end_iter(), u"\n")

class GtkReviewHistoryField(field_gtk.GtkLabelField):
  def get_value(self):
    if not hasattr(self.o, "review_history"): return u"?" # For ObjectPack
    try:
      return "\n".join("%s %s %s %s" % (date.strftime("%c"), self.o._base.root_tag._category_2_tag["review", status].name, _(u"by"), user) for (date, user, status) in self.o.review_history if not status is None) or u"-"
    except:
      sys.excepthook(*sys.exc_info())
      return u"?"
    
    
class Editable(object):
  def __init__(self, title, **kargs):
    self.__dict__ = kargs
    self._title   = title

  def __unicode__(self): return self._title
  def __repr__   (self): return unicode(self).encode("utf8")
  
descr = introsp.description(globdef.Config)
descr.set_field_for_attr("user_name", field.StringField)

descr = introsp.description(Editable)
descr.set_field_for_attr("authors_frequency"      , GtkLongTextField)
descr.set_field_for_attr("journals_frequency"     , GtkLongTextField)
descr.set_field_for_attr("first_authors_frequency", GtkLongTextField)

descr = introsp.description(Base)
descr.set_field_for_attr("review_mode"  , field.BoolField)
descr.set_field_for_attr("auto_export_bibtex", field.BoolField)
descr.set_field_for_attr("name"         , field.StringField)
descr.set_field_for_attr("comment"      , GtkCommentField)
descr.set_field_for_attr("root_tag"     , field.EditButtonField)
descr.set_field_for_attr("sort_criteria", None)
descr.set_field_for_attr("filename"     , None)
descr.set_children_getter("selections", None, lambda base: Reference(tags = base._search_tags), "add_reference", "remove_reference", 0)
descr.set_icon_filename(os.path.join(globdef.DATADIR, "base.png"))
descr.set_field_for_attr("text_export", field.EditButtonField)

descr = introsp.description(Groups)
descr.set_icon_filename(os.path.join(globdef.DATADIR, "base.png"))
descr.set_field_for_attr("text_export", field.EditButtonField)

descr = introsp.description(Group)
descr.set_icon_filename(os.path.join(globdef.DATADIR, "base.png"))

descr = introsp.description(Tag)
descr.set_field_for_attr("name"          , field.StringField)
descr.set_field_for_attr("category_name" , None)
descr.set_field_for_attr("category_value", None)
descr.set_field_for_attr("search_tag"    , None)
descr.set_children_getter("children", None, lambda parent: Tag(parent), "add_child", "remove_child")
descr.set_icon_filename(os.path.join(globdef.DATADIR, "tag.png"))

descr = introsp.description(Reference)
descr.set_field_for_attr("tags"          , GtkTagField)
descr.set_field_for_attr("abstract"      , GtkAbstractField)
descr.set_field_for_attr("comment"       , GtkCommentField)
descr.set_field_for_attr("keywords"      , GtkCommentField)
descr.set_field_for_attr("title"         , field.StringField)
descr.set_field_for_attr("authors"       , GtkLongTextField)
descr.set_field_for_attr("authors_short" , None)
descr.set_field_for_attr("editor"        , field.StringField)
descr.set_field_for_attr("publisher"     , field.StringField)
descr.set_field_for_attr("address"       , field.StringField)
descr.set_field_for_attr("journal"       , field.StringField)
descr.set_field_for_attr("vol_n_p"       , field.StringField)
descr.set_field_for_attr("volume"        , None)
descr.set_field_for_attr("issue"         , None)
descr.set_field_for_attr("pages"         , None)
descr.set_field_for_attr("pub_date"      , field.DateField)
descr.set_field_for_attr("epub_date"     , field.DateField)
descr.set_field_for_attr("insert_date"   , field.DateField)
descr.set_field_for_attr("url"           , field.URLField)
descr.set_field_for_attr("path"          , field.FilenameField)
descr.set_field_for_attr("key"           , field.StringField)
descr.set_field_for_attr("doi"           , field.StringField)
descr.set_field_for_attr("pmid"          , field.StringField)
descr.set_field_for_attr("review_history", GtkReviewHistoryField)
descr.set_field_for_attr("conflict_type" , None)
descr.set_details(lambda reference: u"<a href=%s>%s</a>\n\n%s" % (xml_escape_attr(reference.url), xml_escape(reference.url), u", ".join(tag.name for tag in reference.tags)))

introsp.set_field_for_attr("request"    , GtkLongTextField)

EXISTING_CONFLICT_ICONS = set([u"-10", u"-11", u"01", u"-101"])

def reference_icon_filename(reference):
  value = reference.get_value_for_category(u"review")
  if   value is None: value = reference.get_value_for_category(u"pub_type") or u"article"
  elif value < 0: value = -1
  elif value == u"c":
    if getattr(reference, "conflict_type", "c") in EXISTING_CONFLICT_ICONS: value = u"c%s" % reference.conflict_type
  return os.path.join(globdef.DATADIR, "%s.png" % value)
  
descr.set_icon_filename(reference_icon_filename)


MAIN_WINDOWS = []

from collections import Counter

class MainWindow(gtk.Window):
  def __init__(self, base = None):
    gtk.Window.__init__(self)
    self.set_title(u"BibReview")
    self.set_role (u"main")
    self.accel_group = gtk.AccelGroup()
    self.add_accel_group(self.accel_group)
    
    self.last_filename       = u""
    self.old_search_tags     = set()
    self.search_tag_2_button = {}
    self.editor              = editor.HEditorPane("Gtk", self, 1)
    self.set_base(base or Base())
    
    menu_bar = gtk.MenuBar()
    
    file_menu = self.add_menu(menu_bar, _(u"File"))
    self.add_menu_entry(file_menu, _(u"New")       , self.on_new, u"C-n")
    self.add_menu_entry(file_menu, _(u"Open...")   , self.on_open, u"C-o")
    self.add_menu_entry(file_menu, _(u"Import PubMed XML..."), self.on_import_pubmed)
    self.add_menu_entry(file_menu, _(u"Import BibTeX...")    , self.on_import_bibtex)
    self.add_menu_entry(file_menu, _(u"Save")      , self.on_save, u"C-s")
    self.add_menu_entry(file_menu, _(u"Save as..."), self.on_save_as, u"C-S-S")
    self.add_menu_entry(file_menu, _(u"Save selection as..."), self.on_save_selection_as)
    self.add_menu_entry(file_menu, _(u"Export selection as CSV..."), self.on_export_csv)
    file_menu.append(gtk.SeparatorMenuItem())
    self.add_menu_entry(file_menu, _(u"Quit")      , self.on_quit, u"C-q")
    
    edit_menu = self.add_menu(menu_bar, _(u"Edit"))
    self.add_menu_entry(edit_menu, _(u"Undo"), lambda x: undoredo.stack.undo(), u"C-z")
    self.add_menu_entry(edit_menu, _(u"Redo"), lambda x: undoredo.stack.redo(), u"C-y")
    edit_menu.append(gtk.SeparatorMenuItem())
    #for label, criteria in [(_(u"Sort by authors"), u"authors"), (_(u"Sort by date (publication)"), u"pub_date"), (_(u"Sort by date (E-pub)"), u"epub_date"), (_(u"Sort by date (insertion)"), u"insert_date"), (_(u"Sort by title"), u"title"), (_(u"Sort by journal"), u"journal"), (_(u"Sort by review status"), u"review"), (_(u"Sort by lexical proximity"), u"lexical"), (_(u"Sort using neural network"), u"neural"), (_(u"Sort using bayesian classifier"), u"bayes")]:
    for label, criteria in [(_(u"Sort by authors"), u"authors"), (_(u"Sort by date (publication)"), u"pub_date"), (_(u"Sort by date (E-pub)"), u"epub_date"), (_(u"Sort by date (insertion)"), u"insert_date"), (_(u"Sort by review date"), u"review_date"), (_(u"Sort by title"), u"title"), (_(u"Sort by journal"), u"journal"), (_(u"Sort by review status"), u"review")]:
      self.add_menu_entry(edit_menu, label, lambda x, criteria = criteria: self.base.set_sort_criteria(criteria) or observe.scan())
    edit_menu.append(gtk.SeparatorMenuItem())
    #self.add_menu_entry(edit_menu, _(u"Train neural network"), self.on_train_neural_network)
    #self.add_menu_entry(edit_menu, _(u"Train bayesian classifier"), self.on_train_bayesian_classifier)
    #edit_menu.append(gtk.SeparatorMenuItem())
    self.add_menu_entry(edit_menu, _(u"Analyse authors frequency..."),       self.on_analyse_authors_frequency)
    self.add_menu_entry(edit_menu, _(u"Analyse first authors frequency..."), self.on_analyse_first_authors_frequency)
    self.add_menu_entry(edit_menu, _(u"Analyse last authors frequency..."),  self.on_analyse_last_authors_frequency)
    self.add_menu_entry(edit_menu, _(u"Intersection of author lists..."),    self.on_intersect_authors)
    edit_menu.append(gtk.SeparatorMenuItem())
    self.add_menu_entry(edit_menu, _(u"Analyse journals frequency..."), self.on_analyse_journals_frequency)
    edit_menu.append(gtk.SeparatorMenuItem())
    self.add_menu_entry(edit_menu, _(u"Preferences..."), self.on_preferences)
    
    add_menu = self.add_menu(menu_bar, _(u"Add"))
    self.add_menu_entry(add_menu, _(u"Add reference manually"),        self.on_add_manual)
    self.add_menu_entry(add_menu, _(u"Add references with Pubmed..."), self.on_add_pubmed)
    add_menu.append(gtk.SeparatorMenuItem())
    #self.add_menu_entry(add_menu, _(u"Remove reference"), )
    
    self.restrict_menu = self.add_menu(menu_bar, _(u"Restrict to"), on_click = self.on_click_restrict)
    
    cite_menu = self.add_menu(menu_bar, _(u"Cite"))
    self.add_menu_entry(cite_menu, _(u"Cite in LyX"), self.on_lyx)
    
    classifier_menu = self.add_menu(menu_bar, _(u"Classifier"))
    self.add_menu_entry(classifier_menu, _(u"Train Bayes classifier on title"), self.on_bayes_train_on_title)
    self.add_menu_entry(classifier_menu, _(u"Bayes leave-one-out test on title"), self.on_bayes_leave_one_out_on_title)
    classifier_menu.append(gtk.SeparatorMenuItem())
    self.add_menu_entry(classifier_menu, _(u"Classify current base"), self.on_classify)
    
    self.search_field = gtk.Entry()
    self.search_field.connect("activate", self.on_search)
    
    search_button = self.create_button(u"", gtk.image_new_from_stock(gtk.STOCK_FIND , gtk.ICON_SIZE_MENU), self.on_search)  
    clear_button  = self.create_button(u"", gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU), self.on_clear_search)
    
    menu_box = self.menu_box = gtk.HBox()
    menu_box.pack_start(menu_bar)
    menu_box.pack_end  (clear_button , 0)
    menu_box.pack_end  (search_button, 0)
    menu_box.pack_end  (self.search_field, 0)
    
    main_box = gtk.VBox()
    main_box.pack_start(menu_box, 0)
    main_box.pack_end  (self.editor, 1)
    self.add(main_box)

    self.editor.hi_box.remove(self.editor.childhood_pane)
    self.editor.scroll1.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    self.editor.set_position(400)
    self.set_size_request(950, 550)

    self.editor.hierarchy_pane.connect("key-press-event", self.on_key_press)
    self.connect("delete-event", self.on_close)
    
    MAIN_WINDOWS.append(self)

  def on_lyx(self, *arg):
    if   isinstance(self.editor.attribute_pane.o, Reference):
      key = self.editor.attribute_pane.o.gen_key()
    elif isinstance(self.editor.attribute_pane.o, introsp.ObjectPack):
      key = u",".join(r.gen_key() for r in self.editor.attribute_pane.o.objects)
    else: return
    
    os.system('echo "LYXCMD:bibreview:citation-insert:%s" > %s' % (key, globdef.CONFIG.lyx_pipe))
    
  def on_preferences(self, arg):
    def on_validate(o):
      globdef.CONFIG.save()
    editobj2.edit(globdef.CONFIG, on_validate = on_validate)
    
  def on_add_manual(self, *arg):
    reference = introsp.ACTION_ADD.do(editobj2.undoredo.stack, self.base)
    self.editor.hierarchy_pane.select_object(reference)
    
  def on_add_pubmed(self, *args):
    class PubmedRequest(object):
      def __init__(self):
        self.request = u""
      def __unicode__(self): return (u"Add references with Pubmed...")
      
    def on_validate(o):
      if not o: return
      
      from bibreview.parse_pubmed import query_pubmed
      r = o.request.strip()
      if r.endswith(u"/"): r = r[:-1]
      if r.startswith(u"http") or r.startswith("www"): r = r.split("/")[-1]
      try:
        int(r)
        r = [r]
      except: pass
      
      query_pubmed(self.base, r)
      observe.scan()
      self.editor.hierarchy_pane.select_object(self.base.references[-1])
      
    o = PubmedRequest()
    editobj2.edit(o, on_validate = on_validate)
    
  def on_train_neural_network(self, *args):
    import bibreview.neural_network as neural_network
    neural_network.train_neural_network(self.base.selections)
    
  def on_train_bayesian_classifier(self, *args):
    import bibreview.bayesian_classifier as bayesian_classifier
    bayesian_classifier.train_bayesian_classifer(self.base.selections)
    
  def on_show_authors_count(self, *args):
    s = _(u"Authors by frequency:") + "\n\n%s" % u"\n".join("%s : %s %s" % (author, nb, _(u"occurences")) for (author, nb) in AUTHORS_COUNTER.most_common())
    o = Editable(_(u"authors_frequency"), authors_frequency = s)
    editobj2.edit(o)

  def _show_authors_frequency(self, counter):
    total = 0
    l     = []
    for (author, nb) in counter.most_common():
      total += nb
      l.append((author, nb, total))
      
    s = _(u"Authors by frequency:") + "\n\n%s" % u"\n".join("%s : %s (%s cum) %s" % (author, nb, total, _(u"occurences")) for (author, nb, total) in l)
    o = Editable(_(u"authors_frequency"), authors_frequency = s)
    editobj2.edit(o)
    
  def on_analyse_journals_frequency(self, *args):
    counter = self.base.analyze_journal()
    total = 0
    l     = []
    for (journal, nb) in counter.most_common():
      total += nb
      l.append((journal, nb, total))
      
    s = _(u"Journals by frequency:") + "\n\n%s" % u"\n".join("%s : %s (%s cum) %s" % (journal, nb, total, _(u"occurences")) for (journal, nb, total) in l)
    o = Editable(_(u"journals_frequency"), journals_frequency = s)
    editobj2.edit(o)
    
  def on_analyse_authors_frequency      (self, *args): editobj2.edit(self.base.group_references_by_author())
  def on_analyse_first_authors_frequency(self, *args): editobj2.edit(self.base.group_references_by_first_author())
  def on_analyse_last_authors_frequency (self, *args): editobj2.edit(self.base.group_references_by_last_author())
  def on_analyse_journals_frequency     (self, *args): editobj2.edit(self.base.group_references_by_journal())
    
  def on_intersect_authors(self, arg):
    authorss     = [main_window.base.analyze_authors() for main_window in MAIN_WINDOWS]
    intersection = reduce(Counter.__and__, authorss)
    addition     = reduce(Counter.__add__, authorss)
    authors      = Counter()
    for author in intersection: authors[author] = addition[author]
    print authors
    self._show_authors_frequency(authors)
    
    
  def on_click_restrict(self, *args):
    for item in self.restrict_menu.get_children(): item.get_parent().remove(item)
    
    self.restrict_submenus = {}
    for tag in self.base.root_tag.descendants():
      parent_submenu = self.restrict_submenus.get(tag._parent) or self.restrict_menu
      if tag.children:
        self.restrict_submenus[tag] = self.add_menu(parent_submenu, tag.name)
        if not tag._category: self.add_menu_entry(self.restrict_submenus[tag], tag.name, lambda widget, tag = tag: self.on_restrict_tag(tag))
      else:
        self.add_menu_entry(parent_submenu, tag.name, lambda widget, tag = tag: self.on_restrict_tag(tag))
        
    self.show_all()
    
  def on_restrict_tag(self, tag):
    self.base._search_tags = self.base._search_tags | frozenset([tag])
    self.base.search(self.base._search)
    observe.scan()
    
  def on_close(self, *args):
    if self.check_save(): return 1
    
    self.destroy()
    
    MAIN_WINDOWS.remove(self)
    if len(MAIN_WINDOWS) == 0:
      #globdef.config.save()
      sys.exit()
      
  def on_key_press(self, widget, event):
    if self.base.review_mode:
      if   event.keyval == gtk.keysyms.Return: self.set_review_status( 1); return True
      elif event.keyval == gtk.keysyms.p: self.set_review_status( 0); return True
      elif event.keyval == gtk.keysyms.r: self.set_review_status(-1); return True
      elif event.keyval == gtk.keysyms.f: self.set_review_status(-2); return True
      elif event.keyval == gtk.keysyms.a: self.set_review_status(-3); return True
      elif event.keyval == gtk.keysyms.t: self.set_review_status(-4); return True
      elif event.keyval == gtk.keysyms.space: self.select_next_reference(); return True
      
  def set_review_status(self, value):
    if isinstance(self.editor.attribute_pane.o, Reference):
      self.editor.attribute_pane.o.set_value_for_category(u"review", value)
      observe.assert_changed(self.editor.attribute_pane.o)
      self.select_next_reference()
      
  def select_next_reference(self):
    if isinstance(self.editor.attribute_pane.o, Reference):
      next_id = self.base.selections.index(self.editor.attribute_pane.o) + 1
      if next_id < len(self.base.selections):
        self.editor.hierarchy_pane.select_object(self.base.selections[next_id])
        self.editor.hierarchy_pane.scroll_to_cell(self.editor.hierarchy_pane.get_selection().get_selected_rows()[1][0])
        
  def set_base(self, base):
    for tag in self.old_search_tags: self.on_remove_search_tag(tag)
    self.last_undoables  = []
    self.old_search_tags = set()
    self.base            = base
    self.editor.edit(base)
    observe.observe(self.base, self.on_base_changed)
    
  def on_base_changed(self, base, type, new, old):
    if base._search_tags != self.old_search_tags:
      for tag in base._search_tags - self.old_search_tags:
        button = self.search_tag_2_button[tag] = self.create_button(_(u"Restrict to %s") % tag.name, gtk.image_new_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU), lambda widget, tag = tag: self.on_remove_search_tag(tag))
        self.menu_box.pack_end(button , 0)
      for tag in self.old_search_tags - base._search_tags: self.on_remove_search_tag(tag)
      self.menu_box.show_all()
      self.old_search_tags = frozenset(base._search_tags)
      
  def on_remove_search_tag(self, tag):
    button = self.search_tag_2_button.get(tag)
    if button:
      tag.set_search_tag(0)
      del self.search_tag_2_button[tag]
      self.menu_box.remove(button)
      observe.scan()
      
  def check_save(self):
    if undoredo.stack.undoables != self.last_undoables:
      dialog = gtk.MessageDialog(self, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, message_format = _(u"Save modifications before closing?"))
      dialog.add_buttons(_(u"Close without saving"), 0, gtk.STOCK_CANCEL, 1, gtk.STOCK_SAVE, 2)
      dialog.set_default_response(1)
      response = dialog.run()
      dialog.destroy()
      if response == 2:
        self.on_save()
        return self.check_save() # The user may have canceled the "save as" dialog box !
      return response
    
  def on_new(self, *args):
    self.check_save()
    self.set_base(Base())
    
  def on_open(self, *args):
    self.check_save()
    if self.file_dialog(_(u"Open..."), gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)):
      base = parse_bibreview(open(self.last_filename).read())
      base.filename = self.last_filename
      self.set_base(base)
      
  def on_import_pubmed(self, *args):
    self.check_save()
    if self.file_dialog(_(u"Open..."), gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)):
      from bibreview.parse_pubmed import parse_pubmed
      base = parse_pubmed(Base(), open(self.last_filename).read())
      self.set_base(base)
      
  def on_import_bibtex(self, *args):
    self.check_save()
    if self.file_dialog(_(u"Open..."), gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK), "bib"):
      from bibreview.parse_bibtex import parse_bibtex
      base = parse_bibtex(Base(), open(self.last_filename).read())
      self.set_base(base)
      
  def on_save_as(self, *args):
    filename = self.file_dialog(_(u"Save as..."), gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
    if filename:
      self.base.filename = filename
      self.on_save()
      
  def on_save_selection_as(self, *args):
    filename = self.file_dialog(_(u"Save selection as..."), gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK), export = 1)
    if filename:
      if   isinstance(self.editor.attribute_pane.o, introsp.ObjectPack):
        selection = self.editor.attribute_pane.o.objects
      elif isinstance(self.editor.attribute_pane.o, Reference):
        selection = [self.editor.attribute_pane.o]
      else: return
      
      s = self.base.__xml__(selection).encode("utf8")
      open(filename, "w").write(s)
      
  def on_save(self, *args):
    if not self.base.filename: self.on_save_as()
    else:
      s = self.base.__xml__().encode("utf8")
      f = open(self.base.filename, "w")
      f.write(s)
      f.close()
      self.last_undoables = undoredo.stack.undoables
      if self.base.auto_export_bibtex:
        bibreview.export_bibtex.export_bibtex_file(self.base, u"%s.bib" % os.path.splitext(self.base.filename)[0])

  def on_export_csv(self, *args):
    filename = self.file_dialog(_(u"Save selection as..."), gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK), type = "csv", export = 1)
    if filename:
      import csv
      w = csv.writer(open(filename, "w"))
      for ref in self.base.selections:
        if ref.pub_date:
          month = ref.pub_date.month
          year  = ref.pub_date.year
        else:
          month = year = ""
        w.writerow([ref.journal, ref.get_volume(), ref.get_issue(), month, year, ref.title, ref.authors, ref.abstract])
      
      
  def file_dialog(self, name, action, options, type = "xml", export = 0):
    filter = gtk.FileFilter()
    if type == "xml":
      filter.set_name(u"XML")
      filter.add_pattern(u"*.xml")
    else:
      filter.set_name(type)
      filter.add_pattern(u"*.%s" % type)
      
    dialog = gtk.FileChooserDialog(name, self, action, options)
    dialog.set_default_response(gtk.RESPONSE_OK)
    dialog.add_filter(filter)
    
    if action == gtk.FILE_CHOOSER_ACTION_SAVE:
      dialog.set_property("do-overwrite-confirmation", 1)
      dialog.set_current_folder(os.path.dirname(self.last_filename))
      dialog.set_current_name(os.path.basename(self.base.filename))
    else: dialog.set_filename(self.last_filename)
    
    response = dialog.run()
    if response != gtk.RESPONSE_OK: dialog.destroy() ; return 0
    filename = dialog.get_filename()
    if not export:
      self.last_filename = filename
      if action == gtk.FILE_CHOOSER_ACTION_SAVE:
        if not self.last_filename.endswith(u".xml"): self.last_filename = u"%s.xml" % self.last_filename
        self.base.filename = self.last_filename
    dialog.destroy()
    return filename
  
  def on_quit(self, *args):
    self.check_save()
    sys.exit()
    
  def on_search(self, *args):
    self.base.search(self.search_field.get_text())
    observe.scan()
    
  def on_clear_search(self, *args):
    self.search_field.set_text(u"")
    self.base.search(u"")
    observe.scan()

  def on_bayes_train_on_title(self, *args):
    import bibreview.bayes_classifier as bayes_classifier
    bayes_classifier.bayes_train_on_title(self.base)
  
  def on_bayes_leave_one_out_on_title(self, *args):
    import bibreview.bayes_classifier as bayes_classifier
    bayes_classifier.bayes_leave_one_out_on_title(self.base)
    
  def on_classify(self, *args):
    import bibreview.bayes_classifier as bayes_classifier
    bayes_classifier.classify(self.base)
    observe.scan()
    
  def create_button(self, label, image, action):
    button = gtk.Button()
    if image: button.set_image(image)
    if label: button.set_label(label)
    button.set_relief(gtk.RELIEF_NONE)
    button.connect("clicked", action)
    return button

  def add_menu(self, parent, name, on_click = None):
    menu_item = gtk.MenuItem(name)
    parent.append(menu_item)
    if on_click: menu_item.connect("select", on_click)
    submenu = gtk.Menu()
    menu_item.set_submenu(submenu)
    return submenu

  def add_menu_entry(self, parent, name, action, accel = None):
    menu_item = gtk.MenuItem(name)
    menu_item.connect("activate", action)
    if accel:
      mod = 0
      if isinstance(accel, basestring):
        if u"C-" in accel: mod |= gtk.gdk.CONTROL_MASK
        if u"S-" in accel: mod |= gtk.gdk.SHIFT_MASK
        key = ord(accel[-1])
      else: key = accel
      menu_item.add_accelerator("activate", self.accel_group, key, mod, gtk.ACCEL_VISIBLE)
    parent.append(menu_item)
    return menu_item
