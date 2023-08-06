"""Module for RegionsIntersectionSearcher classes."""

import re

import dynamit.motifSearcher
import dynamit.utils

class RegionsIntersectionSearcher(dynamit.motifSearcher.MotifSearcher):
	"""Class implementing a regions intersection motif searcher,
	which performs the coordinates-wise intersection of the input
	sequences (if their coordinates are specified in the FASTA header)
	with a set of regions, the BED file of which is specified in the
	configuration. This allows to have motifs instances as regions
	which intersect the input sequences; name of the searcher and
	consensus to be used as motif consensus can be specified in the
	searcher configuration.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.searcherName = "RegionsIntersection"
		self.searchResults = []
		self.path = ""
		self.regions = []
		self.trackName = ""
		self.trackConsensus = ""

	def setConfiguration(self, path, params):
		"""Loads the searcher parameters specified in the configuration file.

		Args:
			path: path of the BED file containing regions to be
						intersected with input sequences.
			params: track name associated to the specified BED file.

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		# store the path of the BED file containing regions to be intersected
		self.path = path

		# the parameters here are the TRACK name and its consensus
		# (to "name" the searcher/motif and compare it to the others).
		info = params.split(',')
		self.trackName = info[0]
		self.trackConsensus = info[1] if len(info) > 1 else self.trackName

		return 0

	def runSearch(self, sequencesFilename):
		"""Performs motif search, intersecting input sequences
		with the regions specified in the configuration.

		Args:
			sequencesFilename: input sequences filename for this run.

		Returns:
			Returns a list of strings representing identified motif matches
			if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		# load sequences from the input file
		sequences = dynamit.utils.getSequencesRecords(sequencesFilename)

		try:
			# extract and store regions from the BED file.
			with open(self.path) as bedHandle:
				for line in bedHandle.readlines():
					info = line.rstrip('\n').split('\t')
					# check the presence of the minimum required fields.
					if len(info) >= 3:
						# if there are further field after the three required
						# ones they will be appended at the end by info[3:].
						# if there are none, nothing will be appended.
						self.regions.append([info[0], int(info[1]), int(info[2])] + info[3:])
					else:
						raise ValueError(" the specified BED regions file "\
														 "lacks the required three fields.")
			# check that we have a set of regions to intersect, otherwise abort.
			if len(self.regions) == 0:
				print "[ERROR] No regions to intersect with input sequences."
				return 1
		except IOError:
			print "[ERROR] Cannot read the specified BED regions file."
			return 1
		except (IndexError, ValueError, RuntimeError) as e:
			print "[ERROR] Execution error: " + str(e)
			return 1

		# intersect BED file regions with the sequences
		# (only the ones having a position in the from chrN:start-end indicated
		#  in their sequence header line)
		print "  [RegionsIntersectionSearcher] Intersecting BED regions and " \
					"input sequences..."
		for sequence in sequences:
			coordinates = re.search(r"chr[0-9,X,Y,M]+\:[0-9]+\-[0-9]+",
															sequence.description)

			# if sequence coordinates are found in the sequence header line,
			# intersect the sequence with BED regions.
			if coordinates != None:
				(seqChr, seqStart, seqEnd) = re.split(r"[:\-]", coordinates.group(0))
				seqStart = int(seqStart)
				seqEnd = int(seqEnd)

				# regions are in BED format so: 0=chr, 1=start, 2=end
				for region in self.regions:
					if region[0] == seqChr:
						# is there any overlap between the sequence and this region ?
						overlapLength = max(0, min(seqEnd, region[2]) - \
																	 max(seqStart, region[1]))
						if overlapLength > 0:
							# map this overlap to sequence positions
							overlapStart = max(0, region[1] - seqStart) + 1
							# add this overlap to the search results list
							self.searchResults.append(self.trackConsensus + \
																				"\ttrackIntersection\t" + \
																				self.trackName + "\t" + \
																				sequence.description + "\t" + \
																				str(overlapStart) + "\t" + \
																				str(overlapStart + overlapLength))
			else:
				# otherwise simply skip this sequence
				print "  [RegionsIntersectionSearcher] Skipping sequence < " + \
							sequence.description + " >. Coordinates not found in header line."
				continue

		print "  [RegionsIntersectionSearcher] Execution completed."
		return self.searchResults
