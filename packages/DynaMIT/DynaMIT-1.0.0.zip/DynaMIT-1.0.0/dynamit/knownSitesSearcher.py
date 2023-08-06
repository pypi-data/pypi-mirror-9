""" Module for the KnownSitesSearcher classes."""

import dynamit.motifSearcher
import dynamit.utils

class KnownSitesSearcher(dynamit.motifSearcher.MotifSearcher):
	"""Class implementing a known sites motif searcher,
	which adds a set of known sites in the input sequences as
	motifs instances. Known regions (specified in sequence-relative)
	coordinates, are loaded from a BED file specified in the
	configuration. This allows to have previously annotated sites
	as motifs instances to be compared with the results of the
	other searchers; the searcher name and consensus to be used
	can be specified in the searcher configuration.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.searcherName = "KnownSites"
		self.trackName = ""
		self.trackConsensus = ""

	def setConfiguration(self, path, params):
		"""Loads the searcher parameters specified in the configuration file.

		Args:
			path: path of the BED file containing known sites
			positions in input sequences.
			params: track name associated to the specified BED file.

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""

		# store the path of the BED file containing regions to be intersected.
		self.path = path

		# the parameter here are the TRACK name and consensus sequence
		# (to "name" the searcher/motif and compare it to the others).
		if params != "":
			info = params.split(',')
			self.trackName = info[0]
			self.trackConsensus = info[1] if len(info) > 1 else self.trackName

		return 0

	def runSearch(self, sequencesFilename):
		"""Performs motif search, by annotating input sequences
		with the known sites specified in the configuration.

		Args:
			sequencesFilename: input sequences filename for this run.

		Returns:
			Returns a list of strings representing identified motif matches
			if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		# load sequences from the input file
		sequences = dynamit.utils.getSequencesRecords(sequencesFilename)
		sequencesIDs = [sequence.description for sequence in sequences]

		# load known sites from the specified file as search results
		self.searchResults = []
		print "	[KnownSitesSearcher] Loading known sites from the BED file..."

		try:
			with open(self.path) as bedHandle:
				lineCount = 1
				for line in bedHandle.readlines():
					# skip comment lines starting with #
					if not line.startswith("#"):
						info = line.rstrip('\n').split('\t')
						# check the presence of minimally required fields
						if len(info) >= 4:
							# check if the sequence specified for this site
							# exists in input sequences; if not simply skip this site.
							if not info[3] in sequencesIDs:
								print "	[KnownSitesSearcher] Skipping line " + \
											str(lineCount) + \
											". Specified sequence name not found in input sequences."
							else:
								# otherwise add the site to the list of results
								self.searchResults.append(self.trackConsensus + "\tknownSites\t" + \
																					self.trackName + "\t" + info[3] + "\t" + \
																					info[1] + "\t" + info[2])
						else:
							raise ValueError("the specified BED regions file lacks the " \
										"required four fields (chr, start, end, sequenceName).")
					lineCount += 1
		except IOError:
			print "[ERROR] Cannot read the specified BED file."
			return 1
		except (IndexError, ValueError, RuntimeError) as e:
			print "[ERROR] Execution error: " + str(e)
			return 1

		print "	[KnownSitesSearcher] Execution completed."
		return self.searchResults
