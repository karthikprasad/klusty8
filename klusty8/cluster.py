###	CLUSETRING MODULE for Search Results Clustering (Klusty)
##	@author karthik
##	@date 07 Nov 2012
##		  12 Nov 2012
##		  13 Nov 2012
##		  16 Nov 2012 (added stemmer)
##


import re
import random
import collections
import stemmer

###############################################################################################################################
###############################################################################################################################

def jaccard_distance(item1, item2):
	"""
		Function to compute the jaccard similarity and hence the distance between two items based on their title and summary(content).
		@param two rss feed items
		@return Jaccard distance(float) -> 1 - similarity

		@depedencies: re, stemmer, stopwords(file)
	"""
	# creating Porter Stemmer object
	ps = stemmer.PorterStemmer()
	##tokenizing string and stemming
	#words in item1
	wordsItem1 = re.findall(r"[\w']+", item1["title"].lower()) + re.findall(r"[\w']+", item1["summary"].lower())
	wordsItem1[:] = [ps.stem(word) for word in wordsItem1]

	#words in item2
	wordsItem2 = re.findall(r"[\w']+", item2["title"].lower()) + re.findall(r"[\w']+", item2["summary"].lower())
	wordsItem2[:] = [ps.stem(word) for word in wordsItem2]

	#get english stopwords list
	stopWordFile = open("stopwords", "r")
	stopWordList = [word.strip() for word in stopWordFile]

	##Extract features of the items
	feature1 = set(wordsItem1) - set(stopWordList)
	feature2 = set(wordsItem2) - set(stopWordList)
	

	#get jaccard similarity
	similarity = 1.0 * len(feature1 & feature2) / (len((feature1 | feature2) - (feature1 & feature2))+0.1)

	#return jaccard distance
	return (1 - similarity)


###############################################################################################################################
###############################################################################################################################


def build_dist_matrix(items, distFunc = jaccard_distance):
	"""	
		Function to build a distance matrix for the items based on the chosen distance function
		@param: items :: list of items
				distFunc :: distance function
		@return: ditance matrix (2-D dictionary)

		@depedencies: collections
	"""

	distMatrix = collections.defaultdict(dict)
	for item1 in items:
		for item2 in items:
			distMatrix[item1][item2] = distFunc(item1, item2)
	##
	#  can be improved by utilising the fact that the distMatrix is a symmetric matrix
	##

	return distMatrix


###############################################################################################################################
###############################################################################################################################


def kmedoids(items, distMatrix, k=8, threshold=0.8):
	"""
		Function to cluster the given set of items using k-medoids.
		@param: items :: list of items to be clustered
				k :: number of clusters (default is 8)
				threshold :: max acceptable distance (default is 0.8)
				distFunc :: function to measure the distance between items
		@return: dictionary of clusters with:
					key = cluster medoid
					value = list of cluster elements

		@depedencies: random

		####################################################################################################

		K-MEDOIDS ALGORITHM	
		1. Initialize: randomly select k of the n data points as the medoids
		2. Associate each data point to the closest medoid. ("closest" here is defined using any valid distance metric, most commonly Euclidean distance, Manhattan distance or Minkowski distance)
		3. For each medoid m
		   	For each non-medoid data point o
		   		Swap m and o and compute the total cost of the configuration
		4. Select the configuration with the lowest cost.
		5. repeat steps 2 to 4 until there is no change in the medoid.

		MODIFIED K-MEDOIDS ALGORITHM
		1. Initialize: randomly select k of the n data points as the medoids
		2. Associate each data point to the closest medoid. ("closest" here is defined using any valid distance metric, most commonly Euclidean distance, Manhattan distance or Minkowski distance)
		3. For each cluster c
		   	find the new medoid
		4. repeat steps 2 to 3 until there is no change in the medoid.

		MEDOID(cluster center)
		defined as the item which has the smallest sum of distances to the other items in the cluster.
		Suitable for cases in which the distance matrix is known but the original data matrix is not available
	"""


	####################################################################################################
	### STEP 1
	#select k random items as medoids
	medoids = None
	if len(items) >= k:
		medoids = random.sample(items, k)
	
	if medoids == None:
		return "ERROR"

	####################################################################################################

	### STEP 2
	# max 22 iterations for convergence
	for i in range(22):

		# initially empty clusters
		clusters = collections.defaultdict(list)

		#for every item, find the closest medoid and assign it to the medoid's cluster
		for item in items:
			#find the distance to all the medoids
			medoidDistances = map(lambda x: distMatrix[item][x], medoids)

			#get minimum medoid distance and the minimum medoid
			minDist = min(medoidDistances)
			minMedoid = medoids[medoidDistances.index(minDist)]
			
			# if the minimum distance is less than the threshold
			if minDist <= threshold:
				#add this item to the cluster of the medoid
				clusters[minMedoid].append(item)

		####################################################################################################

		### STEP 3
		# keep a copy of the current set of medoids
		prevMedoids = medoids
		# flush the medoids
		medoids = []

		## compute new medoids
		#for every cluster(a list of items), find a new medoid
		for cluster in clusters.values():

			minTotalDist = len(cluster) #this is the maximum value
			newMedoid = None

			# for every item in the cluster
			for item in cluster:
				#find the distance of this item to every other item in the cluster and sum them up
				totalDist = sum([distMatrix[item][anotherItem] for anotherItem in cluster])

				# if this total distance is less than the minimum
				if totalDist <= minTotalDist:
					# set this as the new minimum distance
					minTotalDist = totalDist

					#set this item as the new medoid
					newMedoid = item

			medoids.append(newMedoid)

		####################################################################################################
		## check if the medoids have not changed
		if medoids == prevMedoids:
			# medoids have not changed, so you can break out of the loop
			break

		#else, the medoids have changed and have to be reclustered...so, continue...

		####################################################################################################

	return clusters


###############################################################################################################################
###############################################################################################################################