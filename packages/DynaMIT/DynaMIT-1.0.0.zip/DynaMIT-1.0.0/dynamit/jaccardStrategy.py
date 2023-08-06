""" Module for the Jaccard<strategy classes."""

import dynamit.integrationStrategy
import dynamit.utils

from sklearn.cluster import AffinityPropagation
from numpy import array

class JaccardStrategy(dynamit.integrationStrategy.IntegrationStrategy):
	"""Class implementing a Jaccard overlap integration strategy,
	which performs integration by computing the Jaccard overlap value for
	each motif pair, based on the shared amount of nucleotides occupied by
	both motifs in a pair, over the total nucleotide occupation of each.
	An affinity propagation clustering is then performed, using
	this Jaccard similary score as a similarity measure.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.integrationStrategyName = "Jaccard"
		self.jaccardThreshold = 0.0

	def setConfiguration(self, configString):
		"""Loads the strategy parameters specified in the configuration file.
		In particular, if the configuration string is non-empty, it is
		considered to contain the jaccard similarity score threshold
		for a motifs pair to be considered interesting.

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if len(configString) > 0:
			try:
				# read the minimum Jaccard similarity threshold
				self.jaccardThreshold = float(configString)
			except ValueError:
				print "[ERROR] Wrong score threshold specification " \
							"(needs a floating-point number)."
				return 1

		return 0

	def doIntegration(self, sequences, searchResults):
		"""Performs the motifs integration by computing a Jaccard
		similarity score, computing the overlap of occupied nucleotides
		between the instances of the motifs in each motif pair; then
		proceeds to cluster motifs based on the so computed Jaccard score.

		Args:
			sequences: collection of input sequences for this run.
			searchResults: table containing matches for all motifs on all sequences.
										This table is produced by DynaMIT motif search phase.

		Returns:
			Returns 0 if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		# compute the vectorized representation of the motifs
		vectors = dynamit.utils.getMotifsInstancesVectors(sequences,
																											searchResults,
																											binary=False)

		print "  [JaccardStrategy] Motifs vectorized representation computed."

		# check if there are at least two motifs
		if len(vectors.keys()) < 2:
			print "[ERROR] Less than two motifs found. Need at least two motifs " \
						"to apply an integration strategy."
			return 1

		# compute the jaccard similarity for every motifs pair and store it both
		# into an affinity matrix and a dictionary without self-pairs
		jaccardArray = []
		pairsJaccard = {}
		for key in vectors.keys():
			curKeyJaccards = []
			for key2 in vectors.keys():
				curJaccard = round(dynamit.utils.vectorsJaccard(vectors[key],
																												vectors[key2]), 4)
				curKeyJaccards.append(curJaccard)
				if (key != key2) and (not pairsJaccard.has_key(key2 + "," + key)):
					pairsJaccard[key + "," + key2] = [curJaccard]
			jaccardArray.append(curKeyJaccards)

		print "  [JaccardStrategy] Jaccard pairwise affinities computed."

		# cluster motifs by their jaccard similarity, through
		# an affinity propagation clustering algorithm
		clustering = AffinityPropagation(affinity="precomputed").fit(array(jaccardArray))

		print "  [JaccardStrategy] Motifs clustering completed."

		# get motifs pair with Jaccard similarity over
		# the threshold set in configuration
		pairsOverThreshold = dict([(k, v) \
																for k, v in pairsJaccard.iteritems() \
																if v[0] >= self.jaccardThreshold])

		# store and returns the results of this integration strategy
		# (interesting motifs pairs and motifs clustering)
		self.integrationResults = {"motifs": vectors.keys(),
															 "clustering": clustering.labels_,
															 "clusteringSilhouettes": \
																dynamit.utils.computeClustersSilhouette(
																	array(jaccardArray),
																	clustering.labels_),
															 "pairsOverThreshold": pairsOverThreshold,
															 "threshold": self.jaccardThreshold}
		return self.integrationResults
