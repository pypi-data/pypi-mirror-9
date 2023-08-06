"""Module for SequenceViewPrinter classes."""

import os

import dynamit.resultsPrinter
import dynamit.utils

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class SequenceViewPrinter(dynamit.resultsPrinter.ResultsPrinter):
	"""ResultsPrinter that generates a graphical representation
	of sequences and motifs/motifs clusters matches on them.
	It requires only motif and their matches, so it is compatible
	with any IntegrationStrategy component (it could indeed be run
	even if no such strategy is executed). This printer is able to
	exploit clustering information as well if it is present.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.resultsPrinterName = "SequenceView"
		self.drawGrid = False
		self.drawIndividualMotifs = False
		self.xOffset = 0
		self.sequenceSpacing = 2
		self.fontSize = 7

	def setConfiguration(self, configString):
		"""Loads the printer parameters specified in the configuration file.
		In particular, looks for the drawGrid (indicating to draw a background
		grid to the sequences and their motif matches drawing) and for the
		drawIndividualMotifs (draw individual motifs matches rather than drawing
		them grouped by identified clusters) parameters.

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).
		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if configString.find("drawGrid") >= 0:
			self.drawGrid = True
		if configString.find("drawIndividualMotifs") >= 0:
			self.drawIndividualMotifs = True

		return 0

	def printResults(self, sequences, searchResults,
									 integrationStrategyName, integrationResults):
		"""Performs the sequence graphical printing with passed results.
		Requires the motifs key to be present in integrationResults,
		and exploits clustering key as well if it is are present.

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
		if not integrationResults.has_key("motifs"):
			print "[ERROR] Unable to run the printer. Key \"motifs\" " \
						" not found in the passed integration results data structure."
			return 1

		if (not self.drawIndividualMotifs) and \
			 (not integrationResults.has_key("clustering")):
			print "[ERROR] Unable to run the SequenceViewPrinter. Key \"clustering\" " \
						" not found in the passed integration results data structure, " \
						" but the printer was configured to print clustered motifs."
			return 1

		# get the maximum sequence length and compute the scaling factors
		# and the pixel lengths for shorter sequences
		maxSeqLength = max([len(seqRecord.seq) for seqRecord in sequences])
		scalingFactors = [float(len(seqRecord.seq))/float(maxSeqLength) \
											for seqRecord in sequences]

		# create a new figure with ylim set to have one sequence each
		# point (1,2,3,..), xlim encompassing max length and axes hidden.
		# scale the maximum figure width to compensate an eventual big
		# range of the scaling factor (i.e. min 0.01, max 1.00), and the
		# maximum figure height to allow 0.25 inches per sequence.
		plt.figure(figsize=(
					min(33, 8.0*max(1.0, max(scalingFactors)/(min(scalingFactors)*100))),
					min(150, 0.5*self.sequenceSpacing*len(sequences))))
		plt.xlim(0, 1.1)
		plt.ylim(0, len(sequences) * self.sequenceSpacing + 1)
		plt.axis('off')

		# draw the background grid (if chosen through configuration)
		if self.drawGrid:
			backgroundGridColor = (0.85, 0.85, 0.85, 1)
			# draw horizontal lines
			plt.hlines([y / 5.0 for y in \
									range(0, len(sequences) * self.sequenceSpacing * 5 + 1, 1)],
								[0] * len(sequences) * 5,
								[1.2] * len(sequences) * 5,
								colors=backgroundGridColor, lw=.1)
			# draw vertical lines
			plt.vlines([x / 70.0 for x in range(0, 85, 1)],
								[0] * 70,
								[len(sequences) * self.sequenceSpacing] * 70,
								colors=backgroundGridColor, lw=.1)

		# draw sequences lines.
		plt.hlines(range(1, len(sequences) * self.sequenceSpacing + 1,
										 self.sequenceSpacing),
							 [self.xOffset] * len(sequences),
							 [self.xOffset + sf for sf in scalingFactors],
							 colors=(0.392, 0.392, 0.392, 1), lw=2)

		# get the colormap to pick motifs/clusters colors
		colorMap = dynamit.utils.getMatplotlibColorMap(
									len(integrationResults["motifs"]) + 1 \
									if self.drawIndividualMotifs \
									else len(set(integrationResults["clustering"])) + 1, 0.75)

		# collect all motif matches to be drawn.
		colors = {}
		matchesY = []
		matchesXStart = []
		matchesXEnd = []
		matchesColor = []
		for i in range(0, len(sequences)):
			# get all motif matches for current sequence.
			seqMatches = [match for match in searchResults \
										if match.split('\t')[3] == sequences[i].description]
			for match in seqMatches:
				matchInfo = match.split('\t')
				matchStart = float(matchInfo[4]) - 1
				matchEnd = float(matchInfo[5]) - 1
				# get the name of this match motif.
				motifName = matchInfo[0] + "|" + matchInfo[2]
				# if the motif was retained as an interesting one by integration.
				if motifName in integrationResults["motifs"]:
					# get the match key according to cluster or motif visualization.
					matchKey = motifName if self.drawIndividualMotifs else \
										 integrationResults["clustering"]\
												[integrationResults["motifs"].index(motifName)] \
					# set the color for this motif/cluster, if it already hasn't one.
					if not colors.has_key(matchKey):
						# get a new random color for current motif/cluster (pass
						# the list of used colors to avoid using them twice).
						colors[matchKey] = colorMap(len(colors))
					# add this motif match to the list of matches to be drawn
					# with sequence and cluster/motif distinctive color information.
					matchesY.append(i * self.sequenceSpacing + 1)
					matchesXStart.append(self.xOffset + \
											scalingFactors[i] * matchStart / float(len(sequences[i])))
					matchesXEnd.append(self.xOffset + \
											scalingFactors[i] * matchEnd / float(len(sequences[i])))
					matchesColor.append(colors[matchKey])

		# draw collected motif matches.
		plt.hlines(matchesY, matchesXStart, matchesXEnd, color=matchesColor, lw=4)

		# draw sequence names, 0 and length at each end of each sequence.
		for i in range(0, len(sequences)):
			sequenceYPos = i * self.sequenceSpacing + 1
			plt.annotate(sequences[i].description, xy=(self.xOffset, sequenceYPos),
									 xytext=(0, sequenceYPos + 0.4),
									 xycoords="data", size=self.fontSize, color="black")
			plt.annotate("0", xy=(self.xOffset, sequenceYPos),
									 xytext=(self.xOffset, sequenceYPos - 0.6),
									 xycoords="data", size=self.fontSize, color="black")
			plt.annotate(str(len(sequences[i])),
									 xy=(self.xOffset + scalingFactors[i], sequenceYPos),
									 xytext=(self.xOffset + scalingFactors[i], sequenceYPos - 0.6),
									 xycoords="data", size=self.fontSize, color="black")

		# draw each legend item by a rectangle of its color and its name
		legendItemsPatches = []
		for item in sorted(colors.keys()):
			legendItemsPatches.append(mpatches.Patch(facecolor=colors[item],
													linewidth=0.5, label=str(item)))

			# draw the clusters-motifs association legend at the
		# bottom of the plot, to indicate clusters composition.
		itemsLegend = plt.legend(
								title="MOTIFS" if self.drawIndividualMotifs else "MOTIFS CLUSTERS",
								handles=legendItemsPatches, loc=2, handlelength=.75,
								bbox_to_anchor=(1.05, 1), fontsize=self.fontSize,
								borderpad=1.0, fancybox=True)
		# set the legend title font size.
		plt.setp(itemsLegend.get_title(), fontsize=self.fontSize + 2)

		# draw the figure title
		plt.title("Motifs matches on sequences" if self.drawIndividualMotifs \
							 else "Clustered motifs matches on sequences")

		# save the final figure to file in PDF format and
		# inform the user of its existence.
		plotType = "_byCluster" if not self.drawIndividualMotifs else "_byMotif"
		plt.savefig(os.path.join(os.getcwd(),
								"results_SequenceView" + plotType + ".pdf"),
								bbox_inches="tight", pad_inches=.25,
								bbox_extra_artists=[itemsLegend.legendPatch],
								format="PDF", orientation='landscape', transparent=False)

		print "  [SequenceViewPrinter] Printing completed. Results are stored in\n" \
					"    <" + os.path.join(os.getcwd(),
					"results_SequenceView" + plotType + ".pdf") + ">."
		return 0
