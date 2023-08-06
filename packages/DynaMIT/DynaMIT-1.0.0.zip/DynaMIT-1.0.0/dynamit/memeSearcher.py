"""Module for MEMESearcher classes."""

import os, math, re
import subprocess
from subprocess import CalledProcessError

import dynamit.motifSearcher
import dynamit.utils

class MEMESearcher(dynamit.motifSearcher.MotifSearcher):
	"""Class implementing a MEME motif search component,
	running the MEME tool on the provided input
	sequences with a nucleotide alphabet, eventually
	providing its processed motifs and instances.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.searcherName = "MEME"
		self.path = ""
		self.params = "-dna -nmotifs 10"

	def setConfiguration(self, path, params):
		"""Loads the searcher parameters specified in the configuration file.

		Args:
			path: path of the MEME executable file.
			params: parameters to be passed to MEME
							along with the sequences filename.

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if path != "":
			self.path = path
		if params != "":
			self.params = params
		return 0

	def runSearch(self, sequencesFilename):
		"""Performs motif search by executing the MEME
		motif search tool and processing its results
		to provide motifs and related instances.

		Args:
			sequencesFilename: input sequences filename for this run.

		Returns:
			Returns a list of strings representing identified motif matches
			if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""

		# remove all sequences shorter than 8nts (MEME would crash)
		# and save remaining ones into a new "filtered" file.
		filteredFilename = os.path.splitext(sequencesFilename)[0] + \
											 "_8ntOrLonger.fasta"
		if dynamit.utils.removeSequencesShorterThan(8,
											sequencesFilename, filteredFilename) != 0:
			print "[ERROR] Unable to length-filter sequences file."
			return 1

		# prepare sequences dictionary to be later passed to processMEMEResults.
		sequences = dict([(seqRecord.description, str(seqRecord.seq)) \
				for seqRecord in dynamit.utils.getSequencesRecords(filteredFilename)])

		# compose the complete command-line for launching MEME.
		completePath = os.path.join(self.path, "meme") + " \"" + \
									 filteredFilename + "\" " + self.params + \
									 " -maxsize 10000000 -oc meme_results"

		try:
			# launch MEME and wait for its execution to
			# complete (mute its output by redirecting it to ).
			# MEME creates a subfolder with all its results files,
			# which is left intact in case the user wants to have a look at it.
			subprocess.check_output(completePath, shell=True, stderr=subprocess.STDOUT)
			# check if MEME results exist
			if os.path.isfile(os.path.join("meme_results/", "meme.txt")):
				# extract results from MEME output files.
				print "  [MEMESearcher] Search completed."
				self.searchResults = self._processMEMEResults(sequences,
														 os.path.join("meme_results/", "meme.txt"))
				# inform of successful execution and return the results.
				print "  [MEMESearcher] Execution completed."
				return self.searchResults
			else:
				print "[ERROR] Could not find MEME results files."
				return 1
		except CalledProcessError as e:
			# inform about the error that happened,
			print "[ERROR] MEME execution terminated with an error:" + e.output
			# abort searcher execution.
			return 1

	def _processMEMEResults(self, sequences, resultsFilename):
		""" Process results contained in MEME output files to
		produce a table for subsequent DynaMIT phases.

		Args:
			sequences: a dictionary of sequences (id is key, sequence is value).
			resultsFilename: the MEME results filename.
		Returns:
			Returns a list of strings, one per motif match, containing
			motif sequence, sequence id, match position, etc.
		"""
		processedResults = []

		try:
			# get results lines from MEME output file
			with open(resultsFilename) as f:
				lines = f.readlines()

			lineIndex = 0
			inMotifSites = False
			currentMotifConsensus = ""
			while lineIndex < len(lines):
				# this line contains a new motif consensus
				if lines[lineIndex].startswith("Multilevel "):
					# get current motif consensus
					currentMotifConsensus = re.split(r'\s+', lines[lineIndex].rstrip('\n'))[1]
				# must match "	Motif N sites", i.e. motif sites header line
				elif re.match(r"\sMotif\s[0-9]+\ssites\ssorted", lines[lineIndex]):
					# move to the first motif site line
					lineIndex += 3
					inMotifSites = True
				# matches the end of motif sites lines
				elif lines[lineIndex].startswith("--------------------------------"):
					inMotifSites = False
				# this is a motif site line
				elif inMotifSites:
					info = re.split(r'\s+', lines[lineIndex].rstrip('\n'))
					# append current motif match to results in DynaMIT format
					fullSeqID = dynamit.utils.getFullSequenceID(sequences, info[0],
																		int(info[1]) + len(currentMotifConsensus))
					fullSeqID = info[0] if fullSeqID == -1 else fullSeqID
					processedResults.append(currentMotifConsensus + "\tsequence\t" + \
																	self.searcherName + "\t" + \
																	fullSeqID + "\t" + info[1] + "\t" + \
																	str(int(info[1]) +
																			len(currentMotifConsensus)) + "\t" + \
																	str(-1.0* math.log(float(info[2]), 10)))
				lineIndex += 1

			return processedResults
		except (IOError, IndexError, ValueError, RuntimeError) as e:
			print "  [MEMESearcher] Unexpected error: %s" % str(e)
