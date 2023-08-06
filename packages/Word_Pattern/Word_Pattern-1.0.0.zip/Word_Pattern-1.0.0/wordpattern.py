def wordpattern(word):
	list_pattern = []
	dict_pattern = {}
	count = 0

	for letter in word:
		if letter not in dict_pattern:
			dict_pattern[letter] = str(count)
			count += 1

			list_pattern.append(dict_pattern[letter])
		else:
			list_pattern.append(dict_pattern[letter])

	return '.'.join(list_pattern)
		