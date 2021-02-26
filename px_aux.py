import os
import pickle
from pycorenlp import StanfordCoreNLP
from smart_open import open as _Open
from datetime import datetime


# a dictionary with Stanford POS terms (currently not used)
POSoptions = {
	"CC": "Coordinating conjunction",
	"CD": "Cardinal number",
	"DT": "Determiner",
	"EX": "Existential there",
	"FW": "Foreign word",
	"IN": "Preposition or subordinating conjunction",
	"JJ": "Adjective",
	"JJR": "Adjective, comparative",
	"JJS":	"Adjective, superlative",
	"LS":	"List item marker",
	"MD":	"Modal",
	"NN":	"Noun, singular or mass",
	"NNS":	"Noun, plural",
	"NP":	"Proper noun, singular",
	"NNPS":	"Proper noun, plural",
	"PDT":	"Predeterminer",
	"POS":	"Possessive ending",
	"PRP":	"Personal pronoun",
	"PRP$":	"Possessive pronoun",
	"RB":	"Adverb",
	"RBR":	"Adverb, comparative",
	"RBS":	"Adverb, superlative",
	"RP":	"Particle",
	"SYM":	"Symbol",
	"TO":	"to",
	"UH":	"Interjection",
	"VB":	"Verb, base form",
	"VBD":	"Verb, past tense",
	"VBG":	"Verb, gerund or present participle",
	"VBN":	"Verb, past participle",
	"VBP":	"Verb, non-3rd person singular present",
	"VBZ":	"Verb, 3rd person singular present",
	"WDT":	"Wh-determiner",
	"WP":	"Wh-pronoun",
	"WP$":	"Possessive wh-pronoun",
	"WRB":	"Wh-adverb"
}

# endpoints of DBpedia (SPARQL queries), DBpedia SpotLight, and WikiData

URL_DB = "https://dbpedia.org/sparql"
#URL_DB_SL_annotate = "http://model.dbpedia-spotlight.org/en/annotate"  # dbpedia spotlight original server
#URL_DB_SL_annotate = "http://api.dbpedia-spotlight.org/en/annotate"  # dbpedia spotlight original server
URL_DB_SL_annotate = "http://gssi.det.uvigo.es:2222/rest/annotate"   # dbpedia spotlight mac pro server
URL_WK = "https://query.wikidata.org/sparql"

# folders and filenames involved in corpus construction

# folder  with training texts
TEXTS_FOLDER = './texts/'
ORIGINAL_TEXTS_FOLDER = './texts/originales'

#DEFAULT_TRAINING_TEXTS = "historical_modify.txt"
DEFAULT_TRAINING_TEXTS = "originales.s.w"

# scripts para recalcular los textos de entrenamiento tras cambiar parámetros
SCRIPT_STEP2 = "./module_processCorpus/S2.py"
SCRIPT_STEP3 = "./module_processCorpus/S3.py"

# variable and function to control if program must print log messages (change to True if argument -m)
FMES = False
def Print (*args):
	if FMES == True:
		lista = list(map(lambda x: str(x), args))
		print(" ".join(lista))
	return

# to save some ASCII content in a file
def saveFile (f, content):
	out = _Open(f, 'w')
	out.write(content)
	out.close()
	return

def appendFile(f, line):
	d = str(datetime.now())
	fd = _Open(f, "a")
	fd.write(d+": "+line+"\n")
	fd.close()



# to highlight in a file the entities contained in its '.p' and so generate its '.p.html'
# type ="s" if filename is '.s', implying that it is necessary highlight the field @surfaceForm
# type ="w" if filename is '.w', implying that it is necessary highlight the field entityName
def getContentMarked (filename, type):

	file = _Open(filename, 'r')
	content = file.read()

	pfilename = filename+".p"

	if not os.path.isfile(pfilename):
		print("Does not exist "+pfilename)
		return content

	pfile = _Open(pfilename, 'rb')
	dics = pickle.load(pfile)

	dicOffsets = dics["byOffset"]

	finalHTMLContent = ""
	currentPosition = 0

	# iteration follows the input order in the dictionary, that is supposed to be the offset order, increasing
	for k in dicOffsets:
		entity = dicOffsets[k]
		text = content[currentPosition:int(k)]
		currentPosition += len(text)

		finalHTMLContent += text.replace("\n", "\n<br>")

		urlEntity = entity["@URI"]

		if type == "s":
			name = entity["@surfaceForm"]
		else:
			name = entity["entityName"]

		finalHTMLContent += "<a href='"+urlEntity+"?lang=en'>"+name+"</a>"
		currentPosition += len(name)

	return finalHTMLContent
