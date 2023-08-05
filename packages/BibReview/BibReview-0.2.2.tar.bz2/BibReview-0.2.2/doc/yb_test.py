# -*- coding: utf-8 -*-
# BibReview
# Copyright (C) 2012 Jean-Baptiste LAMY


# Paramètres généraux :

# Année
annee = "2012"

# Dossier où seront stockés les bases biblio
dossier = "/home/jiba/zip/labo/yearbook/" + annee

# Répertoire BibReview (celui contenant bibreview/bibreview)
bibreview_path = ""

# Paramètres dépendants de la section :

# Requête avec mot-clef MeSH (SANS les critères de date, langue et type de publication)
q_mesh = '''(
("Decision support techniques"[MAJR] NOT "Data Interpretation, Statistical"[MAJR]) OR
 "Decision support systems, clinical"[MAJR] OR
 "Decision support systems, management"[MAJR] OR
 "Medical Order Entry Systems"[MAJR] OR
("Medical Records Systems, Computerized"[MAJR] AND "Decision Making, Computer-Assisted"[MAJR]) OR
 "Reminder Systems"[MAJR]
)'''

# Requête en texte libre


# XXX ajouter expert system ?


q_text = '''(
 "decision support"[TIAB] OR
 "clinical decision support system"[TIAB] OR
 "computerized decision support"[TIAB] OR
 "electronic decision support"[TIAB] OR
 "clinical decision support"[TIAB] OR
 "reminder system"[TIAB] OR
 "electronic reminder"[TIAB] OR
 "computer reminder"[TIAB] OR
 "computerized reminder"[TIAB] OR
 "electronic alerts"[TIAB] OR
 "computer alerts"[TIAB] OR
 "computerized alerts"[TIAB] OR
 "CPOE"[TIAB] OR
 "computer order entry"[TIAB] OR
 "computerized order entry"[TIAB] OR
 "computerized provider order entry"[TIAB] OR
 "computerized physician order entry"[TIAB] OR
("EHR"[TIAB] AND "decision"[TIAB]) OR
("EMR"[TIAB] AND "decision"[TIAB]) OR
("electronic health record"[TIAB] AND "decision"[TIAB]) OR
("electronic medical record"[TIAB] AND "decision"[TIAB])
)'''



#q_journal = '''(NOT "Yearbook of medical informatics"[Journal])'''
q_journal = ''''''


# Le reste du script ne change pas a priori

# Import de module Python
import sys, os, datetime

if not bibreview_path: bibreview_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "..", ".."))

sys.path.insert(0, bibreview_path)

import bibreview, bibreview.command_line


# Détermine s'il s'agit d'une base partielle (année en cours) ou complète
if datetime.date.today().year == int(annee): partielle = 1
else:                                        partielle = 0

# Détermine si la base est partielle ou complète
if partielle: suffixe = "_partielle"
else:         suffixe = "_complete"

# Enlève les sauts de ligne dans les requêtes
q_mesh = q_mesh.replace("\n", " ")
q_text = q_text.replace("\n", " ")

# Définit les éléments de base des requêtes
q_date = '("2005/01/01"[Date - Publication] : "3000"[Date - Publication])'
q_lang = '("english"[Language])'
q_type = '("journal article"[Publication Type])'

q_base = q_date + " AND " + q_lang + " AND " + q_type + q_journal


def commande(ligne_de_commande):
  #ligne_de_commande = bibreview_path + " " + s
  #os.system(ligne_de_commande)
  ligne_de_commande = ligne_de_commande.replace("\\", "\\\\")
  print "bibreview %s" % ligne_de_commande
  bibreview.command_line.run(ligne_de_commande)


commande("--query-pubmed '" + q_mesh + " AND " + q_base + "' --remove-without-author CURRENT --remove-without-abstract CURRENT --save-as /tmp/reviewer.xml")
