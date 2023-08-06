""" Module for the BiclusteringStrategy classes."""

import dynamit.integrationStrategy
import dynamit.utils

from sklearn.cluster.bicluster import SpectralBiclustering
from numpy import array

class BiclusteringStrategy(dynamit.integrationStrategy.IntegrationStrategy):
	"""Class implementing a biclustering-based integration strategy,
	which performs integration by a spectral biclustering algorithm,
	producing biclusters of related motifs and sequences.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.integrationStrategyName = "Biclustering"
		self.biclustersNumber = 3

	def setConfiguration(self, configString):
		"""Loads the strategy parameters specified in the configuration file.
		In particular, if the configuration string is non-empty, it is
		considered to contain the number of desired biclusters to derive.

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if len(configString) > 0:
			try:
				# load the desired number of biclusters
				self.biclustersNumber = int(configString)
			except ValueError:
				print "[ERROR] Wrong number of biclusters specification " \
							"(needs an integer number)."
				return 1

		return 0

	def doIntegration(self, sequences, searchResults):
		"""Performs the motifs integration by biclustering motifs
		and sequences based on the occurrence of each motif in
		each of the sequences. Returns an indication of which
		bicluster each motif("biclustering_motifs") and each
		sequence ("biclustering_sequences") belong to.

		Args:
			sequences: collection of input sequences for this run.
			searchResults: table containing matches for all motifs on all sequences.
										This table is produced by DynaMIT motif search phase.

		Returns:
			Returns 0 if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		# compute the per-sequence vectorized binary representation of the motifs
		vectors = dynamit.utils.getBySequenceMotifsInstancesVectors(sequences,
																																searchResults,
																																binary=True)
		print "  [BiclusteringStrategy] Per-sequence motifs binary vectorized " \
					"representation computed."

		# check if there are at least two motifs, otherwise abort
		if len(vectors.keys()) < 2:
			print "[ERROR] Less than two motifs found. Need at least two motifs " \
						"to apply an integration strategy."
			return 1

		# compute the matrix to be biclustered (motifs on rows and sequences on
		# columns, content is the presence or absence of motifs in sequences)
		presencesArray = []
		for key in vectors.keys():
			curKeyPres = []
			# set the motif row to be made of 1 for columns (sequences) in which
			# the motif is found and 0 otherwise
			motifSeqs = [seq for (seq, vect) in vectors[key].iteritems() \
									 if vect.count(1) > 0]
			for seq in sequences:
				# mark a present motif in this sequence with a "2" and an absent
				# motif with a "1": using 1 and 0 as would be natural can cause
				# DivideByZero errors if a row/column is full of zeros.
				curKeyPres.append(2 if (seq.description in motifSeqs) else 1)
			# add the motif row to the final matrix
			presencesArray.append(curKeyPres)

		print "  [BiclusteringStrategy] Biclustering matrix generated."
		# bicluster motifs by their presence in the sequences through
		# a spectral biclustering algorithm
		biclustering = SpectralBiclustering(n_clusters=self.biclustersNumber)
		biclustering.fit(array(presencesArray))
		print "  [BiclusteringStrategy] Motifs-sequences biclustering completed."

		# store and returns the results of this integration strategy
		# (employed motifs and sequences, and biclustering labels)
		self.integrationResults = {"motifs": vectors.keys(),
															 "sequences": [seq.description for seq in sequences],
															 "biclustering_motifs":biclustering.row_labels_,
															 "biclustering_sequences":biclustering.column_labels_}
		return self.integrationResults
