
# This script contains functions to process one or several files to detect pairs "NAME romanNumber" (event) and proceed to the following changes
# 1. change future occurrences of NAME without romanNumber to "NAME romanNumber" (where 'romanNumber' is the last event detected for NAME)
# 2. change any occurrence of NAME previous to a unique event from NAME (NAME happens only once with a romanNumber) to "NAME romanNumber"  (being romanNumber the one of the future event)
#
# input: a file or folder received as parameter
#			if folder, the subfolder folder/files_txt/ must exist, and all '.txt' files in folder/files_txt will be processed
# outputs:	for each processed file, several files will be created
#			a file with the original name and the suffix '.s', for every processed file
#			a .s.html' file with the changes in green, for every processed file (just to easily read changes)
#           a .s.nr with report about studied changes finally not done (for debugging)
#           a .s.nr.html with HTML report about studied changes finally not done (for debugging)

# every file is read twice and stored in memory (could be a problem for large files)

# the actual job of changing contents is done by the external processContent() function, shared with the main project

# these functions can be used with scripts S1.py (to process a file or a folder) and S1L.py (to process a list of files)

import os
import time
import sys
import glob
sys.path.append('../')  # to search for imported files in the parent folder

from px_aux import Print as _Print, saveFile as _saveFile
from px_aux_add_suffix import processContent as _processContent   # this is the function that actually changes the content

from aux_process import  TXT_FOLDER as _TXT_FOLDER, SPW_FOLDER as _SPW_FOLDER


# processFile: to process a file (parameter 'filename') and store the result as filename.s
def processS1File (filename):
	with open(filename, 'r') as content_file:
		content = content_file.read()  # the original content of the file is read

		# to process a textual content
		# returns a 4-tupla (text changed, html text with highlighted changes, no changes report, HTML no changes report)
		result = _processContent(content)

		if result == None:
			_Print("no change")
			_saveFile(filename+".s", content)    # store result without changes in a file with '.s' extension
			_saveFile(filename+".s.html", content)  # store result without changes in an HTML report file
		else:
			_Print("some changes")
			_saveFile(filename+".s", result[0])     # store result with changes in a file with '.s' extension
			_saveFile(filename+".s.html", result[1])   # store result with changes in an HTML report file

			# store results reporting studied changes finally not done
			if result[2] != "":
				_saveFile(filename+".s.nr", result[2])
				_saveFile(filename+".s.nr.html", result[3])
	return




# it receives the CORPUS base folder for input and output files
# it must have a 'files_txt' folder inside with the input .txt files
# outputs:	for each processed file, several files will be created in folder/files_s_p_w
def processS1Folder (foldername):

	if not foldername.endswith("/"):
		foldername = foldername+"/"

	txt_folder = foldername + _TXT_FOLDER  # subfolder with the input .txt files
	# check that the subfolder files_txt/  exists
	if not os.path.exists(txt_folder):
		print("processS1Folder:", txt_folder, "not found!")
		return -1

	listFullFilenamesTXT = sorted(glob.glob(txt_folder+"*.txt"))

	numProcessed = processS1List (foldername, listFullFilenamesTXT)

	return numProcessed



# it receives a list with the input filenames of the the CORPUS
# it receives the CORPUS base folder (FOLDER) for output files
# outputs:	for each processed file, several files will be created in FOLDER/files_s_p_w
def processS1List (foldername, fileList):

	print("\nS1: Processing list of .txt files to folder "+foldername)

	if not foldername.endswith("/"):
		foldername = foldername+"/"

	if not os.path.exists(foldername):  # create CORPUS folder for output files if does not exist
		os.makedirs(foldername)

	# create the folder to store output files if does not exist
	spw_folder = foldername + _SPW_FOLDER
	if not os.path.exists(spw_folder):
		os.makedirs(spw_folder)

	numFiles = 0
	numProcessed = 0
	for filename in fileList:
		numFiles += 1
		_Print(numFiles, " S1: Processing file ", filename)

		final_name = filename[(1+filename.rfind("/")):]
		basename = spw_folder+final_name

		if os.path.exists(basename+".s"):  # this is case insensitive
			_Print("S file already available in local DB: "+basename+".s")
			continue

		_Print("Creating .s file: "+basename+".s")

		with open(filename, 'r') as content_file:
			content = content_file.read()  # the original content of file is read

			# to process a textual content
			# returns a tupla (text changed, html text with highlighted changes, no changes report, HTML no changes report)
			result = _processContent(content)

			if result == None:
				_Print("no change, saving .s", basename+".s")
				_saveFile(basename+".s", content)    # store result without changes in a file with '.s' extension
				_saveFile(basename+".s.html", content)  # store result without changes in an HTML report file
			else:
				_Print("changes, saving .s", basename+".s")
				_saveFile(basename+".s", result[0])     # store result with changes in a file with '.s' extension
				_saveFile(basename+".s.html", result[1])   # store result with changes in an HTML report file

				# store results reporting studied changes finally not done
				if result[2] != "":
					_saveFile(basename+".s.nr", result[2])
					_saveFile(basename+".s.nr.html", result[3])

		numProcessed += 1

	return numProcessed




# to aggregate in a global file 'foldername/foldername.s' (foldername received as parameter) ) all .s files in a folder 'foldername/files_s_p_w'
# files are joined following alphabetic order of the file names
def generateAgregate (foldername):
	print("\nCreating aggregation "+foldername+".s...")
	numFiles = 0
	global_content = ""

	spw_folder = foldername + _SPW_FOLDER

	if not os.path.exists(spw_folder):
		print(spw_folder, "not found!")
		return -1

	for filename in sorted(os.listdir(spw_folder)):   # files are ordered by alphabetic file name
		if not filename.endswith(".s"):   # only .s files are joined
			continue
		else:
			numFiles += 1
			_Print(numFiles, "====================", filename)
			with open(spw_folder+"/"+filename, 'r') as content_file:
				content = content_file.read()
				global_content += content

	_saveFile(foldername+"/"+foldername+".s", global_content)
	return

# end of aux functions
