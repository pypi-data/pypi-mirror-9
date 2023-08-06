"""Module for GibbsSearcher classes."""

import  os, re
import subprocess
from subprocess import CalledProcessError

import dynamit.motifSearcher
import dynamit.utils

class GibbsSearcher(dynamit.motifSearcher.MotifSearcher):
	"""Class implementing a Gibbs Motif Sampler search
	component, running this tool on the provided input
	sequences with a nucleotide alphabet, eventually
	providing its processed motifs and instances.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.path = ""
		self.searcherName = "Gibbs"

	def setConfiguration(self, path, params):
		"""Loads the searcher parameters specified in the configuration file.

		Args:
			path: path of the Gibbs executable file.
			params: parameters to be passed to the Gibbs Motif
							Sampler along with the sequences filename.

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		self.path = path
		if params != "":
			self.params = params

		return 0

	def runSearch(self, sequencesFilename):
		"""Performs motif search by executing the Gibbs
		Motif Sampler motif search tool and providing
		processed results as motifs and related instances.

		Args:
			sequencesFilename: input sequences filename for this run.

		Returns:
			Returns a list of strings representing identified motif matches
			if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		# compose the complete command-line for launching Gibbs.
		completePath = os.path.join(self.path, "Gibbs") + \
																 " '" + sequencesFilename + \
																"' " + self.params + " -n"

		# prepare sequences dictionary to be later passed to processGibbsResults.
		sequences = dict([(seqRecord.description, str(seqRecord.seq)) \
				for seqRecord in dynamit.utils.getSequencesRecords(sequencesFilename)])

		try:
			# launch Gibbs and wait for its execution to
			# complete (store its stderr for use if an error happens).
			callOutput = subprocess.check_output(completePath, shell=True,
																					 stderr=subprocess.STDOUT)
			print "  [GibbsSearcher] Search completed."
			self.searchResults = self._processGibbsResults(sequences, callOutput)
		except CalledProcessError as e:
			# inform about the error that happened, and abort searcher execution.
			print "[ERROR] Gibbs execution terminated with an error:" + e.output
			return 1

		print "  [GibbsSearcher] Execution completed."
		return self.searchResults

	def _processGibbsResults(self, sequences, results):
		""" Process results contained in Gibbs output files to
		produce a table for subsequent DynaMIT phases.

		Args:
			sequences: a dictionary of sequences (id is key, sequence is value).
			results: the Gibbs Motif Sampler console output.
		Returns:
			Returns a list of strings, one per motif match, containing
			motif sequence, sequence id, match position, etc.
		"""
		try:
			lines = results.split('\n')

			processedResults = []
			isInMotif = False
			isInInstances = False

			i = 0
			while i < len(lines):
				line = lines[i].rstrip('\n')
				# if we are inside a motif already.
				if isInMotif:
					# if motifs instances lines are beginning.
					if line.startswith("Num Motifs"):
						isInInstances = True
					else:
						if isInInstances:
							# current motif instances section just ended.
							if line.startswith("        "):
								isInInstances = False
								isInMotif = False
							else:
								# add current instance to processed results if not
								# already seen (to avoid duplicate matches).
								info = re.split(r'\s+', line)
								endIndex = len(info) - 4
								start = info[3] if int(info[3]) < int(info[endIndex]) else info[endIndex]
								end = info[endIndex] if int(info[endIndex]) > int(info[3]) else info[3]
								fullSeqID = dynamit.utils.getFullSequenceID(sequences,
																														info[len(info) - 1],
																														int(end))
								fullSeqID = info[len(info) - 1] if fullSeqID == -1 else fullSeqID
								match = info[5] + "\tsequence\t" + self.searcherName + \
												"\t" + fullSeqID + "\t" + start + "\t" + \
												end + "\t" + str(float(info[len(info) - 3])*100.0) + \
												"\t" + info[len(info) - 2]

								if not match in processedResults:
									processedResults.append(match)
				# we have found a new motif beginning line.
				elif line.endswith("---------------") and \
						 lines[i+1].find("    MOTIF") >= 0:
					# we have reached the start of a motif, so
					isInMotif = True
					# skip the motif header line and continue.
					i += 2
					continue

				# go to the next output line.
				i += 1

			return processedResults
		except (IOError, IndexError, RuntimeError, ValueError) as e:
			print "  [GibbsSearcher] Unexpected error: %s" % str(e)
			return 1
