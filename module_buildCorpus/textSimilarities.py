import time
from datetime import datetime

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics.pairwise import cosine_similarity
import spacy

from smart_open import open as _Open

from aux_build import CORPUS_FOLDER as _CORPUS_FOLDER
from ourSimilarityListsFunctions import ourSimilarityListsFunctions as _ourSimilarityListsFunctions
from aux_build import getWikicatComponents as _getWikicatComponents
from aux_build import getSubjectComponents as _getSubjectComponents, filterSimpleWikicats as _filterSimpleWikicats

from px_DB_Manager import getCategoriesInText as _getCategoriesInText
from px_aux import Print as _Print, saveFile as _saveFile,  appendFile as _appendFile

from gensim.models.doc2vec import Doc2Vec
from gensim.parsing.preprocessing import remove_stopwords
from gensim.utils import simple_preprocess

class Doc2VecSimilarity():

	def __init__(self, modelName, original_text):

		self.model = Doc2Vec.load(modelName)


		self.remove_stopwords = True
		if (self.remove_stopwords == True):
			original_text = remove_stopwords(original_text)

		# Use gensim.utils.simple_preprocess for processing:
		# tokenize text to individual words, remove punctuations, set to lowercase, and remove words less than 2 chars or more than 50 chars
		self.original_text_tokens  = simple_preprocess(original_text, max_len=50)

		# Generate a vector from the tokenized original text
		self.original_text_inferred_vector = self.model.infer_vector(self.original_text_tokens, epochs=50)

		# Use our basic math functions instead of sklearn's cosine similarity and euclidean distance
		self.ourMeasures = _ourSimilarityListsFunctions()
		return

	# Doc2Vec similarity: Calculate text similarity based on the trained model

	# text or file parameter must be received
	def doc2VecTextSimilarity (self, candidate_text=None, candidate_file=None):

		if not candidate_text:
			candidate_fileFD = _Open(candidate_file, "r")
			candidate_text = candidate_fileFD.read()

		if (self.remove_stopwords == True):
			candidate_text = remove_stopwords(candidate_text)

		# Use gensim.utils.simple_preprocess for processing:
		# tokenize text to individual words, remove punctuations, set to lowercase, and remove words less than 2 chars or more than 50 chars
		candidate_text_tokens  = simple_preprocess(candidate_text, max_len=50)

		# infer_vector(): Generates a vector from a document
		# The document should be tokenized in the same way the model's training documents were tokenized
		# The function may accept some optional parameters (alpha, min_alpha, epochs, steps)

		# infer_vector(doc_words, alpha=None, min_alpha=None, epochs=None, steps=None)
		# doc_words (list of str) – A document for which the vector representation will be inferred.
		# alpha (float, optional) – The initial learning rate. If unspecified, value from model initialization will be reused.
		# min_alpha (float, optional) – Learning rate will linearly drop to min_alpha over all inference epochs. If unspecified, value from model initialization will be reused.
		# epochs (int, optional) – Number of times to train the new document. Larger values take more time, but may improve quality and run-to-run stability of inferred vectors. If unspecified, the epochs value from model initialization will be reused.
		# steps (int, optional, deprecated) – Previous name for epochs, still available for now for backward compatibility: if epochs is unspecified but steps is, the steps value will be used.

		# Generate a vector from the tokenized candidate text
		candidate_text_inferred_vector = self.model.infer_vector(candidate_text_tokens, epochs=50)

		# The sklearn math functions returns an array with the results
		# We shall keep only one of them, either sklearn or ourSimilarityListsFunctions

		# Measure vectors similarity using cosine similarity
		# cos_similarity = cosine_similarity([original_text_inferred_vector], [text_inferred_vector])

		# Measure vectors similarity using euclidean distance
		# euc_distance = euclidean_distances([original_text_inferred_vector], [text_inferred_vector])

		# Measure vectors similarity using cosine similarity
		cos_similarity = self.ourMeasures.oCosineSimilarity(self.original_text_inferred_vector, candidate_text_inferred_vector)

		# Measure vectors similarity using euclidean distance
		# euc_distance = self.ourMeasures.oEuclideanDistance(self.original_text_inferred_vector, candidate_text_inferred_vector)

		# Measure vectors similarity using manhattan distance
		# man_distance = self.ourMeasures.oManhattanDistance(self.original_text_inferred_vector, candidate_text_inferred_vector)

		return cos_similarity





# other similarities

class textSimilarityFunctions():

	# Load the nlp large package for spacy metrics
	# It is better to load it once at the class initialization, to save loading time each time it is used
	nlp = spacy.load('en_core_web_lg')

	def __init__(self, original_text, original_text_wikicats, original_text_subjects, logFilename):
		self.logFilename = logFilename
		self.original_text = original_text
		self.original_text_wikicats = original_text_wikicats
		self.pairs_original_text_wikicats = list(map(lambda x: (x, _getWikicatComponents(x)), original_text_wikicats))
		self.original_text_subjects = original_text_subjects
		self.pairs_original_text_subjects = list(map(lambda x: (x, _getSubjectComponents(x)), original_text_subjects))

		# Tokenize original text based on the spacy package
		self.original_text_doc_tokens_without_stopwords = self.nlp(self.remove_spacy_stopwords(original_text))  # this could be done only once, at the object creation stage
		self.original_text_doc_tokens = self.nlp(original_text)

		self.oMeasures = _ourSimilarityListsFunctions()   # Create an object from the ourSimilarityListsFunctions class
		return


	# token.text , token.lemma_ , token.pos_ , token.is_punct, token.dep_
	def remove_spacy_stopwords(self, text):
		doc = self.nlp(text.lower()) # return a list of tokens. Each token contains data about a word
		# words = [token.text for token in doc if (token.lemma_ != '-PRON-') and (token.text not in self.nlp.Defaults.stop_words) and (not token.is_punct)]
		words = [token.text for token in doc if (token.text not in self.nlp.Defaults.stop_words) and (not token.is_punct)]
		return " ".join(words)

	#############################################################################################################################################

	# spaCy similarity: Takes two pieces of text and returns the text similarity based on spaCy

	def spacyTextSimilarity (self, candidate_text=None, candidate_file=None):
		if not candidate_text:
			candidate_fileFD = _Open(candidate_file, "r")
			candidate_text = candidate_fileFD.read()

		# Tokenize candidate text based on the spacy package
		candidate_text_doc_tokens_without_stopwords = self.nlp(self.remove_spacy_stopwords(candidate_text))

		# Measure both texts similarity with spaCy method and return it
		return self.original_text_doc_tokens_without_stopwords.similarity(candidate_text_doc_tokens_without_stopwords)



	def compute_similarity_without_stopwords_punct(self, doc1, doc2):
		import numpy as np

		vector1 = np.zeros(300)
		for token in doc1:
			if (token.text not in self.nlp.Defaults.stop_words) and (not token.is_punct):
				vector1 = vector1 + token.vector
		vector1 = np.divide(vector1, len(doc1))

		vector2 = np.zeros(300)
		for token in doc2:
			if (token.text not in self.nlp.Defaults.stop_words) and (not token.is_punct):
				vector2 = vector2 + token.vector
		vector2 = np.divide(vector2, len(doc2))

		return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))


	def spacyTextSimilarity_calc (self, candidate_text=None, candidate_file=None):
		if not candidate_text:
			candidate_fileFD = _Open(candidate_file, "r")
			candidate_text = candidate_fileFD.read()

		candidate_text_doc_tokens = self.nlp(candidate_text)

		return self.compute_similarity_without_stopwords_punct(self.original_text_doc_tokens, candidate_text_doc_tokens)




#############################################################################################################################################

	# Shared Wikicats Jaccard similarity between two texts
	# it measures shared matching between wikicats (similarity among components of two wikicat names)
	def sharedWikicatsJaccardSimilarity (self, fileNameCandidateWikicats):

		try:  # try to read candidate text wikicats from local DB
			with _Open(fileNameCandidateWikicats) as fp:
				candidate_text_wikicats = fp.read().splitlines()
		except Exception as e:
			_Print("Candidate wikicats file not found in local DB:", fileNameCandidateWikicats)
			_appendFile(self.logFilename, "ERROR sharedWikicatsJaccardSimilarity(): Candidate ikicats file not found: "+fileNameCandidateWikicats+" "+str(e))
			return -1

		if len(candidate_text_wikicats) == 0:
			return 0

		# the wikicats lists for both texts are now available

		try:
			# change every candidate wikicat by the pair (wikicat, list of wikicat components)
			pairs_candidate_text_wikicats = list(map(lambda x: (x, _getWikicatComponents(x)), candidate_text_wikicats))

			numContributions=0  # number of matches - contributions with some similarity
			sum_sims = 0  # to aggregate similarities contributions

			for (wko,wkocl) in self.pairs_original_text_wikicats:
				for (wkc,wkccl) in pairs_candidate_text_wikicats:
					min_long = min(len(wkocl), len(wkccl)) # length of the shorter wikicat

					if (min_long < 3):  # both wikicats must have at least 3 components
						continue

					intersection_cardinality = len(set.intersection(set(wkocl), set(wkccl)))

					# for the shorter wikicat, we require at most 1 component not to be included in the larger wikicat
					if (intersection_cardinality < (min_long - 1)):
						continue

					# this fullfils the requirements: it is a contribution

					numContributions += 1
					union_cardinality = len(set.union(set(wkocl), set(wkccl)))
					component_jaccard_similarity = intersection_cardinality/float(union_cardinality)
					sum_sims += component_jaccard_similarity
					_Print(numContributions, "->", wko, ",", wkc, component_jaccard_similarity)

			if numContributions == 0: # no intersection at all
				return 0

			wikicats_jaccard_similarity = sum_sims / numContributions
		except Exception as e:
			_Print("ERROR sharedWikicatsJaccardSimilarity(): Exception while computing Jaccard wikicats similarity: "+str(e))
			_appendFile(self.logFilename, "ERROR sharedWikicatsJaccardSimilarity(): Exception while computing Jaccard wikicats similarity: "+str(e))
			return -1

		if wikicats_jaccard_similarity > 1:
			_Print("Candidate with wikicats similarity > 1:", fileNameCandidateWikicats, sum_sims, denominator, wikicats_jaccard_similarity)
			_appendFile(self.logFilename, "ERROR sharedWikicatsJaccardSimilarity(): similarity > 1")
			return -1

		return wikicats_jaccard_similarity





	# Shared subjects similarity between two texts
	# it measures shared matching between subjects (similarity among components of two subjects names)
	def sharedSubjectsJaccardSimilarity (self, fileNameCandidateSubjects):

		try:  # try to read candidate text subjects from local DB
			with _Open(fileNameCandidateSubjects) as fp:
				candidate_text_subjects = fp.read().splitlines()
		except Exception as e:
			_Print("Candidate subjects file not found in local DB:", fileNameCandidateSubjects)
			_appendFile(self.logFilename, "ERROR sharedSubjectsJaccardSimilarity(): Candidate subjects file not found: "+fileNameCandidateSubjects+" "+str(e))
			return -1

		if len(candidate_text_subjects) == 0:
			return 0

		# the subjects lists for both texts are now available
		subjects_jaccard_similarity = 0

		try:
			# change every candidate subject by the pair (subject, list of subject components)
			pairs_candidate_text_subjects = list(map(lambda x: (x, _getSubjectComponents(x)), candidate_text_subjects))

			numContributions=0  # number of matches - contributions with some similarity
			sum_sims = 0  # to aggregate similarities contributions

			for (sbo,sbocl) in self.pairs_original_text_subjects:
				for (sbc,sbccl) in pairs_candidate_text_subjects:
					min_long = min(len(sbocl), len(sbccl)) # length of the shorter subject

					if (min_long < 3):  # both subjects must have at least 3 components
						continue

					intersection_cardinality = len(set.intersection(set(sbocl), set(sbccl)))

					# for the shorter subject, we require at most 1 component not to be included in the larger subject
					if (intersection_cardinality < (min_long - 1)):
						continue

					# this fulfills the requirements: it is a contribution

					numContributions += 1
					union_cardinality = len(set.union(set(sbocl), set(sbccl)))
					component_jaccard_similarity = intersection_cardinality/float(union_cardinality)
					sum_sims += component_jaccard_similarity
					_Print(numContributions, "->", sbo, ",", sbc, component_jaccard_similarity)

					if numContributions == 0: # no intersection at all
						return 0

					subjects_jaccard_similarity = sum_sims / numContributions
		except Exception as e:
			_Print("ERROR sharedSubjectsJaccardSimilarity(): Exception while computing Jaccard subjects similarity: "+str(e))
			_appendFile(self.logFilename, "ERROR sharedSubjectsJaccardSimilarity(): Exception while computing Jaccard subjects similarity: "+str(e))
			return -1

		if subjects_jaccard_similarity > 1:
			_Print("Candidate with subjects similarity > 1:", fileNameCandidateSubjects, sum_sims, denominator, subjects_jaccard_similarity)
			_appendFile(self.logFilename, "ERROR sharedSubjectsJaccardSimilarity(): similarity > 1")
			return -1

		return subjects_jaccard_similarity




	#############################################################################################################################################

	# Full Wikicats jaccard similarity between the original text and a new one, using ourSimilarityListsFunctions
	# the original text wikicats were received in object creation phase
	# it measures complete matching between wikicats
	def fullWikicatsJaccardSimilarity (self, fileNameCandidateWikicats):

		try:  # try to read candidate text wikicats from local DB
			with _Open(fileNameCandidateWikicats) as fp:
				candidate_text_wikicats = fp.read().splitlines()
		except Exception as e:
			_Print("Candidate wikicats file not found in local DB:", fileNameCandidateWikicats)
			_appendFile(self.logFilename, "ERROR fullWikicatsJaccardSimilarity(): Candidate wikicats file not found: "+fileNameCandidateWikicats+" "+str(e))
			return -1

		if len(self.original_text_wikicats) == 0 or len(candidate_text_wikicats) == 0:
			return 0

		wikicats_jaccard_similarity = self.oMeasures.oJaccardSimilarity(self.original_text_wikicats, candidate_text_wikicats)

		return wikicats_jaccard_similarity



	# Full Subjects jaccard similarity between the original text and a new one, using ourSimilarityListsFunctions
	# the original text subjects were received in object creation phase
	# it measures complete matching between subjects
	def fullSubjectsJaccardSimilarity (self, fileNameCandidateSubjects):

		try:  # try to read candidate text subjects from local DB
			with _Open(fileNameCandidateSubjects) as fp:
				candidate_text_subjects = fp.read().splitlines()
		except Exception as e:
			_Print("Candidate subjects file not found in local DB:", fileNameCandidateSubjects)
			_appendFile(self.logFilename, "ERROR fullSubjectsJaccardSimilarity(): Candidate subjects file not found: "+fileNameCandidateSubjects+" "+str(e))
			return -1

		if len(self.original_text_subjects) == 0 or len(candidate_text_subjects) == 0:
			return 0

		subjects_jaccard_similarity = self.oMeasures.oJaccardSimilarity(self.original_text_subjects, candidate_text_subjects)

		return subjects_jaccard_similarity



	#############################################################################################################################################

	# Euclidean similarity, using SKLEARN

	def euclideanTextSimilarity (self, candidate_text=None, candidate_file=None):
		try:
			if not candidate_text:
				candidate_fileFD = _Open(candidate_file, "r")
				candidate_text = candidate_fileFD.read()

			list_of_text = [self.original_text, candidate_text]   # Create a list of documents of the original text and the new candidate text

			vectorizer = CountVectorizer()   # Create a CountVectorizer Object

			# Transform arbitrary data into numerical features
			# Description: remove stopwords, tokenize the text, create a vocabulary from distinct words, map each document to vocabulary (tokens)
			features = vectorizer.fit_transform(list_of_text).todense()

			# Measure the euclidean distance, returns an array with the euclidean distance
			euclideanDistances = euclidean_distances(features[0], features[1])

			euclidean_distance = euclideanDistances[0][0]   # between 0 and N, 0 is the best

			euclidean_similarity = 1 / (1 + euclidean_distance) # between 0 and 1, 1 is the best
		except Exception as e:
			print("** ERROR euclideanTextSimilarity:", str(e))
			raise e

		return euclidean_similarity
