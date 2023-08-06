"""Module for various DynaMIT utility functions."""

from Bio import SeqIO
from Bio.Alphabet import IUPAC
from numpy import array, log, sqrt, mean
from sklearn import metrics
import matplotlib.cm as cmx
import matplotlib.colors as colors


def getClassInstance(fullClassName):
	"""Returns an instance of the class object specified
	by the name string.

	Args:
		fullClassName: The full class name string.

	Returns:
		Returns a new instance of the specified class.

	Raises: ValueError if the full name of the class is
					not correctly specified.
	"""
	moduleName, _, className = fullClassName.rpartition('.')
	if not moduleName:
		raise ValueError('Invalid class specification: missing module or name part.')
	return getattr(__import__(moduleName, globals(), locals(),
														[className], -1), className)()

def getFullNames(classes):
	"""Return passed classes objects as a list of full class names.

	Args:
		classes: list of classes to get the names from.

	Returns:
		list of full class names of the passed classes.
	"""
	names = []
	for thisClass in classes:
		names.append(thisClass.__module__ + "." + thisClass.__name__)
	return names

def getSequencesRecords(sequencesFilename):
	"""Loads sequences from the specified FASTA file.

	Args:
		sequencesFilename: filename containing sequences to be loaded.

	Returns:
		a set of SeqRecord objects containing loaded sequences if
		everyhing went fine, returns 1 and prints an error message otherwise.
	"""
	try:
		# open the sequences file.
		with open(sequencesFilename) as seqHandle:
			sequences = []
			# load every sequence and adds it to the collection.
			for seqRecord in SeqIO.parse(seqHandle, "fasta",
																	 alphabet=IUPAC.unambiguous_dna):
				sequences.append(seqRecord)
			# return the sequences collection.
			return sequences
	except IOError:
		# describe the error that occurred.
		print "[ERROR] Unable to load sequences from the specified filename: <" + \
					sequencesFilename + "> ."
		return 1

def getFullSequenceID(sequences, partialSequenceID, minLength):
	"""Look for the full sequence ID to which the beginning
	of the passed partial ID corresponds: this to solve the
	issue of many search tools truncating the sequence ID
	after a certain length.

	Args:
		sequences: a dictionary of sequences in which the ID must be
							 looked for (id is key, sequence is value).
		partialSequenceID: the part of the ID that we know.
		minLength: minimum length the sequence must have to
							 be the correct one (helps in discriminating
							 between sequences with ID starting in the
							 same way.

	Returns:
		Returns the full sequence ID if found, -1 otherwise.
	"""
	# get all IDs matching which begining matches the partial one.
	fullSeqIDList = [seqID for seqID in sequences.keys() \
												 if seqID.startswith(partialSequenceID)]
	if len(fullSeqIDList) > 0:
		# if more than one sequence matched the ID beginning,
		# try to figure out the right one with the minLength.
		if len(fullSeqIDList) > 1:
			for i in range(0, len(fullSeqIDList)):
				if len(sequences[fullSeqIDList[i]]) >= minLength:
					return fullSeqIDList[i]
		else:
			# return the only matching ID.
			return fullSeqIDList[0]
	else:
		# no matching IDs were found, return an error indication.
		return -1


def makeSingleLineFASTA(sequencesFilename, outputFilename):
	"""Make sequences from the specified FASTA file into single line
	sequences for use by some tools (e.g. RNAfold)

	Args:
		sequencesFilename: filename containing sequences to be made single-line.
		outputFilename: filename for single-line sequences to be stored.

	Returns:
		Returns 0 if conversion went fine, returns 1 and
		prints an error message otherwise.
	"""
	try:
		# gets lines from the input FASTA file.
		with open(sequencesFilename) as f:
			fastaLines = f.readlines()

		outHandle = open(outputFilename, "wb")
		first = True

		for line in fastaLines:
			# this is the beginning of a sequence (its header line).
			if line.startswith(">"):
				if not first:
					outHandle.write("\n")
				else:
					first = False
				outHandle.write(line)
			else:
				# we are inside a sequences, so simply print this line
				# avoiding the '\n' - this basically concatenates all
				# sequence lines into a single one.
				outHandle.write(line.rstrip("\n"))

		# close the output file and report everything went fine.
		outHandle.close()
		return 0
	except (IOError, RuntimeError, ValueError) as e:
		print "[ERROR] Unexpected exception: %s" % str(e)
		return 1

def removeSequencesShorterThan(n, sequencesFilename, outputFilename):
	"""Remove sequences shorter than n nucleotides from the input
	filename, and save remaining sequences into the output filename.

	Args:
		n: minimal length in nucleotides for a sequence to be kept.
		sequencesFilename: filename containing sequences to be loaded.
		outputFilename: filename for filtered sequences to be stored.

	Returns:
		Returns 0 if the removal went fine, returns 1 and
		prints an error message otherwise.
	"""
	try:
		# open the input filename.
		with open(sequencesFilename) as seqHandle:
			# load every sequence, and adds it to the collection
			# only if it is equal or longer than n
			sequences = []
			for seqRecord in SeqIO.parse(seqHandle, "fasta"):
				if len(seqRecord) >= n:
					sequences.append(seqRecord)
			# write the filtered sequences to the output file.
			with open(outputFilename, "wb") as outputHandle:
				SeqIO.write(sequences, outputHandle, "fasta")
			return 0
	except IOError:
		# describe the error that occurred.
		print "[ERROR] Unable to load sequences from the specified filename: <" + \
					sequencesFilename + "> . or to write to the output filename: <" + \
					outputFilename + ">."
		return 1

def formatStringToLineLength(s, n):
	"""Format a string to have lines of at most n characters,
	respecting pre-existent line breaks in the passed string.

	Args:
		s: the string to be formatted.
		n: the desired line length.

	Returns:
		A string with \n inserted to respect the requested line length.
	"""
	# need to respect the pre-existent \n's so split by lines.
	if len(s) > n:
		lines = s.split('\n')
		splitLines = []
		for line in lines:
			# split the line to obtain lines of the requested length
			# and add to the list of split lines.
			splitLines.extend([line[i:i+n] for i in range(0, len(line) + 1, n)])
		# return the new lines as a single string.
		return  "\n".join(splitLines)
	else:
		# s is shorter than requested length, so return it unchanged.
		return s

def vectorsJaccard(vector1, vector2):
	"""Compute the Jaccard similarity of the two vectors.

	Args:
		vector 1: first vector for similarity computation.
		vector 2: second vector for similarity computation.

	Returns:
		A float value represing the Jaccard similarity of the two vectors.
	"""
	if len(vector1) == 0 or len(vector2) == 0:
		return 0
	return float(len(set(vector1) & set(vector2))) / \
				 float(len(set(vector1) | set(vector2)))

def binaryVectorsNormMI(vector1, vector2):
	"""Compute the normalized [0,1] mutual information
	(MI) of the two input vectors.

	Args:
		vector1: first vector to use for MI computation
		vector2: second vector to use for MI computation

	Returns:
		Returns the computed MI value.
	"""
	mutualInfo = 0

	#compute the probability of 0 and 1 in the two vectors.
	v1p1 = float(len([v1 for v1 in vector1 if v1 == 1])) / float(len(vector1))
	v2p1 = float(len([v2 for v2 in vector2 if v2 == 1])) / float(len(vector2))

	# compute the joint probabilities and the mutual information.
	p11 = float(len([v1 for v1, v2 in zip(vector1, vector2) \
									 if (v1 == v2) and (v1 == 1)])) / float(len(vector1))
	if p11 > 0:
		mutualInfo += p11 * log(p11 / (v1p1*v2p1))

	# compute the two MI normalization components.
	v1h = - ((v1p1 * log(v1p1)))
	v2h = - ((v2p1 * log(v2p1)))

	# normalize the computed MI to range in [0,1] and return it.
	return mutualInfo / sqrt(v1h*v2h)

def getMatplotlibColorMap(maxColorsNumber, colorAlpha):
	"""Returns a function that maps each index in 0, 1, ... maxColorsNumber-1
	to a distinct RGBA color.

	Args:
		maxColorsNUmber: maximum number of colors required for plotting.
		colorAlpha: desired alpha level for the colors (0.0-1.0).

	Returns:
		Returns a matplotlib color mapper function returning an RGBA color when
		called by passing an integer index number.
	"""
	# normalize the color scale to the number of colors we require.
	color_norm = colors.Normalize(vmin=0, vmax=maxColorsNumber-1)
	# produce a function to map our indexes to a matplotlib color.
	scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='Paired')
	def map_index_to_rgb_color(index):
		""" Provides a map from an integer index to an
		RGBA color from the matplotlib package.
		"""
		return scalar_map.to_rgba(index, alpha=colorAlpha)
	# return this function to be used for color picking.
	return map_index_to_rgb_color

def getMotifsFromSearchResults(motifsMatches):
	"""Extracts the list of motifs from the table containing all their matches.

	Args:
		motifsMatches: table containing matches for all motifs on all sequences.
									 This table is produced by DynaMIT motif search phase.

	Returns:
		A dictionary which keys are in the form motifSequence|searchTool,
		and values correspond to the motif sequence.
	"""
	# keys are in the form <motif|motifSearcherName>, while values
	# contain the actual motif (e.g. AGACC|Weeder: AGACC).
	return {match.split('\t')[0] + "|" + \
					match.split('\t')[2]: \
					match.split('\t')[0] for match in motifsMatches}


def getMotifsInstancesVectors(sequences, motifsMatches, binary=False):
	"""Produces a vector for each motif containing positions of the motif on
	analyzed sequences. To be easily comparable across motifs, positions are
	summed up so that the start of the nth sequence (its position 0) is the sum
	of lengths of sequences 1..n-1, and its end is shifted from this value by the
	length of sequence n itself. This virtually "concatenates" all sequences to
	obtain a single vector per motif describing all its matches on all sequences.

	Args:
		sequences: collection of sequences onto which the vectors must be computed.
		motifsMatches: table containing matches for all motifs on all sequences.
									 This table is produced by DynaMIT motif search phase.
		binary: boolean indicating wether the resulting vectors will be binary
						or composed by match positions only (see Returns for details).

	Returns:
		If the binary parameter is False, motif matches positions will range
		from 0 (beginning of sequence 1) to M (sum of lengths of all sequences).
		Only positions occupied by a motif will be indicated in the vector by their
		position, (e.g. if the motif matches position 2..6 on sequence 1, its vector
		will be [2,3,4,5,6,...]).
		If instead the binary parameter is True, motif matches will be indicated by
		a 1 in the corresponding positions of the vector, non-matched positions will
		instead be denoted by a 0. (e.g. if the motif matches position 2..6 on
		sequence n, positions sum(lengths(seq 1...n-1)) + 2..sum(lengths(seq 1...n-1))
		+ 6 will be 1 in the vector).
	"""

	vectors = {}
	motifs = list(set([match.split('\t')[0] + "|" + match.split('\t')[2] \
										 for match in motifsMatches]))
	startPosition = 0

	for seqRecord in sequences:
		# process each motif matches on this sequence
		for motif in motifs:
			if not vectors.has_key(motif):
				vectors[motif] = []
			currentMotifInfo = motif.split('|')
			# get all matches for this motif on this sequence
			currentMotifMatches = [match for match in motifsMatches \
														 if ((match.split('\t')[0] == currentMotifInfo[0]) and
														 (match.split('\t')[2] == currentMotifInfo[1]) and
														 (match.split('\t')[3] == seqRecord.description))]

			matchPositions = []
			for match in currentMotifMatches:
				# add start to end positions of this match to the list of
				# valid match positions.
				matchInfo = match.split('\t')
				matchPositions.extend(range(startPosition + int(matchInfo[4]) -1,
																		startPosition + int(matchInfo[5]) - 1))

			# report matching positions according to the binary parameter
			for pos in range(startPosition, startPosition + len(seqRecord.seq)):
				if binary:
					vectors[motif].append(1 if (pos in matchPositions) else 0)
				else:
					if pos in matchPositions:
						vectors[motif].append(pos)

		startPosition += len(seqRecord.seq)

	# returns the resulting vectors
	return vectors


def getBySequenceMotifsInstancesLists(sequences, motifsMatches):
	"""Produces a vector for each motif-sequence pair containing the list of
	motif matches on analyzed sequences in the form (matchStart, matchEnd).

	Args:
		sequences: collection of sequences onto which the vectors must be computed.
		motifsMatches: table containing matches for all motifs on all sequences.
									 This table is produced by DynaMIT motif search phase.

	Returns:
		A dictionary containing motifs as keys, each value is then a dictionary
		containing sequences as keys. Values of this last dictionary are then
		lists of tuples in the form (matchStartPosition, matchEndPosition),
		representing current motif matches on the current sequence.
	"""

	vectors = {}
	motifs = list(set([match.split('\t')[0] + "|" + match.split('\t')[2] \
										 for match in motifsMatches]))

	for seqRecord in sequences:
		# process each motif matches on this sequence
		for motif in motifs:

			if not vectors.has_key(motif):
				vectors[motif] = {}

			if not vectors[motif].has_key(seqRecord.description):
				vectors[motif][seqRecord.description] = []

			currentMotifInfo = motif.split('|')
			# get all matches for this motif on this sequence
			currentMotifMatches = [match for match in motifsMatches \
														 if ((match.split('\t')[0] == currentMotifInfo[0]) and
														 (match.split('\t')[2] == currentMotifInfo[1]) and
														 (match.split('\t')[3] == seqRecord.description))]

			for match in currentMotifMatches:
				matchInfo = match.split('\t')
				# add starting and ending positions of the match to this motif
				# matches on this sequence
				vectors[motif][seqRecord.description].append((int(matchInfo[4]) - 1,
																											 int(matchInfo[5]) - 1))

	return vectors


def getBySequenceMotifsInstancesVectors(sequences, motifsMatches, binary=False):
	"""Produces a vector for each motif-sequence pair containing positions of the
	motif on analyzed sequences.

	Args:
		sequences: collection of sequences onto which the vectors must be computed.
		motifsMatches: table containing matches for all motifs on all sequences.
									 This table is produced by DynaMIT motif search phase.
		binary: boolean indicating wether the resulting vectors will be binary
						or composed by match positions only (see Returns for details).

	Returns:
		If the binary parameter is true, motif matches will be indicated by a 1
		in the corresponding positions of the vector corresponding to that motif and
		that givens sequence, non-matched positions will instead be denoted by a 0.
		(e.g. if the motif matches position 2..6 on a sequence, positions 2..6 will
		be 1 in the vector, all the other positions will be 0).
		If instead the binary parameter is False, motif matches will be indicated
		by the corresponding positions of the vector corresponding to that motif and
		that givens sequence, non-matched positions will instead be omitted.
		(e.g. if the motif matches position 2..6 on a sequence, positions 2..6 will
		be in the vector, all the other positions will be not).
	"""

	vectors = {}
	motifs = list(set([match.split('\t')[0] + "|" + match.split('\t')[2] \
										 for match in motifsMatches]))

	for seqRecord in sequences:
		# process each motif matches on this sequence
		for motif in motifs:

			if not vectors.has_key(motif):
				vectors[motif] = {}

			if not vectors[motif].has_key(seqRecord.description):
				vectors[motif][seqRecord.description] = []

			currentMotifInfo = motif.split('|')
			# get all matches for this motif on this sequence
			currentMotifMatches = [match for match in motifsMatches \
														 if ((match.split('\t')[0] == currentMotifInfo[0]) and
														 (match.split('\t')[2] == currentMotifInfo[1]) and
														 (match.split('\t')[3] == seqRecord.description))]

			matchPositions = []
			for match in currentMotifMatches:
				matchInfo = match.split('\t')
				matchPositions.extend(range(int(matchInfo[4]) - 1, int(matchInfo[5]) - 1))

			# report matching positions according to the binary parameter
			for pos in range(0, len(seqRecord.seq)):
				if binary:
					vectors[motif][seqRecord.description].append(1 if \
								(pos in matchPositions) else 0)
				else:
					if pos in matchPositions:
						vectors[motif][seqRecord.description].append(pos)

	return vectors


def computeClustersSilhouette(affinities, clustering, precomputed=True):
	""" Computes by-cluster average silhouette
	score given a distance and a clustering.

	Args:
		affinities: square matrix reporting affinities
							 between samples.
		clustering: list of cluster labels, one per sample.
		precomputed: indicate whether affinities is already
								 an affinity matrix (True, default) or a
								 feature matrix(False).

	Returns:
		Returns the average per-cluster silhouette score.
	"""
	# compute distances as 1-affinities.
	if precomputed:
		# change affinities into distances.
		distances = array([[1.0-v for v in lst] for lst in affinities])
		# compute silhouette score for each sample (motif) with precomputed distances.
		sil = metrics.silhouette_samples(distances, clustering, metric='precomputed')
	else:
		# compute silhouette score for each sample (motif), computing distances.
		sil = metrics.silhouette_samples(affinities, clustering, metric='euclidean')

	# return the silhouette score average by motif cluster.
	return [mean(sils) for sils in \
				 [[sil[i] for i, curlab in enumerate(clustering) if curlab == label] \
					for label in set(clustering)]]
