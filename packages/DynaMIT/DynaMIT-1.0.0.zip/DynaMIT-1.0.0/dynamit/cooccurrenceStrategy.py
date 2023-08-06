"""Module for CoOccurrenceStrategy classes."""

import dynamit.integrationStrategy
import dynamit.utils

from sklearn.cluster import AffinityPropagation
from numpy import array

class CoOccurrenceStrategy(dynamit.integrationStrategy.IntegrationStrategy):
	"""Class implementing a co-occurrence integration strategy,
	which performs integration by computing a score for each motif pair,
	based on the fraction of sequences in which two motifs have co-occurrent
	instances; an affinity propagation clustering is then performed, using
	this co-occurrence score as a similarity measure.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.integrationStrategyName = "Co-occurrence"
		self.coOccurrenceScoreThreshold = 0.0

	def setConfiguration(self, configString):
		"""Loads the strategy parameters specified in the configuration file.
		In particular, if the configuration string is non-empty, it is
		considered to contain the co-occurrence score threshold
		for a motifs pair to be considered interesting.

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if len(configString) > 0:
			# read the minimum co-occurrence score threshold.
			self.coOccurrenceScoreThreshold = float(configString)
		return 0

	def doIntegration(self, sequences, searchResults):
		"""Performs motifs integration by computing a co-occurrence
		score for each motif pair and subsequently clustering motifs
		based on this score, used as a similarity measure.

		Args:
			sequences: collection of input sequences for this run.
			searchResults: table containing matches for all motifs on all sequences.
										This table is produced by DynaMIT motif search phase.

		Returns:
			Returns 0 if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		# extract motifs from search results
		motifs = dynamit.utils.getMotifsFromSearchResults(searchResults)

		# check if there are at least two motifs
		if len(motifs) < 2:
			print "[ERROR] Less than two motifs found. Need at least two motifs " \
						"to apply an integration strategy."
			return 1

		# compute the vectorized binary by-sequence representation of the motifs
		vectors = dynamit.utils.getBySequenceMotifsInstancesVectors(sequences,
																																searchResults,
																																binary=True)

		# compute pairwise co-occurrence score for every motifs pair and
		# store it both into an affinity matrix and a dictionary without self-pairs
		coOccurrenceScoresMatrix = []
		pairsScores = {}
		for key in motifs.keys():
			curKeyScores = []
			for key2 in motifs.keys():

				# compute the co-occurrence score of these two motifs as the Jaccard
				# similarity of their sequence sets (i.e. the set of sequences in
				# which the motif has at least a match)
				m1 = [seq for (seq, vect) in vectors[key].iteritems() \
							if vect.count(1) > 0]
				m2 = [seq for (seq, vect) in vectors[key2].iteritems() \
							if vect.count(1) > 0]
				curScore = dynamit.utils.vectorsJaccard(m1, m2)

				# add the co-occurrence score to the motif affinity scores list
				curKeyScores.append(curScore)

				# add current co-occurrence score to the results
				# dictionary without self-pairs
				if ((key != key2) and
						(not pairsScores.has_key(key2 + "," + key))):
					pairsScores[key + "," + key2] = [curScore]

			# add all co-occurrence score scores for this motif to
			# the global affinity matrix
			coOccurrenceScoresMatrix.append(curKeyScores)

		print "  [CoOccurrenceStrategy] Motifs pairwise co-occurrence " \
					"scores computed."

		# get motifs pair with co-occurrence score over the
		# threshold set in configuration
		pairsOverThreshold = dict([(k, v) for k, v in pairsScores.iteritems() \
																if v[0] >= self.coOccurrenceScoreThreshold])

		# cluster motifs by their co-occurrence score affinity through
		# an affinity propagation algorithm
		clustering = AffinityPropagation(affinity="precomputed").fit(array(coOccurrenceScoresMatrix))

		print "  [CoOccurrenceStrategy] Motifs clustering computed."

		# store and returns the results of this integration strategy
		# (pairwise co-occurrence score-derived interesting motifs pairs
		#  and motifs clustering)
		self.integrationResults = {"pairsOverThreshold": pairsOverThreshold,
															 "threshold": self.coOccurrenceScoreThreshold,
															 "motifs": motifs.keys(),
															 "clustering":clustering.labels_,
															 "clusteringSilhouettes": \
																dynamit.utils.computeClustersSilhouette(
																	array(coOccurrenceScoresMatrix),
																	clustering.labels_)
}
		return self.integrationResults
