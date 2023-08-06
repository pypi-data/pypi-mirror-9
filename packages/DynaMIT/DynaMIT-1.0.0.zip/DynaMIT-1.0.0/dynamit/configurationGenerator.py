"""Module containing the class for DynamitConfigurationGenerator
Tkinter GUI application."""

import pkg_resources

import Tkinter as tk
import ttk
import tkMessageBox
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
from tkFileDialog import askdirectory

from dynamit import *

class DynamitConfigurationGenerator(tk.Frame):
	"""This Tkinter application provides a simple tool to generate
	a configuration file for DynaMIT, allowing the users not to worry
	about tabs, parameters order, etc. Also provides full class names
	for pre-implemented MotifSearchers, IntegrationStrategies and ResultsPrinters,
	to allow a seamless selection and insertion of these n the configuration.
	Allows to load an exisiting configuration or to start from scratch, reorder
	and delete lines and eventually save the results to file.
	"""

	def __init__(self, master=None):
		"""Initialize the frame by setting its icon,
		its size at 805x600 and non-resizable.
		"""
		tk.Frame.__init__(self, master)

		# load the tool icon from package resources and use it as window icon
		img = tk.PhotoImage(file=pkg_resources.resource_filename("dynamit",
																						"graphics/logo_noname.gif"))
		self.master.call('wm', 'iconphoto', self.master._w, img)

		# set the frame size and non-resizeability
		self.master.geometry("805x600")
		self.master.resizable(width=False, height=False)

		# generate and adds all the frame content and displays it.
		self.grid()
		# generate the application menu
		self.__createMenu()
		# generate IntegrationStrategy lines widgets
		self.__createSearcherLineWidgets()
		# generate IntegrationStrategy lines widgets
		self.__createStrategyLineWidgets()
		# generate ResultsPrinter lines widgets
		self.__createPrinterLineWidgets()
		# generate comment lines widgets
		self.__createCommentLineWidgets()

		# generate configuration lines box and related buttons
		self.__createConfigurationBoxWidgets()

		# bottom frame and its content
		self.__createBottomFrameWidgets()

	def __createMenu(self):
		"""Creates the frame menu widgets.
		"""
		# frame menu bar
		self.menuBar = tk.Menu(self.master)
		self.master.config(menu=self.menuBar)
		# file submenu
		self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
		self.menuBar.add_cascade(label='File', menu=self.fileMenu)
		self.newMenu = tk.Menu(self.fileMenu, tearoff=0)
		self.fileMenu.add_cascade(label="New", menu=self.newMenu)
		self.newMenu.add_command(label="Empty", command=lambda: self.newConfig("empty"))
		self.newMenu.add_command(label="DNA", command=lambda: self.newConfig("DNA"))
		self.newMenu.add_command(label="RNA", command=lambda: self.newConfig("RNA"))
		self.newMenu.add_command(label="CLIP", command=lambda: self.newConfig("CLIP"))
		self.fileMenu.add_command(label="Open...", command=self.open)
		self.fileMenu.add_command(label="Save...", command=self.save)
		self.fileMenu.add_separator()
		self.fileMenu.add_command(label="Quit", command=self.quit)
		# about submenu
		self.aboutMenu = tk.Menu(self.menuBar, tearoff=0)
		self.menuBar.add_cascade(label='?', menu=self.aboutMenu)
		self.aboutMenu.add_command(label="About...", command=self.about)

	def __createSearcherLineWidgets(self):
		"""Creates the MotifSearcher line widgets.
		"""
		# MotifSearchers selection frame and related content
		self.searchersFrame = tk.Frame(self)
		self.searchersFrame.columnconfigure(1, minsize=40)
		self.searchersFrame.columnconfigure(2, minsize=100)
		self.searchersFrame.columnconfigure(3, minsize=40)
		self.searchersFrame.columnconfigure(4, minsize=100)
		self.searchersFrame.columnconfigure(5, minsize=40)
		self.searchersFrame.columnconfigure(6, minsize=100)
		self.searchersFrame.columnconfigure(7, minsize=40)
		self.searchersFrame.grid(row=1, column=1, sticky=tk.W)

		self.searchersLabel = tk.Label(self.searchersFrame, text="Motif searchers:")
		self.searchersLabel.grid(column=1, row=1, columnspan=2, sticky=tk.W,
														 ipadx=5, ipady=5)

		self.searchersNameLabel = tk.Label(self.searchersFrame, text="Name:")
		self.searchersNameLabel.grid(column=1, row=2, sticky=tk.W, ipadx=15)
		self.searchersNameBox = ttk.Combobox(self.searchersFrame,
			values=utils.getFullNames(motifSearcher.MotifSearcher.__subclasses__()))
		self.searchersNameBox.grid(column=2, row=2, sticky=tk.W, ipadx=10)

		self.searchersPathLabel = tk.Label(self.searchersFrame, text="Path:")
		self.searchersPathLabel.grid(column=3, row=2, sticky=tk.W, ipadx=15)
		self.sptFrame = tk.Frame(self.searchersFrame)
		self.searchersPathText = tk.Text(self.sptFrame, height=1, width=15)
		self.searchersPathText.grid(column=1, row=1, sticky=tk.W, ipadx=10)
		self.searchersPathButton = tk.Button(self.sptFrame, text="Select",
																				 command=self.selectSearcherDirectory,
																				 )
		self.searchersPathButton.grid(column=2, row=1, padx=4)
		self.sptFrame.grid(column=4, row=2, sticky=tk.W, ipadx=0)

		self.searchersParamsLabel = tk.Label(self.searchersFrame, text="Parameters:")
		self.searchersParamsLabel.grid(column=5, row=2, sticky=tk.W, ipadx=15)
		self.searchersParamsText = tk.Text(self.searchersFrame, height=1, width=15)
		self.searchersParamsText.grid(column=6, row=2, sticky=tk.W, ipadx=10)

		self.searchersAddButton = tk.Button(self.searchersFrame, text="Add",
																				width=5, command=self.addMotifSearcher)
		self.searchersAddButton.grid(column=7, row=2, sticky=tk.N, padx=15)

	def __createStrategyLineWidgets(self):
		"""Creates the IntegrationStrategy line widgets.
		"""
		# IntegrationStrategy selection frame and related content
		self.integrationFrame = tk.Frame(self)
		self.integrationFrame.columnconfigure(1, minsize=40)
		self.integrationFrame.columnconfigure(2, minsize=100)
		self.integrationFrame.columnconfigure(3, minsize=40)
		self.integrationFrame.columnconfigure(4, minsize=100)
		self.integrationFrame.columnconfigure(5, minsize=40)
		self.integrationFrame.columnconfigure(6, minsize=100)
		self.integrationFrame.columnconfigure(7, minsize=40)
		self.integrationFrame.grid(row=2, column=1, sticky=tk.W, pady=15)

		self.integrationLabel = tk.Label(self.integrationFrame,
																		 text="Integration strategy:")
		self.integrationLabel.grid(column=1, row=1, columnspan=2, sticky=tk.W,
															 ipadx=5, ipady=5)

		self.integrationNameLabel = tk.Label(self.integrationFrame, text="Name:")
		self.integrationNameLabel.grid(column=1, row=2, sticky=tk.W, ipadx=15)
		self.integrationNameBox = ttk.Combobox(self.integrationFrame,
			values=utils.getFullNames(integrationStrategy.IntegrationStrategy.__subclasses__()))
		self.integrationNameBox.grid(column=2, row=2, sticky=tk.W, ipadx=10)

		self.integrationPathLabel = tk.Label(self.integrationFrame, text="Path:")
		self.integrationPathLabel.grid(column=3, row=2, sticky=tk.W, ipadx=15)

		self.iptFrame = tk.Frame(self.integrationFrame)
		self.integrationPathText = tk.Text(self.iptFrame, height=1, width=15)
		self.integrationPathText.grid(column=1, row=1, sticky=tk.W, ipadx=10)
		self.integrationPathButton = tk.Button(self.iptFrame, text="Select",
																				 command=self.selectIntegrDirectory)
		self.integrationPathButton.grid(column=2, row=1, padx=4)
		self.iptFrame.grid(column=4, row=2, sticky=tk.W, ipadx=0)

		self.integrationParamsLabel = tk.Label(self.integrationFrame,
																					 text="Parameters:")
		self.integrationParamsLabel.grid(column=5, row=2, sticky=tk.W, ipadx=15)
		self.integrationParamsText = tk.Text(self.integrationFrame,
																				 height=1, width=15)
		self.integrationParamsText.grid(column=6, row=2, sticky=tk.W, ipadx=10)

		self.integrationAddButton = tk.Button(self.integrationFrame,
																					text="Add", width=5,
																					command=self.addIntegrationStrategy)
		self.integrationAddButton.grid(column=7, row=2, sticky=tk.N, padx=15)

	def __createPrinterLineWidgets(self):
		"""Creates the ResultsPrinter line widgets.
		"""
		# ResultsPrinters selection frame and related content
		self.printersFrame = tk.Frame(self)
		self.printersFrame.columnconfigure(1, minsize=40)
		self.printersFrame.columnconfigure(2, minsize=100)
		self.printersFrame.columnconfigure(3, minsize=40)
		self.printersFrame.columnconfigure(4, minsize=100)
		self.printersFrame.columnconfigure(5, minsize=40)
		self.printersFrame.columnconfigure(6, minsize=100)
		self.printersFrame.columnconfigure(7, minsize=40)
		self.printersFrame.grid(row=3, column=1, sticky=tk.W, pady=15)

		self.printersLabel = tk.Label(self.printersFrame, text="Results printers:")
		self.printersLabel.grid(column=1, row=1, columnspan=2, sticky=tk.W,
														ipadx=5, ipady=5)

		self.printersNameLabel = tk.Label(self.printersFrame, text="Name:")
		self.printersNameLabel.grid(column=1, row=2, sticky=tk.W, ipadx=15)
		self.printersNameBox = ttk.Combobox(self.printersFrame,
			values=utils.getFullNames(resultsPrinter.ResultsPrinter.__subclasses__()))
		self.printersNameBox.grid(column=2, row=2, sticky=tk.W, ipadx=10)

		self.printersPathLabel = tk.Label(self.printersFrame, text="Path:")
		self.printersPathLabel.grid(column=3, row=2, sticky=tk.W, ipadx=15)

		self.pptFrame = tk.Frame(self.printersFrame)
		self.printersPathText = tk.Text(self.pptFrame, height=1, width=15)
		self.printersPathText.grid(column=1, row=1, sticky=tk.W, ipadx=10)
		self.printersPathButton = tk.Button(self.pptFrame, text="Select",
																				 command=self.selectPrinterDirectory)
		self.printersPathButton.grid(column=2, row=1, padx=4)
		self.pptFrame.grid(column=4, row=2, sticky=tk.W, ipadx=0)

		self.printersParamsLabel = tk.Label(self.printersFrame, text="Parameters:")
		self.printersParamsLabel.grid(column=5, row=2, sticky=tk.W, ipadx=15)
		self.printersParamsText = tk.Text(self.printersFrame, height=1, width=15)
		self.printersParamsText.grid(column=6, row=2, sticky=tk.W, ipadx=10)

		self.printersAddButton = tk.Button(self.printersFrame, text="Add",
																			 width=5, command=self.addResultsPrinter)
		self.printersAddButton.grid(column=7, row=2, sticky=tk.N, padx=15)


	def __createCommentLineWidgets(self):
		"""Creates the comment line widgets.
		"""
		# Comment line frame and related content
		self.commentFrame = tk.Frame(self)
		self.commentFrame.columnconfigure(1, minsize=40)
		self.commentFrame.columnconfigure(2, minsize=100)
		self.commentFrame.columnconfigure(3, minsize=40)
		self.commentFrame.columnconfigure(4, minsize=100)
		self.commentFrame.columnconfigure(5, minsize=40)
		self.commentFrame.columnconfigure(6, minsize=100)
		self.commentFrame.columnconfigure(7, minsize=40)
		self.commentFrame.grid(row=4, column=1, sticky=tk.W)

		self.commentLabel = tk.Label(self.commentFrame, text="Comment line:")
		self.commentLabel.grid(column=1, row=1, columnspan=2, sticky=tk.W,
													 ipadx=5, ipady=5)

		self.commentLineLabel = tk.Label(self.commentFrame, text="Comment text:")
		self.commentLineLabel.grid(column=1, row=2, sticky=tk.W, ipadx=15)
		self.commentLineText = tk.Text(self.commentFrame, height=1, width=68)
		self.commentLineText.grid(column=2, row=2, columnspan=5, sticky=tk.W, ipadx=5)

		self.commentAddButton = tk.Button(self.commentFrame, text="Add", width=5,
																			command=self.addCommentLine)
		self.commentAddButton.grid(column=7, row=2, sticky=tk.N+tk.E, padx=27)

	def __createConfigurationBoxWidgets(self):
		"""Creates the configuration box and buttons widgets.
		"""
		# generated configuration lines frame and its content
		self.generatedConfigFrame = tk.Frame(self)
		self.generatedConfigFrame.columnconfigure(1, minsize=40)
		self.generatedConfigFrame.columnconfigure(2, minsize=100)
		self.generatedConfigFrame.columnconfigure(3, minsize=40)
		self.generatedConfigFrame.columnconfigure(4, minsize=100)
		self.generatedConfigFrame.columnconfigure(5, minsize=40)
		self.generatedConfigFrame.columnconfigure(6, minsize=100)
		self.generatedConfigFrame.grid(row=5, column=1, pady=15)

		self.generatedConfigLabel = tk.Label(self.generatedConfigFrame,
																				 text="Generated configuration lines:")
		self.generatedConfigLabel.grid(column=1, row=1, columnspan=2, sticky=tk.W,
																	 ipadx=5, ipady=5)

		self.generatedConfigScrollbar = tk.Scrollbar(self.generatedConfigFrame,
																									orient=tk.HORIZONTAL)
		self.generatedConfigListBox = tk.Listbox(self.generatedConfigFrame,
																						 height=10, width=65,
																						 selectmode=tk.SINGLE,
																						 activestyle='none',
													xscrollcommand=self.generatedConfigScrollbar.set)
		self.generatedConfigListBox.grid(column=2, row=2)
		self.generatedConfigScrollbar.grid(column=2, row=3, sticky=tk.W + tk.E)
		self.generatedConfigScrollbar.config(command=self.generatedConfigListBox.\
																									xview)

		# buttons for moving and deleting configuration lines
		self.configButtonsFrame = tk.Frame(self.generatedConfigFrame)
		self.configButtonsFrame.grid(column=3, row=2, padx=15, sticky=tk.N)
		self.removeSelectedLineButton = tk.Button(self.configButtonsFrame,
																							text="Remove selected line",
																							width=16,
																							command=self.removeSelectedLine)
		self.removeSelectedLineButton.grid(column=1, row=1, sticky=tk.W)
		self.lineUpButton = tk.Button(self.configButtonsFrame,
																	text="Move line up", width=16,
																	command=self.moveLineUp)
		self.lineUpButton.grid(column=1, row=2, sticky=tk.W, pady=10)
		self.lineDownButton = tk.Button(self.configButtonsFrame,
																		text="Move line down", width=16,
																		command=self.moveLineDown)
		self.lineDownButton.grid(column=1, row=3, sticky=tk.W)

	def __createBottomFrameWidgets(self):
		"""Creates the bottom frame widgets.
		"""
		# bottom frame and its content
		self.bottomFrame = tk.Frame(self)
		self.bottomFrame.columnconfigure(1, minsize=400)
		self.bottomFrame.columnconfigure(2, minsize=400)
		self.bottomFrame.grid(row=6, column=1, columnspan=7,
													pady=10, sticky=tk.W)

		self.saveButton = tk.Button(self.bottomFrame, text='Save configuration',
																command=self.save)
		self.saveButton.grid(column=1, row=1, padx=10, sticky=tk.E)
		self.resetButton = tk.Button(self.bottomFrame, text='Reset configuration',
																 command=self.resetConfig)
		self.resetButton.grid(column=2, row=1, padx=10, sticky=tk.W)

	def newConfig(self, configType):
		"""Creates a new configuration with type specified by the user.

			Args:
				configType: type of the configuration to create. Can be one of
										"empty", "DNA", "RNA" or "CLIP".
		"""
		if configType == "empty":
			self.resetConfig()
			self.resetTextBoxes()
		elif configType == "DNA":
			self.resetConfig()
			self.resetTextBoxes()

			# add MEME and Weeder Searchers.
			searcherLine = "MotifSearcher    dynamit.weederSearcher.WeederSearcher    " + \
									 "/home/dynamit/software/Weeder1.4.2    HS large"
			self.generatedConfigListBox.insert(tk.END, searcherLine)
			searcherLine = "MotifSearcher    dynamit.memeSearcher.MEMESearcher    " + \
									 "/home/dynamit/software/meme_4.10.0    "
			self.generatedConfigListBox.insert(tk.END, searcherLine)

			# add a Mutual Information integration Strategy.
			strategyLine = "IntegrationStrategy    dynamit.miStrategy.MIStrategy" + \
									 "        "
			self.generatedConfigListBox.insert(tk.END, strategyLine)

			# add a Table, a SeqView and a PositionalDensity printer.
			printerLine = "ResultsPrinter    dynamit.tablePrinter.TablePrinter" + \
										"        "
			self.generatedConfigListBox.insert(tk.END, printerLine)
			printerLine = "ResultsPrinter    dynamit.sequenceViewPrinter." \
										"SequenceViewPrinter        "
			self.generatedConfigListBox.insert(tk.END, printerLine)
			printerLine = "ResultsPrinter    dynamit.positionalDensityPrinter." \
										"PositionalDensityPrinter        "
			self.generatedConfigListBox.insert(tk.END, printerLine)
		elif configType == "RNA":
			self.resetConfig()
			self.resetTextBoxes()

			# add MEMERIS and CMfinder Searchers.
			searcherLine = "MotifSearcher    dynamit.memerisSearcher.MEMERISSearcher    " + \
									 "/home/dynamit/software/memeris_1.0    -dna -w 6 -nmotifs 10"
			self.generatedConfigListBox.insert(tk.END, searcherLine)
			searcherLine = "MotifSearcher    dynamit.cmfinderSearcher.CMfinderSearcher" + \
									 "    /home/dynamit/software/CMfinder_0.2/bin    "
			self.generatedConfigListBox.insert(tk.END, searcherLine)

			# add a Mutual Information integration Strategy.
			strategyLine = "IntegrationStrategy    dynamit.miStrategy.MIStrategy" + \
									 "        "
			self.generatedConfigListBox.insert(tk.END, strategyLine)

			# add a Table, a SeqView and a PositionalDensity printer.
			printerLine = "ResultsPrinter    dynamit.tablePrinter.TablePrinter" + \
										"        "
			self.generatedConfigListBox.insert(tk.END, printerLine)
			printerLine = "ResultsPrinter    dynamit.sequenceViewPrinter." \
										"SequenceViewPrinter        "
			self.generatedConfigListBox.insert(tk.END, printerLine)
			printerLine = "ResultsPrinter    dynamit.positionalDensityPrinter." \
										"PositionalDensityPrinter        "
			self.generatedConfigListBox.insert(tk.END, printerLine)
		elif configType == "CLIP":
			self.resetConfig()
			self.resetTextBoxes()

			# add a GraphProt and CMfinder Searchers.
			searcherLine = "MotifSearcher    dynamit.graphProtSearcher.GraphProtSearcher    " + \
									"/home/dynamit/software/GraphProt-1.1.1    negatives.fasta,-percentile 95"
			self.generatedConfigListBox.insert(tk.END, searcherLine)
			searcherLine = "MotifSearcher    dynamit.cmfinderSearcher.CMfinderSearcher" + \
									 "    /home/dynamit/software/CMfinder_0.2/bin    "
			self.generatedConfigListBox.insert(tk.END, searcherLine)

			# add an alignment integration Strategy.
			strategyLine = "IntegrationStrategy    dynamit.alignmentStrategy." \
										 "AlignmentStrategy        0.1"
			self.generatedConfigListBox.insert(tk.END, strategyLine)

			# add a Table, a SeqView and a WebLogo printer.
			printerLine = "ResultsPrinter    dynamit.tablePrinter.TablePrinter" + \
										"        "
			self.generatedConfigListBox.insert(tk.END, printerLine)
			printerLine = "ResultsPrinter    dynamit.sequenceViewPrinter." \
										"SequenceViewPrinter        "
			self.generatedConfigListBox.insert(tk.END, printerLine)
			printerLine = "ResultsPrinter    dynamit.webLogoPrinter." \
										"WebLogoPrinter        "
			self.generatedConfigListBox.insert(tk.END, printerLine)

		return 0

	def open(self):
		"""Load configuration lines from the user-specified filename.
		"""
		# ask the user for a filename to open
		inputFilename = askopenfilename()
		# and load the lines it contains
		inputHandle = open(inputFilename)
		newConfigLines = inputHandle.readlines()
		inputHandle.close()

		# if there are any generated config lines,
		# ask whether to reset them and restart from scratch
		if self.generatedConfigListBox.size() > 0:
			answer = tkMessageBox.askyesno("DynaMIT",
																		 "Reset the existing configuration lines and load the specified file ?")
			if answer == True:
				# clear existing configuration lines
				self.generatedConfigListBox.delete(0, tk.END)
			else:
				# the answer was negative, so stop here
				return 1

		# load all lines obtained from the user-specified file
		for i in range(0, len(newConfigLines)):
			self.generatedConfigListBox.insert(i,
								newConfigLines[i].replace("\t", "    ").rstrip("\n"))

		return 0

	def save(self):
		"""Save current configuration lines to the user-specified filename.
		"""
		# ask the user for a filename where to save the configuration
		outputFilename = asksaveasfilename()

		# compose the file content by merging individual config lines
		configString = ""
		for line in self.generatedConfigListBox.get(0, tk.END):
			configString += line.replace("    ", "\t") + "\n"

		# write down the obtained configuration to file
		outputHandle = open(outputFilename, "wb")
		outputHandle.write(configString[:-1])
		outputHandle.close()

		return 0

	def addMotifSearcher(self):
		"""Add the input motif searcher line to the generated
		configuration lines listbox.
		"""
		searcherLine = "MotifSearcher    " + self.searchersNameBox.get() + "    " + \
									 self.searchersPathText.get("1.0", "end-1c") + "    " + \
									 self.searchersParamsText.get("1.0", "end-1c")
		self.generatedConfigListBox.insert(tk.END, searcherLine)
		return 0

	def addIntegrationStrategy(self):
		"""Add the input integration strategy line to the generated
		configuration lines listbox.
		"""
		strategyLine = "IntegrationStrategy    " + self.integrationNameBox.get() + \
									 "    " + self.integrationPathText.get("1.0", "end-1c") + \
									 "    " + self.integrationParamsText.get("1.0", "end-1c")
		self.generatedConfigListBox.insert(tk.END, strategyLine)
		return 0

	def addResultsPrinter(self):
		"""Add the input results printer line to the generated
		configuration lines listbox.
		"""
		printerLine = "ResultsPrinter    " + self.printersNameBox.get() + "    " + \
									self.printersPathText.get("1.0", "end-1c") + "    " + \
									self.printersParamsText.get("1.0", "end-1c")
		self.generatedConfigListBox.insert(tk.END, printerLine)
		return 0

	def addCommentLine(self):
		"""Add the input comment line to the generated
		configuration lines listbox.
		"""
		commentLine = "#" + self.commentLineText.get("1.0", "end-1c")
		self.generatedConfigListBox.insert(tk.END, commentLine)
		return 0

	def removeSelectedLine(self):
		"""Removes the selected lines from the generated
		configuration lines listbox.
		"""
		self.generatedConfigListBox.delete(tk.ACTIVE)
		return 0

	def moveLineUp(self):
		"""Move currently selected lines (if any) up by one position in the
		configuration lines list box.
		"""
		selIndex = self.generatedConfigListBox.curselection()
		if selIndex and (int(selIndex[0]) > 0):
			selIndex = int(selIndex[0])
			line = self.generatedConfigListBox.get(selIndex)
			self.generatedConfigListBox.delete(selIndex)
			self.generatedConfigListBox.insert(selIndex - 1, line)
			self.generatedConfigListBox.selection_set(selIndex - 1)
			return 0
		return 0

	def moveLineDown(self):
		"""Move currently selected lines (if any) down by one position in the
		configuration lines list box.
		"""
		selIndex = self.generatedConfigListBox.curselection()
		if (selIndex and
			 (int(selIndex[0]) < (self.generatedConfigListBox.size() - 1))):
			selIndex = int(selIndex[0])
			line = self.generatedConfigListBox.get(selIndex)
			self.generatedConfigListBox.delete(selIndex)
			self.generatedConfigListBox.insert(selIndex + 1, line)
			self.generatedConfigListBox.selection_set(selIndex + 1)
			return 0
		return 0

	def resetConfig(self):
		"""Removes all lines from the generated configuration lines listbox.
		"""
		self.generatedConfigListBox.delete(0, tk.END)
		return 0

	def resetTextBoxes(self):
		"""Removes all text from all text and combo boxes.
		"""
		self.searchersNameBox.set("")
		self.searchersPathText.delete("1.0", tk.END)
		self.searchersParamsText.delete("1.0", tk.END)
		self.integrationNameBox.set("")
		self.integrationPathText.delete("1.0", tk.END)
		self.integrationParamsText.delete("1.0", tk.END)
		self.printersNameBox.set("")
		self.printersPathText.delete("1.0", tk.END)
		self.printersParamsText.delete("1.0", tk.END)

		return 0

	def selectSearcherDirectory(self):
		"""Display the directory selection dialog and set the searcher path
		textbox with the selected directory as value."""
		selectedDir = askdirectory()
		if selectedDir:
			self.searchersPathText.delete("1.0", tk.END)
			self.searchersPathText.insert(tk.INSERT, selectedDir)

	def selectIntegrDirectory(self):
		"""Display the directory selection dialog and set the integration path
		textbox with the selected directory as value."""
		selectedDir = askdirectory()
		if selectedDir:
			self.integrationPathText.delete("1.0", tk.END)
			self.integrationPathText.insert(tk.INSERT, selectedDir)

	def selectPrinterDirectory(self):
		"""Display the directory selection dialog and set the printer path
		textbox with the selected directory as value."""
		selectedDir = askdirectory()
		if selectedDir:
			self.printersPathText.delete("1.0", tk.END)
			self.printersPathText.insert(tk.INSERT, selectedDir)

	def about(self):
		"""Displays a message box with informations about this application.
		"""
		tkMessageBox.showinfo(self.master.title(),
			"DynaMIT\nConfiguration File Generator v 1.0\nhttp://bitbucket.org/erikdassi/dynamit")


# start the application and show its main window
app = DynamitConfigurationGenerator()
# load the tool icon from package resources and use it as window icon
app.master.title('DynaMIT Configuration Generator')
app.mainloop()
