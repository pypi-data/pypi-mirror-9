""" Module for the WebLogoPrinter classes."""

import dynamit.resultsPrinter

import os, tempfile
import weblogolib

from Bio.Align.Applications import ClustalOmegaCommandline

class WebLogoPrinter(dynamit.resultsPrinter.ResultsPrinter):
	"""ResultsPrinter that generates a graphical and a textual
	WebLogo from the alignment of each cluster composants (it
	is thus compatible with any integration strategy performing
	motifs clustering and cluster components alignment, as is,
	for instance, the AlignmentStrategy). Requires the
	clusters multipleAlignment and consensuses fields to be
	present in integrationResults; if these fields are not available
	but clustering information is it will compute the weblogo of
	each cluster (by the cluster instances on sequences). If even
	clustering is not available, it will draw weblogos for single
	motifs (by their instances, thus being compatible with any
	integration strategy).
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.resultsPrinterName = "WebLogo"
		self.clustalOmegaPath = ""

	def setConfiguration(self, configString):
		"""Loads the printer parameters specified in the configuration file.

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if configString != "":
			# if something was specified, it should be clustalOmega tool path.
			self.clustalOmegaPath = configString

		return 0

	def printResults(self, sequences, searchResults,
									 integrationStrategyName, integrationResults):
		"""Performs the WebLogo generation with specified parameters.
		Requires at minimum the motifs field of integrationResults;
		if the clusters multiple alignments and consensuses fields
		are present they are used. If no alignment result
		is present, but clustering informations are, it will compute
		the weblogo for each motifs cluster (based on its instances);
		if neither alignment nor clustering informations are present,
		it will compute the weblogo for each individual motif (based on
		its instances).

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
			print "[ERROR] Unable to run the WebLogoPrinter. \"motifs\"" \
						" key not found in the passed integration results data structure."
			return 1

		# get an easy to access sequence dictionary.
		seqsDict = dict([(seq.description, seq) for seq in sequences])

		# set weblogo printing options
		options = weblogolib.LogoOptions()
		options.creator_text = "DynaMIT"
		options.fineprint = "DynaMIT through WebLogo"
		options.stack_width = 30
		options.stack_aspect_ratio = 2

		options.title_fontsize = 12
		options.logo_title = "Motif WebLogo"

		# do one weblogo per cluster, made with the multiple alignment of
		# its composing motifs consensuses.
		if (integrationResults.has_key("clustersMultipleAlignments") and
			 integrationResults.has_key("clustersConsensuses")):
			# do weblogo for each cluster.
			for i, multAlign in enumerate(integrationResults["clustersMultipleAlignments"]):
				# write motifs sequences to file for weblogo generation
				motifsFilename = os.path.join(tempfile.gettempdir(), "motifs.fasta")
				motifsHandle = open(motifsFilename, "wb")
				for line in multAlign.split('\n'):
					motifInfo = line.split(' ')
					motifsHandle.write(">" + motifInfo[1] + "\n" + motifInfo[0] + "\n")
				motifsHandle.close()

				# load sequences into weblogo required format
				inputSeqsHandle = open(motifsFilename)
				data = weblogolib.LogoData.from_seqs(
												weblogolib.read_seq_data(inputSeqsHandle))
				inputSeqsHandle.close()

				# set the logo title
				options.logo_title = "Cluster " + str(i) +" consensus: " + \
															integrationResults["clustersConsensuses"][i]
				# set the logo format.
				myLogoFormat = weblogolib.LogoFormat(data, options)

				# generate the eps weblogo and save it into the printer results folder
				pdfFile = open(os.path.join(os.getcwd(),
											 "Cluster_" + str(i) + "_WebLogo.pdf"), "wb")
				pdfFile.write(weblogolib.pdf_formatter(data, myLogoFormat))
				pdfFile.close()

				# generate the text weblogo and save it into the printer results folder
				txtFile = open(os.path.join(os.getcwd(),
											 "Cluster_" + str(i) + "_WebLogo.txt"), "wb")
				txtFile.write(weblogolib.txt_formatter(data, myLogoFormat))
				txtFile.close()

			# report printer completion and inform the user of output file existence.
			print "  [WebLogoPrinter] Printing completed. " + \
						"PDF and text weblogos are stored in \n    <" + \
						os.path.join(os.getcwd(), "Cluster_<number>_WebLogo.pdf") + \
						"> and <" + \
						os.path.join(os.getcwd(), "Cluster_<number>_WebLogo.txt") + ">."

		# do cluster components multiple alignment weblogo no clusters
		# alignments, so print individual clusters weblogos (by instances).
		elif integrationResults.has_key("clustering"):
			# do by motif cluster instances weblogo
			for cluster in list(set(integrationResults["clustering"])):
				# open cluster matches sequences file.
				matchesFilename = os.path.join(tempfile.gettempdir(), "matches.fasta")
				# get the output alignment filename.
				alignmentFilename = os.path.join(tempfile.gettempdir(), "matches.aln")
				# remove the alignment filename to avoid future problems.
				if os.path.isfile(alignmentFilename):
					os.remove(alignmentFilename)
				matchesHandle = open(matchesFilename, "wb")
				# do for all motifs belonging to this cluster.
				instIndex = 0
				for motif in [m for i, m in enumerate(integrationResults["motifs"]) \
											if integrationResults["clustering"][i] == cluster]:
					motifInfo = motif.split('|')
					matches = [m for m in searchResults \
										 if ((m.split('\t')[0] == motifInfo[0]) and
										 (m.split('\t')[2] == motifInfo[1]))]
					# write down all matches sequences to the cluster matches file.
					for match in matches:
						matchInfo = match.split('\t')
						matchSeq = seqsDict[matchInfo[3]][max(0, int(matchInfo[4])-1):int(matchInfo[5])-1]
						matchesHandle.write(">" + str(instIndex) + "\n" + str(matchSeq.seq) + "\n")
						instIndex += 1
				# we are done writing matches for this cluster.
				matchesHandle.close()
				# compute the multiple alignment of all motifs and its consensus.
				clustalomega_cline = ClustalOmegaCommandline(
															os.path.join(self.clustalOmegaPath, "clustalo"),
															infile=matchesFilename, outfile=alignmentFilename)
				# run the actual alignment with clustalomega
				clustalomega_cline()
				# load the aligned cluster sequences into the format required by weblogo
				inputSeqsHandle = open(alignmentFilename)
				data = weblogolib.LogoData.from_seqs(
													weblogolib.read_seq_data(inputSeqsHandle))
				inputSeqsHandle.close()
				# remove the alignment filename to avoid future problems.
				os.remove(alignmentFilename)

				# set the logo title.
				options.logo_title = "Cluster " + str(cluster)
				# set the logo format.
				myLogoFormat = weblogolib.LogoFormat(data, options)

				# generate the pdf weblogo and save it into the printer results folder
				pdfFile = open(os.path.join(os.getcwd(),
											 "Cluster_" + str(cluster) + "_instances_WebLogo.pdf"), "wb")
				pdfFile.write(weblogolib.pdf_formatter(data, myLogoFormat))
				pdfFile.close()

				# generate the text weblogo and save it into the printer results folder
				txtFile = open(os.path.join(os.getcwd(),
											 "Cluster_" + str(cluster) + "_instances_WebLogo.txt"), "wb")
				txtFile.write(weblogolib.txt_formatter(data, myLogoFormat))
				txtFile.close()

			# report printer completion and inform the user of output file existence.
			print "  [WebLogoPrinter] Printing completed. " + \
						"PDF and text weblogos are stored in \n    <" + \
						os.path.join(os.getcwd(),
												 "Cluster_<number>_instances_WebLogo.pdf") + \
						"> and <" + \
						os.path.join(os.getcwd(),
												 "Cluster_<number>_instances_WebLogo.txt") + ">."

		# no clustering, no clusters alignments, so print individual motifs
		# weblogos (by instances).
		else:
			# get individual motifs from search results.
			motifs = dynamit.utils.getMotifsFromSearchResults(searchResults)
			for motif in motifs:
				motifInfo = motif.split('|')
				matches = [m for m in searchResults \
									 if ((m.split('\t')[0] == motifInfo[0]) and
									 (m.split('\t')[2] == motifInfo[1]))]
				# write down all motif matches to file.
				matchesFilename = os.path.join(tempfile.gettempdir(), "matches.fasta")
				matchesHandle = open(matchesFilename, "wb")
				instIndex = 0
				for match in matches:
					matchInfo = match.split('\t')
					matchSeq = seqsDict[matchInfo[3]][max(0, int(matchInfo[4])-1):int(matchInfo[5])-1]
					matchesHandle.write(">" + str(instIndex) + "\n" + str(matchSeq.seq) + "\n")
					instIndex += 1
				matchesHandle.close()
				# load sequences into the format required by weblogo
				inputSeqsHandle = open(matchesFilename)
				data = weblogolib.LogoData.from_seqs(
													weblogolib.read_seq_data(inputSeqsHandle))
				inputSeqsHandle.close()

				# set the logo title.
				options.logo_title = motif
				# set the logo format.
				myLogoFormat = weblogolib.LogoFormat(data, options)

				# generate the pdf weblogo and save it into the printer results folder
				pdfFile = open(os.path.join(os.getcwd(),
											 motifInfo[0] + "_" + motifInfo[1] + "_instances_WebLogo.pdf"), "wb")
				pdfFile.write(weblogolib.pdf_formatter(data, myLogoFormat))
				pdfFile.close()

				# generate the text weblogo and save it into the printer results folder
				txtFile = open(os.path.join(os.getcwd(),
											 motifInfo[0] + "_" + motifInfo[1] + "_instances_WebLogo.txt"), "wb")
				txtFile.write(weblogolib.txt_formatter(data, myLogoFormat))
				txtFile.close()

			# report printer completion and inform the user of output file existence.
			print "  [WebLogoPrinter] Printing completed. " + \
						"PDF and text weblogos are stored in \n    <" + \
						os.path.join(os.getcwd(),
												 "<motifName>_instances_WebLogo.pdf") + \
						"> and <" + \
						os.path.join(os.getcwd(),
												 "<motifName>_instances_WebLogo.txt") + ">."

		return 0
