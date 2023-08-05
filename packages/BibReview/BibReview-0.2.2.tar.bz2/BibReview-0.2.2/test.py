
import sys, os, os.path, inspect

import bibreview, bibreview.globdef, bibreview.model, bibreview.command_line
from bibreview.parse_bibreview import *

def commande(ligne_de_commande):
  #ligne_de_commande = bibreview_path + " " + s
  #os.system(ligne_de_commande)
  ligne_de_commande = ligne_de_commande.replace("\\", "\\\\").replace("\n", " ")
  print "bibreview %s" % ligne_de_commande
  bibreview.command_line.run(ligne_de_commande)


commande("""--query-pubmed '
(
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
	"rule-bases"[TIAB] OR 
)



AND (2013[DP] NOT 2014[DP] NOT pubstatusaheadofprint)
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

AND ( 	clinical[tiab] OR 
	medical[tiab] OR 
	patient[tiab] OR 
	patients[tiab] OR 
	hospital[tiab] OR 
	hospitals[tiab] OR 
	ward[tiab] OR 
	wards[tiab] OR 
	department[tiab] OR 
	departments[tiab] OR 
	service[tiab] OR 
	services[tiab] OR 
	health[tiab] OR 
	healthcare[tiab] OR 
	clinician[tiab] OR 
	clinicians[tiab] OR 
	doctor[tiab] OR
	doctors[tiab] OR
	physician[tiab] OR
	physicians[tiab] OR
	nurse[tiab] OR
	nurses[tiab] OR
	personnel[tiab] OR
	professional[tiab] OR
	professionals[tiab] OR
	participant[tiab] OR
	participants[tiab]OR

	practioner[tiab]OR
	practioners[tiab]OR
	internist[tiab]OR
	internists[tiab]OR
	resident[tiab]OR
	residents[tiab]
	)

AND (	computer[Tiab] OR
	computers[Tiab] OR
	computerised[tiab] OR
	computerized[tiab] OR
	program[tiab] OR
	programs[tiab] OR
	system[tiab] OR
	systems[tiab] OR
	"digital assistant"[tiab] OR
	"digital assistants"[tiab] OR
	PDA[tiab] OR
	PDAs[tiab] OR
	smartphone[tiab] OR
	smartphones[tiab] OR
	software[tiab] OR
	internet[tiab] OR
	web[tiab] OR
	reminder[tiab] OR
	reminders[tiab] OR
	alert[tiab] OR
	alerts[tiab] OR
	"decision support"[tiab] OR
	electronic[tiab] OR
	"medical record"[tiab] OR
	"medical records"[tiab] OR
	"patient record"[tiab] OR
	"patient records"[tiab] OR
	"electronic record"[tiab] OR
	"electronic records"[tiab] OR
	"health record"[tiab] OR
	"health records"[tiab]
	)


' --save-as /tmp/test.xml""")

