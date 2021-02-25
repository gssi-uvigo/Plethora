This is the tool to build the ad hoc corpus.

Depends on the following modules of the main tool: px_aux, px_DB_Manager

How to use it:

- launch python3 pp_app_corpus.py   (-d for easier understanding of flow, only developers)

- open in browser localhost:5060/corpus

Input: a text  (initialText.txt)

It creates a KORPUS folder (inside the one of the tool) with results:
- Identifies DB entities in text
- Shows their wikicats and asks the user for selection
- Finds the URLs that have associated such wikicats
- Fetchs such URLs and clean them (remove mark up)
- Assesses if each text is related to the initial one. If related, adds it to the corpus

It uses D2V for assessing relatedness, with a model trained with an initial corpus


- This software uses the DBpedia SpotLight, located in a remote server indicated in ../ps_aux.py, that could be:

1. Well-known DBpedia Spotlight endpoint

URL_DB_SL_annotate = "http://model.dbpedia-spotlight.org/en/annotate"

2. Our copy of DBpedia SpotLight. For example, running in gssi.det.uvigo.es

URL_DB_SL_annotate = "http://gssi.det.uvigo.es:2222/rest/annotate"

IMPORTANT: when running in gssi.det.uvigo.es, the service must be
URL_DB_SL_annotate = "http://localhost:2222/rest/annotate"


To run such server, we must
- install docker
- run the docker daemon (start docker app)
- pull the dbpedia spotlight image (sure?)
- and run

docker run -d -e JAVA_OPTS='-Xmx16g' -p 2222:80 dbpedia/spotlight-english spotlight.sh

it takes some time to start

You can also run

docker run -i -e JAVA_OPTS='-Xmx16g' -p 2222:80 dbpedia/spotlight-english spotlight.sh

to see when the service is ready
