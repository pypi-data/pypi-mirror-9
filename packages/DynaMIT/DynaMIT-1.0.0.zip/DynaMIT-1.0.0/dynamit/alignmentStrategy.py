"""Module for AlignmentStrategy classes."""

import dynamit.integrationStrategy
import dynamit.utils

import os, tempfile

from Bio import AlignIO, pairwise2
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Align import MultipleSeqAlignment
from Bio.Align.AlignInfo import SummaryInfo
from Bio.Align.Applications import ClustalOmegaCommandline

from sklearn.cluster import AffinityPropagation
from numpy import array

class AlignmentStrategy(dynamit.integrationStrategy.IntegrationStrategy):
	"""Class implementing an alignment-based integration strategy,
	which performs integration through a pairwise alignment for all
	motif pairs (used to cluster motifs) and a multiple alignment
	used to generate a consensus and a PSSM matrix representing all motifs.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.integrationStrategyName = "Alignment"
		self.alignmentScoreThreshold = 0.0
		self.clustalOmegaPath = ""

	def setConfiguration(self, configString):
		"""Loads the strategy parameters specified in the configuration file.
		In particular, the first parameter (first part before a , or the whole
		string if no , is found) is considered to be the alignment score threshold
		for a motifs pair to be considered interesting. If a , is found, the part
		after it is considered to be the absolute path to the clustalo alignment
		program, which is considered to be on the system known path if
		not specified.

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if len(configString) > 0:
			# split the configuration string in its subcomponents.
			configInfo = configString.split(",")
			# read the minimum alignment score threshold.
			try:
				self.alignmentScoreThreshold = float(configInfo[0])
			except ValueError:
				print "[ERROR] Wrong alignment score threshold " \
							"specification (needs float)."
				return 1
			# if clustalOmega alignment tool absolute path was specified,
			# read it from the configuration string.
			if len(configInfo) > 1:
				self.clustalOmegaPath = configInfo[1]

		return 0

	def doIntegration(self, sequences, searchResults):
		"""Performs motifs integration by executing both a pairwise
		alignment for all motif pairs and a multiple alignment
		including all motifs. The pairwise alignment score is then used
		to cluster motifs, while the multiple alignment is used to generate
		a consensus and a PSSM matrix representing all motifs.

		Args:
			sequences: collection of input sequences for this run.
			searchResults: table containing matches for all motifs on all sequences.
										This table is produced by DynaMIT motif search phase.

		Returns:
			Returns 0 if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		# extract motifs sequences from search results
		motifs = dynamit.utils.getMotifsFromSearchResults(searchResults)

		# check if there are at least two motifs
		if len(motifs) < 2:
			print "[ERROR] Less than two motifs found. Need at least two motifs " \
						"to apply an integration strategy."
			return 1

		# compute pairwise alignment score for every motifs pair and store it
		# both into an affinity matrix and a dictionary without self-pairs
		alignmentScoresMatrix = []
		silhouetteScoresMatrix = []
		pairsScores = {}
		for key in motifs.keys():
			curKeyScores = []
			curSilScores = []
			for key2 in motifs.keys():
				# perform the pairwise alignment of these two motifs
				curAlignments = pairwise2.align.globalms(motifs[key], motifs[key2],
																									2, -1, -.5, -.1)
				# extract and use the best alignment from the results
				curAlign = None
				for alignment in curAlignments:
					if curAlign != None:
						if alignment[2] > curAlign[2]:
							curAlign = alignment
					else:
						curAlign = alignment

				# add the alignment score to the motif affinity scores list
				curKeyScores.append(curAlign[2])
				# convert pairwise affinities in [0,1] ranging similarities
				# for clusters silhouette computation.
				curSilScores.append(float(curAlign[2]) /
														float(2*max(len(motifs[key]), len(motifs[key2]))))

				# compute the pairwise alignment consensus and add it to
				# the alignment informations collected so far
				curAlignObj = MultipleSeqAlignment([SeqRecord(Seq(curAlign[0])),
																						SeqRecord(Seq(curAlign[1]))])
				curAlign = curAlign + (str(SummaryInfo(curAlignObj).dumb_consensus()), )

				# add current alignment to the results dictionary without self-pairs
				if (key != key2) and (not pairsScores.has_key(key2 + ", " + key)):
					pairsScores[key + ", " + key2] = [curAlign[2], "Motif 1 alignment: " \
																					+ curAlign[0], "Motif 2 alignment: " \
																					+ curAlign[1], "Consensus: " + curAlign[5]]

			# add all alignment scores for this motif to the global affinity matrix
			alignmentScoresMatrix.append(curKeyScores)
			silhouetteScoresMatrix.append(curSilScores)

		print "  [AlignmentStrategy] Motifs pairwise alignments computed."

		# get motifs pair with alignment score over the threshold set in configuration
		pairsOverThreshold = dict([(k, v) for k, v in pairsScores.iteritems() \
																if v[0] >= self.alignmentScoreThreshold])

		# cluster motifs by their alignment affinity through an affinity propagation algorithm
		clustering = AffinityPropagation(affinity="precomputed").fit(array(alignmentScoresMatrix))


		print "  [AlignmentStrategy] Motifs clustering computed."

		# compute the multiple alignment of the motifs and
		# the consensus for each motif cluster.
		clustersMultAligns = []
		clustersConsensuses = []
		clustersPSSMs = []
		for cluster in list(set(clustering.labels_)):
			# write motifs sequences of this cluster to file for multiple alignment.
			motifsFilename = os.path.join(tempfile.gettempdir(), "motifs.fasta")
			alignmentFilename = os.path.join(tempfile.gettempdir(), "matches.aln")
			# remove the alignment filename to avoid future problems.
			if os.path.isfile(alignmentFilename):
				os.remove(alignmentFilename)
			motifsHandle = open(motifsFilename, "wb")
			clusterMotifs = [motifs.keys()[i] \
											 for i, clust in enumerate(clustering.labels_) \
											 if clust == cluster]
			if len(clusterMotifs) > 1:
				for m in clusterMotifs:
					motifsHandle.write(">" + m + "\n" + motifs[m] + "\n")
				motifsHandle.close()

				# compute the multiple alignment of all motifs and its consensus.
				clustalomega_cline = ClustalOmegaCommandline(
															os.path.join(self.clustalOmegaPath, "clustalo"),
															infile=motifsFilename, outfile=alignmentFilename,
															force=True)
				# run the actual alignment with clustalomega
				clustalomega_cline()
				# get the results for this cluster from clustalomega output file.
				multAlign = AlignIO.read(alignmentFilename, "fasta")
				multAlignInfo = SummaryInfo(multAlign)
				# append the results for this cluster to the list of clusters results.
				clustersMultAligns.append(str(multAlign)[str(multAlign).index("\n")+1:])
				clustersConsensuses.append(str(multAlignInfo.dumb_consensus()))
				clustersPSSMs.append(str(multAlignInfo.\
														pos_specific_score_matrix(clustersConsensuses[-1])))
			else:
				# this is a one-motif cluster, so cannot align.
				clustersMultAligns.append(motifs[clusterMotifs[0]] + " " + clusterMotifs[0])
				clustersConsensuses.append(motifs[clusterMotifs[0]])
				clustersPSSMs.append("")

			# remove the alignment filename to avoid future problems.
			if os.path.isfile(alignmentFilename):
				os.remove(alignmentFilename)

		print "  [AlignmentStrategy] Clusters multiple alignments, " \
					"consensus and PSSMs computed."

		# store and returns the results of this integration strategy (pairwise
		# alignment-derived interesting motifs pairs and motifs clustering plus
		# multiple alignment results)
		self.integrationResults = {"pairsOverThreshold":pairsOverThreshold,
															"threshold": self.alignmentScoreThreshold,
															"motifs": motifs.keys(),
															"clustering":clustering.labels_,
															"clusteringSilhouettes": \
																dynamit.utils.computeClustersSilhouette(
																	array(silhouetteScoresMatrix),
																	clustering.labels_),
															"clustersMultipleAlignments": clustersMultAligns,
															"clustersPSSMs": clustersPSSMs,
															"clustersConsensuses": clustersConsensuses}
		return self.integrationResults
