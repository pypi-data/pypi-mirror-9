# -*- coding: utf-8 -*-
# BibReview
# Copyright (C) 2012 Jean-Baptiste LAMY


# Paramètres généraux :

# Année
annee = "2013"

# Dossier où seront stockés les bases biblio
dossier = "/home/jiba/zip/labo/yearbook/" + annee

# Répertoire BibReview (celui contenant bibreview/bibreview)
bibreview_path = ""

# Paramètres dépendants de la section :

# Requête avec mot-clef MeSH (SANS les critères de date, langue et type de publication)
q_mesh = '''(
	"Decision support systems, clinical"[MH] OR
	"Decision support systems, management"[MH] OR
	"Medical Order Entry Systems"[MH] OR
 	"Reminder Systems"[MH] OR
	"Expert Systems"[MH] OR
	"Electronic Prescribing"[MH] OR

	("Decision support techniques"[MAJR]  NOT "Statistics as topic"[MH]) OR
	("Decision Making, Computer-Assisted"[MAJR] NOT "Statistics as topic"[MH])
)'''

# Requête en texte libre
q_text = '''(
	"decision support"[TIAB] OR
	"CDSS"[TIAB] OR
	"CDSSs"[TIAB] OR
	"DSS"[TIAB] OR
	"DSSs"[TIAB] OR

	"reminder system"[TIAB] OR 
	"reminder systems"[TIAB] OR 
	"computer reminder"[TIAB] OR
 	"computer reminders"[TIAB] OR 
	"electronic reminder"[TIAB] OR
 	"electronic reminders"[TIAB] OR 
	"computerized reminder"[TIAB] OR
 	"computerized reminders"[TIAB] OR 
	"computerised reminder"[TIAB] OR
 	"computerised reminders"[TIAB] OR 

	"alert system"[TIAB] OR 
	"alert systems"[TIAB] OR 
	"computer alert"[TIAB] OR
 	"computer alerts"[TIAB] OR 
	"electronic alert"[TIAB] OR
 	"electronic alerts"[TIAB] OR 
	"computerized alert"[TIAB] OR
 	"computerized alerts"[TIAB] OR 
	"computerised alert"[TIAB] OR
 	"computerised alerts"[TIAB] OR 

	"CPOE"[TIAB] OR 
	"CPOEs"[TIAB] OR 
	"order entry"[TIAB] OR 
	"electronic prescribing"[TIAB] OR 
	"electronic prescription"[TIAB] OR 
	"electronic prescriptions"[TIAB] OR 
	"computer prescribing"[TIAB] OR 
	"computer prescription"[TIAB] OR 
	"computer prescriptions"[TIAB] OR 
	"computerized prescribing"[TIAB] OR 
	"computerized prescription"[TIAB] OR 
	"computerized prescriptions"[TIAB] OR 
	"computerised prescribing"[TIAB] OR 
	"computerised prescription"[TIAB] OR 
	"computerised prescriptions"[TIAB] OR 

	("EHR"[TIAB] 
		AND ("decision"[TIAB] OR "decisions"[TIAB])) OR 
	("EMR"[TIAB] 
		AND ("decision"[TIAB] OR "decisions"[TIAB])) OR 
	(("electronic health record*"[TIAB] OR 
		"computerized health record*"[TIAB] OR
		"computerised health record*"[TIAB]
		) 
	   	AND ("decision"[TIAB] OR "decisions"[TIAB])) OR 
	(("electronic medical record*"[TIAB] OR 
		"computerized medical record*"[TIAB] OR
		"computerised medical record*"[TIAB]	
		) 
		AND ("decision"[TIAB] OR "decisions"[TIAB])) OR

	"expert system"[TIAB] OR 
	"expert systems"[TIAB] OR 

	"rule-based"[TIAB] OR 
	"rule-base"[TIAB] OR 
	"rule-bases"[TIAB] 
)'''

q_common = '''(2013[DP] NOT 2014[DP] NOT pubstatusaheadofprint)
AND ("journal article"[pt] 
	NOT Bibliography[pt] 
	NOT Portraits[pt] 
	NOT Comment[pt] 
	NOT Editorial[pt] 
	NOT Letter[pt] 
	NOT News[pt] 
	NOT Case Reports[pt] 
	NOT Published Erratum[pt] 
	NOT Historical Article[pt] 
	NOT Legal Cases[pt] 
	NOT legislation[pt])
NOT "Yearb Med Inform"[jour]
AND "english"[LA]
AND hasabstract

NOT Sanitation[MH]
NOT "Computer simulation"[MH]
NOT "Image Interpretation, Computer-Assisted"[MH] 
NOT "Radiotherapy Planning, Computer-Assisted"[MH] 
NOT "Radiotherapy, Conformal"[MH]
NOT "Surgery, Computer-Assisted"[MH]
NOT "Computational Biology"[MH]
NOT (animals[mh] NOT humans[mh])

AND ( 	"clinical"[tiab] OR 
	"medical"[tiab] OR 
	"patient"[tiab] OR 
	"patients"[tiab] OR 
	"hospital"[tiab] OR 
	"hospitals"[tiab] OR 
	"ward"[tiab] OR 
	"wards"[tiab] OR 
	"department"[tiab] OR 
	"departments"[tiab] OR 
	"clinic"[tiab] OR
	"clinics"[tiab] OR
	"health"[tiab] OR 
	"healthcare"[tiab] OR
	"medicine"[tiab] OR 
	"clinician"[tiab] OR 
	"clinicians"[tiab] OR 
	"doctor"[tiab] OR
	"doctors"[tiab] OR
	"physician"[tiab] OR
	"physicians"[tiab] OR
	"nurse"[tiab] OR
	"nurses"[tiab] OR
	"general practitioner"[tiab] OR
	"general practitioners"[tiab] OR
	"internist"[tiab] OR
	"internists"[tiab] OR
	"resident"[tiab] OR
	"residents"[tiab]
	)

AND (	"computer"[tiab] OR
	"computers"[tiab] OR
	"computerised"[tiab] OR
	"computerized"[tiab] OR
	"program"[tiab] OR
	"programs"[tiab] OR
	"system"[tiab] OR
	"systems"[tiab] OR
	"digital assistant"[tiab] OR
	"digital assistants"[tiab] OR
	"PDA"[tiab] OR
	"PDAs"[tiab] OR
	"smartphone"[tiab] OR
	"smartphones"[tiab] OR
	"software"[tiab] OR
	"internet"[tiab] OR
	"web"[tiab] OR
	"reminder"[tiab] OR
	"reminders"[tiab] OR
	"alert"[tiab] OR
	"alerts"[tiab] OR
	"decision support"[tiab] OR
	"electronic"[tiab] OR
	"medical record"[tiab] OR
	"medical records"[tiab] OR
	"patient record"[tiab] OR
	"patient records"[tiab] OR
	"electronic record"[tiab] OR
	"electronic records"[tiab] OR
	"health record"[tiab] OR
	"health records"[tiab]
	)'''


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
q_mesh   = q_mesh  .replace("\n", " ")
q_text   = q_text  .replace("\n", " ")
q_common = q_common.replace("\n", " ")


# Définition de fonctions
def fichier(nom, ext = ".xml", suf = None, fusion = 0):
  if suf is None: suf = suffixe
  if fusion: return os.path.join(dossier, nom + suf + "_fusion" + ext)
  return os.path.join(dossier, nom + suf + ext)

def commande(ligne_de_commande):
  #ligne_de_commande = bibreview_path + " " + s
  #os.system(ligne_de_commande)
  ligne_de_commande = ligne_de_commande.replace("\\", "\\\\")
  print "bibreview %s" % ligne_de_commande
  bibreview.command_line.run(ligne_de_commande)


### Crée le dossier s'il n'existe pas

if not os.path.exists(dossier): os.mkdir(dossier)


### Crée la base yb partielle ou complète (selon la date), si celle-ci n'existe pas

if os.path.exists(fichier("yb")):
  print
  print "La base %s existe déjà -- supprimez le fichier si vous souhaitez recréer la base et refaire les requêtes." % fichier("yb")
  
else:
  print
  print "Création de la base %s..." % fichier("yb")
  print
  
  # Effectue la requête MeSH
  commande("--query-pubmed '" + q_mesh + " AND " + q_common + "' --review-mode CURRENT --remove-without-author CURRENT --remove-without-abstract CURRENT --save-as " + fichier("pubmed_mesh"))
  
  # Effectue la requête en texte libre
  commande("--query-pubmed '" + q_text + " AND " + q_common + "' --review-mode CURRENT --remove-without-author CURRENT --remove-without-abstract CURRENT --save-as " + fichier("pubmed_text"))
  
  # Retire les références avec mots clefs des résultats de la requête en texte libre
  #commande("--remove-with-keyword " + fichier("pubmed_text") + " --review-mode CURRENT --save-as " + fichier("pubmed_text_withoutkeyword"))
  
  # Réunit les résultats de la requête MeSH avec les résultats de la requête en texte libre sans mot-clef
  #commande("--union " + fichier("pubmed_mesh") + " " + fichier("pubmed_text_withoutkeyword") + " --review-mode CURRENT --save-as " + fichier("pubmed"))
  commande("--union " + fichier("pubmed_mesh") + " " + fichier("pubmed_text") + " --review-mode CURRENT --save-as " + fichier("pubmed"))

  # Recherche les fichiers .bib de l'extraction web of sciences
  bibtex = []
  for f in os.listdir(dossier):
    if f.endswith(".bib"):
      if (partielle and f.startswith("wos_partielle_")) or ((not partielle) and f.startswith("wos_complete_")):
        bibtex.append(open(os.path.join(dossier, f)).read())

  if bibtex:
    open(fichier("wos", ".bib"), "w").write("\n".join(bibtex))

    # Importe le fichier .bib dans BibReview
    commande("--import-bibtex '" + fichier("wos", ".bib") + "' --review-mode CURRENT --remove-without-author CURRENT --remove-without-abstract CURRENT --save-as " + fichier("wos"))

    commande("--union " + fichier("pubmed") + " " + fichier("wos") + " --review-mode CURRENT --save-as " + fichier("yb"))

  else:
    # Pas de requête web of sciences => copie le contenu de la requête Pubmed sans fusion
    xml = open(fichier("pubmed")).read()
    open(fichier("yb"), "w").write(xml)
  


### Fusionne les bases des différents relecteurs

def fusionner(fichiers, nom):
  commande('"' + fichiers[0] + '"' + "".join(' --merge CURRENT "%s" ' % f for f in fichiers[1:]) + " --review-mode CURRENT --save-as " + nom)
  
for suf in ["_partielle", "_complete"]:
  fichier_fusion = fichier("yb", suf = suf, fusion = 1)
  if os.path.exists(fichier_fusion):
    print
    print "La base fusionnée %s existe déjà -- supprimez le fichier si vous souhaitez refaire la fusion" % fichier_fusion
    print
    
  else:
    a_fusionner = []
    for f in os.listdir(dossier):
      if f.startswith("yb" + suf + "_") and f.endswith(".xml") and (not f.startswith("yb" + suf + "_fusion")):
        a_fusionner.append(os.path.join(dossier, f))
    if len(a_fusionner) >= 2:
      print
      print "Fusion des bases %s..." % " ".join(a_fusionner)
      print
      fusionner(a_fusionner, fichier_fusion)


# Si c'est la base complète, on copie les statuts de revue depuis la base partielle
if not partielle:
  print
  print "Union des bases partielles relues avec la base complète, pour chaque relecteur..."
  print
  for f in os.listdir(dossier):
    if f.startswith("yb_partielle_") and f.endswith(".xml"):
      f = os.path.join(dossier, f)
      fichier_fusion = f.replace("_partielle_", "_complete_")
      if os.path.exists(fichier_fusion):
        print
        print "La base fusionnée %s existe déjà -- supprimez le fichier si vous souhaitez refaire la fusion" % fichier_fusion
        print
        
      else:
        commande('--union "' + f + '" ' + fichier("yb") + ' --review-mode CURRENT --save-as "' + fichier_fusion + '"')
  
