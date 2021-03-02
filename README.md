# GSSI Plethora
This is a repository for the code of the project Plethora

module_buildCorpus - subproject to build a corpus of ad hoc texts selected from Internet

module_processCorpus - subproject to process original corpus files downloaded from Internet

module_train - subproject to train W2V and D2V neural networks

module_buildModel - subproject with a tool to automatize the training of Word2Vec and Doc2Vec models


REQUIREMENTS

1. This project has been developed and tested with Pyhton 3.7

2. The following packages are used (with the indicated version number).

smart_open==4.1.0

Flask==1.1.2

requests-futures==0.9.9

numpy==1.19.5

requests==2.21.0

gensim==3.8.3

nltk==3.4.5

bs4==0.0.1

spacy==2.1.4

scikit-learn==0.21.2

To install a package (if you have pip3 installed):

pip3 install package (to install a new package)

or

pip3 install --upgrade package (to upgrade an existing package)

3. An english model is needed to compute similarities with spaCy. You must downloaded with the following command:

python3 -m spacy download en_core_web_lg
