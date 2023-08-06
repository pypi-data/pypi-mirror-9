"""Module for ProximityStrategy classes."""

import dynamit.integrationStrategy
import dynamit.utils

from sklearn.cluster import AffinityPropagation
from numpy import array

class ProximityStrategy(dynamit.integrationStrategy.IntegrationStrategy):
	"""Class implementing a proximity score integration strategy,
	which performs integration by computing for each motif pair the fraction
	of instances of the two motifs which are within an user-specified
	distance on the sequences.An affinity propagation clustering is then
	performed, using this proximity score as a similarity measure.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.integrationStrategyName = "Proximity"
		self.maxProximityDistance = 0
		self.proximityScoreThreshold = 0.0

	def setConfiguration(self, configString):
		"""Loads the strategy parameters specified in the configuration file.
		In particular, if the configuration string is non-empty, it is
		considered to contain the the maximum distance in nucleotides for two
		motif matches to be considered proximal and the proximity score threshold
		for a motifs pair to be considered interesting.

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if configString != "":
			# read the maximum distance and the minimum proximity score
			# threshold between two motifs instances to consider these as proximal.
			info = configString.split(",")
			try:
				self.maxProximityDistance = float(info[0])
				if len(info) > 1:
					self.proximityScoreThreshold = float(info[1])
			except ValueError:
				print "[ERROR] Wrong maximum distance and/or score threshold " \
							"specification (both parameters need a floating-point number)."
				return 1

		return 0

	def doIntegration(self, sequences, searchResults):
		"""Performs the motifs integration by computing a proximity score,
		finding, for each motif pair, the amount of instances of the two
		motifs that are within a certain distance on the sequences; then,
		a clustering is performed using this score as a similarity score.

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

		# get the by-sequence matches list for each motif
		vectors = dynamit.utils.getBySequenceMotifsInstancesLists(sequences,
																															searchResults)

		# compute pairwise proximity score for every motifs pair and store it
		# both into an affinity matrix and a dictionary without self-pairs
		proximityScoresMatrix = []
		pairsScores = {}
		for key in motifs.keys():
			curKeyScores = []
			for key2 in motifs.keys():
				curScore = 0
				matchPairs = 0
				if key != key2:
					for sequence in vectors[key].keys():
						for match in vectors[key][sequence]:
							for match2 in vectors[key2][sequence]:
								matchPairs += 1
								if match[1] <= match2[0]:
									# seq1--seq2: seq1 before, no overlap.
									if (match2[0] - match[1]) <= self.maxProximityDistance:
										curScore += 1
								elif match2[1] <= match[0]:
									# seq2--seq1: seq2 before, no overlap.
									if (match[0] - match2[1]) <= self.maxProximityDistance:
										curScore += 1
								elif (max(0, min(match[1], match2[1]) - \
											max(match[0], match2[0]))) > 0:
									# matches are overlapping, so under the
									# specified maximum distance threshold.
									curScore += 1

					# add the proximity score (proximal match pairs / # matches pairs)
					# to the motif affinity scores list.
					curKeyScores.append(float(curScore) / float(matchPairs) \
															if matchPairs > 0 else 0.0)
					# add this co-occurrence score to the results dictionary
					# without self-pairs.
					if not pairsScores.has_key(key2 + "," + key):
						pairsScores[key + "," + key2] = [float(curScore) / float(matchPairs) \
																						 if matchPairs > 0 else 0.0]
				else:
					# we're dealing with the similarity of the motif to itself, so add 1.
					curKeyScores.append(1.0)

			# add all co-occurrence score scores for this motif to
			# the global affinities matrix.
			proximityScoresMatrix.append(curKeyScores)

		print "  [ProximityStrategy] Motifs pairwise proximity scores computed."

		# get motifs pair with proximity score over
		# the threshold set in configuration.
		pairsOverThreshold = dict([(k, v) for k, v in pairsScores.iteritems() \
																if v[0] >= self.proximityScoreThreshold])

		# cluster motifs by their proximity score affinity through
		# an affinity propagation algorithm.
		clustering = AffinityPropagation(affinity="precomputed").fit(array(proximityScoresMatrix))

		# store and returns the results of this integration strategy
		# (pairwise proximity score-derived interesting motifs pairs
		# and motifs clustering)
		print "  [ProximityStrategy] Motifs clustering computed."
		self.integrationResults = {"pairsOverThreshold":pairsOverThreshold,
															 "threshold": self.proximityScoreThreshold,
															 "motifs": motifs.keys(),
															 "clustering":clustering.labels_,
															 "clusteringSilhouettes": \
																dynamit.utils.computeClustersSilhouette(
																	array(proximityScoresMatrix),
																	clustering.labels_)}
		return self.integrationResults
