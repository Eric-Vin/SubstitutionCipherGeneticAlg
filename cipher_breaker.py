import math
import random
import copy
from spellchecker import SpellChecker
import time
import string
import re

__VERBOSE__ = True

"""
A class representing a training environment for a certain group of chromosomes.
"""
class Incubator:
	#Class variables:
	#	sample_block_table: A dictionary containing all blocks in sample_path and their frequency
	#	spellchecker: A pyspellchecker instance with all the words in words_path added
	#	population: Total population of the incubator, indicating how many chromosomes exist at one time
	#	elites: How many elites are carried over for each generation
	#	children: How many children are created for each generation
	#	randoms: How many random chromosomes are added each generation
	#	tournament_size: How many chromosomes are considered in a tournament
	#	cross_chance: Chance of crossing chromosomes when creating a child. cross_chance + mutation_chance should equal one
	#	mutation_chance: Change of mutating a chromosome when creating a child. cross_chance + mutation_chance should equal one
	#	shock_enabled: True if genetic shock enabled, false otherwise
	#	shock_threshold: Number of cycles of fitness stagnation before genetic shock is triggered.
	#	max_cycles: Cycle # at which the simulation terminates
	def __init__(self, sample_path, words_path, elites, children, randoms, tournament_size, cross_chance, mutation_chance, shock_value, max_cycles):
		#Parameters:
			#	sample_path: A path to a samples source file containing all training data to be fed to the incubator
			#	words_path: A path to all words which the cipher_breaker should consider valid in addition
			#		to those already in pyspellchecker.
			#	elites: How many elites are carried over for each generation
			#	children: How many children are created for each generation
			#	randoms: How many random chromosomes are added each generation
			#	tournament_size: How many chromosomes are considered in a tournament
			#	cross_chance: Chance of crossing chromosomes when creating a child. cross_chance + mutation_chance should equal one
			#	mutation_chance: Change of mutating a chromosome when creating a child. cross_chance + mutation_chance should equal one
			#	shock_value: 0 if genetic shock disabled. Otherwise shock is enabled and shock_threshold is set to shock_value
			#	max_cycles: Cycle # at which the simulation terminates

			#Initializes sample_block_tables
			self.sample_block_table = self.getSampleBlockTable(sample_path)

			#Initializes spellchecker
			self.spellchecker = SpellChecker()
			self.spellchecker.word_frequency.load_text_file((words_path))

			#Checks cross_chance and mutation_chance are valid
			assert (cross_chance + mutation_chance) == 1

			#Loads all incubator paramaters
			self.elites = elites
			self.children = children
			self.randoms = randoms
			self.population = self.elites + self.children + self.randoms

			self.tournament_size = tournament_size

			self.cross_chance = cross_chance
			self.mutation_chance = mutation_chance

			#Handles shock_value
			if shock_value <= 0:
				self.shock_enabled = False
				self.shock_threshold = 0
			else:
				self.shock_enabled = True
				self.shock_threshold = shock_value

			self.max_cycles = max_cycles

			#Prints incubator summary if verbose enables
			if __VERBOSE__:
				print("Incubator Summary:")
				print("sample_path: " + sample_path + "  words_path: " + words_path)
				print("Total population: " + str(self.population))
				print("Elites: " + str(self.elites) + "  Children: " + str(self.children) + "  Randoms: " + str(self.randoms))
				print("Tournament size: " + str(self.tournament_size) + "  Cross chance: " + str(self.cross_chance) + "  Mutation chance: " + str(self.mutation_chance))
				print("Shock enabled: " + str(self.shock_enabled) + "  Shock threshold: " + str(self.shock_threshold))
				print("Max cycles: " + str(self.max_cycles))
				print("\n")

	"""TRAINING FUNCTIONS"""
	#Takes ciphertext, returns a chromosome that should decrypt ciphertext
	def train(self, cipher_text):
		#Initializes cycle counter
		cycles = 0

		#Generates pool of chromosomes
		chromosomes = []

		for chromosome_iter in range(self.population):
			chromosomes.append(self.getRandomChromosome())

		#Genetic shock trigger variables. Triggers if fitness is stagnant for shock_threshold cycles
		best_fitness = 0
		shock_ticker = 0

		#Starts timer
		start_time = time.time()

		while True:
			#Increments cycle counter
			cycles += 1

			#Creates list of (chromosome, fitness) tuples in order of increasing fitness
			chromosome_fitness = []

			#Checks all chromosomes to see if the correct one has been found
			for chromosome in chromosomes:
				if len(self.spellchecker.unknown((chromosome.convertText(cipher_text)).split(" "))) == 0:
					if __VERBOSE__:
						print("Found key! " + str(chromosome))
						print("Decrypted text:  " + chromosome.convertText(cipher_text))
						print("")

						return (chromosome, cycles)

			#Gets fitness of each chromosome and sorts them according to fitness
			for chromosome in chromosomes:
				chromosome_fitness.append((chromosome, self.getFitness(chromosome, cipher_text)))

			chromosome_fitness.sort(key=lambda x: x[1])
			chromosome_fitness.reverse()

			#Checks if max_cycles exceeded. If so, returns the fittest chromosome
			if cycles >= self.max_cycles:
				print("Best Key: " + str(chromosome_fitness[0][0]))
				print("Decrypted text:  " + chromosome_fitness[0][0].convertText(cipher_text))
				print("")
				return (chromosome_fitness[0][0], cycles)

			#Checks if fitness is stagnant
			if chromosome_fitness[0][1] <= best_fitness:
				shock_ticker += 1
			else:
				best_fitness = max(chromosome_fitness[0][1], best_fitness)
				shock_ticker = 0

			#If __VERBOSE__, provide report on most fit chromosome
			if __VERBOSE__:
				converted_text = chromosome_fitness[0][0].convertText(cipher_text)
				print("Cycle# " + str(cycles))
				print("Best Chromosome: " + str(chromosome_fitness[0][0]))
				print("Fitness: " + str(chromosome_fitness[0][1]))
				print("Shock Ticker: " + str(shock_ticker))
				print("Cycle Time: " + str(time.time()-start_time))
				print("Attempted Decrypt: " + converted_text)
				print("Known words: " + str(self.spellchecker.known((chromosome_fitness[0][0].convertText(cipher_text).split(" ")))))
				print("Unknown words: " + str(self.spellchecker.unknown((chromosome_fitness[0][0].convertText(cipher_text).split(" ")))))
				print("")

			start_time = time.time()

			#Creates a new chromosomes list
			new_chromosomes = []

			#Copies over elite to new chromosomes
			for chromosome_iter in range(self.elites):
				new_chromosomes.append(chromosome_fitness[chromosome_iter][0].clone())

			#Creates children in new_chromsomes

			#Performs tournament process to select breeding candidates
			tournament_selections = []
			while len(tournament_selections) < (self.children):
				tournament_selections.append(self.tournament(chromosome_fitness))

			#Breeds selected candidates
			while len(tournament_selections)>0:
				chance = random.random()
				if chance < self.cross_chance and len(tournament_selections) > 1:
					chromosome_one = tournament_selections.pop()
					chromosome_two = tournament_selections.pop()

					crossed_chromosomes = self.crossChromosomes(chromosome_one, chromosome_two)

					new_chromosomes.append(crossed_chromosomes[0])
					new_chromosomes.append(crossed_chromosomes[1])
				elif chance < (self.mutation_chance + self.cross_chance):
					new_chromosomes.append(self.mutateChromosome(tournament_selections.pop()))
				else:
					new_chromosomes.append(self.getRandomChromosome())

			#Adds random chromosomes to new_chromosomes
			for random_iter in range(self.randoms):
				new_chromosomes.append(self.getRandomChromosome())

			#Checks if genetic shock should be triggered
			if shock_ticker >= self.shock_threshold and self.shock_enabled:
				if __VERBOSE__:
					print("Triggering genetic shock...\n")

				#Performs genetic shock, culling top 10% of population and mutation all others
				for chromosome_iter in range(len(new_chromosomes)):
					if self.getFitness(new_chromosomes[chromosome_iter], cipher_text) > .9 * best_fitness:
						new_chromosomes[chromosome_iter] = self.getRandomChromosome()
					else:
						new_chromosomes[chromosome_iter] = self.mutateChromosome(new_chromosomes[chromosome_iter])

				#Resets shock tickers and trackers
				shock_ticker = 0
				best_fitness = 0

			#Shifts new_chromosomes into gene pool
			chromosomes = new_chromosomes

	#Returns a mutated chromosome
	def mutateChromosome(self, chromosome):
		new_chromosome = chromosome.clone()

		#Chooses two mappings to swap
		mutation_one_index = random.randint(0,25)
		mutation_two_index = random.randint(0,25)

		while mutation_two_index == mutation_one_index:
			mutation_two_index = random.randint(0,25)

		mutation_one = new_chromosome.mappings[mutation_one_index]
		mutation_two = new_chromosome.mappings[mutation_two_index]

		new_chromosome.removeMapping(mutation_one)
		new_chromosome.removeMapping(mutation_two)

		mapping_one = (mutation_one[0], mutation_two[1])
		mapping_two = (mutation_two[0], mutation_one[1])

		new_chromosome.addMapping(mapping_one)
		new_chromosome.addMapping(mapping_two)

		return new_chromosome

	#Takes two chromosomes and returns two crosses of those chromosomes in the format (new_chromosome_one, new_chromosome_two)
	def crossChromosomes(self, chromosome_one, chromosome_two):
		new_chromosome_one = chromosome_one.clone()
		new_chromosome_two = chromosome_two.clone()

		for chromosome_iter in range(26):
			if(random.random() > .5):
				old_mapping_one = new_chromosome_one.mappings[chromosome_iter]
				old_mapping_two = new_chromosome_two.mappings[chromosome_iter]

				if old_mapping_one != old_mapping_two:
					complement_mapping_one = new_chromosome_one.getMappingTarget(old_mapping_two[1])
					complement_mapping_two = new_chromosome_two.getMappingTarget(old_mapping_one[1])

					old_origin_one = complement_mapping_one[0]
					old_origin_two = complement_mapping_two[0]

					new_chromosome_one.removeMapping(complement_mapping_one)
					new_chromosome_two.removeMapping(complement_mapping_two)

					new_chromosome_one.removeMapping(old_mapping_one)
					new_chromosome_two.removeMapping(old_mapping_two)

					complement_mapping_one = (old_origin_two, complement_mapping_one[1])
					complement_mapping_two = (old_origin_one, complement_mapping_two[1])

					new_chromosome_one.addMapping(old_mapping_two)
					new_chromosome_one.addMapping(complement_mapping_two)
					new_chromosome_two.addMapping(old_mapping_one)
					new_chromosome_two.addMapping(complement_mapping_one)

		return (new_chromosome_one, new_chromosome_two)

	#Returns a new random chromosome
	def getRandomChromosome(self):
		new_chromosome = Chromosome()

		origin = []
		destination = []

		for letterIter in range(26):
			origin.append(chr(letterIter+97))
			destination.append(chr(letterIter+97))

		random.shuffle(destination)

		for mappingIter in range(26):
			new_chromosome.addMapping((origin[mappingIter], destination[mappingIter]))

		return new_chromosome

	#Performs a tournament selection of chromosomes based on tournament_size
	def tournament(self, chromosome_fitness):
		tournament_pool = []

		for tournament_iter in range(self.tournament_size):
			tournament_pool.append(chromosome_fitness[random.randint(0, self.population-1)])

		return (max(tournament_pool, key=lambda x: x[1]))[0].clone()

	#Takes a chromosome and cipher_text and evaluates the chromosomes fitness
	def getFitness(self, chromosome, cipher_text):
		total_fitness = 0
		parsed_block_table = self.getBlockTable(chromosome.convertText(cipher_text))

		for block in parsed_block_table.keys():
			if block in self.sample_block_table.keys():
				total_fitness += math.log(self.sample_block_table[block],2)*(parsed_block_table[block])

		return total_fitness

	"""
	BLOCK FUNCTIONS
	"""
	#Returns the blocks located in the passed samples path.
	def getSampleBlockTable(self, sample_path):
		#Opens input file
		input_file = open(sample_path)
		block_table = {}

		for line in input_file:
			components = line.split(" ")

			components[1] = int(components[1][0:len(components[1])-1])

			block_table[components[0]] = components[1]

		input_file.close()

		return block_table

	#Takes a string and returns a hash table of blocks
	def getBlockTable(self, input_string):
		block_table = {}
		input_words = input_string.split(" ")

		#Hashes blocks in dictionary to count them
		for word in input_words:
			word_blocks = self.getBlocks(word)

			for block in word_blocks:
				if block in block_table:
					block_table[block] += 1
				else:
					block_table[block] = 1

		return block_table

	#Returns all substrings of a passed string
	def getBlocks(self, input_string):
		blocks = []

		for block_len in range(len(input_string)):
			start_point = 0
			end_point = block_len+1

			while end_point <= len(input_string):
				blocks.append(input_string[start_point:end_point])
				end_point+=1
				start_point+=1

		return blocks

"""
A class representing a complete group of mappings
"""
class Chromosome:
	#Class variables:
	#	mappings: A list of mappings that are applied by the converter. A mapping is a tuple of length 2 following the format (origin, destination)
	def __init__(self):
		self.mappings = []

	#Adds a mapping assuming both origin and destination aren't present in converter
	def addMapping(self, new_mapping):
		#Confirms both mapping.origin and mapping.destination are not already present as
		#an origin or destination of any mapping in the mappings array
		if self.getMappingOrigin(new_mapping[0]) == None and self.getMappingTarget(new_mapping[1]) == None:
			self.mappings.append(new_mapping)
			self.sortMappings()
		else:
			print("ERROR: Trying to insert duplicate mapping (" + new_mapping[0] + ", " + new_mapping[1] + ") " + str(self))

	#Removes a mapping equivalent to the passed mapping
	def removeMapping(self, remove_mapping):
		for mapping in self.mappings:
			if mapping[0] == remove_mapping[0] and mapping[1] == remove_mapping[1]:
				self.mappings.remove(mapping)

	#Returns the mapping that contains the passed origin as its origin
	def getMappingOrigin(self, target_origin):
		for mapping in self.mappings:
			if mapping[0] == target_origin:
				return mapping

		return None

	#Returns the mapping that contains the passed destination as its destination
	def getMappingTarget(self, target_destination):
		for mapping in self.mappings:
			if mapping[1] == target_destination:
				return mapping

		return None

	#Sorts the mappings by their origin, a-z
	def sortMappings(self):
		self.mappings.sort(key=lambda x: x[0])

	#Converts the passed text using contained mappings
	def convertText(self, raw_text):
		char_list = list(raw_text)

		for char_iter in range(len(char_list)):
			for mapping in self.mappings:
				if char_list[char_iter] == mapping[0]:
					char_list[char_iter] = mapping[1]
					break

		converted_text = "".join(char_list)

		return converted_text

	#Returns a deep copy of the chromosome
	def clone(self):
		clone_chromosome = Chromosome()

		for mapping in self.mappings:
			clone_chromosome.addMapping(mapping)

		return clone_chromosome

	def __str__(self):
		output = "["

		for mapping in self.mappings:
			output += str(mapping)

		output += "]"

		return output

if __name__ == '__main__':
	cipher_text_one = "lgdtmodtl o ytts miam o ligwsr stm bgw ass qfgc miam mitkt ol a dgflmtk cioei iortl ztiofr mit zsaeqzgakr of esall zwm mitf om sggql rtth ofmg db tbtl citf o eafm ktdtdztk ciam dami o ad lwhhgltr mg zt masqofu azgwm afr o qfgc miam o ad fgm alltkmoxt tfgwui mg mtss bgw aslg om cgwsr zt uggr mg mtss bgw miam ciost ct al a mtaeiofu lmayy eakt azgwm bgw gwk lmwrtfml a uktam rtas ct aslg hkogkomont gwk laytmb yaoksb iouisb lg oy miol dgflmtk txtk rgtl zktaq gwm ykgd ztiofr mit zsaeqzgakr o coss zt kwffofu al yalm al o eaf gwm gy mit rggk maqofu arxafmaut gy mit yaem miam om coss utm gft gy bgw afr mitf zt mgg zwlb mg eialt dt"

	incubator = Incubator("dataset/samples.txt", "dataset/words_source.txt", 150, 700, 150, 10, .65, .35, 4, 200)
	incubator.train(cipher_text_one)