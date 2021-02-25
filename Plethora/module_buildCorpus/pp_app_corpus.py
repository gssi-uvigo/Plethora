# this is the main program of the corpus builder tool
# it can be launched standalone, using a Flask server started here and calling localhost:5000/corpus
# or from the main tool with its Flask server, selecting the corresponding option

# argument '-d' makes button labels in the interface to show calls (routes) associated in the server,
# to be easier to understand the flow among interface and python server modules

# it depends on px_DB_Manager and px_aux modules of the main tool, as well as the

import sys
from smart_open import open as _Open

# this program has been launched in the Plethora/buildCorpus folder
# this is to search px_DB_Manager and px_aux in the Plethora folder
# such modules are not needed here, but in routesCorpus and routesCorpus2 modules loaded next
sys.path.append('../')

# functions to be executed when Flask requests are received
from routesCorpus import doPh1getWikicatsFromText as _doPh1getWikicatsFromText, doPh2getUrlsCandidateFiles as _doPh2getUrlsCandidateFiles
from routesCorpus import getWikicatUrls as _getWikicatUrls
from routesCorpus import doPh3downloadCandidateTexts as _doPh3downloadCandidateTexts, doPh4identifyWikicats as _doPh4identifyWikicats
from routesCorpus import doPh5computeSimilarities as _doPh5computeSimilarities, doPh6trainD2V as _doPh6trainD2V, doPh7reviewCorpus as _doPh7reviewCorpus
from aux_build import INITIAL_TEXT as _INITIAL_TEXT
import aux_build
import px_aux


# load the initial text shown at the beginning of the interface
initialTextFile = _Open(_INITIAL_TEXT, "r")
initialText = initialTextFile.read()

FLAB = False	# to control if buttons must show additional label details (change to True if argument -l)

# the following is only executed if this is the main program, that is, if we launch the corpus tool directly from the 'buildCorpus' folder
# not executed if we launch the corpus tool from the main tool, as the 'app' object is already available from the main tool
if __name__ == '__main__':
	import os

	# Flask is a module to launch a web server. It permits to map a function for each request template
	from flask import Flask, render_template, request, flash, json, jsonify, redirect, url_for, send_from_directory

	# templates dir is shared with the main tool because it is possible for this tool to be called from the main one
	template_dir = os.path.abspath('../templates')
	# Create the Flask app to manage the HTTP request
	app = Flask(__name__, template_folder=template_dir)

	# only to serve style.js from the js folder of the main tool (also done in the main tool, so only necessary if standalone)
	@app.route('/css/<path:path>')
	def send_js(path):
		return send_from_directory('../css', path)

	arguments = range(len(sys.argv))
	for argument in arguments:
		if (argument == 0):
			continue

		if sys.argv[argument] == "-l":   # argument '-l' prints button labels with routes associated
			FLAB = True
			print("Flag labels activated!!!")
		if sys.argv[argument] == "-s":   # argument '-s' forces stop after every phase
			aux_build.FSTOP = True
			print("Flag stop activated!!!")
		if sys.argv[argument] == "-m":   # argument '-m' print enhanced log messages
			px_aux.FMES = True
			print("Flag messages activated!!!")

# Flask routes binding for interface requests (not done in the main tool, so always necessary)
app.add_url_rule("/doPh1getWikicatsFromText", "doPh1getWikicatsFromText", _doPh1getWikicatsFromText, methods=["POST"])  # to send a text and request the wikicats in it
app.add_url_rule("/doPh2getUrlsCandidateFiles", "doPh2getUrlsCandidateFiles", _doPh2getUrlsCandidateFiles, methods=["POST"])  # to request the finding of the candidate files URLs
app.add_url_rule("/doPh3downloadCandidateTexts", "doPh3downloadCandidateTexts", _doPh3downloadCandidateTexts, methods=["POST"])  # to request the downloading of the candidate files
app.add_url_rule("/doPh4identifyWikicats", "doPh4identifyWikicats", _doPh4identifyWikicats, methods=["POST"])  # to request the identification of wikicats in candidate files
app.add_url_rule("/doPh5computeSimilarities", "doPh5computeSimilarities", _doPh5computeSimilarities, methods=["POST"])  # to request to compute similarities for candidate texts
app.add_url_rule("/doPh6trainD2V", "doPh6trainD2V", _doPh6trainD2V, methods=["POST"])  # to request to train the Doc2Vec network
app.add_url_rule("/doPh7reviewCorpus", "doPh7reviewCorpus", _doPh7reviewCorpus, methods=["POST"])  # to request to review the corpus with Doc2Vec
app.add_url_rule("/getWikicatUrls", "getWikicatUrls", _getWikicatUrls, methods=["GET"])  # to send the Urls derived from a wikicat

# this is the main entry point of the corpus builder tool (not done in the main tool, so always necessary)
@app.route('/corpus',  methods=["GET", "POST"])
def hello_world():
	return render_template('./template_corpus.html', parDefaultText=initialText, parDebug=FLAB) # parDebug=True prints button labels with routes associated


# start web server listening port 5060 by default if we have launched the corpus tool standalone

# the following is only executed if this is the main program, that is, if we launch the corpus tool directly from the 'buildCorpus' folder
# not executed if we launch the corpus tool from the main tool, as the 'app' object is already available from the main tool
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5060, threaded=True)
