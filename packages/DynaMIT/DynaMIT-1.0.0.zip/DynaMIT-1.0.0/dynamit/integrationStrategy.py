""" Module for the base abstract class of DynaMIT
IntegrationStrategy component.
"""

from abc import ABCMeta, abstractmethod

class IntegrationStrategy:
	"""Class representing an IntegrationStrategy component,
	providing a logic to integrate a set of motifs and related
	instances, obtained through DynaMIT phase 1, i.e. motif search.
	"""
	__metaclass__ = ABCMeta

	def __init__(self):
		"""Initialize all class attributes with their default values.
		"""
		self.integrationStrategyName = ""
		self.integrationResults = None

	@abstractmethod
	def setConfiguration(self, configString):
		"""Loads the strategy parameters specified in the configuration file.

		Args:
			configString: the configuration string derived from the run configuration
										filename (provided by the Runner component).

		Returns:
			Returns 0 if everything went fine, 1 and an error message otherwise.
		"""
		return 1

	@abstractmethod
	def doIntegration(self, sequences, searchResults):
		"""Performs the motifs integration.

		Args:
			sequences: collection of input sequences for this run.
			searchResults: table containing matches for all motifs on all sequences.
										This table is produced by DynaMIT motif search phase.

		Returns:
			Returns 0 if everything went fine (details on results filenames, etc.,
			are printed to the console); returns 1 and an error message otherwise.
		"""
		return 1

	def getResults(self):
		"""Returns the integration results dictionary
		produced by a call to doIntegration().
		"""
		return self.integrationResults
