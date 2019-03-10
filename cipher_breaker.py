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