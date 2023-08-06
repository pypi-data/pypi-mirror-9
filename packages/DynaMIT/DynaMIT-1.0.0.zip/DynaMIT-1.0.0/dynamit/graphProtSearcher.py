""" Module for the GraphProtSearcher classes."""

import os, shutil, subprocess, itertools
from subprocess import CalledProcessError

import dynamit.motifSearcher
import dynamit.utils

class GraphProtSearcher(dynamit.motifSearcher.MotifSearcher):
	"""Class implementing a motif searcher running the
	GraphProt motif search tool, identifying the binding
	preferences for an RBP. Requires a positive binding
	sequences set (the input sequences) and a negative
	non-binding set (specified in the searcher configuration).
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.path = ""
		self.sfoldPath = ""
		self.negativesFilename = ""
		self.searcherName = "GraphProt"

	def setConfiguration(self, path, params):
		"""Loads the searcher parameters specified in the configuration file.

		Args:
			path: path of the GraphProt executable file.
			params: parameters to be given to GraphProt along with the sequences filename.

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if path != "":
			self.path = path
		if params != "":
			info = params.split(',')
			# store negative sequences filename.
			self.negativesFilename = info[0]
			# store additional parameters, if any.
			if len(info) > 1:
				self.params = info[1]

		if self.negativesFilename == "":
			print "[ERROR] Negative sequences (unbound sites) filename " \
						"specification missing."
			return 1

		return 0

	def runSearch(self, sequencesFilename):
		"""Performs motif search with the GraphProt
		tool, looking for the RBP binding preference,
		with provided input sequences filename, negative
		non-bound sequences and configured parameters.

		Args:
			sequencesFilename: input sequences filename for this run.

		Returns:
			Returns a list of strings representing motifs matches if
			everything went fine (details on results filenames, etc., are
			printed to the console); returns 1 and an error message otherwise.
		"""
		# get current working directory
		cwd = os.getcwd()
		# move to GraphProt directory (it won't work if launched outside it)
		os.chdir(self.path)

		# prepare sequences list to be later passed to processGraphProtResults.
		sequences = [(seq.description, str(seq.seq)) for seq in \
								 dynamit.utils.getSequencesRecords(sequencesFilename)]

		try:
			# perform model training.
			completePath = "perl " + os.path.join(self.path, "GraphProt.pl") + \
										 " -action train -fasta \"" + sequencesFilename + \
										 "\" -negfasta \"" + self.negativesFilename + "\""
			subprocess.check_output(completePath, shell=True, stderr=subprocess.STDOUT)

			# perform binding sites prediction
			completePath = os.path.join(self.path, "GraphProt.pl") + \
										 " -action predict_has -fasta \"" + \
										 sequencesFilename + "\" -negfasta \"" + \
										 self.negativesFilename + "\" -model GraphProt.model"
			subprocess.check_output(completePath, shell=True, stderr=subprocess.STDOUT)

			# check if GraphProt results exist
			if os.path.isfile("GraphProt.has"):
				# extract results
				print "  [GraphProtSearcher] Search completed."
				self.searchResults = self._processGraphProtResults(sequences,
																													 "GraphProt.has")
			else:
				print "[ERROR] Could not find GraphProt results file."
				return 1
			# go back to working directory.
			os.chdir(cwd)
		except CalledProcessError as e:
			# inform about the error that happened,
			print "[ERROR] GraphProt execution terminated with an error:" + e.output
			# go back to working directory
			os.chdir(cwd)
			# abort searcher execution.
			return 1

		# move GraphProt results files to our working folder.
		if os.path.isfile(os.path.join(self.path, "GraphProt.model")):
			shutil.move(os.path.join(self.path, "GraphProt.model"),
									os.path.join(cwd, "GraphProt.model"))
		if os.path.isfile(os.path.join(self.path, "GraphProt.has")):
			shutil.move(os.path.join(self.path, "GraphProt.has"),
									os.path.join(cwd, "GraphProt.has"))

		print "  [GraphProtSearcher] Execution completed."
		return self.searchResults

	def _processGraphProtResults(self, sequences, resultsFilename):
		""" Process results contained in GraphProt output files to
		produce a table for subsequent DynaMIT phases.

		Args:
			sequences: list of sequences sorted by their position in
										the input sequences filename, allow to map GraphProt
										sequences IDs to input filename IDs.
			resultsFilename: the GraphProt results filename.
		Returns:
			Returns a list of strings, one per motif match, containing
			motif sequence, sequence id, match position, etc.
		"""
		print "  [GraphProtSearcher] Processing results: <", \
					os.path.basename(resultsFilename), ">"
		try:
			# get results lines from GraphProt output file.
			with open(resultsFilename) as f:
				lines = f.readlines()

			processedResults = []
			positionsBySeq = {}

			if len(lines) == 0:
				# GraphProt found zero motifs, so return an empty results list.
				return []
			else:
				# now read lines to put together contiguous nucleotides to form
				# instances of the motifs.
				for line in lines:
					info = line.rstrip('\n').split('\t')
					if not positionsBySeq.has_key(info[0]):
						positionsBySeq[info[0]] = []
					positionsBySeq[info[0]].append(int(info[1]))

				for seq in positionsBySeq.keys():
					# get ranges of contiguous positions to form motifs matches.
					for _, g in itertools.groupby(enumerate(positionsBySeq[seq]),
																				lambda (index, item): index-item):
						# get the list of contiguous positions for this range.
						matchPos = [v[1] for v in g]
						# if motif match is longer than 2 nucleotides.
						if max(matchPos) - min(matchPos) > 1:
							# add current match to the list of GraphProt matches.
							fullSeqID = dynamit.utils.getFullSequenceID(sequences,
																													sequences[int(seq)][0],
																													max(matchPos)+1)
							processedResults.append(sequences[int(seq)][1][min(matchPos)-1:max(matchPos)] + \
																			"\tsequence\t" + self.searcherName + "\t" + \
																			fullSeqID + "\t" + \
																			str(min(matchPos)) + "\t" + \
																			str(max(matchPos)+1))

			# return processed motifs matches.
			return processedResults
		except (IOError, IndexError, KeyError, RuntimeError, ValueError) as e:
			print "  [GraphProtSearcher] Unexpected error:%s" % str(e)
			raise
