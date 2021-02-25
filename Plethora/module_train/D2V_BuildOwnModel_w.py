# training Doc2Vec models with .w files (preprocessed .txt files, but still text files)

import os
import collections
import glob
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.parsing.preprocessing import remove_stopwords as Gensim_remove_stopwords
from gensim.utils import simple_preprocess


# A function to build a model based on Doc2Vec, trained by our own training .w files
# receives a folder with .w documents
def buildD2VModelFrom_W_Folder(wfiles_folder, model_name, vector_size, window, alpha, min_alpha, min_count, distributed_memory, epochs):

	if not os.path.exists(wfiles_folder):
		print(wfiles_folder, "not found!")
		return -1

	print("Training with .w files in", wfiles_folder)

	training_files = glob.glob(wfiles_folder+"*.w")	# Get all .w files in the training documents folder

	buildD2VModelFrom_FileList(training_files, model_name, vector_size, window, alpha, min_alpha, min_count, distributed_memory, epochs)
	return 0


# A function to build a model based on Doc2Vec, trained by our own training .txt files
# receives a folder with .txt documents
def buildD2VModelFrom_txt_Folder(files_folder, model_name, vector_size, window, alpha, min_alpha, min_count, distributed_memory, epochs):

	if not os.path.exists(files_folder):
		print(files_folder, "not found!")
		return -1

	print("Training with .txt files in", files_folder)

	training_files = glob.glob(files_folder+"*.txt")	# Get all .txt files in the training documents folder

	buildD2VModelFrom_FileList(training_files, model_name, vector_size, window, alpha, min_alpha, min_count, distributed_memory, epochs)
	return 0




# A function to build a model based on Doc2Vec, trained by our own training documents
# receives a list of filenames of .w documents
def buildD2VModelFrom_FileList(training_files, model_name, vector_size, window, alpha, min_alpha, min_count, distributed_memory, epochs):
	flag_remove_stopWords = True	# use flag_remove_stopWords to indicate if stopwords must be removed or not

	print("Training with", len(training_files), "files")

	training_texts = []	# each member is a text

	# Add the content of the training_files to the training corpus (training_texts)
	for training_file in training_files:
		training_fd = open(training_file, "r")
		text = training_fd.read()
		training_texts.append(text)

	# remove stopwords, if specified, with Gensim remove_stopwords function
	if (flag_remove_stopWords):
		training_texts = [Gensim_remove_stopwords(text) for text in training_texts]

	# preprocess each text (tokenize, lower, remove punctuation, remove <2 and >50 length words)
	training_lists = [simple_preprocess(text, max_len=50) for text in training_texts]

	# Tag the training lists (add an increasing number as tag)
	tagged_training_lists = [TaggedDocument(words=l, tags=[i]) for i,l in enumerate(training_lists)]

	# this is the input for training
	# tagged_training_lists is a list [TaggedDocument(['word1','word2',...], ['0']), TaggedDocument(['word1','word2',...], ['1']), ...]

	# Create a Doc2Vec model with the selected parameters
	model = Doc2Vec(vector_size=vector_size, window=window, alpha=alpha, min_alpha=min_alpha, min_count=min_count, dm=distributed_memory)

	# Build vocabulary from the tagged training lists
	model.build_vocab(tagged_training_lists)

	# Train the model from the tagged training lists
	model.train(tagged_training_lists, total_examples=model.corpus_count, epochs=epochs, start_alpha=alpha,end_alpha=min_alpha)

	# Save the trained model to file
	model.save(model_name)
	print(model_name, "model saved!")


	# Model assessment with the training dataset

	# for doc_index in range(len(tagged_training_lists)):  	# Go through each tagged document of the training corpus
	# 	if (doc_index % 1000) == 0:
	# 		print(doc_index, end=' ', flush=True)
	# 	# tagged_training_lists[doc_index].tags = [doc_index]
	# 	inferred_vector = model.infer_vector(tagged_training_lists[doc_index].words)  # Infer a new vector for each document of the training corpus
	# 	list_more_similar_docs = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs)) # get the docs most similar to it
	# 	rankList = [simdoc_index for simdoc_index,sim in list_more_similar_docs]
	# 	rank = rankList.index(doc_index)   # get the rank of this document in the list of its more similar docs, ideally should be 1
	# 	if doc_index == rankList[0]:
	# 		r1 += 1
	# 	ranks.append(rank)
	#
	# print("r1 =", r1/len(tagged_training_lists))
	# # Count how many times each document ranks with respect to the training corpus
	# documents_ranks = collections.Counter(ranks)
	# print(model_name, "ranks[0] =", documents_ranks[0])

	# quality check 1: compute 1-ranks to show the percentage of cases where each document is the most similar to itself (ideally should be 100%)
	# ranks = []
	# print("Checking quality #1 of:", model_name)
	# print("Computing ranks")
	# r1 = 0
	#
	# for doc_index in range(len(tagged_training_lists)):  	# Go through each tagged document of the training corpus
	# 	if (doc_index % 1000) == 0:
	# 		print(doc_index, end=' ', flush=True)
	# 	# tagged_training_lists[doc_index].tags = [doc_index]
	# 	inferred_vector = model.infer_vector(tagged_training_lists[doc_index].words)  # Infer a new vector for each document of the training corpus
	# 	list_more_similar_docs = model.docvecs.most_similar([inferred_vector], topn=1) # get the docs most similar to it
	# 	rankList = [simdoc_index for simdoc_index,sim in list_more_similar_docs]
	# 	first_in_rank = rankList[0]
	# 	if doc_index == first_in_rank:
	# 		r1 += 1
	#
	# print("r1 =", r1/len(tagged_training_lists))

	return 0
