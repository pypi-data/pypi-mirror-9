"""Module for ClusterEvaluationPrinter classes."""

import os
import dynamit.resultsPrinter, dynamit.utils

from numpy import mean

from Bio import pairwise2

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class ClusterEvaluationPrinter(dynamit.resultsPrinter.ResultsPrinter):
	"""ResultsPrinter that computes per-cluster scores of various
	aspects (clusters size, number of different motif types,
	clusters instances, gc content, consensuses coherence,
	silhouette score) and generates a graphical representation
	of these values, along with a text file containing all the
	details, to allow the identification of potentially
	stronger cluster to be considered for validation.It requires
	motifs and their clustering, so it is compatible with any
	IntegrationStrategy component returning such data.
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.resultsPrinterName = "ClusterEvaluation"

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
		"""Performs the graphical results printing as a 2x2 plot
		after having computed scores for each cluster. Also produces
		a text file containing all scores and details. Requires the
		motifs and clustering keys to be present in integrationResults.
		"""

		# check whether the required integration results fields are available
		if ((not integrationResults.has_key("motifs")) or
			(not integrationResults.has_key("clustering"))):
			print "[ERROR] Unable to run the ClusterEvaluationPrinter. Keys " \
						"\"motifs\" and \"clustering\" not found in the passed " \
						"integration results data structure."
			return 1

		# compute an overall per-cluster score along with individual sub-scores.
		clusters = list(set(integrationResults["clustering"]))
		# the first part of the score is the number of motifs
		# composing it (size score).
		clustersScores = [10.0 * list(integrationResults["clustering"]).count(c) \
											 for c in clusters]
		clustersMotifsTypes = [[] for i in range(len(clusters))]
		silhouettesScores = []
		instancesScores = []
		consensusesScores = []

		# if present, add the silhouette score to the overall one.
		if integrationResults.has_key("clusteringSilhouettes"):
			silhouettesScores = [100.0 * s for s \
													 in integrationResults["clusteringSilhouettes"]]
			clustersScores = [curScore + silhouettesScores[i] \
												for i, curScore in enumerate(clustersScores)]

		# compute a motif goodness based on its instances weights (based on
		# the agreement with consensus / score / pval) and obtain an overall
		# score for the cluster as the average of the individual motifs ones.
		for cluster in clusters:
			clusterMotifs = [integrationResults["motifs"][i] for i, curClust \
											 in enumerate(integrationResults["clustering"]) \
											 if curClust == cluster]
			scores = []
			for motif in clusterMotifs:
				motifInfo = motif.split("|")
				motifMatches = [match.split('\t') for match in searchResults \
												if ((match.split('\t')[0] == motifInfo[0]) and
													 (match.split('\t')[2] == motifInfo[1]))]
				# add the current motif type to the list of motif
				# types for this cluster.
				if not motifMatches[0][1] in clustersMotifsTypes[cluster]:
					clustersMotifsTypes[cluster].append(motifMatches[0][1])
				# compute the mean of instances scores as the score for this motif.
				if len(motifMatches[0]) > 6:
					try:
						motifScores = [float(match[6]) for match in motifMatches]
						scores.append(mean(motifScores))
					except ValueError:
						continue

			instancesScores.append(mean(scores) if len(scores) > 0 else 0)
			clustersScores[cluster] += instancesScores[cluster]
			# keep the presence of multiple motif types into account as well.
			clustersScores[cluster] += 10.0 * len(clustersMotifsTypes[cluster])

		# compute a cluster consensus coherence score
		consensusesScores = [0] * len(clusters)
		for cluster in clusters:
			clusterMotifs = [integrationResults["motifs"][i] for i, curClust \
											 in enumerate(integrationResults["clustering"]) \
											 if curClust == cluster]
			if len(clusterMotifs) > 1:
				scores = []
				for m1 in clusterMotifs:
					for m2 in clusterMotifs:
						if m1 != m2:
							# perform the pairwise alignment of these two motifs
							curAlignments = pairwise2.align.globalxx(m1.split("|")[0],
																											m2.split("|")[0])
							# extract and use the best alignment from the results
							# (scaling it in 0-100.0 as the identity percent).
							scores.append(100.0 * float(max([aln[2] for aln in curAlignments])) /
														float(max(len(m1), len(m2))))
				# store the mean pairwise alignment score as cluster cons. score.
				consensusesScores[cluster] = mean(scores)
				clustersScores[cluster] += consensusesScores[cluster]
			else:
				consensusesScores[cluster] = 0
				clustersScores[cluster] += 0

		# plot per-cluster gc content based on composing motifs consensuses.
		clustersGC = [0] * len(clusters)
		for cluster in clusters:
			clusterMotifs = [integrationResults["motifs"][i].split("|")[0] \
											 for i, curClust in \
											 enumerate(integrationResults["clustering"]) \
											 if curClust == cluster]
			clustersGC[cluster] = 100.0 * mean([(float(m.upper().count("G")) + \
																						float(m.upper().count("C"))) /
																				float(len(m)) for m in clusterMotifs])

		# clean the slate with a new figure.
		plt.figure()
		barsWidth = .3
		clustersPos = [c + 1 for c in clusters]
		clustersLabPos = [c + barsWidth / 2 for c in clustersPos]
		titleFontDict = {"fontsize":10, "fontweight":"bold"}

		# plot the overall clusters scores.
		plt.subplot(221)
		plt.bar(clustersPos, clustersScores, width=barsWidth)
		# set axes labels, titles and graphical parameters.
		plt.xlim([.5, len(clusters)+.5])
		plt.xticks(clustersLabPos, ["Cluster " + str(c) for c in clusters],
							 rotation=90)
		plt.tick_params(axis="both", which='major', labelsize=10, pad=10,
										right="off", top="off", bottom="off")
		plt.ylabel("Score", fontsize=10)
		# draw the plot title
		plt.title("Overall clusters score", y=1.03, fontdict=titleFontDict)

		# plot the per-cluster average instances scores.
		plt.subplot(222)
		plt.bar(clustersPos, instancesScores, width=barsWidth)
		plt.xlim([.5, len(clusters)+.5])
		# set axes labels, titles and graphical parameters.
		plt.xticks(clustersLabPos, ["Cluster " + str(c) for c in clusters],
							 rotation=90)
		plt.tick_params(axis="both", which='major', labelsize=10, pad=10,
										right="off", top="off", bottom="off")
		plt.ylabel("Score", fontsize=10)
		# draw the plot title
		plt.title("Clusters instances score", y=1.03, fontdict=titleFontDict)

		# plot the per-cluster consensuses coherence score.
		plt.subplot(223)
		plt.bar(clustersPos, consensusesScores, width=barsWidth)
		plt.xlim([.5, len(clusters)+.5])
		# set axes labels, titles and graphical parameters.
		plt.xticks(clustersLabPos, ["Cluster " + str(c) for c in clusters],
							 rotation=90)
		plt.tick_params(axis="both", which='major', labelsize=10, pad=10,
										right="off", top="off", bottom="off")
		plt.ylabel("Score", fontsize=10)
		# draw the plot title
		plt.title("Clusters consensuses coherence", y=1.03, fontdict=titleFontDict)

		# if clusters silhouette scores are available, plot them.
		plt.subplot(224)
		if len(silhouettesScores) > 0:
			plt.bar(clustersPos, silhouettesScores, width=barsWidth)
			plt.ylabel("Score", fontsize=10)
		# otherwise plot GC contents in their place.
		else:
			plt.bar(clustersPos, clustersGC, width=barsWidth)
			plt.ylabel("GC %", fontsize=10)
		# set axes labels, titles and graphical parameters.
		plt.xlim([.5, len(clusters)+.5])
		plt.xticks(clustersLabPos, ["Cluster " + str(c) for c in clusters],
							 rotation=90)
		plt.tick_params(axis="both", which='major', labelsize=10, pad=10,
										right="off", top="off", bottom="off")
		# draw the plot title
		plt.title("Clusters silhouettes" if len(silhouettesScores) > 0 \
							else "Clusters consensuses GC content", y=1.03,
							fontdict=titleFontDict)

		# prepare cluster patches and labels for the legend.
		clustersPatches = []
		for key in clusters:
			keyDesc = "Cluster " + str(key) + " (" + ("%.1f" % clustersGC[key]) + \
							"% GC, motif types: " + ", ".join(clustersMotifsTypes[key]) + \
							") :\n" + ", ".join([integrationResults["motifs"][i] \
							for i in range(0, len(integrationResults["clustering"])) \
							if integrationResults["clustering"][i] == int(key)]) + "\n"
			# format the cluster label to be in lines of max 60 characters.
			keyDesc = dynamit.utils.formatStringToLineLength(keyDesc, 60)
			clustersPatches.append(mpatches.Patch(facecolor=(0, 0, 0, 0.75),
														 linewidth=0.5, label=keyDesc[:-1]))

		# draw the clusters-motifs association legend at the
		# bottom of the plot, to indicate clusters composition.
		clustersLegendPatch = plt.legend(title="Clusters composition",
															handles=clustersPatches,
															handlelength=.75, loc=9,
															bbox_to_anchor=(0.5, -0.05),
															bbox_transform=plt.gcf().transFigure, fontsize=10,
															borderpad=1.0, fancybox=True).legendPatch

		# use tight layout to have a correct spacing around subplots.
		plt.tight_layout()

		# save the final figure to file in PDF format.
		plt.savefig(os.path.join(os.getcwd(), "results_ClusterEvaluation.pdf"),
								bbox_inches="tight", pad_inches=.25,
								bbox_extra_artists=[clustersLegendPatch],
								format="PDF", orientation='landscape', transparent=False)

		# write the text file with per-cluster scores and detailed information.
		with open("results_ClusterEvaluation.txt", "wb") as outHandle:
			for cluster in clusters:
				outHandle.write("Cluster " + str(cluster) + ":\n")
				outHandle.write("Overall score: " + "%.2f" % clustersScores[cluster] \
												+ "\n")
				outHandle.write("Size score: " + "%.2f" % (10.0 * \
												list(integrationResults["clustering"]).count(cluster)) \
												+ "\n")
				outHandle.write("Instances score: " + \
												"%.2f" % instancesScores[cluster] + "\n")
				outHandle.write("Consensuses coherence score: " + \
												"%.2f" % consensusesScores[cluster] + "\n")
				if len(silhouettesScores) > 0:
					outHandle.write("Silhouette score: " + \
													"%.2f" % silhouettesScores[cluster] + "\n")
				outHandle.write("Motifs types: " + \
												", ".join(sorted(clustersMotifsTypes[cluster])) + "\n")
				outHandle.write("Motifs types score: " + \
												str(10.0*len(clustersMotifsTypes[cluster])) + "\n")
				outHandle.write("Motifs consensuses average GC content: " + \
												"%.1f" % clustersGC[cluster] + "%\n\n")

		print "  [ClusterEvaluationPrinter] Printing completed. Results are stored in" \
					"    <" + os.path.join(os.getcwd(), "results_ClusterEvaluation.pdf") + \
					"> and    <" + os.path.join(os.getcwd(), "results_ClusterEvaluation.txt") + "."
		return 0
