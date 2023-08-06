"""Module for HeatmapPrinter classes."""

import dynamit.resultsPrinter
import dynamit.utils
import os

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

class HeatmapPrinter(dynamit.resultsPrinter.ResultsPrinter):
	"""ResultsPrinter that generates a graphical representation
	of identified motifs/motifs clusters in the form of an
	heatmap (based on motif/cluster presence/absence on a sequence,
	or on fraction of occupied bases of a motif/cluster on a sequence).
	It requires motifs and their matches, so it is compatible
	with any IntegrationStrategy component. If (bi)clustering information
	is present, it can be exploited as well (depending on user configuration).
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.resultsPrinterName = "Heatmap"
		self.drawBinaryHeatmap = False
		self.drawIndividualMotifs = False
		self.drawBiclusters = True

	def setConfiguration(self, configString):
		"""Loads the printer parameters specified in the configuration file.
		In particular, looks for the drawBinaryHeatmap (indicating to draw a
		heatmap representing only presence/absence of a motif match in a sequence
		rather than the fraction of the sequence occupied by the motif matches),
		the drawBiclusters (highlight to which bicluster each sequence and motif
		belong, considered only if biclustering annotations are found) and for
		the drawIndividualMotifs (draw individual motifs heatmap rather than
		grouped by identified clusters) parameters.

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).
		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if configString.find("drawBinaryHeatmap") >= 0:
			self.drawBinaryHeatmap = True
		if configString.find("drawBiclusters") >= 0:
			self.drawBiclusters = True
		if configString.find("drawIndividualMotifs") >= 0:
			self.drawIndividualMotifs = True

		return 0


	def printResults(self, sequences, searchResults,
									 integrationStrategyName, integrationResults):
		"""Performs the heatmap graphical printing with passed
		results and specified configuration. Requires the motifs
		key to be present in integrationResults, and exploits
		clustering/biclustering keys as well if it is present.

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
			print "[ERROR] Unable to run the HeatmapPrinter. Keys \"motifs\" and " \
						"\"clustering\" not found in the passed integration results " \
						"data structure, but drawing by cluster was requested."
			return 1

		# compute the vectorized per-sequence motifs representations.
		vectors = dynamit.utils.getBySequenceMotifsInstancesVectors(sequences,
																																 searchResults,
																																 binary=False)

		# get all sequences lengths for motifs relative position (0 to 1) computation
		seqLengths = {seq.description: float(len(seq)) for seq in sequences}

		# compute the distribution of motif matches position for each cluster/motif
		# (depending on user choice as specified by the configuration
		#  parameter self.drawIndividualMotifs)
		heatmap = []
		keys = []
		for motif in integrationResults["motifs"]:
			# obtain the key for the heatmap (cluster or motif ID)
			key = motif
			tmp = []
			if not self.drawIndividualMotifs:
				key = repr(integrationResults["clustering"][integrationResults["motifs"].index(motif)])
			if not key in keys:
				keys.append(key)

			# add presence/absence or sequence occupation of current motif on
			# this sequence to its heatmap row
			for seq in seqLengths.keys():
				if not self.drawBinaryHeatmap:
					tmp.append(float(len(vectors[motif][seq])) / seqLengths[seq])
				else:
					tmp.append(1.0 if len(vectors[motif][seq]) > 0 else 0.0)

			if not self.drawIndividualMotifs:
				if len(heatmap) > keys.index(key):
					if not self.drawBinaryHeatmap:
						heatmap[keys.index(key)] = [(t[0] + t[1]) / 2 \
																				 for t in \
																				 zip(heatmap[keys.index(key)], tmp)]
					else:
						heatmap[keys.index(key)] = [(t[0] or t[1]) \
																				 for t in \
																				 zip(heatmap[keys.index(key)], tmp)]
				else:
					heatmap.append(tmp)
			else:
				heatmap.append(tmp)

		# clean the slate with a new figure
		fig = plt.figure(figsize=(min(80, 6.0 + 0.8*len(seqLengths)),
															min(70, 5.0 + 0.8*len(keys))))

		# draw the heatmap, with one row per motif and column per sequence
		# try to plot, catch an eventual exception and replot if it is raised
		# (sometimes the first call fails; this seems a weird matplotlib bug)
		img = None
		try:
			img = plt.imshow(np.array(heatmap), extent=[-.5, len(seqLengths)-.5, -.5, len(keys)-.5],
											 origin="lower", interpolation='none')
		except ValueError:
			img = plt.imshow(np.array(heatmap), extent=[-.5, len(seqLengths)-.5, -.5, len(keys)-.5],
											 origin="lower", interpolation='none')

		# draw the heatmap colorkey next to it.
		cbar = plt.colorbar(img, use_gridspec=True)
		cbar.ax.tick_params(labelsize=8)

		legends = []
		# if the user asked to highlight biclusters and that annotation
		# is in the integrationResults dictionary, draw them.
		if self.drawBiclusters and integrationResults.has_key("biclustering_motifs"):
			biclusters = set(list(integrationResults["biclustering_motifs"]) + \
											 list(integrationResults["biclustering_sequences"]))
			bicPatches = []
			# set colormap for biclustering showing.
			colorMap = dynamit.utils.getMatplotlibColorMap(len(biclusters) + 1, 1)

			# draw the biclusters on top of the heatmap
			for bicluster in sorted(biclusters):
				# motifs order is the one passed in integration results.
				rows = [r for r, bic in enumerate(integrationResults["biclustering_motifs"]) \
									if bic == bicluster]
				# instead, need to map sequence bicluster index to current sequence order
				bicSeqs = [integrationResults["sequences"][c] for c, bic \
									 in enumerate(integrationResults["biclustering_sequences"]) \
									 if bic == bicluster]
				cols = [c for c, seq in enumerate(seqLengths.keys()) \
									if seq in bicSeqs]

				# get the cluster color and set its alpha to allow seeing motif points.
				bicColor = (colorMap(bicluster)[0], colorMap(bicluster)[1],
										colorMap(bicluster)[2], 0.6)
				# prepare cluster patch (colored rectangle) and label for the legend.
				bicMotifs = [integrationResults["motifs"][i] for i in rows]
				bicLabel = str(bicluster) + ": " + ", ".join(bicMotifs) + " " + \
									 ", ".join(bicSeqs) + "\n"

				# format cluster labels to a maximum of 80 chars/line.
				bicLabel = dynamit.utils.formatStringToLineLength(bicLabel, 80)
				bicPatches.append(mpatches.Patch(facecolor=bicColor,
																					edgecolor=(0.5, 0.5, 0.5, 0.75),
																					linewidth=0.5,
																					label=bicLabel[:-1]))

				# get the region encompassing all cluster points.
				for row in rows:
					# highlight the row as belonging to the bicluster,
					# with a semitransparent filled region over it.
					plt.gca().add_patch(mpatches.FancyBboxPatch((-.5, row - .5),
																len(integrationResults["biclustering_sequences"]),
																1, boxstyle="round,pad=0", fc=bicColor, ec="none"))
				for col in cols:
					# highlight the row as belonging to the bicluster,
					# with a semitransparent filled region over it.
					plt.gca().add_patch(mpatches.FancyBboxPatch((col - .5, -.5),
																1, len(integrationResults["biclustering_motifs"]),
																boxstyle="round,pad=0", fc=bicColor, ec="none"))

				# draw the biclusters composition legend at the
				# bottom of the plot, to indicate clusters composition.
				legends.append(plt.legend(title="Biclusters composition",
																	handles=bicPatches, loc=9,
																	bbox_to_anchor=(0.5, -0.5), fontsize=10,
																	borderpad=1.0, fancybox=True).legendPatch)

		# set axes labels, titles and graphical parameters
		plt.ylabel("Motifs" if (self.drawIndividualMotifs) else "Clusters",
							 fontsize=10, labelpad=15)
		plt.xlabel("Sequences", fontsize=10, labelpad=15)
		plt.tick_params(axis="both", which='major', labelsize=10, pad=10,
										left="off", right="off", top="off", bottom="off")
		plt.yticks(range(0, len(keys), 1),
							 keys if (self.drawIndividualMotifs) else \
							 ["Cluster " + c for c in keys])
		plt.xticks(range(0, len(seqLengths.keys()), 1),
							 [s[:15] for s in seqLengths.keys()], rotation=90)
		plt.subplots_adjust(left=0.2,
												bottom=0.2 if self.drawIndividualMotifs else 0.5)

		# draw a custom grid to separate the heatmap blocks
		# basically draws between major axes ticks rather than
		# at the axis tick positions (i.e. at 1.5 rater than 1, etc.)
		for xmaj in [x+0.5 for x in range(0, len(seqLengths))]:
			plt.axvline(x=xmaj, ls='-', color=(0.5, 0.5, 0.5, 0.7))
		for ymaj in [y+0.5 for y in range(0, len(keys))]:
			plt.axhline(y=ymaj, ls='-', color=(0.5, 0.5, 0.5, 0.7))

		# compose the plot title and draw clusters composition legend if needed.
		if self.drawIndividualMotifs:
			heatmapTitle = "Motifs " + \
										 ("occupation of sequences" if not self.drawBinaryHeatmap \
										 else "presence/absence in sequences")
		else:
			heatmapTitle = "Clusters " + \
										 ("occupation of sequences" if not self.drawBinaryHeatmap  \
										 else "presence/absence in sequences")
			# prepare cluster patches and labels for the legend.
			clustersPatches = []
			for key in sorted(keys):
				keyDesc = "Cluster " + key + ": " + \
						", ".join([integrationResults["motifs"][i] \
										for i in range(0, len(integrationResults["clustering"])) \
										if integrationResults["clustering"][i] == int(key)]) + "\n"
				# format legend entries to a maximum of 60 chars/line.
				keyDesc = dynamit.utils.formatStringToLineLength(keyDesc, 60)
				clustersPatches.append(mpatches.Patch(facecolor=(0, 0, 0, 0.75),
																		linewidth=0.5, label=keyDesc[:-1]))
			# draw the clusters-motifs association legend at the
			# bottom of the plot, to indicate clusters composition.
			# call draw to initialize the renderer needed to get
			# the y space occupied by x-axis labels.
			plt.draw()
			# get the y space occupied by x-axis labels.
			xLabelsSpace = (0.0, plt.gca().get_xaxis().\
											get_text_heights(fig.canvas.renderer)[1])
			# transform x labels height in display coordinates
			xLabelsHeight = plt.gca().transAxes.inverted().transform_point(xLabelsSpace)[1]
			legends.append(plt.legend(title="Clusters composition",
												handles=clustersPatches, loc=9,
												handlelength=.75,
												bbox_to_anchor=(0.5, xLabelsHeight), fontsize=10,
												borderpad=.75, fancybox=True).legendPatch)

		# draw the plot title
		plt.title(heatmapTitle, y=1.05)

		# save the final figure to file in PDF format and
		# inform the user of its existence.
		plotType = "_byCluster" if not self.drawIndividualMotifs else "_byMotif"
		plt.savefig(os.path.join(os.getcwd(),
								"results_Heatmap" + plotType + ".pdf"),
								bbox_inches="tight", pad_inches=.25,
								bbox_extra_artists=legends,
								format="PDF", orientation='landscape', transparent=False)
		print "  [HeatmapPrinter] Printing completed. Results are stored in \n" \
					"    <" + os.path.join(os.getcwd(),
					"results_Heatmap" + plotType + ".pdf") + ">."
		return 0
