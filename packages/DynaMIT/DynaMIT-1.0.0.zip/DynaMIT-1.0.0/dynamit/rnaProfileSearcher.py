"""Module for RNAprofileSearcher classes."""

import os
import subprocess
from subprocess import CalledProcessError

from Bio.Seq import Seq
from Bio.Alphabet import IUPAC, Gapped
from Bio.motifs import Motif, Instances

import dynamit.motifSearcher
import dynamit.utils

class RNAprofileSearcher(dynamit.motifSearcher.MotifSearcher):
	"""Class implementing an RNAprofile RNA secondary
	structure motif search component, running this tool
	on the provided input sequences and providing its
	processed motifs and instances as results.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.path = ""
		self.searcherName = "RNAprofile"

	def setConfiguration(self, path, params):
		"""Loads the searcher parameters specified in the configuration file.

		Args:
			path: path of the RNAprofile executable file.
			params: parameters to be passed to RNAprofile
							along with the sequences filename.

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		self.path = path
		self.params = params
		return 0

	def runSearch(self, sequencesFilename):
		"""Performs motif search by executing the RNAprofile
		secondary structure motif search tool and processing
		its results to provide motifs and related instances.

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
		# now convert sequences file to single line sequences FASTA
		singleLineFilename = os.path.splitext(filteredFilename)[0] + \
												 "_singleLine.fasta"
		if dynamit.utils.makeSingleLineFASTA(filteredFilename,
																					singleLineFilename) != 0:
			print "[ERROR] Unable to create single line sequences file."
			return 1

		# compose the complete command-line for launching RNAprofile.
		completePath = os.path.join(self.path, "rnaprofile") + \
																 " -f \"" + singleLineFilename + \
																"\" " + self.params

		# prepare sequences dictionary to be later passed
		# to processRNAprofileResults
		sequences = dict([(seqRecord.description, str(seqRecord.seq)) \
											for seqRecord in \
											dynamit.utils.getSequencesRecords(singleLineFilename)])

		try:
			# launch RNAprofile and wait for its execution to
			# complete (store its stderr for use if an error happens).
			callOutput = subprocess.check_output(completePath, shell=True,
																					 stderr=subprocess.STDOUT)
			rpfFilename = ""
			# check if RNAprofile results exist by getting the
			# output RNAprofile filename from its console output.
			lines = callOutput.split('\n')
			if len(lines) > 2:
				info = lines[-2].split('\'')
				if len(info) == 3:
					rpfFilename = info[1]
				else:
					raise ValueError('')
			else:
				raise ValueError('')

			# if the output file exists, proceed to results extraction.
			if os.path.isfile(rpfFilename):
				print "  [RNAprofileSearcher] Search completed."
				self.searchResults = self._processRNAprofileResults(sequences,
																													 rpfFilename)
			else:
				raise ValueError('')
		except ValueError:
			print "[ERROR] Could not find RNAprofile results file."
			return 1
		except CalledProcessError as e:
			# inform about the error that happened, and abort searcher execution.
			print "[ERROR] RNAprofile execution terminated with an error:" + e.output
			return 1

		print "  [RNAprofileSearcher] Execution completed."
		return self.searchResults

	def _processRNAprofileResults(self, sequences, resultsFilename):
		""" Process results contained in RNAprofile output files to
		produce a table for subsequent DynaMIT phases.

		Args:
			resultsFilename: the RNAprofile results filename.
		Returns:
			Returns a list of strings, one per motif match, containing
			motif sequence, sequence id, match position, etc.
		"""
		print "  [RNAprofileSearcher] Processing results: <", \
					os.path.basename(resultsFilename), ">"
		try:
			with open(resultsFilename) as f:
				lines = f.readlines()

			profilesAlphabet = Gapped(IUPAC.unambiguous_dna)
			processedResults = []
			isInProfile = False
			profileLength = 0
			profileMatches = []

			i = 0
			while i < len(lines):
				line = lines[i].rstrip('\n')

				if isInProfile:
					# collect profile instances to find matches and build
					# the profile consensus.
					if line.startswith(">"):
						# get current profile match sequence ID.
						fullSeqID = dynamit.utils.getFullSequenceID(sequences,
																		line.rstrip('\n').lstrip('>'), 0)
						fullSeqID = line.rstrip('\n').lstrip('>') if fullSeqID == -1 \
																											 else fullSeqID
						# get match information.
						sequenceChunk = lines[i+1].rstrip('\n').upper()
						structureChunk = lines[i+2].rstrip('\n').split(' ')[0]
						fitness = lines[i+2].rstrip('\n').split(' ')[4].rstrip(')')
						chunkPos = sequences[fullSeqID].find(sequenceChunk) + 1
						# if the motif instance was not found on the sequence, we
						# likely selected the wrong full sequence ID, so try again
						# systematically on all sequence until found.
						if chunkPos == 0:
							for seqId, seq in sequences.iteritems():
								if seqId.startswith(line.rstrip('\n').lstrip('>')):
									chunkPos = seq.find(sequenceChunk) + 1
									if chunkPos > 0:
										fullSeqID = seqId
										break
						# update profile max length and store match for later.
						profileLength = max(profileLength, len(sequenceChunk))
						profileMatches.append((fullSeqID, sequenceChunk,
																	str(chunkPos),
																	str(chunkPos + len(sequenceChunk)),
																	fitness,
																	structureChunk))
						i += 2
						continue
					elif line == "":
						# a profile just ended, so compute its consensus.
						profileInstances = [Seq(match[1].ljust(profileLength, "-"),
																		alphabet=profilesAlphabet) \
																for match in profileMatches]
						profileMotif = Motif(instances=Instances(instances=profileInstances),
																 alphabet=profilesAlphabet)
						# then add its matches to the results.
						for match in profileMatches:
							processedResults.append(str(profileMotif.consensus) + \
																		"\tstructure\t" + self.searcherName + \
																		"\t" + match[0] + "\t" + match[2] + \
																		"\t" + match[3] + "\t" + match[4] + \
																		"\t" + match[5])
						# reset variables for the next profile.
						profileMatches = []
						isInProfile = False
				elif line.startswith("Profile "):
					# we have reached the start of a profile, so
					isInProfile = True
					# skip the profile matrix and go directly
					# to instances lines.
					i += 13
					continue

				i += 1
			return processedResults
		except (IOError, IndexError, KeyError, RuntimeError, ValueError) as e:
			print "  [RNAprofileSearcher] Unexpected error: %s" % str(e)
			return 1
