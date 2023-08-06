"""Main module for launching DynaMIT execution.
"""

import sys, time
from dynamit import runner

def main():
	"""Main entry point for command-line DynaMIT execution.
	Prints usage information if no parameter is specified,
	otherwise launches the Runner with passed parameters.
	"""
	# if the -h parameter or no parameter at all were specified,
	# display the command line reference.
	if (len(sys.argv) < 3) or ("-h" in sys.argv):
		print "\n-----------------------------------------\nDynaMIT command " + \
					"line reference\n-----------------------------------------"

		print "\nSYNOPSIS -----------------------------------\n\n" \
					"\tmain.py CONFIGURATION_FILE SEQUENCES_FILE [options]"

		print "\nDESCRIPTION -----------------------------------\n"
		print "DynaMIT searches for motifs in a given set of sequences by combining"
		print "searches by multiple tools, eventually integrating all found motifs"
		print "through an integration strategy. Both search tools and the integration"
		print "strategy to use are specified through a configuration file: the software"
		print "can thus be extendedwith new search tools or integration " + \
					"strategies\nin a seamless way.\n"

		print "HOW TO BUILD THE CONFIGURATION FILE -----------------------------------\n"
		print "The configuration file is composed by multiple lines specifying " \
					"motif\nsearch tools, a line indicating which integration strategy " \
					"to use and one or more lines specifying results printers.\nEvery " \
					"search tool line must look like this:\n"
		print "\tMotifSearcher	full_python_class_name	tool_path	parameters\n"
		print "- full_python_class_name: class name, complete with module name " \
					"of the Python class defining the desired search tool.\n"
		print "- tool_path: path of the folder containing the tool executable.\n"
		print "- parameters: a string specifying all parameters needed for tool execution.\n"
		print "All fields MUST be tab-separated.\nThe integration strategy line must look like this:\n"
		print "\tIntegrationStrategy	full_python_class_name	empty	parameters\n"
		print "- full_python_class_name: class name, complete with module name of the "\
					"Python class defining the desired integration strategy.\n"
		print "- empty: bookmark for empty field, used to keep the number of fields " \
					"constant in every line of the file.\n"
		print "- parameters: a string specifying all parameters needed for strategy execution.\n"
		print "All field MUST be tab-separated.\nThe results printer line(s) must look like this:\n"
		print "\tResultsPrinter	full_python_class_name	empty	parameters\n"
		print "- full_python_class_name: class name, complete with module name "\
					"of the Python class defining the desired results printer.\n"
		print "- empty: bookmark for empty field, used to keep the number of "\
					"fields constant in every line of the file.\n"
		print "- parameters: a string specifying all parameters needed for " \
					"printer execution.\n\nAll field MUST be tab-separated.\n"
		print "COMMENTS: comment lines can be added to the configuration file; "\
					"every line starting with # will be considered as a comment line by DynaMIT."

		print "\nOPTIONS -----------------------------------\n" \
					"\n\t-h \n\t   display the command line reference.\n" \
					"\n\t-o \n\t   specify the output directory (default=dynamit_current date and time)." \
					"\n\t-p \n\t   set the number of processor cores to use for the search (default=1)."

		print "\nQUESTIONS & BUGS -----------------------------------\n" \
					"\n\tShould you have any question or notice a bug in DynaMIT, " \
					"please report it to erik.dassi@unitn.it.\n" \
					"\n-----------------------------------"
		sys.exit()

	# get filenames containing configuration and sequences.
	configFilename = sys.argv[1]
	sequencesFilename = sys.argv[2]

	# instantiate the class responsible for running DynaMIT.
	myRunner = runner.Runner()

	# check for the presence and store the parameter for the results
	# output directory to be used
	outputDirectory = "dynamit_" + time.strftime("%d%m%y") + "_" + \
										time.strftime("%H%M%S")
	if "-o" in sys.argv:
		try:
			outputDirectory = sys.argv[sys.argv.index("-o") + 1]
			if outputDirectory == "":
				raise ValueError('')
		except (IndexError, RuntimeError, ValueError):
			print "[ERROR] Incorrect specification of the -o parameter. Aborting..."
			sys.exit(1)

	# check for the presence and store the parameter for the number of
	# processor cores to use
	nproc = 1
	if "-p" in sys.argv:
		try:
			nproc = int(sys.argv[sys.argv.index("-p") + 1])
			if nproc < 1:
				raise ValueError('')
		except (IndexError, RuntimeError, ValueError):
			print "[ERROR] Incorrect specification of the -p parameter. Aborting..."
			sys.exit(1)

	# load DynaMIT configuration, including motif searchers and integration
	# strategy along with their parameters
	if myRunner.loadConfiguration(configFilename) != 0:
		print "[ERROR] Error while loading configuration. Aborting..."
		sys.exit(1)

	# run DynaMIT with the configured motif searchers, integration strategy,
	# results printers, output directory and input sequences.
	if myRunner.run(outputDirectory, sequencesFilename, nproc) != 0:
		print "[ERROR] Error while executing DynaMIT with current " \
					"configuration. Aborting..."
		sys.exit(1)

	# everything went fine, so exit quietly from the software
	return 0


# this check launches the main procedure when the library is called directly;
# it also avoids main to be run again when launching a new Process
# through the multiprocessing module (which imports main by default): on
# windows there is no fork so this would result in main code being executed
# again for each proces producing an infinite loop.
if __name__ == '__main__':
	main()
