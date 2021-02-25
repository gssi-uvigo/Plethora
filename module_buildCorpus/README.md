This is the tool to build the ad hoc corpus.

It depends on the following modules of the main tool: px_aux, px_DB_Manager

How to use it:

- launch python3 pp_app_corpus.py   (-d for help understanding the flow, only developers)

- open in browser localhost:5060/corpus

Input: a text  (initialText.txt)

It creates a KORPUS folder in user home (configure in aux_build.py) to read/store results:
- Identifies DB entities in text
- Shows their wikicats and asks the user for selection
- Finds the URLs that have associated such wikicats
- Fetchs such URLs and clean them (remove mark up)
- Studies different similarities between each candidate and the initial initialText
- Reports about the best similarity

It uses D2V for assessing similarity, with a model pretrained with a generic corpus (AP)

- This software uses the DBpedia SpotLight (endpoint indicated in ../ps_aux.py, that could be:

1. Well-known DBpedia Spotlight endpoint
URL_DB_SL_annotate = "http://model.dbpedia-spotlight.org/en/annotate"

2. Our copy of DBpedia SpotLight. For example, running in gssi.det.uvigo.es
URL_DB_SL_annotate = "http://gssi.det.uvigo.es:2222/rest/annotate"
