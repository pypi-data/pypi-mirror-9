"""Module for MEMERISSearcher classes."""

import os, math, re
import subprocess
from subprocess import CalledProcessError

import dynamit.motifSearcher
import dynamit.utils

class MEMERISSearcher(dynamit.motifSearcher.MotifSearcher):
	"""Class implementing a MEMERIS RNA motif search
	component, running the MEME tool on the provided
	input sequences, eventually providing its
	processed motifs and instances.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.searcherName = "MEMERIS"
		self.path = ""
		self.params = "-nmotifs 5"
		self.motifLength = 6

	def setConfiguration(self, path, params):
		"""Loads the searcher parameters specified in the configuration file.

		Args:
			path: path of the MEMERIS executable file.
			params: parameters to be passed to MEMERIS
							along with the sequences filename.

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if path != "":
			self.path = path
		if params != "":
			self.params = params
			if params.find("-w") >= 0:
				try:
					# -w was specified so try to read its value.
					self.motifLength = int(params[params.find("-w") + 3:
																 params.find(" ", params.find("-w") + 3)])
					# remove it from params as we insert it in the code in both
					# MEMERIS execution steps.
					self.params = self.params.replace("-w " + str(self.motifLength), "")
				except ValueError:
					print "[ERROR] Uncorrect parameter specification (-w)."
					return 1
		return 0

	def runSearch(self, sequencesFilename):
		"""Performs motif search by executing the MEMERIS
		RNA motif search tool and processing its results
		to provide motifs and related instances.

		Args:
			sequencesFilename: input sequences filename for this run.

		Returns:
			Returns a list of strings representing identified motif matches
			if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""

		# remove all sequences shorter than 8nts (MEMERIS would crash)
		# and save remaining ones into a new "filtered" file.
		filteredFilename = os.path.splitext(sequencesFilename)[0] + \
											 "_8ntOrLonger.fasta"
		if dynamit.utils.removeSequencesShorterThan(8,
											sequencesFilename, filteredFilename) != 0:
			print "[ERROR] Unable to length-filter sequences file."
			return 1
		# now make the sequences single-line to avoid RNA folding issues.
		finalFilename = os.path.splitext(filteredFilename)[0] + \
												 "_singleLine.fasta"
		if (dynamit.utils.makeSingleLineFASTA(filteredFilename,
																					finalFilename) != 0):
			print "[ERROR] Unable to create single line sequences file."
			return 1

		# prepare sequences dictionary to be later passed to processMEMERISResults.
		sequences = dict([(seqRecord.description, str(seqRecord.seq)) \
				for seqRecord in dynamit.utils.getSequencesRecords(finalFilename)])

		# compose the complete command-line for launching MEMERIS.
		try:
			# launch MEMERIS first step: compute EF/PU values.
			completePath = os.path.join(self.path, "GetSecondaryStructureValues.perl") + \
										 " -f \"" + finalFilename + \
										 "\" -l " + str(self.motifLength)
			subprocess.check_output(completePath, shell=True, stderr=subprocess.STDOUT)

			# launch MEMERIS second step and wait for its execution to
			# complete (mute its output by redirecting it to ).
			completePath = os.path.join(self.path, "memeris") + \
										 " \"" + finalFilename + \
										 "\" -dna -w " + str(self.motifLength) + \
										 " -secstruct \"" + finalFilename + ".sec\" " + \
										 self.params  + " -maxsize 10000000 "
			callOutput = subprocess.check_output(completePath, shell=True,
																						stderr=subprocess.STDOUT)

			# extract results from MEMERIS output files.
			print "  [MEMERISSearcher] Search completed."
			self.searchResults = self._processMEMERISResults(sequences, callOutput)
			# inform of successful execution and return the results.
			print "  [MEMERISSearcher] Execution completed."
			return self.searchResults
		except CalledProcessError as e:
			# inform about the error that happened, and abort searcher execution.
			print "[ERROR] MEMERIS execution terminated with an error:" + e.output
			return 1

	def _processMEMERISResults(self, sequences, results):
		""" Process results contained in MEMERIS output to
		produce a table for subsequent DynaMIT phases.

		Args:
			sequences: a dictionary of sequences (id is key, sequence is value).
			results: MEMERIS console output.
		Returns:
			Returns a list of strings, one per motif match, containing
			motif sequence, sequence id, match position, etc.
		"""
		processedResults = []

		try:
			# get results lines from MEMERIS output.
			lines = results.split('\n')

			lineIndex = 0
			inMotifSites = False
			currentMotifConsensus = ""
			while lineIndex < len(lines):
				# this line contains a new motif consensus.
				if lines[lineIndex].startswith("Multilevel "):
					# get current motif consensus.
					currentMotifConsensus = re.split(r'\s+', lines[lineIndex].rstrip('\n'))[1]
				# must match "	Motif N sites", i.e. motif sites header line.
				elif re.match(r"\sMotif\s[0-9]+\ssites\ssorted", lines[lineIndex]):
					# move to the first motif site line
					lineIndex += 3
					inMotifSites = True
				# matches the end of motif sites lines.
				elif lines[lineIndex].startswith("--------------------------------"):
					inMotifSites = False
				# this is a motif site line.
				elif inMotifSites:
					info = re.split(r'\s+', lines[lineIndex].rstrip('\n'))
					if len(info) > 3:
						# append current motif match to results in DynaMIT format.
						fullSeqID = dynamit.utils.getFullSequenceID(sequences, info[0],
																		int(info[1]) + len(currentMotifConsensus))
						fullSeqID = info[0] if fullSeqID == -1 else fullSeqID
						processedResults.append(currentMotifConsensus + "\tsequence\t" + \
																		self.searcherName + "\t" + \
																		fullSeqID + "\t" + info[1] + "\t" + \
																		str(int(info[1]) +
																				len(currentMotifConsensus)) + "\t" + \
																		info[2] + "\t" + \
																		str(-1.0* math.log(float(info[6]), 10)))
				lineIndex += 1

			return processedResults
		except (IOError, IndexError, ValueError, RuntimeError) as e:
			print "  [MEMERISSearcher] Unexpected error: %s" % str(e)
