""" Module for the PCAStrategy classes."""

import dynamit.integrationStrategy
import dynamit.utils

from sklearn.decomposition import KernelPCA
from sklearn.cluster import AffinityPropagation
from numpy import array

class PCAStrategy(dynamit.integrationStrategy.IntegrationStrategy):
	"""Class implementing a PCA integration strategy, which performs
	integration by computing the motifs reduced representation (bidimensional)
	through a Principal Component Analysis. An affinity propagation
	clustering is then performed, using this reduced representation.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.integrationStrategyName = "PCA"

	def setConfiguration(self, configString):
		"""Loads the strategy parameters specified in the configuration file.

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		return 0

	def doIntegration(self, sequences, searchResults):
		"""Performs the motifs integration by computing the motifs
		reduced representation through a PCA analysis; this bidimensional
		representation of the motifs is then used to cluster them.

		Args:
			sequences: collection of input sequences for this run.
			searchResults: table containing matches for all motifs on all sequences.
										This table is produced by DynaMIT motif search phase.

		Returns:
			Returns 0 if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		# compute the binary vectorized representation of the motifs
		vectors = dynamit.utils.getMotifsInstancesVectors(sequences,
																											searchResults,
																											binary=True)

		print "  [PCAStrategy] Motifs binary vectorized representation computed."

		# check if there are at least two motifs
		if len(vectors.keys()) < 2:
			print "[ERROR] Less than two motifs found. Need at least two motifs " \
						"to apply an integration strategy."
			return 1

		# compute a kernel PCA reduction on the binary instances
		# vectors of all motifs
		motifs_reducedByPCA = KernelPCA(n_components=2).fit_transform(array(vectors.values()))

		print "  [PCAStrategy] PCA motifs vectors transformation computed."

		# cluster motifs by their Kernel PCA reduced representation,
		# through an affinity propagation clustering algorithm
		clustering = AffinityPropagation().fit(motifs_reducedByPCA)

		print "  [PCAStrategy] Motifs clustering completed."

		# store and returns the results of this integration strategy
		# (interesting motifs pairs, motifs clustering and
		# reduced motifs representation)
		self.integrationResults = {"motifs": vectors.keys(),
															 "clustering":clustering.labels_,
															 "clusteringSilhouettes": \
																dynamit.utils.computeClustersSilhouette(
																	array(vectors.values()),
																	clustering.labels_, precomputed=False),
															 "reducedMotifsRepresentation": motifs_reducedByPCA}
		return self.integrationResults
