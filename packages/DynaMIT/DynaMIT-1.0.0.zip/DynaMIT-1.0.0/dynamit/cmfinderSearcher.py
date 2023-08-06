"""Module for CMfinderSearcher classes."""

import os, re
import subprocess
from subprocess import CalledProcessError

import dynamit.motifSearcher
import dynamit.utils

class CMfinderSearcher(dynamit.motifSearcher.MotifSearcher):
	"""Class implementing a CMfinder motif search component,
	running the CMfinder tool on the provided input sequences,
	exploiting its CombMotif.pl helper script to merge similar
	motifs and finally providing processed motifs and instances.
	"""

	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.path = ""
		self.searcherName = "CMfinder"

	def setConfiguration(self, path, params):
		"""Loads the searcher parameters specified in the configuration file.

		Args:
			path: path of the CMfinder executable file.
			params: parameters to be passed to CMfinder
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
		"""Performs motif search by running the CMfinder
		tool, combining its resulting motifs with the
		helper CombMotif.pl script and processing the
		resulting combined motifs and related instances.

		Args:
			sequencesFilename: input sequences filename for this run.

		Returns:
			Returns a list of strings representing identified motif matches
			if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		# compose the complete command-line for launching CMfinder.
		completePath = os.path.join(self.path, "cmfinder.pl ") + \
																self.params + " \"" + \
																os.path.basename(sequencesFilename) + "\" ''"

		# remove previous CMfinder motifs files with the same sequence prefix
		# (if any) as they would interfere with CombMotifs later on.
		for filename in os.listdir(os.getcwd()):
			if filename.find(".motif.h") > 0:
				os.remove(filename)

		# prepare sequences dictionary to be later passed to processCMfinderResults.
		sequences = dict([(seqRecord.description, str(seqRecord.seq)) \
				for seqRecord in dynamit.utils.getSequencesRecords(sequencesFilename)])

		try:
			# launch CMfinder motif identification (first step).
			callOutput = subprocess.check_output(completePath, shell=True,
																					 stderr=subprocess.STDOUT)

			# get individual motifs output filenames from cmfinder.pl console output.
			motifsFilenames = [line.replace("Alignment saved in file ", "").\
												 replace("align", "motif") \
												 for line in callOutput.split('\n') \
												 if line.startswith("Alignment saved in file")]

			# check if CMfinder output included results filenames
			if len(motifsFilenames) > 0:
				# compose the path for performing CMfinder motifs combination.
				completePath = os.path.join(self.path, "CombMotif.pl") + \
																" \"" + os.path.basename(sequencesFilename) \
																+ "\" " + "\"" + \
																"\" \"".join(motifsFilenames) + "\""

				# launch CMfinder motif combination (second and last step).
				callOutput = subprocess.check_output(completePath, shell=True)

				# get merged motifs output filenames from cmfinder.pl console output.
				# check for successful combination and results file presence
				mergedMotifsInfo = [line.replace("Merge ", "").\
												 split(" > ") \
												 for line in callOutput.split('\n') \
												 if line.startswith("Merge")]

				# compose the list of final motifs filenames, made of merged
				# motifs and motifs which where not merged (remove motifs
				# which are part of a merged motif).
				finalMotifsFilenames = []
				for motif in motifsFilenames:
					isNonMergedMotif = True
					for info in mergedMotifsInfo:
						# if this motif is part of a merged motif.
						if info[0].find(motif) >= 0:
							isNonMergedMotif = False
					# if the motif was found as never merged,
					# add it to the list of final motifs.
					if isNonMergedMotif:
						finalMotifsFilenames.append(motif)
				# add merged motifs to the list of final motifs.
				finalMotifsFilenames.extend([info[1] for info in mergedMotifsInfo])

				# if any, process final motifs to extract consensus and matches.
				if len(finalMotifsFilenames) > 0:
					print "  [CMfinderSearcher] Search completed."
					self.searchResults = self._processCMfinderResults(sequences,
																														finalMotifsFilenames)
				else:
					raise ValueError("Could not find CMfinder results files.")
			else:
				raise ValueError("Could not find CMfinder results files.")
		except ValueError as e:
			print "[ERROR] " + str(e)
			return 1
		except CalledProcessError as e:
			# inform about the error that happened and abort searcher execution.
			print "[ERROR] CMfinder execution terminated with an error:" + e.output
			return 1

		# everything went fine, so return the processed results.
		print "  [CMfinderSearcher] Execution completed."
		return self.searchResults

	def _processCMfinderResults(self, sequences, motifsFilenames):
		""" Process results contained in CMfinder output files to
		produce a table for subsequent DynaMIT phases.

		Args:
			sequences: a dictionary of sequences (id is key, sequence is value).
			motifsFilenames: list containing CMfinder-derived motifs filenames.
		Returns:
			Returns a list of strings, one per motif match, containing
			motif sequence, sequence id, match position, etc.
		"""
		# final list of processed results for all CMfinder motifs.
		processedResults = []

		try:
			for motifFile in motifsFilenames:

				# store sequence and secondary structure consensus (could be
				# multiline as per the Stockholm format if the motif is too
				# long for a single line, so need to use these variables to
				# "append" parts of these consensus).
				seqConsensus = ""
				structConsensus = ""

				# temporary processed motif matches list (matches will be
				# completed with sequence and structure consensus at the
				# end of file parsing, when we have collected these consensus).
				motifProcessedMatches = []

				# read current motif file lines.
				with open(motifFile) as f:
					lines = f.readlines()

				for line in lines:
					# motif instance position and score line.
					if line.startswith("#=GS") and line.find(" DE ") > 0:
						info = re.split(r'\s+', line.rstrip('\n'))
						print info
						start = info[3].rstrip('.') if len(info) > 5 \
										else re.split(r'\.+', info[3])[0]
						end = info[4] if len(info) > 5 else re.split(r'\.+', info[3])[1]
						score = info[5] if len(info) > 5 else info[4]
						fullSeqID = dynamit.utils.getFullSequenceID(sequences,
																												info[1], int(end))
						fullSeqID = info[1] if fullSeqID == -1 else fullSeqID
						# add motif instance to processed results.
						motifProcessedMatches.append("structure\t" + self.searcherName + \
																				 "\t" + fullSeqID + "\t" + start + \
																				 "\t" + end + "\t" + score)
					# sequence consensus line.
					if line.startswith("#=GC RF"):
						seqConsensus += re.split(r'\s+', line.rstrip('\n'))[2]
					# secondary structure consensus line.
					if line.startswith("#=GC SS_cons"):
						structConsensus += re.split(r'\s+', line.rstrip('\n'))[2]

				# complete motif matches in processed results with
				# sequence and structure consensus, and append them
				# to the global list of processed matches.
				processedResults.extend([seqConsensus + "\t" + \
																 match + "\t" + structConsensus \
																 for match in motifProcessedMatches])

			return processedResults
		except (IOError, IndexError, RuntimeError, ValueError) as e:
			print "  [CMfinderSearcher] Unexpected error: %s" % str(e)
