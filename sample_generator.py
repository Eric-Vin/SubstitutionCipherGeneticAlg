__VERBOSE__ = True
__INPUTPATH__ = "dataset/combined_source.txt"
__OUTPUTPATH__ = "dataset/samples.txt"

#A tool to generate samples for cipher_breaker.py
def sample_generator(input_path, output_path):
	if __VERBOSE__:
		print("Loading input file: " + input_path)

	#Opens input file
	input_file = open(input_path)

	#Adds every word in the sample to a list
	input_words = []
	current_word = []

	if __VERBOSE__:
		print("File loaded.\n")
		print("Parsing file into words.")

	for line in input_file:
		for char in line:
			#If character is a letter, add it to current word.
			#Otherwise, word is done
			if char.isalpha():
				current_word.append(char.lower())
			else:
				#If current word is not empty, add it to the list and reset current word
				if current_word != []:
					input_words.append("".join(current_word))
				
				current_word = []
	else:
		if current_word != []:
			input_words.append("".join(current_word))
				
		current_word = []

	input_file.close()

	if __VERBOSE__:
		print("File parsed.\n")
		print("Splitting words into blocks.")
	
	block_table = {}

	#Hashes blocks in dictionary to count them
	for word in input_words:
		word_blocks = getBlocks(word)

		for block in word_blocks:
			if block in block_table:
				block_table[block] += 1
			else:
				block_table[block] = 1

	if __VERBOSE__:
		print("Blocks hashed.\n")
		print("Converting dictionary to list and sorting.")

	#Converts hash table to a list
	block_list = []

	for key in block_table.keys():
		block_list.append((key, block_table[key]))

	#Sorts list with respect to keys in alphabetic order
	block_list.sort(key=lambda x: x[0])

	if __VERBOSE__:
		print("Saving to : " + output_path)

	#Stores block data in output path
	output_file = open(output_path, "w")

	for block in block_list:
		output_file.write(block[0] + " " + str(block[1]) + "\n")

	output_file.close()

#Returns all substrings of a passed string
def getBlocks(input_string):
	blocks = []

	for block_len in range(len(input_string)):
		start_point = 0
		end_point = block_len+1

		while end_point <= len(input_string):
			blocks.append(input_string[start_point:end_point])
			end_point+=1
			start_point+=1

	return blocks

if __name__ == '__main__':
	sample_generator(__INPUTPATH__, __OUTPUTPATH__)