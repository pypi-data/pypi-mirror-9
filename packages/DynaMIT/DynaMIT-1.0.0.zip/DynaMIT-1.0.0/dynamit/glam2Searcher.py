"""Module for GLAM2Searcher classes."""

import os, math, re
import subprocess
from subprocess import CalledProcessError

import dynamit.motifSearcher
import dynamit.utils

class GLAM2Searcher(dynamit.motifSearcher.MotifSearcher):
	"""Class implementing a GLAM2 gapped motif search
	component, running the GLAM2 tool on the provided input
	sequences with a nucleotide alphabet, eventually
	providing its processed motifs and instances.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.searcherName = "GLAM2"
		self.path = ""
		self.params = ""

	def setConfiguration(self, path, params):
		"""Loads the searcher parameters specified in the configuration file.

		Args:
			path: path of the GLAM2 executable file.
			params: parameters to be passed to GLAM2
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
		"""Performs motif search by executing the GLAM2
		gapped motif search tool and processing its results
		to provide motifs and related instances.

		Args:
			sequencesFilename: input sequences filename for this run.

		Returns:
			Returns a list of strings representing identified motif matches
			if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""

		# remove all sequences shorter than 8nts (GLAM2 would crash)
		# and save remaining ones into a new "filtered" file.
		filteredFilename = os.path.splitext(sequencesFilename)[0] + \
											 "_8ntOrLonger.fasta"
		if dynamit.utils.removeSequencesShorterThan(8,
											sequencesFilename, filteredFilename) != 0:
			print "[ERROR] Unable to length-filter sequences file."
			return 1

		# compose the complete command-line for launching GLAM2.
		completePath = os.path.join(self.path, "glam2") + " " + self.params + \
									 (" " if len(self.params) > 0 else "") + \
									 "n \"" + filteredFilename + "\""
		try:
			# launch GLAM2 and wait for its execution to
			# complete (mute its output by redirecting it to ).
			# GLAM2 creates a subfolder with all its results files,
			# which is left intact in case the user wants to have a look at it.
			subprocess.check_output(completePath, shell=True,
															stderr=subprocess.STDOUT)
			# check if GLAM2 results exist
			if os.path.isfile(os.path.join("glam2_out/", "glam2.txt")):
				# extract results from GLAM2 output files.
				print "  [GLAM2Searcher] Search completed."
				self.searchResults = self._processGLAM2Results(
														 filteredFilename,
														 os.path.join("glam2_out/", "glam2.txt"))
				# inform of successful execution and return the results.
				print "  [GLAM2Searcher] Execution completed."
				return self.searchResults
			else:
				print "[ERROR] Could not find GLAM2 results files."
				return 1
		except CalledProcessError as e:
			# inform about the error that happened, and abort searcher execution.
			print "[ERROR] GLAM2 execution terminated with an error:" + e.output
			return 1

	def _processGLAM2Results(self, sequencesFilename, resultsFilename):
		""" Process results contained in GLAM2 output files to
		produce a table for subsequent DynaMIT phases.

		Args:
			sequencesFilename: input sequences filename for this run.
			resultsFilename: the GLAM2 results filename.
		Returns:
			Returns a list of strings, one per motif match, containing
			motif sequence, sequence id, match position, etc.
		"""
		processedResults = []

		try:
			# get results lines from GLAM2 output file
			with open(resultsFilename) as f:
				lines = f.readlines()

			# get sequences (GLAM2 cuts their iD after a certain number of chars.,
			# so need to get the full version to output in processed results).
			sequences = dict([(seqRecord.description, str(seqRecord.seq)) \
				for seqRecord in dynamit.utils.getSequencesRecords(sequencesFilename)])

			lineIndex = 0
			inMotifSites = False
			currentMotifMatches = []
			while lineIndex < len(lines):
				# this line contains a new motif consensus
				if lines[lineIndex].startswith("Score: "):
					# move to the first motif site line
					lineIndex += 3
					inMotifSites = True
					continue
				# this is a motif site line or
				# section end prior to motif consensus.
				elif inMotifSites:
					# motif sites are finished, so get the consensus,
					# write down this motif matches and reset stuff for the next motif.
					if lines[lineIndex] == "\n":
						currentMotifConsensus = re.split(r'\s+', lines[lineIndex + 1].\
																		rstrip('\n'))[1].upper()
						processedResults.extend([currentMotifConsensus + match \
																		 for match in currentMotifMatches])
						inMotifSites = False
						currentMotifMatches = []
					# this is truly a site for the current motif.
					else:
						info = re.split(r'\s+', lines[lineIndex].rstrip('\n'))
						# get the match full sequence ID.
						fullSeqID = dynamit.utils.getFullSequenceID(sequences,
																												info[0],
																												int(info[3]))
						fullSeqID = info[0] if fullSeqID == -1 else fullSeqID
						# append current motif match to results in DynaMIT format
						currentMotifMatches.append("\tsequence\t" + self.searcherName + \
																		"\t" + fullSeqID + "\t" + info[1] + \
																		"\t" + info[3] + "\t" + \
																		str(-1.0* math.log(float(info[5]), 10)))
				# move to the next results line.
				lineIndex += 1

			return processedResults
		except (IOError, IndexError, KeyError, ValueError, RuntimeError) as e:
			print "  [GLAM2Searcher] Unexpected error: %s" % str(e)
			return 1
