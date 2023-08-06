"""Module for PositionalDensityPrinter classes."""

import dynamit.resultsPrinter, dynamit.utils
import os

from scipy.stats import chisquare, histogram

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class PositionalDensityPrinter(dynamit.resultsPrinter.ResultsPrinter):
	"""ResultsPrinter that generates a graphical representation
	of identified motifs/motifs clusters and the distribution of
	their instances position on input sequences: it thus allows to
	identify potential positional preferences for identified motifs.
	It requires motifs and their matches, so it is compatible
	with any IntegrationStrategy component. If clustering information
	is present, it can be exploited as well (depending on user configuration).
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.resultsPrinterName = "PositionalDensity"
		self.drawIndividualMotifs = False

	def setConfiguration(self, configString):
		"""Loads the printer parameters specified in the configuration file.
		In particular, looks for the drawIndividualMotifs parameter (draw
		individual motifs violin plots rather than clusters violin plots).

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if configString.find("drawIndividualMotifs") >= 0:
			self.drawIndividualMotifs = True

		return 0


	def printResults(self, sequences, searchResults,
									 integrationStrategyName, integrationResults):
		"""Performs the positional density graphical printing with
		passed results by means of violin plots (one per motif/cluster).
		Requires the motifs key to be present in integrationResults,
		and exploits clustering key as well if it is present.

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

		# check whether the required integration results fields are available
		if ((not integrationResults.has_key("motifs")) or
				((not integrationResults.has_key("clustering"))
				 and (not self.drawIndividualMotifs))):
			print "[ERROR] Unable to run the PositionalDensityPrinter. Keys \"motifs\" and " \
						"\"clustering\" not found in the passed integration results " \
						"data structure, but drawing by cluster was requested."
			return 1

		# compute the vectorized per-sequence motifs representations.
		vectors = dynamit.utils.getBySequenceMotifsInstancesVectors(sequences,
																																searchResults,
																																binary=False)

		# get all sequences lengths for motifs relative position computation
		seqLengths = {seq.description: float(len(seq)) for seq in sequences}

		# compute the distribution of motif matches position for each cluster/motif
		# (depending on user choice as specified by the configuration parameter
		#  self.drawIndividualMotifs)
		distributions = {}
		for motif in vectors.keys():
			# obtain the key for the distribution (cluster or motif ID)
			key = motif if self.drawIndividualMotifs else \
						repr(integrationResults["clustering"][integrationResults["motifs"].index(motif)])
			if not distributions.has_key(key):
				distributions[key] = []
			# add relative positions (normalized to seq.length) of this
			# motif matches to its distribution.
			for seq in vectors[motif].keys():
				distributions[key].extend([float(pos) / seqLengths[seq] \
																	 for pos in vectors[motif][seq]])

		# perform a chi-square tets for each distribution,
		# to obtain a non-uniformity p-value (i.e. is the positional
		# preference of the motif significantly different from uniformity?)
		pvals = {}
		for key in distributions.keys():
			# compute the 20-bin frequency (one every 5%) for current key distribution.
			distFreqs = histogram(distributions[key], numbins=20, defaultlimits=(0, 1))[0]
			# compute a p-value of difference from a uniform distribution.
			pvals[key] = "%.3e"%chisquare(f_obs=distFreqs)[1]


		# clean the slate with a new figure, scaling its height to
		# the number of items (clusters/motifs) in the plot.
		plt.figure(figsize=(8.0, min(45, 5.0 + 0.25*len(distributions))))

		# draw the violin plots, with one series per cluster/motif
		# try to plot, catch an eventual exception and replot if it is raised
		# (sometimes the first call fails; this seems a weird matplotlib bug)
		try:
			plt.violinplot(distributions.values(),
										 positions=range(0, len(distributions)*2, 2),
										 vert=False, widths=1.1, showmeans=True,
										 showextrema=True, showmedians=True)
		except ValueError:
			plt.violinplot(distributions.values(),
										 positions=range(0, len(distributions)*2, 2),
										 vert=False, widths=1.1, showmeans=True,
										 showextrema=True, showmedians=True)

		# set axes labels, titles and graphical parameters.
		plt.xlim([0, 1])
		plt.ylim([-1, len(distributions)*2])
		plt.xlabel("Relative position along the sequence", fontsize=10)
		plt.tick_params(axis="both", which='major', labelsize=10, pad=10,
										right="off", top="off")
		plt.yticks(range(0, len(distributions)*2, 2),
							[d + "(pval: " + pvals[d] + ")" \
														 for d in distributions.keys()] \
							if (self.drawIndividualMotifs) \
							else ["Cluster " + d + "(pval: " + pvals[d] + ")" \
										for d in distributions.keys()])
		plt.subplots_adjust(left=0.2)

		# draw the plot title
		if self.drawIndividualMotifs:
			plt.title("Motifs matches positional density", y=1.02)
		else:
			plt.title("Clusters matches positional density", y=1.02)
			# prepare cluster patches and labels for the legend.
			clustersPatches = []
			for key in sorted(distributions.keys()):
				keyDesc = "Cluster " + key + ": " + \
								", ".join([integrationResults["motifs"][i] \
										for i in range(0, len(integrationResults["clustering"])) \
										if integrationResults["clustering"][i] == int(key)]) + "\n"
				# format the cluster label to be in lines of max 60 characters.
				keyDesc = dynamit.utils.formatStringToLineLength(keyDesc, 60)
				clustersPatches.append(mpatches.Patch(facecolor=(0, 0, 0, 0.75),
															 linewidth=0.5, label=keyDesc[:-1]))

			# draw the clusters-motifs association legend at the
			# bottom of the plot, to indicate clusters composition.
			clustersLegendPatch = plt.legend(title="Clusters composition",
																handles=clustersPatches, loc=9,
																handlelength=.75,
																bbox_to_anchor=(0.5, -0.15), fontsize=10,
																borderpad=.75, fancybox=True).legendPatch

		# save the final figure to file in PDF format and
		# inform the user of its existence.
		plotType = "_byCluster" if not self.drawIndividualMotifs else "_byMotif"
		plt.savefig(os.path.join(os.getcwd(),
								"results_PositionalDensity" + plotType + ".pdf"),
								bbox_inches="tight", pad_inches=.25,
								bbox_extra_artists=[] if self.drawIndividualMotifs \
																			else [clustersLegendPatch],
								format="PDF", orientation='landscape', transparent=False)
		print "  [PositionalDensityPrinter] Printing completed. Results are stored in" \
					"    <" + os.path.join(os.getcwd(),
					"results_PositionalDensity" + plotType + ".pdf") + ">."
		return 0
