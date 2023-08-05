# -*- coding: utf-8 -*-
# BibReview
# Copyright (C) 2012 Jean-Baptiste LAMY


# Paramètres généraux :

# Année
annee = "2012"

# Dossier où seront stockés les bases biblio
#dossier = "D:\\svoros\\taff\\YEARBOOK_2012\\base_pubmed" + annee
dossier = "C:\\" + annee

# Répertoire BibReview (celui contenant bibreview/bibreview)
bibreview_path = ""

# Paramètres dépendants de la section :

# Requête avec mot-clef MeSH (SANS les critères de date, langue et type de publication)
q_mesh = '''(
(	computer literacy[MH] OR
	"computer user training"[MH] OR
	"computer-assisted instruction"[MH] OR
	"computing methodologies"[MH] OR
	"electronic prescribing"[MH] OR
	"medical informatics"[MH] OR
	"computational biology"[MH] OR
	"Informatics"[MH] OR
	"Medical Records Systems, Computerized"[MH] OR
	"Telemedicine"[MH]
)
AND
(	"Surgery, computer-assisted"[MAJR] OR
	"Image processing, Computer-Assisted"[MAJR] OR
	"Image interpretation, Computer-Assisted"[MAJR] OR
	"Monitoring, physiologic"[MAJR] OR
	"Signal Processing, Computer-Assisted"[MAJR] OR
	"Signal-To-Noise Ratio"[MAJR] OR
	"Clinical alarms"[MAJR] OR
	"Biosensing techniques"[MAJR] OR
	"Feedback"[MAJR] OR
	"Pattern recognition, automated"[MAJR] OR
	"Image enhancement"[MAJR] OR
	"Transducers"[MAJR]
)
)'''

# Requête en texte libre

q_text = '''(
 (
	"computer literacy"[TIAB] OR
	"computer literacies"[TIAB] OR
	"literacy, computer"[TIAB] OR
	"computer" [TIAB] OR
	"computers" [TIAB] OR
	"algorithms"[TIAB] OR
	"algorithm"[TIAB] OR
	"analog-digital conversion"[TIAB] OR
	"analogue digital conversion"[TIAB] OR
	"analogue-digital conversion"[TIAB] OR
	"artificial intelligence"[TIAB] OR
	"ai (artificial intelligence)"[TIAB] OR
	"machine intelligence"[TIAB] OR
	"automatic data processing"[TIAB] OR
	"electronic data processing"[TIAB] OR
	"computing methodologies"[TIAB] OR
	"computing methodology"[TIAB] OR
	"database"[TIAB] OR
	"databases"[TIAB] OR
	"data base management systems"[TIAB] OR
	"modems"[TIAB] OR
	"dataphone"[TIAB] OR
	"modem"[TIAB] OR
	"expert systems"[TIAB] OR
	"expert system"[TIAB] OR
	"system, expert"[TIAB] OR
	"fourier analysis"[TIAB] OR
	"analysis, cyclic"[TIAB] OR
	"cyclic analysis"[TIAB] OR
	"image enhancement"[TIAB] OR
	"image enhancements"[TIAB] OR
	"image quality enhancement"[TIAB] OR
	"image quality enhancements"[TIAB] OR
	"computer assisted image processing"[TIAB] OR
	"computer-assisted image processing"[TIAB] OR
	"local area networks"[TIAB] OR
	"lan"[TIAB] OR
	"local area network"[TIAB] OR
	"mathematical computing"[TIAB] OR
	"microcomputers"[TIAB] OR
	"microcomputer"[TIAB] OR
	"minicomputers"[TIAB] OR
	"minicomputer"[TIAB] OR
	"natural language processing"[TIAB] OR
	"programming languages"[TIAB] OR
	"programming language"[TIAB] OR
	"punched-card systems"[TIAB] OR
	"punched-card system"[TIAB] OR
	"radiographic image enhancement"[TIAB] OR
	"robotics"[TIAB] OR
	"computer-assisted"[TIAB] OR
	"software"[TIAB] OR
	"softwares"[TIAB] OR
	"user-computer interface"[TIAB] OR
	"word processing"[TIAB] OR
	"dual energy scanned projection radiography"[TIAB] OR
	"dual-energy scanned projection radiography"[TIAB] OR
	"grateful med"[TIAB] OR
	"mass storage device"[TIAB] OR
	"mass storage devices"[TIAB] OR
	"optical storage devices"[TIAB] OR
	"optical storage device"[TIAB] OR
	"compact disks"[TIAB] OR
	"compact disc"[TIAB] OR
	"compact discs"[TIAB] OR
	"compact disk"[TIAB] OR
	"CD-ROM"[TIAB] OR
	"cdrom"[TIAB] OR
	"compact disk read only memory"[TIAB] OR
	"compact disk read-only memory"[TIAB] OR
	"video display terminal"[TIAB] OR
	"video display terminals"[TIAB] OR
	"neural networks (Computer)"[TIAB] OR
	"connectionist model"[TIAB] OR
	"connectionist models"[TIAB] OR
	"neural network (computer)"[TIAB] OR
	"neural network model"[TIAB] OR
	"neural network models"[TIAB] OR
	"perceptron"[TIAB] OR
	"perceptrons"[TIAB] OR
	"computer-aided design"[TIAB] OR
	"computer-aided designs"[TIAB] OR
	"fuzzy logic"[TIAB] OR
	"video games"[TIAB] OR
	"games, video"[TIAB] OR
	"video game"[TIAB] OR
	"CD-I"[TIAB] OR
	"interactive compact disk"[TIAB] OR
	"hypermedia"[TIAB] OR
	"internet"[TIAB] OR
	"internets"[TIAB] OR
	"world wide web"[TIAB] OR
	"web"[TIAB] OR
	"3 d imaging"[TIAB] OR
	"3-d imaging"[TIAB] OR
	"imaging, 3-d"[TIAB] OR
	"three-dimensional imaging"[TIAB] OR
	"three-dimensional imagings"[TIAB] OR
	"data compression"[TIAB] OR
	"knowledge bases"[TIAB] OR
	"knowledge base"[TIAB] OR
	"knowledgebase"[TIAB] OR
	"knowledgebases"[TIAB] OR
	"molecular dynamics simulation"[TIAB] OR
	"molecular dynamics simulations"[TIAB] OR
	"blogging"[TIAB] OR
	"wavelet analysis"[TIAB] OR
	"spatiotemporal wavelet analysis"[TIAB] OR
	"wavelet analyses"[TIAB] OR
	"wavelet signal processing"[TIAB] OR
	"wavelet transform"[TIAB] OR
	"wavelet transforms"[TIAB] OR
	"support vector machines"[TIAB] OR
	"support vector machine"[TIAB] OR
	"social media"[TIAB] OR
	"social medium"[TIAB] OR
	"social mediums"[TIAB] OR
	"electronic prescribing"[TIAB] OR
	"E Prescribing"[TIAB] OR
	"E-Prescribing"[TIAB] OR
	"ambulatory care information systems"[TIAB] OR
	"clinical laboratory information systems"[TIAB] OR
	"laboratory information system"[TIAB] OR
	"laboratory information systems"[TIAB] OR
	"statistical data analyses"[TIAB] OR
	"statistical data analysis"[TIAB] OR
	"statistical data interpretation"[TIAB] OR
	"data base management systems"[TIAB] OR
	"decision support techniques"[TIAB] OR
	"decision support technics"[TIAB] OR
	"decision support technique"[TIAB] OR
	"hospital information systems"[TIAB] OR
	"hospital information system"[TIAB] OR
	"information systems"[TIAB] OR
	"information system"[TIAB] OR
	"systems, information"[TIAB] OR
	"management information systems"[TIAB] OR
	"management information system"[TIAB] OR
	"medical informatics"[TIAB] OR
	"medical informatics applications"[TIAB] OR
	"medical informatics application"[TIAB] OR
	"MEDLARS"[TIAB] OR
	"medical literature analysis AND
	retrieval system"[TIAB] OR
	"online systems"[TIAB] OR
	"on line systems"[TIAB] OR
	"on-line system"[TIAB] OR
	"on-line systems"[TIAB] OR
	"online system"[TIAB] OR
	"operating room information systems"[TIAB] OR
	"radiology information systems"[TIAB] OR
	"radiologic information system"[TIAB] OR
	"radiologic information systems"[TIAB] OR
	"radiology information system"[TIAB] OR
	"factual data bank"[TIAB] OR
	"factual data banks"[TIAB] OR
	"factual data base"[TIAB] OR
	"factual databank"[TIAB] OR
	"factual databanks"[TIAB] OR
	"MEDLINE"[TIAB] OR
	"grateful med"[TIAB] OR
	"information storage AND
	retrieval"[TIAB] OR
	"clinical pharmacy information systems"[TIAB] OR
	"automated medical record system"[TIAB] OR
	"automated medical record systems"[TIAB] OR
	"automated medical records system"[TIAB] OR
	"automated medical records systems"[TIAB] OR
	"computerized medical record system"[TIAB] OR
	"computerized medical record systems"[TIAB] OR
	"computerized medical records system"[TIAB] OR
	"computerized medical records systems"[TIAB] OR
	"computerized patient medical records"[TIAB] OR
	"integrated advanced information management systems"[TIAB] OR
	"iaims"[TIAB] OR
	"national practitioner data bank"[TIAB] OR
	"national practitioner databank"[TIAB] OR
	"reminder systems"[TIAB] OR
	"reminder system"[TIAB] OR
	"community networks"[TIAB] OR
	"community network"[TIAB] OR
	"clinical decision support systems"[TIAB] OR
	"conformal radiotherapies"[TIAB] OR
	"conformal radiotherapy"[TIAB] OR
	"computer-aided surgeries"[TIAB] OR
	"computer-aided surgery"[TIAB] OR
	"genetic data bank"[TIAB] OR
	"genetic data banks"[TIAB] OR
	"genetic data base"[TIAB] OR
	"genetic data bases"[TIAB] OR
	"genetic databank"[TIAB] OR
	"genetic databanks"[TIAB] OR
	"PubMed"[TIAB] OR
	"geographic information systems"[TIAB] OR
	"geographic information system"[TIAB] OR
	"digital libraries"[TIAB] OR
	"digital library"[TIAB] OR
	"healthcare common procedure coding system"[TIAB] OR
	"hcpcs"[TIAB] OR
	"MedlinePlus"[TIAB] OR
	"intensity-modulated radiotherapies"[TIAB] OR
	"intensity-modulated radiotherapy"[TIAB] OR
	"knowledge bases"[TIAB] OR
	"knowledge base"[TIAB] OR
	"knowledgebase"[TIAB] OR
	"knowledgebases"[TIAB] OR
	"visible human projects"[TIAB] OR
	"data mining"[TIAB] OR
	"multifactor dimensionality reduction"[TIAB] OR
	"human genome project"[TIAB] OR
	"human genome projects"[TIAB] OR
	"computational biology"[TIAB] OR
	"genomics"[TIAB] OR
	"proteomics"[TIAB] OR
	"systems biology"[TIAB] OR
	"nutrigenomics"[TIAB] OR
	"nutrigenomic"[TIAB] OR
	"nutritional genomics"[TIAB] OR
	"glycomics"[TIAB] OR
	"glycobiology"[TIAB] OR
	"glycomic"[TIAB] OR
	"metabolomics"[TIAB] OR
	"Metabolomic"[TIAB] OR
	"epigenomics"[TIAB] OR
	"epigenomic"[TIAB] OR
	"HapMap project"[TIAB] OR
	"HapMap projects"[TIAB] OR
	"medical informatics"[TIAB] OR
	"public health informatics"[TIAB] OR
	"dental informatics"[TIAB] OR
	"informatics"[TIAB] OR
	"nursing informatics"[TIAB] OR
	"online"[TIAB] OR
	"on line"[TIAB] OR
	"on-line"[TIAB] OR
	"computerized"[TIAB] OR
	"automated medical record system"[TIAB] OR
	"automated medical record systems"[TIAB] OR
	"automated medical records system"[TIAB] OR
	"automated medical records systems"[TIAB] OR
	"computerized medical record system"[TIAB] OR
	"computerized medical record systems"[TIAB] OR
	"computerized medical records system"[TIAB] OR
	"computerized medical records systems"[TIAB] OR
	"computerized patient medical records"[TIAB] OR
	"electronic health records"[TIAB] OR
	"electronic health record"[TIAB] OR
	"electronic medical record"[TIAB] OR
	"electronic medical records"[TIAB] OR
	"telemedicine"[TIAB] OR
	"teleradiology"[TIAB] OR
	"telepathology"[TIAB] OR
	"remote consultation"[TIAB] OR
	"telemonitoring"[TIAB]
)
AND
(	"computer aided surgery"[TIAB] OR
	"computer assisted surgery"[TIAB] OR
	"computer-aided surgeries"[TIAB] OR
	"computer-aided surgery"[TIAB] OR
	"computer-assisted surgeries"[TIAB] OR
	"computer-assisted surgery"[TIAB] OR
	"image guided surgery"[TIAB] OR
	"image-guided surgeries"[TIAB] OR
	"image-guided surgery"[TIAB] OR
	"image enhancement"[TIAB] OR
	"image enhancements"[TIAB] OR
	"image quality enhancement"[TIAB] OR
	"image quality enhancements"[TIAB] OR
	"computer assisted image analysis"[TIAB] OR
	"computer assisted image processing"[TIAB] OR
	"computer-assisted image analyses"[TIAB] OR
	"computer-assisted image analysis"[TIAB] OR
	"computer-assisted image processing"[TIAB] OR
	"image reconstruction"[TIAB] OR
	"image reconstructions"[TIAB] OR
	"radiographic image enhancement"[TIAB] OR
	"digital radiography"[TIAB] OR
	"dual energy scanned projection radiography"[TIAB] OR
	"dual-energy scanned projection radiography"[TIAB] OR
	"3 d image"[TIAB] OR
	"3 d imaging"[TIAB] OR
	"3-d image"[TIAB] OR
	"3-d images"[TIAB] OR
	"3-d imaging"[TIAB] OR
	"computer assisted three dimensional imaging"[TIAB] OR
	"computer-assisted three-dimensional imaging"[TIAB] OR
	"images, 3-d"[TIAB] OR
	"imaging, 3-d"[TIAB] OR
	"three dimensional image"[TIAB] OR
	"three-dimensional image"[TIAB] OR
	"three-dimensional images"[TIAB] OR
	"three-dimensional imaging"[TIAB] OR
	"three-dimensional imagings"[TIAB] OR
	"data compression"[TIAB] OR
	"image compression"[TIAB] OR
	"computer-assisted image interpretation"[TIAB] OR
	"Radionuclide Emission Computed Tomography"[TIAB] OR
	"Radionuclide-Emission Computed Tomography"[TIAB] OR
	"computed radionuclide tomography"[TIAB] OR
	"computed tomographic scintigraphy"[TIAB] OR
	"computerized emission tomography"[TIAB] OR
	"emission computed tomography"[TIAB] OR
	"emission-computed tomography"[TIAB] OR
	"radionuclide computed tomography"[TIAB] OR
	"radionuclide-computed tomography"[TIAB] OR
	"X ray computer assisted tomography"[TIAB] OR
	"X ray computerized tomography"[TIAB] OR
	"X-Ray CT scan"[TIAB] OR
	"X-Ray CT scans"[TIAB] OR
	"X-Ray computer assisted tomography"[TIAB] OR
	"cine ct"[TIAB] OR
	"cine-ct"[TIAB] OR
	"computed X ray tomography"[TIAB] OR
	"computed x-ray tomography"[TIAB] OR
	"ct x ray"[TIAB] OR
	"ct x rays"[TIAB] OR
	"electron beam computed tomography"[TIAB] OR
	"electron beam tomography"[TIAB] OR
	"tomodensitometry"[TIAB] OR
	"transmission computed tomography"[TIAB] OR
	"x ray, ct"[TIAB] OR
	"x-ray computed tomography"[TIAB] OR
	"x-ray computerized tomography"[TIAB] OR
	"Single-Photon emission CT scan"[TIAB] OR
	"Single-Photon emission Computer-Assisted tomography"[TIAB] OR
	"Single-Photon emission computerized tomography"[TIAB] OR
	"single photon emission CT scan"[TIAB] OR
	"single photon emission computed tomography"[TIAB] OR
	"single photon emission computer assisted tomography"[TIAB] OR
	"single photon emission computerized tomography"[TIAB] OR
	"single-photon emission-computed tomography"[TIAB] OR
	"spect"[TIAB] OR
	"computed tomographic colonography"[TIAB] OR
	"ct colonography"[TIAB] OR
	"virtual colonoscopy"[TIAB] OR
	"helical computed tomography"[TIAB] OR
	"helical ct"[TIAB] OR
	"helical cts"[TIAB] OR
	"spiral CAT scan"[TIAB] OR
	"spiral CAT scans"[TIAB] OR
	"spiral CT scan"[TIAB] OR
	"spiral CT scans"[TIAB] OR
	"spiral Computer-Assisted tomography"[TIAB] OR
	"spiral computed tomography"[TIAB] OR
	"spiral computerized tomography"[TIAB] OR
	"spiral ct"[TIAB] OR
	"spiral cts"[TIAB] OR
	"neuronavigation"[TIAB] OR
	"frameless stereotaxy"[TIAB] OR
	"Positron-Emission tomography"[TIAB] OR
	"pet scan"[TIAB] OR
	"pet scans"[TIAB] OR
	"scan, pet"[TIAB] OR
	"Cardiac-Gated SPECT"[TIAB] OR
	"Cardiac-Gated SPECT imaging"[TIAB] OR
	"cardiac gated SPECT"[TIAB] OR
	"cardiac gated SPECT imaging"[TIAB] OR
	"Four-Dimensional computed tomography"[TIAB] OR
	"4D CT"[TIAB] OR
	"4D CT scan"[TIAB] OR
	"4D CT scans"[TIAB] OR
	"4D computed tomography"[TIAB] OR
	"CT scans, 4D"[TIAB] OR
	"Four-Dimensional CT"[TIAB] OR
	"Four-Dimensional CT scan"[TIAB] OR
	"Four-Dimensional CT scans"[TIAB] OR
	"computed tomography, 4D"[TIAB] OR
	"four dimensional CT"[TIAB] OR
	"four dimensional CT scan"[TIAB] OR
	"Positron-Emission Tomography/Computed tomography"[TIAB] OR
	"CT/PET"[TIAB] OR
	"CT/SPECT"[TIAB] OR
	"PET/CT"[TIAB] OR
	"SPECT/CT"[TIAB] OR
	"SPECT/CTs"[TIAB] OR
	"computed Tomography/Positron emission tomography"[TIAB] OR
	"computed Tomography/Positron-Emission tomography"[TIAB] OR
	"hybrid Pet/CT"[TIAB] OR
	"hybrid SPECT/CT"[TIAB] OR
	"integrated PET CT"[TIAB] OR
	"integrated PET/CT"[TIAB] OR
	"integrated SPECT/CT"[TIAB] OR
	"multidetector computed tomography"[TIAB] OR
	"Multidetector-Row computed tomography"[TIAB] OR
	"multidetector row computed tomography"[TIAB] OR
	"multisection computed tomography"[TIAB] OR
	"multislice computed tomography"[TIAB] OR
	"fetal monitoring"[TIAB] OR
	"fetal monitorings"[TIAB] OR
	"patient monitoring"[TIAB] OR
	"physiologic monitoring"[TIAB] OR
	"physiological monitoring"[TIAB] OR
	"telemetry"[TIAB] OR
	"telemetries"[TIAB] OR
	"cardiotocography"[TIAB] OR
	"antepartum ctg"[TIAB] OR
	"cardiotocogram"[TIAB] OR
	"cardiotocograms"[TIAB] OR
	"immune monitoring"[TIAB] OR
	"immunologic monitoring"[TIAB] OR
	"immunological monitoring"[TIAB] OR
	"immunosurveillance"[TIAB] OR
	"radioimmunological monitoring"[TIAB] OR
	"blood glucose self-monitoring"[TIAB] OR
	"blood sugar self monitoring"[TIAB] OR
	"blood sugar self-monitoring"[TIAB] OR
	"home blood glucose monitoring"[TIAB] OR
	"ambulatory electrocardiographic monitoring"[TIAB] OR
	"ambulatory electrocardiography"[TIAB] OR
	"ambulatory electrocardiography monitoring"[TIAB] OR
	"dynamic electrocardiography"[TIAB] OR
	"holter electrocardiography"[TIAB] OR
	"holter monitoring"[TIAB] OR
	"intraoperative monitoring"[TIAB] OR
	"drug monitoring"[TIAB] OR
	"therapeutic drug monitoring"[TIAB] OR
	"polysomnography"[TIAB] OR
	"polysomnographies"[TIAB] OR
	"sleep monitoring"[TIAB] OR
	"somnographies"[TIAB] OR
	"somnography"[TIAB] OR
	"uterine monitoring"[TIAB] OR
	"tocodynamometry"[TIAB] OR
	"tocogram"[TIAB] OR
	"tocograms"[TIAB] OR
	"tocography"[TIAB] OR
	"ambulatory blood pressure monitoring"[TIAB] OR
	"home blood pressure monitoring"[TIAB] OR
	"self blood pressure monitoring"[TIAB] OR
	"ambulatory monitoring"[TIAB] OR
	"outpatient monitoring"[TIAB] OR
	"esophageal pH monitoring"[TIAB] OR
	"ambulatory 24 hour esophageal ph monitoring"[TIAB] OR
	"ambulatory 24-hour esophageal ph monitoring"[TIAB] OR
	"ambulatory esophageal ph monitoring"[TIAB] OR
	"esophageal ph monitorings"[TIAB] OR
	"esophageal ph recording"[TIAB] OR
	"esophageal ph recordings"[TIAB] OR
	"actigraphy"[TIAB] OR
	"remote sensing technology"[TIAB] OR
	"remote sensing technologies"[TIAB] OR
	"fourier analysis"[TIAB] OR
	"analysis, cyclic"[TIAB] OR
	"cyclic analysis"[TIAB] OR
	"fourier series"[TIAB] OR
	"fourier transform"[TIAB] OR
	"computer-assisted signal processing"[TIAB] OR
	"digital signal processing"[TIAB] OR
	"data compression"[TIAB] OR
	"image compression"[TIAB] OR
	"wavelet analysis"[TIAB] OR
	"spatiotemporal wavelet analysis"[TIAB] OR
	"wavelet analyses"[TIAB] OR
	"wavelet signal processing"[TIAB] OR
	"wavelet transform"[TIAB] OR
	"wavelet transforms"[TIAB] OR
	"Signal-To-Noise ratio"[TIAB] OR
	"Signal-To-Noise ratios"[TIAB] OR
	"clinical alarms"[TIAB] OR
	"clinical alarm"[TIAB] OR
	"physiologic monitor alarms"[TIAB] OR
	"biosensing techniques"[TIAB] OR
	"bioprobe"[TIAB] OR
	"bioprobes"[TIAB] OR
	"biosensing technique"[TIAB] OR
	"biosensor"[TIAB] OR
	"biosensors"[TIAB] OR
	"enzyme electrode"[TIAB] OR
	"enzyme electrodes"[TIAB] OR
	"surface plasmon resonance"[TIAB] OR
	"surface plasmon resonances"[TIAB] OR
	"Biofeedbacks"[TIAB] OR
	"biofeedback"[TIAB] OR
	"bogus physiological feedback"[TIAB] OR
	"false physiological feedback"[TIAB] OR
	"myofeedback"[TIAB] OR
	 "Physiological Feedback"[TIAB] OR
	"Physiological Feedbacks"[TIAB] OR
	"biochemical feedback"[TIAB] OR
	"biochemical feedback inhibition"[TIAB] OR
	"biochemical feedbacks"[TIAB] OR
	"biochemical negative feedback"[TIAB] OR
	"biochemical positive feedback"[TIAB] OR
	"psychological feedback"[TIAB] OR
	"audio feedback"[TIAB] OR
	"proprioceptive feedback"[TIAB] OR
	"proprioceptive feedbacks"[TIAB] OR
	"sensorimotor feedback"[TIAB] OR
	"sensorimotor feedbacks"[TIAB] OR
	"sensory feedback"[TIAB] OR
	"sensory feedbacks"[TIAB] OR
	"visual feedback"[TIAB] OR
	"visual feedbacks"[TIAB] OR
	"neurofeedback"[TIAB] OR
	"EEG feedback"[TIAB] OR
	"alpha biofeedback"[TIAB] OR
	"alpha feedback"[TIAB] OR
	"electroencephalography biofeedback"[TIAB] OR
	"electromyography feedback"[TIAB] OR
	"neurofeedbacks"[TIAB] OR
	"automated pattern recognition"[TIAB] OR
	"pattern recognition system"[TIAB] OR
	"pattern recognition systems"[TIAB] OR
	"neural networks (
	Computer)
	"[TIAB] OR
	"connectionist model"[TIAB] OR
	"connectionist models"[TIAB] OR
	"neural network (
	computer)
	"[TIAB] OR
	"neural network model"[TIAB] OR
	"neural network models"[TIAB] OR
	"perceptron"[TIAB] OR
	"perceptrons"[TIAB] OR
	"biometric identification"[TIAB] OR
	"Biometric Authentication"[TIAB] OR
	"automated facial recognition"[TIAB] OR
	"support vector machines"[TIAB] OR
	"support vector machine"[TIAB] OR
	"image enhancement"[TIAB] OR
	"image enhancements"[TIAB] OR
	"image quality enhancement"[TIAB] OR
	"image quality enhancements"[TIAB] OR
	"radiographic image enhancement"[TIAB] OR
	"digital radiography"[TIAB] OR
	"Radionuclide Emission Computed Tomography"[TIAB] OR
	"Radionuclide-Emission Computed Tomography"[TIAB] OR
	"computed radionuclide tomography"[TIAB] OR
	"computed tomographic scintigraphy"[TIAB] OR
	"computerized emission tomography"[TIAB] OR
	"emission computed tomography"[TIAB] OR
	"emission-computed tomography"[TIAB] OR
	"radionuclide computed tomography"[TIAB] OR
	"radionuclide-computed tomography"[TIAB] OR
	"X ray computer assisted tomography"[TIAB] OR
	"X ray computerized tomography"[TIAB] OR
	"X-Ray CT scan"[TIAB] OR
	"X-Ray CT scans"[TIAB] OR
	"X-Ray computer assisted tomography"[TIAB] OR
	"cine ct"[TIAB] OR
	"cine-ct"[TIAB] OR
	"computed X ray tomography"[TIAB] OR
	"computed x-ray tomography"[TIAB] OR
	"ct x ray"[TIAB] OR
	"ct x rays"[TIAB] OR
	"electron beam computed tomography"[TIAB] OR
	"electron beam tomography"[TIAB] OR
	"tomodensitometry"[TIAB] OR
	"transmission computed tomography"[TIAB] OR
	"x ray, ct"[TIAB] OR
	"x-ray computed tomography"[TIAB] OR
	"x-ray computerized tomography"[TIAB] OR
	"Single-Photon emission CT scan"[TIAB] OR
	"Single-Photon emission Computer-Assisted tomography"[TIAB] OR
	"Single-Photon emission computerized tomography"[TIAB] OR
	"single photon emission CT scan"[TIAB] OR
	"single photon emission computed tomography"[TIAB] OR
	"single photon emission computer assisted tomography"[TIAB] OR
	"single photon emission computerized tomography"[TIAB] OR
	"single-photon emission-computed tomography"[TIAB] OR
	"spect"[TIAB] OR
	"dual energy scanned projection radiography"[TIAB] OR
	"dual-energy scanned projection radiography"[TIAB] OR
	"digital subtraction angiography"[TIAB] OR
	"dental digital radiography"[TIAB] OR
	"digora"[TIAB] OR
	"scanora"[TIAB] OR
	"sens a ray"[TIAB] OR
	"sens-a-ray"[TIAB] OR
	"visualix"[TIAB] OR
	"computed tomographic colonography"[TIAB] OR
	"ct colonography"[TIAB] OR
	"virtual colonoscopy"[TIAB] OR
	"helical computed tomography"[TIAB] OR
	"helical ct"[TIAB] OR
	"helical cts"[TIAB] OR
	"spiral CAT scan"[TIAB] OR
	"spiral CAT scans"[TIAB] OR
	"spiral CT scan"[TIAB] OR
	"spiral CT scans"[TIAB] OR
	"spiral Computer-Assisted tomography"[TIAB] OR
	"spiral computed tomography"[TIAB] OR
	"spiral computerized tomography"[TIAB] OR
	"spiral ct"[TIAB] OR
	"spiral cts"[TIAB] OR
	"Positron-Emission tomography"[TIAB] OR
	"pet scan"[TIAB] OR
	"pet scans"[TIAB] OR
	"scan, pet"[TIAB] OR
	"Positron-Emission Tomography/Computed tomography"[TIAB] OR
	"CT/PET"[TIAB] OR
	"CT/SPECT"[TIAB] OR
	"PET/CT"[TIAB] OR
	"SPECT/CT"[TIAB] OR
	"SPECT/CTs"[TIAB] OR
	"computed Tomography/Positron emission tomography"[TIAB] OR
	"computed Tomography/Positron-Emission tomography"[TIAB] OR
	"hybrid Pet/CT"[TIAB] OR
	"hybrid SPECT/CT"[TIAB] OR
	"integrated PET CT"[TIAB] OR
	"integrated PET/CT"[TIAB] OR
	"integrated SPECT/CT"[TIAB] OR
	"multidetector computed tomography"[TIAB] OR
	"Multidetector-Row computed tomography"[TIAB] OR
	"multidetector row computed tomography"[TIAB] OR
	"multisection computed tomography"[TIAB] OR
	"multislice computed tomography"[TIAB] OR
	"transducers"[TIAB] OR
	"transducer"[TIAB] OR
	"pressure transducer"[TIAB] OR
	"pressure transducers"[TIAB]
)
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
q_mesh = q_mesh.replace("\n", " ")
q_text = q_text.replace("\n", " ")

# Définit les éléments de base des requêtes
q_date = '("' + annee + '/01/01"[Date - Publication] : "3000"[Date - Publication] NOT pubstatusaheadofprint)'
q_lang = '("english"[Language])'
q_type = '("journal article"[Publication Type])'

# Version proposée par l'équipe Cismef -- à éviter : exclue les revues uniquement électroniques
#q_date = '("%s/01/01"[PPDAT] : "%s/12/31"[PPDAT])' % (annee, annee)

# Version proposée par l'équipe Cismef -- plus restrictive
#q_type = '("english"[Language] NOT Bibliography[pt] NOT Comment[pt] NOT Editorial[pt] NOT Letter[pt] NOT News[pt] NOT Case Reports[pt] NOT Published Erratum[pt] NOT Historical Article[pt] NOT Legal Cases[pt] NOT legislation[pt])'


q_base = q_date + " AND " + q_lang + " AND " + q_type


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
  commande("--query-pubmed '" + q_mesh + " AND " + q_base + "' --review-mode CURRENT --remove-without-author CURRENT --remove-without-abstract CURRENT --save-as " + fichier("pubmed_mesh"))

  # Effectue la requête en texte libre
  commande("--query-pubmed '" + q_text + " AND " + q_base + "' --review-mode CURRENT --remove-without-author CURRENT --remove-without-abstract CURRENT --save-as " + fichier("pubmed_text"))

  # Retire les références avec mots clefs des résultats de la requête en texte libre
  commande("--remove-with-keyword " + fichier("pubmed_text") + " --review-mode CURRENT --save-as " + fichier("pubmed_text_withoutkeyword"))

  # Réunit les résultats de la requête MeSH avec les résultats de la requête en texte libre sans mot-clef
  commande("--union " + fichier("pubmed_mesh") + " " + fichier("pubmed_text_withoutkeyword") + " --review-mode CURRENT --save-as " + fichier("pubmed"))

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
      commande('--union "' + f + '" ' + fichier("yb") + ' --review-mode CURRENT --save-as "' + f.replace("_partielle_", "_complete_") + '"')
  
