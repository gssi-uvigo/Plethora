
# This script receives as parameter a file (.s) or a folder and, for each file, it generate other (.s.p) with the entities identified in DB-SL
# input: a .s file or a folder
#			if folder, it is supposed to be the CORPUS base folder, and folder/files_s_p_w must exist, and all '.s' files in folder/files_s_p_w will be processed
# outputs: several files will be created in folder/files_s_p_w
#			a file with '.s.p' extension for each processed file
#			a .s.p.html file with the entities marked in green

# IMPORTANT: the identification of entities in DB-SL is done with parameters 'confidence=0.5' and 'support=1'

# select ?uri ?label (group_concat(?subject; separator=";") as ?subjects) (group_concat(?type; separator=";") as ?types)
# where {

# VALUES ?uri {<http://dbpedia.org/resource/Hera> <http://dbpedia.org/resource/Eurotas> <http://dbpedia.org/resource/Dodona> <http://dbpedia.org/resource/Determinism> <http://dbpedia.org/resource/Julius_Caesar>} .
# ?uri rdfs:label ?label; rdf:type ?type .
# ?uri dct:subject ?subject .
# FILTER(regex(?type,'http://dbpedia.org/ontology|http://dbpedia.org/class/yago')) . FILTER(lang(?label) = 'en')} group by ?label ?uri

# these functions can be used with script S2.py (to process a file or a folder)

import os
import pickle
import json
import requests
import time
import sys
import glob
sys.path.append('../')  # to search for imported files in the parent folder


from px_aux import URL_DB_SL_annotate as _URL_DB_SL_annotate, getContentMarked as _getContentMarked, Print as _Print, saveFile as _saveFile
from px_DB_Manager import DBManager as _DBManager

from aux_process import SPW_FOLDER as _SPW_FOLDER


# to process a file and return dictionaries with the entities detected and filtered
def findEntities (filename, confPar, supPar):

	content_file = open(filename, 'r')
	content = content_file.read()

	# DB-SL is queried for teh preferred entity for each candidate detected in the file
	# see section 6.4 of the document describing the architecture for the formats of request and answer
	dbsl_response = requests.post(_URL_DB_SL_annotate, data={"text": content, "confidence": confPar, "support": supPar}, headers={"accept": "application/json", "content-type": "application/x-www-form-urlencoded"})

	if (dbsl_response.status_code != 200):
		raise Exception("DBpedia SpotLight connection error: "+_URL_DB_SL_annotate)

	# the previous one is a synchronous call, anly returns after receiving the answer, that will be passed now to JSON
	try:
		dbsl_json = dbsl_response.json()
		dbsl_json["Resources"] # if no entity is detected an exception is raised
	except:
		_Print("No entity detected in the file")
		return {'byUri': {}, 'byType': {}, 'byOffset': {}}

	_Print("Detected", len(dbsl_json["Resources"]), "entities")

	# create class  _DBManager to parse results
	dbpediaManager = _DBManager()
	dbpediaManager.scanEntities(dbsl_json)
	allDicts = dbpediaManager.getDictionaries()

	byUri = allDicts["byUri"]
	byType = allDicts["byType"]
	byOffset = allDicts["byOffset"]
	byuriplana = [item for sublist in byUri.values() for item in sublist]
	_Print(len(byUri.keys()), len(byuriplana), len(byType.keys()), len(byOffset.keys()))

	return allDicts


# to process a file and save results
# input 'source' .s file
# output 'source.p' result file and 'source.p.html' with entities highlighted
def processS2File(source, confidence=0.5, support=1):
	if not source.endswith(".s"):
		message = source+" has not '.s' extension"
		print(message)
		raise Exception(message)

	if not os.path.exists(source):
		message = source+" not found!"
		print(message)
		raise Exception(message)

	_Print("Processing file "+source+"...\n")
	try:
		entities = findEntities(source, confidence, support)
		pickle.dump(entities, open(source+".p", "wb" ))

		highlightedContent = _getContentMarked(source, 's')
		_saveFile(source+".p.html", highlightedContent)
	except Exception as e:
		message = "Problem detecting entities: "+str(e)
		print(message)
		raise Exception(message)

	return 0


# to process a folder and save results.
# input: 'source' folder
# output: for each .s file in source/files_s_p_w, both '.s.p' result file and '.s.p.html' with entities highlighted
def processS2Folder (foldername, confidence=0.5, support=1):

	if not foldername.endswith("/"):
		foldername = foldername+"/"

	spw_folder = foldername + _SPW_FOLDER
	if not os.path.exists(spw_folder):
		print(spw_folder, "not found!")
		return -1

	print("\nS2: Processing folder "+foldername)

	listFullFilenamesS = sorted(glob.glob(spw_folder+"*.s"))

	numProcessed = processS2List(listFullFilenamesS, confidence=0.5, support=1)

	return numProcessed




# to process a list of .s files and save results.
# input: list of .s files to process
# output: for each .s file in list, both '.s.p' result file and '.s.p.html' with entities highlighted are saved
def processS2List(fileList, confidence=0.5, support=1):

	print("\nS2: Processing list of .s files")

	numFiles = 0
	numProcessed = 0

	for sFullFilename in fileList:
		if not sFullFilename.endswith(".s"):
			continue

		numFiles += 1
		_Print(numFiles, " S2: Processing file ", sFullFilename)

		if os.path.exists(sFullFilename+".p"):
			_Print("P file already available in local DB: "+sFullFilename+".p")
			continue

		_Print("Creating .p file: "+sFullFilename+".p")

		try:
			entities = findEntities(sFullFilename, confidence, support)
		except Exception as ex:
			print("processS2List: findEntities raised exception ("+str(ex)+")! Could not process ", sFullFilename)
			input("Continue?")
			continue

		time.sleep(2)
		pickle.dump(entities, open(sFullFilename+".p", "wb" ))

		highlightedContent = _getContentMarked(sFullFilename, "s")
		_saveFile(sFullFilename+".p.html", highlightedContent)

		numProcessed += 1

	return numProcessed
