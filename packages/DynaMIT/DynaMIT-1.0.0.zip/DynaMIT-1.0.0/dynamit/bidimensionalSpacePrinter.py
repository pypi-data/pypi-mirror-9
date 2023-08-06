"""Module for BidimensionalSpacePrinter classes."""

import dynamit.resultsPrinter
import dynamit.utils

import os

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms

class BidimensionalSpacePrinter(dynamit.resultsPrinter.ResultsPrinter):
	"""ResultsPrinter that generates a graphical representation
	of identified motifs/motifs clusters on a 2D-space through passed
	reduced representation coordinates: it thus allows to
	identify similar motifs and clusters composition on an euclidean
	space.It requires motifs and their matches, and motifs reduced
	representation, so it is compatible with any IntegrationStrategy
	component computing such a representation (i.e. PCAStrategy).
	If clustering information is present, it can be exploited as well
	(depending on the selected user configuration).
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.resultsPrinterName = "BidimensionalSpace"
		self.doNotShowClusters = False

	def setConfiguration(self, configString):
		"""Loads the printer parameters specified in the configuration file.
		In particular, looks for the doNotShowClusters parameter (indicating to
		avoid highlighting clusters when drawing the 2D motifs representation).

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).
		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if configString.find("doNotShowClusters") >= 0:
			self.doNotShowClusters = True

		return 0


	def printResults(self, sequences, searchResults,
									 integrationStrategyName, integrationResults):
		"""Performs the graphical results printing on a 2D space,
		exploiting the passed 2D motifs representation as coordinates.
		Requires the motifs and reducedMotifsRepresentation keys to
		be present in integrationResults, and exploits clustering key
		as well if it is present.

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
				(not integrationResults.has_key("reducedMotifsRepresentation"))):
			print "[ERROR] Unable to run BidimensionalSpacePrinter. Keys \"motifs\" and " \
						"\"reducedMotifsRepresentation\" not found in the passed " \
						"integration results data structure."
			return 1

		# clean the slate with a new figure
		plt.figure()

		count = 0
		clusters = {}
		clustersPatches = []
		legends = []
		# set plot title and colormap according to cluster showing or not.
		title = "Motifs 2D representation" if self.doNotShowClusters \
						else "Motifs and clusters 2D representation"
		colorMap = dynamit.utils.getMatplotlibColorMap(
											len(integrationResults["motifs"]) + 1, 1) \
							 if self.doNotShowClusters else \
							 dynamit.utils.getMatplotlibColorMap(
											len(integrationResults["motifs"]) + \
											len(set(integrationResults["clustering"])) + 1, 1)

		for motifRepr in integrationResults["reducedMotifsRepresentation"]:
			# check that the motifs reduced representation is made of two
			# coordinates (at least, ignore additional one if it is the case).
			if len(motifRepr) < 2:
				print "[ERROR] Unable to run the printer. Motifs reduced " \
							"representations are made of less than two coordinates " \
							"(as required to be drawn on a 2D space)."
				return 1

			motifName = integrationResults["motifs"][count]

			# do this to avoid a weird matplotlib error for which sometimes
			# the first plotting fails but the subsequent ones than are ok.
			try:
				plt.scatter(motifRepr[0], motifRepr[1], c=colorMap(count), linewidth=0.5, label=motifName)
			except ValueError:
				plt.scatter(motifRepr[0], motifRepr[1], c=colorMap(count), linewidth=0.5, label=motifName)

			if not self.doNotShowClusters:
				motifCluster = "Cluster " + \
							repr(integrationResults["clustering"][integrationResults["motifs"].index(motifName)])
				if clusters.has_key(motifCluster):
					clusters[motifCluster].append((motifRepr[0], motifRepr[1]))
				else:
					clusters[motifCluster] = [(motifRepr[0], motifRepr[1])]

			count += 1

		# hide unnecessary axis ticks (top and right)
		plt.tick_params(axis="both", top="off", right="off", labelsize=10)
		# set axis labels and legend space on the right
		plt.xlabel("First component", fontsize=10)
		plt.ylabel("Second component", fontsize=10)
		# draw the plot title slightly above the top x-axis
		plt.title(title, y=1.05)

		# draw the individual motifs legend.
		firstLegend = plt.legend(title="Motifs",
														 loc=2, bbox_to_anchor=(1.05, 1), fontsize=10,
														 scatterpoints=1, fancybox=True, borderpad=.75)
		legends.append(firstLegend.legendPatch)

		# proceed to draw the clusters and their legend, if requested.
		if not self.doNotShowClusters:
			# draw the clusters on top of the scatterplot
			for cluster in sorted(clusters.keys()):
				clusterX = [point[0] for point in clusters[cluster]]
				clusterY = [point[1] for point in clusters[cluster]]
				# get the cluster color and set its alpha to allow seeing motif points.
				clusterColor = (colorMap(count)[0], colorMap(count)[1],
												colorMap(count)[2], 0.25)
				# prepare cluster patch (colored rectangle) and label for the legend.
				clusterLabel = cluster + ": " + \
												", ".join([integrationResults["motifs"][i] \
								for i in range(0, len(integrationResults["clustering"])) \
								if integrationResults["clustering"][i] == int(cluster.split(' ')[1])]) + "\n"
				# format cluster labels to a maximum of 70 chars/line.
				clusterLabel = dynamit.utils.formatStringToLineLength(clusterLabel, 70)
				clustersPatches.append(mpatches.Patch(facecolor=clusterColor,
																							edgecolor=(0.5, 0.5, 0.5, 0.75),
																							linewidth=0.5,
																							label=clusterLabel[:-1]))

				# get the region encompassing all cluster points.
				clusterBbox = mtransforms.Bbox([[min(clusterX), min(clusterY)],
																				[max(clusterX), max(clusterY)]])
				# get five percent of the axes range as a bounding box pad
				# around points belonging to a single cluster.
				xlim = plt.gca().get_xlim()
				ylim = plt.gca().get_ylim()
				xlimFivePercent = abs((xlim[1]-xlim[0]) / 20.0)
				ylimFivePercent = abs((ylim[1]-ylim[0]) / 20.0)
				# draw the cluster as a filled region encompassing its motifs (points).
				plt.gca().add_patch(mpatches.FancyBboxPatch(
															(clusterBbox.xmin - xlimFivePercent / 2,
															 clusterBbox.ymin - ylimFivePercent / 2),
															abs(clusterBbox.width) + xlimFivePercent,
															abs(clusterBbox.height) + ylimFivePercent,
															boxstyle="round,pad=0", fc=clusterColor,
															ec=(0.5, 0.5, 0.5, 0.75)))

				count += 1

			# draw the clusters-motifs association legend at the
			# bottom of the plot, to indicate clusters composition.
			legends.append(plt.legend(title="Clusters composition",
																handles=clustersPatches, loc=9,
																bbox_to_anchor=(0.45, -0.15), fontsize=10,
																borderpad=.75, fancybox=True).legendPatch)
			# redraw the first legend (individual motifs) which has been
			# erased by drawing the clusters legend.
			plt.gca().add_artist(firstLegend)

		# save the final figure to file in PDF format and
		# inform the user of its existence.
		plotType = "_byCluster" if not self.doNotShowClusters else "_byMotif"
		plt.savefig(os.path.join(os.getcwd(),
								"results_BidimensionalSpace" + plotType + ".pdf"),
								bbox_inches="tight", bbox_extra_artists=legends,
								format="PDF", orientation='landscape', transparent=False)
		print "  [BidimensionalSpacePrinter] Printing completed. Results are stored in \n" \
					"    <" + \
					os.path.join(os.getcwd(),
					"results_BidimensionalSpace" + plotType + ".pdf") + ">."
		return 0
