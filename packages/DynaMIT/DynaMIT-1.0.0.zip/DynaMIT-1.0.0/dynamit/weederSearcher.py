""" Module for the WeederSearcher classes."""

import os, subprocess
from subprocess import CalledProcessError

import dynamit.motifSearcher

class WeederSearcher(dynamit.motifSearcher.MotifSearcher):
	"""This class implements a motif searcher running the
	Weeder motif search tool (http://159.149.160.51/modtools/,
	Pavesi G, Mereghetti P, Mauri G, Pesole G. Weeder Web: discovery
	of transcription factor binding sites in a set of sequences from
	co-regulated genes. Nucleic Acids Res. 2004 Jul 1;32(Web Server
	issue):W199-203.)
	"""
	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		super(self.__class__, self).__init__()
		self.path = ""
		self.searcherName = "Weeder"

	def setConfiguration(self, path, params):
		"""Loads the searcher parameters specified in the configuration file.

		Args:
			path: path of the Weeder executable file.
			params: parameters to be given to Weeder along with the sequences filename.

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		if path != "":
			self.path = path
		if params != "":
			self.params = params
		return 0

	def runSearch(self, sequencesFilename):
		"""Performs motif search with Weeder, provided
		input sequences filename and configured parameters.

		Args:
			sequencesFilename: input sequences filename for this run.

		Returns:
			Returns a list of strings representing motifs matches if
			everything went fine (details on results filenames, etc., are
			printed to the console); returns 1 and an error message otherwise.
		"""
		# get current working directory
		cwd = os.getcwd()
		# move to Weeder directory (it won't work if launched outside it)
		os.chdir(self.path)
		# compose the complete command-line for launching Weeder.
		completePath = os.path.join(self.path, "weederlauncher.out") + " \"" + \
									 sequencesFilename + "\" " + self.params
		completeAdvisorPath = "adviser.out \"" + sequencesFilename + "\" "

		# check for the presence of previous Weeder results for the specified
		# sequences filename if any file is present, remove it to avoid errors,
		# as Weeder concatenates rather than plain overwriting
		if os.path.isfile(sequencesFilename + ".wee"):
			os.remove(sequencesFilename + ".wee")

		# prepare sequences dictionary to be later passed to processWeederResults.
		sequences = dict([(seqRecord.description, str(seqRecord.seq)) \
				for seqRecord in dynamit.utils.getSequencesRecords(sequencesFilename)])

		try:
			# launch Weeder and wait for its execution to complete
			# (store its stderr for use if an error happens).
			subprocess.check_output(completePath, shell=True, stderr=subprocess.STDOUT)
			# launch weeder advisor producing suggestions on the best motifs to
			# consider. It returns a non-zero exit status, different from 1,
			# when it is succesfully executed, so can't use check_output as is.
			if subprocess.call(completeAdvisorPath, shell=True, stderr=os.pipe()[1]) == 1:
				raise CalledProcessError(1, cmd=completeAdvisorPath,
																 output="\nAdviser execution error.")
			else:
				# move back to working directory
				os.chdir(cwd)
				# check if Weeder results exist
				if os.path.isfile(sequencesFilename + ".wee"):
					# extract results
					print "  [WeederSearcher] Search completed."
					self.searchResults = self._processWeederResults(sequences,
																													sequencesFilename + \
																												 ".wee")
				else:
					print "[ERROR] Could not find Weeder results file."
					return 1
		except CalledProcessError as e:
			# inform about the error that happened,
			print "[ERROR] Weeder execution terminated with an error:" + e.output
			# move back to working directory and
			os.chdir(cwd)
			# abort searcher execution.
			return 1

		# remove Weeder auxiliary output files (html and mix)
		# keep only its main results file (wee)
		if os.path.isfile(sequencesFilename + ".mix"):
			os.remove(sequencesFilename + ".mix")
		if os.path.isfile(sequencesFilename + ".html"):
			os.remove(sequencesFilename + ".html")

		print "  [WeederSearcher] Execution completed."
		return self.searchResults

	def _processWeederResults(self, sequences, resultsFilename):
		""" Process results contained in Weeder output files to
		produce a table for subsequent DynaMIT phases.

		Args:
			sequences: a dictionary of sequences (id is key, sequence is value).
			resultsFilename: the Weeder results filename.
		Returns:
			Returns a list of strings, one per motif match, containing
			motif sequence, sequence id, match position, etc.
		"""
		print "  [WeederSearcher] Processing results: <", \
					os.path.basename(resultsFilename), ">"
		try:
			# get results lines from Weeder output file.
			with open(resultsFilename) as f:
				lines = f.readlines()

			processedResults = []
			mappings = {}
			inMotif = False
			currentMotif = ''

			# get the list of lines starting with "Your sequences";
			# these lines preceed in Weeder the motifs list.
			i = [lineIdx for lineIdx, val in enumerate(lines) \
					 if val.startswith("Your sequences")]
			if len(i) == 0:
				# Weeder found zero motifs, so return an empty results list.
				return []
			else:
				# otherwise, find the starting line as the latest one starting with
				# "Your sequences:" (+ 2 so that we start with first sequence mapping).
				i = i[-1] + 2

			# process lines mapping Weeder sequence IDs to their original FASTA
			# file ID. We start directly from the line with the first mapping,
			# so as soon as we find an empty line we are done.
			while lines[i] != '\n':
				# maps current sequence number assigned by Weeder to its
				# original ID from the input FASTA file.
				currentSequenceNum = lines[i][9:lines[i].find(":", 9) - 1]
				mappings[currentSequenceNum] = lines[i][lines[i].find(">") + \
										1:lines[i].find(" ", lines[i].find(">") + 1)].rstrip('\t')
				i += 1

			# now look for motifs and their instances, and process them.
			while i < len(lines):
				# if we are inside a motif instances lines.
				if inMotif:
					# if we have finished reading this motif instances.
					if (lines[i] == '\n') or (lines[i] == ''):
						# report we are outside of a motif.
						currentMotif = ''
						inMotif = False
					else:
						# split the motif instance line in its non-whitespace components.
						info = [chunk for chunk in lines[i].lstrip(' ').split(' ') \
										if chunk != '']
						fullSeqID = dynamit.utils.getFullSequenceID(sequences,
																								mappings[info[0]],
																								int(info[3])+len(currentMotif))
						fullSeqID = mappings[info[0]] if fullSeqID == -1 else fullSeqID
						# add current match to the list of Weeder matches.
						processedResults.append(currentMotif + "\tsequence\t" + \
																		self.searcherName + "\t" + \
																		fullSeqID + "\t" + info[3] + "\t" + \
																		str(int(info[3])+len(currentMotif)) + \
																		"\t" + info[4].lstrip('(').rstrip(')'))
				# first part: line at beginning of highest ranking motifs.
				# second part: line at beginning of non-highest ranking motifs.
				# third part: line at the end of a motif (and of file if length
				# is not more than 2 lines after current line).
				elif ((lines[i].find("seem to be") > 0) or
						 (lines[i].find("can also be") > 0) or
						 ((lines[i].find("=====") >= 0) and (len(lines) > i+5))):
					# if we have reached the not-highest ranking motifs, stop.
					#if lines[i+2].find("can also be") > 0:
					#	break
					# otherwise we are inside a top-ranking motif, go on.
					inMotif = True
					# get motif consensus line and store it.
					currentMotif = lines[i+5].rstrip('\n') \
												 if lines[i+2].find("can also be") > 0 else \
												 lines[i+3].rstrip('\n')
					#print "---\n",lines[i],lines[i+3],lines[i+10],"---"
					# move to first motif instance line.
					i += 12 if lines[i+2].find("can also be") > 0 else 10
					continue

				i += 1
			# return processed motifs matches.
			return processedResults
		except (IOError, IndexError, KeyError, RuntimeError, ValueError) as e:
			print "  [WeederSearcher] Unexpected error:%s" % str(e)
			raise
