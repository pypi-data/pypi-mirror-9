"""Module for RNAhybridSearcher classes."""

import os, math
import subprocess
from subprocess import CalledProcessError

import dynamit.motifSearcher
import dynamit.utils

class RNAhybridSearcher(dynamit.motifSearcher.MotifSearcher):
	"""Class implementing an RNAhybrid motif search component,
	finding regions of hybridization of an RNA sequence with
	one or more provided miRNA sequences; the component runs
	this tool on the provided input sequences, providing its
	processed miR matches and instances as results.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.path = ""
		self.miRNAsequence = ""
		self.params = ""
		self.searcherName = "RNAhybrid"

	def setConfiguration(self, path, params):
		"""Loads the searcher parameters specified in the configuration file.

		Args:
			path: path of the RNAhybrid executable file.
			params: parameters to be passed to RNAhybrid
							along with the sequences filename.

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		self.path = path

		info = params.split(';')
		# store miRNA sequence to be matched.
		self.miRNAsequence = info[0]
		# store tool parameters, if any.
		if len(info) > 1:
			self.params = info[1]
		# if neither a miR query sequence nor a miR query file
		# were specified, abort configuration.
		if self.miRNAsequence == "" and self.params.find("-q ") < 0:
			print "[ERROR] miRNA sequence specification missing."
			return 1

		return 0

	def runSearch(self, sequencesFilename):
		"""Performs motif search by executing the RNAhybrid
		miRNA-RNA hybridization regions search tool; then
		processes the resulting regions to provide matching
		miRs and related instances.

		Args:
			sequencesFilename: input sequences filename for this run.

		Returns:
			Returns a list of strings representing identified motif matches
			if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		# convert sequences file to single line sequences FASTA
		singleLineFilename = os.path.splitext(sequencesFilename)[0] + \
												 "_singleLine.fasta"
		if (dynamit.utils.makeSingleLineFASTA(sequencesFilename,
																					singleLineFilename) != 0):
			print "[ERROR] Unable to create single line sequences file."
			return 1

		# prepare sequences dictionary to be later passed to processRNAhybridResults.
		sequences = dict([(seqRecord.description, str(seqRecord.seq)) \
				for seqRecord in dynamit.utils.getSequencesRecords(singleLineFilename)])

		# compose the complete command-line for launching RNAhybrid.
		completePath = os.path.join(self.path, "RNAhybrid") + \
									 " -t '" + singleLineFilename + \
									 "' " + self.params + " " + self.miRNAsequence
		try:
			# launch RNAhybrid and wait for its execution to
			# complete (store its stderr for use if an error happens).
			callOutput = subprocess.check_output(completePath, shell=True,
																					 stderr=subprocess.STDOUT)
			print "  [RNAhybridSearcher] Search completed."
			self.searchResults = self._processRNAhybridResults(sequences, callOutput)
		except CalledProcessError as e:
			# inform about the error that happened, and abort searcher execution.
			print "[ERROR] RNAhybrid execution terminated with an error:" + e.output
			return 1

		print "  [RNAhybridSearcher] Execution completed."
		return self.searchResults

	def _processRNAhybridResults(self, sequences, results):
		""" Process results contained in RNAhybrid output files to
		produce a table for subsequent DynaMIT phases.

		Args:
			sequences: a dictionary of sequences (id is key, sequence is value).
			results: the RNAhybrid console output.
		Returns:
			Returns a list of strings, one per motif match, containing
			motif sequence, sequence id, match position, etc.
		"""
		try:
			lines = results.split('\n')
			processedResults = []

			i = 0
			while i < len(lines):
				# if we are at the start of a target instance.
				if lines[i].startswith("target: "):
					# get matching miR ID (if not a single miR specified
					# through the command-line).
					mirID = "_" + lines[i+2].rstrip('\n').split(" ")[-1] \
									if not lines[i+2].rstrip('\n').endswith("command_line") else ""
					# get the match p-value.
					pval = float(lines[i+6].rstrip('\n').lstrip("p-value: "))
					# get the miR match position and sequence.
					start = int(lines[i+8].rstrip('\n').split(' ')[-1]) + 1
					matchSeq = lines[i+10].rstrip('\n').replace(" ", "")
					consensus = matchSeq if mirID != "" else self.miRNAsequence
					# get matching input sequence ID
					fullSeqID = dynamit.utils.getFullSequenceID(sequences,
																		lines[i].rstrip('\n').lstrip("target: "),
																		start + len(matchSeq))
					fullSeqID = lines[i].rstrip('\n').lstrip("target: ") \
											if fullSeqID == -1 else fullSeqID
					# add the match to the list of results.
					processedResults.append(consensus + "\tstructure\t" + \
												self.searcherName + mirID + \
												"\t" + fullSeqID + "\t" + str(start) + "\t" + \
												str(start + len(matchSeq)) + "\t" + \
												str(-1.0* math.log(pval, 10)))

				# go to the next output line.
				i += 1

			return processedResults
		except (IOError, IndexError, RuntimeError, ValueError) as e:
			print "  [RNAhybridSearcher] Unexpected error: %s" % str(e)
			return 1
