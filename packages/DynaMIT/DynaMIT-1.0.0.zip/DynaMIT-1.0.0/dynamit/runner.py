"""Module for handling DynaMIT execution in all its three phases.
"""

import sys, os, shutil, StringIO
from multiprocessing import Pool

import dynamit.utils

def runSearcherThread((processSearcher, sequencesFilename)):
	"""Function executing the run method of the passed
	processSearcher object on the sequencesFilename file.
	Capture stdout and stderr to a StringIO variable for
	threaded execution (thus allowing to print the whole
	output of thread in one block after execution).

	Args:
		processSearcher: the MotifSearcher object for which the
										 run method must be executed.
		sequencesFilename: name of the file containing input sequences.

	Returns:
		Returns a tuple containing the modified processSearcher object,
		the return value of its run method and a StringIO variable
		containing the method console output.
	"""
	try:
		# redirect this process STDOUT/ERR to store the searcher's output.
		processOutput = StringIO.StringIO()
		sys.stdout = sys.stderr = processOutput

		# inform that the searcher is starting.
		print "  [INFO] Starting the " + processSearcher.searcherName + \
					" searcher..."

		# run the searcher and store its return value.
		returnValue = processSearcher.runSearch(sequencesFilename)
	except OSError:
		print "[ERROR] Unable to run the <" + processSearcher.searcherName + \
					"> motif searcher. The likely cause of the error is a wrong " \
					" tool path specification in the configuration file. " \
					"Continuing with remaining searchers..."
		returnValue = 1
	except (IOError, IndexError, RuntimeError, ValueError):
		print "[ERROR] Unable to run the <" + processSearcher.searcherName + \
					"> motif searcher. Continuing with remaining searchers..."
		returnValue = 1

	# we are done with the searcher, so return its object, along with
	# its return value and console output for the parent process.
	return (processSearcher, returnValue, processOutput)


class Runner(object):
	"""Class devoted to running the various phases of DynaMIT workflow.
	Loads the configurations, runs motif searchers and forward the results
	to the selected integration strategy which is then executed.
	Eventually, runs the specified results printers and terminates the
	run execution. This class is instantiated and its methods called only
	by the __main__ script, which acts as an interface to the command-line.
	"""

	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		self.searchers = []
		self.integrator = None
		self.searchesResults = []
		self.integrationResults = {}
		self.printers = []
		self.outputFolder = ""
		self.sequencesFilename = ""

	def loadConfiguration(self, filename):
		"""Reads DynaMIT configuration from the specified filename,
		instantiates and configures all the MotifSearchers and the
		IntegrationStrategy listed in the configuration file.
		filename: Name of the file containing DynaMIT configuration.

		Args:
			filename: filename containing the configuration to be loaded.

		Returns:
			Returns 0 if everything went fine, 1 and prints an error
			message otherwise.
		"""
		print "\n--------------------------------\nLoading DynaMIT " + \
					"configuration...\n--------------------------------"

		try:
			configHandle = open(filename)
			self.searchers = []
			self.integrator = None
			self.printers = []
			linesCount = 1
			for line in configHandle.readlines():
				# allow for comment lines in the configuration file, starting with #.
				if not line.startswith("#"):
					# get the line parts defining the configuration elements
					# (MotifSearcher or Integrator, classname, ecc).
					componentType, fullClassName, path, params = \
														line.rstrip('\n').split('\t')

					try:
						# instantiate the component...
						newComponent = dynamit.utils.getClassInstance(fullClassName)
						# ...and try to configure it.
						configurationOutcome = 0
						# as the motif searcher component may need the underlying tool
						# path, they take one more parameter (the path) than integration
						# strategies and results printers when setting configuration.
						if componentType == "MotifSearcher":
							configurationOutcome = newComponent.setConfiguration(path, params)
						else:
							# path is expected to be empty for IntegrationStrategies and
							# ResultsPrinters configuration lines, and is not used.
							configurationOutcome = newComponent.setConfiguration(params)
						if configurationOutcome == 0:
							if componentType == "MotifSearcher":
								# store the MotifSearcher component.
								self.searchers.append(newComponent)
							elif componentType == "IntegrationStrategy":
								# if an IntegrationStrategy was already loaded from configuration,
								# warn that only the last loaded one will be used
								if self.integrator != None:
									print "[WARNING] The configuration defines more than one " + \
												"integration strategy. DynaMIT will use the last " + \
												"strategy found in the configuration file."
								# store the integrationStrategy component.
								self.integrator = newComponent
							elif componentType == "ResultsPrinter":
								# store the integrationStrategy component.
								self.printers.append(newComponent)
							# inform the user of the new component successful loading.
							print "[SUCCESS:%d] Instance of the < %s > %s was initialized." \
										% (linesCount, fullClassName, componentType)
						else:
							# raise this exception so that, as configuration went wrong
							# (returned value != 0), we stop and report the issue.
							raise ValueError('')
					except ValueError:
						# an error occured in configuring the component, report it
						# abort execution to avoid any problems later on.
						print "[ERROR:%d] Impossible to instantiate the < %s > " \
									"%s at configuration line %d." \
									% (linesCount, fullClassName, componentType, linesCount)
						return 1

				# keep track of line number to report errors if they occur.
				linesCount += 1

			# otherwise, if configuration loading went fine, check that we have
			# all required components in the right quantities.
			if len(self.searchers) < 1:
				print "[ERROR] No motif searcher could be loaded from " \
							"the configuration file."
				return 1
			elif self.integrator == None:
				print "[ERROR] No integration strategy could be loaded from " \
							"the configuration file."
				return 1
			elif len(self.printers) < 1:
				self.printers = [
					dynamit.utils.getClassInstance("dynamit.tablePrinter.TablePrinter"),
					dynamit.utils.getClassInstance("dynamit.clusterEvaluationPrinter" \
																				 ".ClusterEvaluationPrinter")]
				print "[WARNING] No results printer could be loaded from the " + \
							"configuration file. Execution will continue anyway, " + \
							"TablePrinter and ClusterEvaluationPrinter will be run."

			# report success in loading the configuration. DynaMIT can now be run.
			print "[FINISHED] Configuration loaded successfully."
			return 0
		except IOError:
			print "[ERROR] The configuration file < %s > does not exist." % filename
			return 1
		except (ImportError, AttributeError):
			print "[ERROR] Cannot instantiate the < %s > component: please check " \
						"the class name correctness in the configuration file." % fullClassName
			return 1
		except StandardError:
			print "[ERROR] Unexpected error: please check your configuration file " \
						"at line " + str(linesCount) + "."
			print sys.exc_info()[0]
			return 1

	def run(self, outputFolderName, sequencesFilename, nproc=1):
		"""Runs DynaMIT with current configuration, first performing motif
		searches (in rounds of nproc parallel processes) and eventually
		running the integration strategy on all collected results.

		Args:
			outputFolderName: folder into which results will be stored.
			sequencesFilename: filename containing sequences to be analyzed.
			nproc: number of processor cores to use for running the search
						 phase (default=1).

		Returns:
			Returns 0 if everything went fine, 1 and prints an error
			message otherwise.
		"""
		print "\n--------------------------------\nStarting DynaMIT run...\n" + \
					"--------------------------------"

		# check that configuration was loaded prior to trying running DynaMIT.
		if (len(self.searchers) < 1) or (self.integrator == None):
			print "[ERROR] Please call loadConfiguration() prior to calling run()!"
			return 1

		# check for the input sequences file existence.
		if not os.path.isfile(sequencesFilename):
			print "[ERROR] Could not find the specified input sequences filename."
			return 1

		# check that the run folder was specified correctly.
		if outputFolderName == "":
			print "[ERROR] Please specify a non-empty output folder name."
			return 1
		# create the run folder if it does not exist yet, and store its path
		if not os.path.isdir(outputFolderName):
			os.mkdir(outputFolderName)
		self.outputFolder = os.path.abspath(outputFolderName)
		# copy the sequences file into the output folder
		shutil.copy(sequencesFilename, self.outputFolder)
		self.sequencesFilename = os.path.abspath(os.path.join(outputFolderName,
																				 os.path.basename(sequencesFilename)))
		# move to the output folder, so that all subsequent
		# operations can take place there
		os.chdir(self.outputFolder)

		# load sequences into BioPython SeqRecord objects for use by
		# integration strategies and results printers
		sequences = dynamit.utils.getSequencesRecords(self.sequencesFilename)
		# check that there are at least two sequences in the input file.
		if (sequences == 1) or (len(sequences) < 2):
			print "[ERROR] The specified input sequences filename contains less " \
						"than two sequences or is in the wrong format (FASTA required)."
			return 1

		print "[STARTING] Running motif searchers..."

		if nproc > 1 and sys.platform.startswith("win") and sys.version_info[0] == 2:
			print "  [WARNING] Parallel execution of motif searchers in Python 2.x on\n" \
						"            Windows is disabled due to a bug in the multiprocessing module.\n" \
						"            Motif searchers execution will proceed using a single processor."
			nproc = 1

		if nproc > 1:
			# run motif searchers in parallel with nproc processes.
			searchersPool = Pool(processes=nproc)
			results = searchersPool.map(runSearcherThread,
								[(searcher, self.sequencesFilename) for searcher in self.searchers])

			self.searchers = []
			for searcherResults in results:
				# store the searcher containing execution results.
				self.searchers.append(searcherResults[0])
				# if the searcher was successfull, extract its results.
				if searcherResults[1] != 1:
					# appending them to global results list.
					self.searchesResults.extend(searcherResults[1])
				# print the searcher console output to the console.
				print searcherResults[2].getvalue()
		else:
			# execute motif search in single-processor mode:
			# run all searchers loaded by configuration one-by-one.
			for searcher in self.searchers:
				try:
					# run the searcher and append its results to overall search results.
					print "  [INFO] Starting the " + searcher.searcherName + " searcher..."
					currentSearcherResults = searcher.runSearch(self.sequencesFilename)
					# check that the searcher run with success and store its results.
					if currentSearcherResults != 1:
						self.searchesResults.extend(currentSearcherResults)
					else:
						raise ValueError('Unexpected searcher error')
				except OSError:
					print "[ERROR] Unable to run the <" + searcher.searcherName + \
								"> motif searcher. The likely cause of the error is a wrong " \
								" tool path specification in the configuration file. " \
								"Continuing with remaining searchers..."
				except (IOError, IndexError, RuntimeError, ValueError):
					print "[ERROR] Unable to run the <" + searcher.searcherName + \
								"> motif searcher. Continuing with remaining searchers..."

		# check if search results are empty, if so abort.
		if len(self.searchesResults) == 0:
			print "[ERROR] Motif search with the specified configuration yielded no results."
			return 1

		# save motifs matches to a tab-separated file
		# (for debugging purposes and user inspection)
		with open("motifSearchesResults.txt", "wb") as resultsHandle:
			resultsHandle.write("#motif	motifType	motifSearcher	sequenceID	startPos	endPos\n")
			for match in self.searchesResults:
				resultsHandle.write(match + "\n")

		print "  [INFO] Motifs matches saved to < motifSearchesResults.txt >.\n" \
					"[FINISHED] Motif searches completed successfully.\n"

		# perform motifs integration according to the selected integration strategy.
		print "[STARTING] Running results integration strategy..."
		self.integrationResults = self.integrator.doIntegration(sequences,
																														self.searchesResults)

		if self.integrationResults != 1:
			# save integration results to a file (for debugging purposes and user inspection).
			with open("integrationResults_" + \
								self.integrator.integrationStrategyName + ".txt", "wb") as resultsHandle:
				for (key, value) in self.integrationResults.iteritems():
					resultsHandle.write(key + ":\n" + str(value) + "\n")
			print "  [INFO] Raw integration results saved to < integrationResults.txt >."
			print "[FINISHED] Results integration completed successfully.\n"
		else:
			print "[ERROR] Unable to run the <" + \
						self.integrator.integrationStrategyName + \
						"> integration strategy."
			# integration failed, so if any printer was specified, try to run it
			# anyway with motifs list as the only integration result.
			if len(self.printers) > 0:
				self.integrationResults = {"motifs":
																		dynamit.utils.getMotifsFromSearchResults(
																										self.searchesResults)}
				print "[INFO] Trying to run specified results printers with " \
							" motifs list only as integration results..."

		# perform results printing with each of the selected printers, if any.
		if len(self.printers) > 0:
			print "[STARTING] Running results printers..."

			for printer in self.printers:
				# make a folder for the printer results and move into it
				# so that the output of this printer will be stored in its folder
				printerDir = "results_" + printer.resultsPrinterName
				if not os.path.isdir(printerDir):
					os.mkdir(printerDir)
				os.chdir(printerDir)
				# run the printer
				printer.printResults(sequences, self.searchesResults,
														 self.integrator.integrationStrategyName,
														 self.integrationResults)
				# move back to global results folder
				os.chdir(self.outputFolder)

			print "[FINISHED] Results printing completed successfully."

		print "\n--------------------------------\nDynaMIT run completed!\n---" + \
					"-----------------------------\n[INFO] Results can be found in " + \
					"the <" + self.outputFolder + "> folder."

		return 0


	def exportResults(self):
		"""Obtains the raw run results (prior to running the printers) from
		the integrator component used.

		Returns:
			Returns the integration strategy results.
		"""
		if not self.integrationResults:
			print "[ERROR] Results generation failed or not yet performed."
			return 1
		else:
			return self.integrationResults
