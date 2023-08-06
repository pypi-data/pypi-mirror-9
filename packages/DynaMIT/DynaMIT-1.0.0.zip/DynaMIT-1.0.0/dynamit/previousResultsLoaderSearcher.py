""" Module for the PreviousResultsLoaderSearcher classes."""

import os
import dynamit.motifSearcher

class PreviousResultsLoaderSearcher(dynamit.motifSearcher.MotifSearcher):
	"""Class implementing a motif searcher which simply loads
	the motif search results from a previous DynaMIT run (i.e.
	the motifSearchesResults.txt file) to be reused for a new run.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.path = ""
		self.searcherName = "PreviousResultsLoader"

	def setConfiguration(self, path, params):
		"""Loads the searcher parameters specified in the configuration file.

		Args:
			path: path to a DynaMIT motif search
						intermediate results file (motifSearchesResults.txt)
			params: no parameters are used in this context.

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		self.path = path.rstrip("\"").lstrip("\"")
		return 0

	def runSearch(self, sequencesFilename):
		"""Loads previous DynaMIT motif search results
		as current searcher results to reuse them for
		the current run.

		Args:
			sequencesFilename: input sequences filename for this run.

		Returns:
			Returns a list of strings representing identified motif matches
			if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		# check if the intermediate search results file specified in
		# the searcher configuration exists
		if not os.path.isfile(self.path):
			print "[ERROR] Could not find the intermediate search results file " \
						"specified in PreviousResultsLoaderSearcher configuration."
			return 1

		# open the file and loads its content.
		intResultsHandle = open(self.path)
		lines = intResultsHandle.readlines()
		# process lines by removing header lines (starting with #)
		# and newline characters from the end of each line.
		lines = [line.rstrip('\n') for line in lines \
						 if (line != '\n') and (not line.startswith("#"))]
		# check for file emptiness.
		if len(lines) == 0:
			print "[ERROR] The intermediate search results file specified " \
						"in PreviousResultsLoaderSearcher configuration is empty."
			return 1

		print "  [PreviousResultsLoaderSearcher] Execution completed."
		self.searchResults = lines
		return self.searchResults
