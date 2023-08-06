""" Module for the MIStrategy classes."""

import dynamit.integrationStrategy
import dynamit.utils

from sklearn.cluster import AffinityPropagation
from numpy import array

class MIStrategy(dynamit.integrationStrategy.IntegrationStrategy):
	"""Class implementing a mutual information integration strategy,
	which performs integration by computing the MI value for each motif
	pair, based on the shared amount of nucleotides occupied by
	both motifs in a pair. An affinity propagation clustering is then
	performed, using this MI score as a similarity measure.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.integrationStrategyName = "MutualInformation"
		self.miThreshold = 0.0

	def setConfiguration(self, configString):
		"""Loads the strategy parameters specified in the configuration file.
		In particular, if the configuration string is non-empty, it is
		considered to contain the minimum mutual information score threshold
		for a motifs pair to be considered interesting.

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if len(configString) > 0:
			try:
				# read the minimum MI score threshold.
				self.miThreshold = float(configString)
			except ValueError:
				print "[ERROR] Wrong score threshold specification " \
							"(needs a floating-point number)."
				return 1

		return 0

	def doIntegration(self, sequences, searchResults):
		"""Performs the motifs integration by computing a mutual
		information score for each motif pair, based on nucleotides
		occupied by each motif in each sequence; then proceeds to cluster
		motifs based on the so computed mutual information score.

		Args:
			sequences: collection of input sequences for this run.
			searchResults: table containing matches for all motifs on all sequences.
										This table is produced by DynaMIT motif search phase.

		Returns:
			Returns 0 if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		# compute the vectorized binary representation of the motifs
		vectors = dynamit.utils.getMotifsInstancesVectors(sequences,
																											searchResults,
																											binary=True)

		print "  [MIStrategy] Motifs binary vectorized representation computed."

		# check if there are at least two motifs
		if len(vectors.keys()) < 2:
			print "[ERROR] Less than two motifs found. Need at least two motifs " \
						"to apply an integration strategy."
			return 1

		# compute MI for every motifs pair and store it both into
		# an affinity matrix and a dictionary without self-pairs
		MIarray = []
		pairsMI = {}
		for key in vectors.keys():
			curKeyMIs = []
			for key2 in vectors.keys():
				curMI = round(dynamit.utils.binaryVectorsNormMI(vectors[key], vectors[key2]), 4)
				curKeyMIs.append(curMI if (key != key2) else 1)
				if (key != key2) and (not pairsMI.has_key(key2 + "," + key)):
					pairsMI[key + "," + key2] = [curMI]
			MIarray.append(curKeyMIs)

		print "  [MIStrategy] Pairwise mutual information computed."

		# get motifs pair with MI over the threshold set in configuration
		pairsOverThreshold = dict([(k, v) for k, v in pairsMI.iteritems() \
																if v[0] >= self.miThreshold])

		# cluster motifs by their MI affinity through
		# an affinity propagation algorithm
		clustering = AffinityPropagation(affinity="precomputed").fit(array(MIarray))

		print "  [MIStrategy] Motifs clustering completed."

		# store and returns the results of this integration strategy
		# (interesting motifs pairs and motifs clustering)
		self.integrationResults = {"pairsOverThreshold":pairsOverThreshold,
																"threshold": self.miThreshold,
																"motifs": vectors.keys(),
																"clustering":clustering.labels_,
																"clusteringSilhouettes": \
																dynamit.utils.computeClustersSilhouette(
																	array(MIarray),
																	clustering.labels_)}
		return self.integrationResults
