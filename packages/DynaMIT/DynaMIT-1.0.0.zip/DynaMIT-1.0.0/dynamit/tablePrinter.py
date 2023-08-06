""" Module for the TablePrinter classes."""

import dynamit.resultsPrinter
import os

class TablePrinter(dynamit.resultsPrinter.ResultsPrinter):
	"""ResultsPrinter that generates a tabular representation
	of identified motifs, motifs clusters and related instances
	on input sequences. It requires only motif and their matches,
	so it is compatible with any IntegrationStrategy component
	(it could indeed be run even if no such strategy is executed).
	This printer is able to exploit clustering and/or biclustering
	information as well if it is present.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.resultsPrinterName = "Table"

	def setConfiguration(self, configString):
		"""Loads the printer parameters specified in the configuration file.

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		return 0

	def printResults(self, sequences, searchResults,
									 integrationStrategyName, integrationResults):
		"""Performs the tabular results printing with passed results.
		Requires the motifs key to be present in integrationResults,
		and exploits clustering and biclustering keys as well if
		these are present.

		Args:
			sequences: collection of input sequences for this run.
			searchResults: table containing matches for all motifs on all sequences.
										This table is produced by DynaMIT motif search phase.
			integrationStrategyName: name of the strategy used to perform
															 the integration step.
			integrationResults: dictionary of results produced by the
													integration step.

		Returns:
			Returns 0 if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""

		if not integrationResults.has_key("motifs"):
			print "[ERROR] Unable to run the TablePrinter. Key \"motifs\" " \
						" not found in the passed integration results data structure."
			return 1

		# open the results output file.
		outputHandle = open("results_Table.txt", "wb")

		# print motifs in tabular format.
		outputHandle.write("**** MOTIFS *********************" + \
											 "***************************\n")
		outputHandle.write("\n".join(integrationResults["motifs"]) + "\n")

		# print integration strategy name and the obtained
		# clustering in tabular format.
		outputHandle.write("\nIntegration strategy was: " + \
											 integrationStrategyName + ".\n")
		if integrationResults.has_key("clustering"):
			outputHandle.write("\n**** CLUSTERING *************" + \
												 "***********************************\n")
			for cluster in set(integrationResults["clustering"]):
				outputHandle.write("Cluster " + repr(cluster) + ": " + \
													 ", ".join([integrationResults["motifs"][i] \
																			for i in range(0, len(integrationResults["clustering"])) \
																			if integrationResults["clustering"][i] == cluster]) + "\n")
		# if otherwise integration produced biclusters, print them.
		elif integrationResults.has_key("biclustering_motifs"):
			outputHandle.write("\n**** BICLUSTERING ***********" + \
												 "*************************************\n")
			for bicluster in set(integrationResults["biclustering_motifs"]).\
											 union(set(integrationResults["biclustering_sequences"])):
				outputHandle.write("Bicluster " + repr(bicluster) + ": " + "\n")
				outputHandle.write("\tMotifs: " + \
													 ", ".join([integrationResults["motifs"][i] \
																			for i in range(0, len(integrationResults["biclustering_motifs"])) \
																			if integrationResults["biclustering_motifs"][i] == bicluster]) + "\n")
				outputHandle.write("\tSequences: " + \
													 ", ".join([integrationResults["sequences"][i] \
																			for i in range(0, len(integrationResults["biclustering_sequences"])) \
																			if integrationResults["biclustering_sequences"][i] == bicluster]) + "\n")


		# additionally, if the pairsOverThreshold key is present,
		# report this information as well
		if ((integrationResults.has_key("pairsOverThreshold")) and
				(integrationResults.has_key("threshold"))):
			outputHandle.write("\n************************* MOTIF PAIRS WITH " + \
												 "INTEGRATION METRIC OVER THRESHOLD ***********" + \
												 "**************\n")
			outputHandle.write("Integration metric threshold was " + \
												 repr(integrationResults["threshold"]) + ".\n")
			outputHandle.write("Motif pair\tScore\tDetails\n")
			for (mpair, details) in integrationResults["pairsOverThreshold"].iteritems():
				outputHandle.write(mpair + "\t" + repr(details[0]) + "\t" + \
													 "\t".join([str(d) for d in details[1:]]) + "\n")

		# then print all motifs matches by specifying the cluster/bicluster #
		# to which the match belong, if these info is available.
		outputHandle.write("\n************************* MOTIFS MATCHES ******" + \
											 "*******************\n")
		outputHandle.write("bicluster	"
											 if integrationResults.has_key("biclustering_motifs")
											 else \
											 ("cluster	" \
												if integrationResults.has_key("clustering") else "") \
											 + \
			"motif	motifType	motifSearcher	sequenceID	startPosition	endPosition\n")

		for match in searchResults:
			matchInfo = match.split('\t')
			matchMotif = matchInfo[0] + "|" + matchInfo[2]
			# if the motif was retained by integration as an interesting one.
			if matchMotif in integrationResults["motifs"]:
				# write the match with its corresponding cluster/bicluster no. to output
				# if no cluster/bicluster is available, write raw matches instead.
				if integrationResults.has_key("clustering"):
					outputHandle.write(str(integrationResults["clustering"][\
														 integrationResults["motifs"].index(matchMotif)]) + \
														 "\t" + match + "\n")
				elif integrationResults.has_key("biclustering_motifs"):
					outputHandle.write(str(integrationResults["biclustering_motifs"][\
														 integrationResults["motifs"].index(matchMotif)]) + \
														 "\t" + match + "\n")
				else:
					outputHandle.write(match + "\n")


		# close the output file and inform the user of its existence.
		outputHandle.close()
		print "  [TablePrinter] Printing completed. Results are stored in\n" \
					"    <" + os.path.join(os.getcwd(), "results_Table.txt") + ">."

		return 0
