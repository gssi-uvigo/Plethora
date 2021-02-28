This is the tool to build the ad hoc corpus.
Please, read the README.md file in root folder for requirements about the python installation context

How to use it:

- launch backend
python3 pp_app_corpus.py

- open frontend in browser
localhost:5060/corpus

- Input: a text  (default in initialText.txt in this folder)

It creates a KORPUS folder in user home (configure in aux_build.py) to read/store results:
- Identifies DB entities in text
- Shows their wikicats and asks the user for selection
- Finds the URLs that have associated such wikicats
- Fetchs such URLs and clean them (remove mark up)
- Studies different similarities between each candidate and the initial initialText
- Reports about the best similarity

IMPORTANT!!

1.
This software stores data in a repository folder named KORPUS, configurable in file aux_build.py
CORPUS_FOLDER = os.getenv('HOME') + "/KORPUS/"

2.
This software uses Doc2Vec for assessing similarity, with a model pretrained with a generic corpus (AP).
This pretrained model is not distributed with this software (3 files -700 MB- quite large for GitHub)
Those files can be downloaded from https://github.com/shreyanse081/gensim_Doc-Word2Vec

3.
This software uses the DBpedia SpotLight (endpoint configurable in file ../ps_aux.py, that could be:

A. Well-known DBpedia Spotlight endpoint (not always available)
URL_DB_SL_annotate = "http://model.dbpedia-spotlight.org/en/annotate"

B. Our organization local copy of DBpedia SpotLight (default), running at gssi.det.uvigo.es
URL_DB_SL_annotate = "http://gssi.det.uvigo.es:2222/rest/annotate"
