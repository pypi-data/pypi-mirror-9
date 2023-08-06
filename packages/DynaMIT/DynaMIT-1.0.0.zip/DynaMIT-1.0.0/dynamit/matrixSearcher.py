""" Module for the MatrixSearcher classes."""

import dynamit.motifSearcher
import dynamit.utils

from Bio import motifs
from Bio.motifs.matrix import PositionWeightMatrix
from Bio.motifs.matrix import PositionSpecificScoringMatrix
from Bio.motifs.thresholds import ScoreDistribution
from Bio.Alphabet import IUPAC

class MatrixSearcher(dynamit.motifSearcher.MotifSearcher):
	"""Class implementing a matrix match search component,
	matching a PFM/PWM/PSSM specified in the configuration
	with the input sequences, keeping only matches below a
	user-specified p-value threshold (0.05 as default).
	Significant matches are provided as results of this
	searcher with the matrix consensus as motif.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.searcherName = "Matrix"
		self.searchResults = []
		self.params = ""
		self.matrixType = "pfm"
		self.matrixName = ""
		self.fprThreshold = 0.05
		self.bothStrands = False

	def setConfiguration(self, path, params):
		"""
		Stores path and parameters for running this searcher.
		path: path of the motif matrix file to be used for
					matching over input sequences.
		params: parameters to be passed to the searcher,
						along with the sequences filename.
		"""
		# store the motif matrix path to use and return
		# an error if it was not specified.
		if path != "":
			self.path = path
		else:
			print "[ERROR] Matrix file was not specified in configuration."
			return 1

		# params should be made of:
		#		matrixType,fprThreshold,[bothStrands].
		if params != "":
			self.params = params

			# set the matrix name and the match false positive rate parameter.
			info = self.params.split(',')
			self.matrixName = info[0]
			if len(info) > 1:
				self.fprThreshold = float(info[1])

			# set the motif matrix type parameter.
			if self.params.find("pfm") >= 0:
				self.matrixType = "pfm"
			elif self.params.find("pwm") >= 0:
				self.matrixType = "pwm"
			elif self.params.find("pssm") >= 0:
				self.matrixType = "pssm"

			# set the single/both strands parameter.
			if self.params.find("bothStrands") >= 0:
				self.bothStrands = True

		return 0

	def runSearch(self, sequencesFilename):
		"""Performs motif search by matching the
		provided matrix with the input sequences,
		and providing significant matches as results.

		Args:
			sequencesFilename: input sequences filename for this run.

		Returns:
			Returns a list of strings representing identified motif matches
			if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		try:
			# open the matrix file to provide Biopython with a file handle
			motifHandle = open(self.path)
			# Read the matrix as if it was a JASPAR PFM, regardless of
			# its actual values (PFM, PWM, PSSM).
			matrixMotif = motifs.read(motifHandle, "pfm")
			# set neutral background for pssm computation from pfm
			matrixMotif.background = dict.fromkeys(["A", "C", "G", "T"], 1.0)
			# add a little pseudocounts to avoid -inf weights
			matrixMotif.pseudocounts = 0.5
			# close the matrix file.
			motifHandle.close()
			# convert the matrix to a PSSM according to its initial type
			matrix = None
			if self.matrixType == "pfm":
				# go from PFM to pssm directly
				matrix = matrixMotif.pssm
			elif self.matrixType == "pwm":
				# create a PWM with the loaded counts.
				# add a 0.0001 pseudocount everywhere to avoid -infs.
				matrix = PositionWeightMatrix(matrixMotif.alphabet,
									dict([(key, [v+0.0001 for v in lst]) \
												for key, lst in matrixMotif.counts.iteritems()]))
				# and convert it to a PSSM.
				matrix = matrix.log_odds()
			elif self.matrixType == "pssm":
				# create a PSSM with the loaded counts.
				matrix = PositionSpecificScoringMatrix(IUPAC.unambiguous_dna,
																							 matrixMotif.counts)

			# load sequences into a dictionary for matrix matching
			sequences = dynamit.utils.getSequencesRecords(sequencesFilename)
			# try to compute the match score threshold to obtain a false positive
			# rate correpsonding to the selected false positive rate.
			try:
				scoreThreshold = ScoreDistribution(pssm=matrix,
													background=dict.fromkeys(["A", "C", "G", "T"], 1.0)).\
													threshold_fpr(self.fprThreshold)
			except ValueError:
				print "  [MatrixSearcher] Cannot compute a score threshold associated" \
							" to the desired FPR. All matches will be reported."
				scoreThreshold = 0

			for sequence in sequences:
				# hits is a list of matching (startPosition, score) tuples
				hits = matrix.search(sequence.seq, both=self.bothStrands)
				# select significant hits only.
				significantHits = [(startPosition + 1, score)
													 for (startPosition, score) in hits
													 if score >= scoreThreshold]
				# add significant hits to search results list.
				self.searchResults.extend([str(matrixMotif.consensus) + "\tsequence\t" + \
															(self.searcherName + "_" + self.matrixName \
															 if self.matrixName != "" else self.searcherName) + \
															"\t" + sequence.description + \
															"\t" + str(startPosition) + "\t" + \
															str(startPosition + len(matrixMotif)) + \
															"\t" + str(score)
															for (startPosition, score) in significantHits])

			print "  [MatrixSearcher] Execution completed."
			return self.searchResults
		except (IOError, ValueError, RuntimeError) as e:
			print "  [MatrixSearcher] Unexpected error: %s" % str(e)
			return 1
