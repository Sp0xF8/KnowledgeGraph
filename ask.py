
import requests
import datetime
import string

class QUESTION:

	def __conditins_meet_expectations(self, condition_answers: list):
		"""
		Validates that each condition-answer pair in the provided list meets the expected format.

		Each element in `condition_answers` should be a list or tuple of length 2:
			- The first element must be a tuple representing the condition, and its length must match `self.number_of_conditions`.
			- The second element is expected to be a function to call when the condition is true.

		Raises:
			ValueError: If any condition-answer pair does not have exactly two elements.
			ValueError: If the first element of a pair is not a tuple.
			ValueError: If the length of the condition tuple does not match `self.number_of_conditions`.

		Args:
			condition_answers (list[tuple[tuple, callable]]): A list of condition-answer pairs to validate.
		"""
		for condition_answer in condition_answers:
			if len(condition_answer) != 2:
				raise ValueError(f'Each condition must be accompanied by a function to call when the condition is true. Got: {condition_answer}')
			if not isinstance(condition_answer[0], tuple):
				raise ValueError(f'Condition must be a tuple. Got: {condition_answer[0]}')
			if len(condition_answer[0]) != self.number_of_conditions:
				raise ValueError(f'Number of conditions in {condition_answer[0]} does not match the number of * in the question. Expected {self.number_of_conditions}, got {len(condition_answer[0])}')
		

	def __init__(self, question_with_mask: str, condition_answers: list):
		"""
		Initializes an instance with a masked question and corresponding condition answers.
		Args:
			question_with_mask (str): The question template containing mask(s) represented by '*', e.g., 'how * *'.
			condition_answers (list[tuple[tuple, callable]]): A list of condition-answer pairs, where each condition is associated with a function or value.
		Raises:
			ValueError: If the provided condition_answers do not meet the expected format or count based on the question_with_mask.
		Attributes:
			question_with_mask (str): The original question template with masks.
			mask_parts (list): The split parts of the question template, separating static text and masks.
			number_of_conditions (int): The number of mask placeholders in the question template.
			conditions (list): The validated list of condition-answer pairs.
			injected_parts (list): The result of injecting condition parts into the question template.
		"""
		self.question_with_mask = question_with_mask ## e.g. 'how * *', 'what * *'
		self.mask_parts = self.__split_mask()  ## e.g. ['how ', '*', ' ', '*'] for 'how * *'
		self.number_of_conditions = len(question_with_mask.split('*')) - 1

		try:
			self.__conditins_meet_expectations(condition_answers)
		except ValueError as e:
			print(f'Error in conditions: {e}')
			raise ValueError(f'Error in conditions: {e}')

		self.conditions = condition_answers ## e.g. [(('old is', '*'), function_on_true), (('is the population of', '*'), function_on_true)]
		self.injected_parts = self.__inject_condition_parts()


	def add_condition(self, condition: tuple, function_on_true):
		"""
		Adds a new condition and its associated function to the list of conditions.
		Args:
			condition (tuple): A tuple representing the condition to be checked.
			function_on_true (callable): A function to be executed if the condition is met.
		Raises:
			ValueError: If the condition does not meet the required expectations.
		Side Effects:
			Appends the (condition, function_on_true) pair to self.conditions.
			Resets self.injected_parts to None. This is to avoid re-injecting parts every time a condition is added; handing responsibility to the user to call inject_conditions() when needed.
		"""
		try:
			self.__conditins_meet_expectations([(condition, function_on_true)])
		except ValueError as e:
			print(f'Error in condition: {e}')
			raise ValueError(f'Error in condition: {e}')

		self.conditions.append((condition, function_on_true))

		self.injected_parts = None  # Reset injected parts


	def inject_conditions(self):
		"""
		Injects condition parts into the object if they have not already been injected.

		This method checks if the `injected_parts` attribute is `None`. If so, it calls
		the private method `__inject_condition_parts()` to generate and assign the condition parts.

		Returns:
			None
		"""
		if self.injected_parts is None:
			self.injected_parts = self.__inject_condition_parts()
		

	def __split_mask(self):
		"""
		Splits the `question_with_mask` string into a list of parts, separating by the '*' character.
		Returns:
			list: A list of strings and '*' characters, where each '*' is a separate element and other substrings are grouped between asterisks.
		Example:
			If `question_with_mask` is "What is * of *", the result will be:
			['What is ', '*', ' of ', '*']
		"""
		parts = []
		mask = self.question_with_mask
		i = 0
		part = ''
		while i < len(mask):
			if mask[i] == '*':
				if part != '':
					parts.append(part)
				parts.append('*')
				part = ''
			else:
				part += mask[i]
			i += 1
		if part != '':
			parts.append(part)

		print(parts)
		return parts


	def __inject_condition_parts(self):
		"""
		Replaces wildcard '*' entries in the question mask with corresponding condition parts for each condition.
		Iterates over all conditions, and for each, constructs a new list of parts where each '*' in `self.mask_parts`
		is replaced by the corresponding element from the condition. Non-wildcard parts remain unchanged.
		Returns a list of all such injected parts lists, one for each condition.
		Returns:
			list[list[str]]: A list containing lists of parts with wildcards replaced by condition values.
		Example:
			If `self.mask_parts` is ['how ', '*', ' ', '*'] and the conditions are [(('old is', '*'), GetAgeOf)],
			the result will be [['how ', 'old is', ' ', '*']].
			This means that the final '*' will be treated as a wildcard, which is also passed to the function.

			Example:
			'how old is Tom Cruise' matches 'how * *' with injected parts ['how ', 'old is', ' ', '*'].
			Then the wild card variable is "Tom Cruise", which is passed to the function GetAgeOf("Tom Cruise").
		"""
		## check if the question mask matches the question e.g. 'how * *' matches 'how old is Tom Cruise'
		all_injected_parts = []
		for condition in self.conditions:
		## create a new list of parts, where '*' parts are replaced with the condition parts (e.g. 'how * *' becomes 'how old is *')
			injected_parts = []
			star_index = 0
			for i, part in enumerate(self.mask_parts):
				if part == '*':
					injected_parts.append(condition[0][star_index])
					star_index += 1
				else:
					injected_parts.append(part)
			all_injected_parts.append(injected_parts)

		print(all_injected_parts)
		return all_injected_parts



	def __find_next_part(self, question: str, start_index: int, part: tuple):
		"""
		Finds the end index of the next specified part within a question string, starting from a given index.
		This method searches for a substring (part) within the question, as defined by the `injected_parts` attribute.
		If the part to look for is a wildcard ('*'), it either returns the end of the question (if it's the last part)
		or recursively searches for the next part. If the part is found, returns the index immediately after the found substring.
		If not found, returns None.
		Args:
			question (str): The question string to search within.
			start_index (int): The index to start searching from.
			part (tuple): A tuple (i, j) indicating which part to look for in `injected_parts`.
		Returns:
			int or None: The index immediately after the found part, the end of the question if wildcard is last,
						 or None if the part is not found.
		"""
		looking_for = self.injected_parts[part[0]][part[1]]
		if looking_for == '*':
			## if this is the last part, return the end of the question
			if part[1] == len(self.injected_parts[part[0]]) - 1:
				return len(question)

			return self.__find_next_part(question, start_index, (part[0], part[1] + 1))

		# else is implicit
		end_index = question.find(looking_for, start_index)
		if end_index == -1:
			return None
		return end_index + len(looking_for)


	def __find_matching_condition(self, question: str):
		"""
		Attempts to match the given question string against a set of injected parts (patterns with wildcards).
		Iterates through each pattern, checking if the question matches the fixed and wildcard segments in order.
		If a match is found, extracts and returns the variable parts of the question corresponding to wildcards.
		Args:
			question (str): The input question string to be matched against the patterns.
		Returns:
			tuple:
				- int or None: The index of the matching injected_parts pattern, or None if no match is found.
				- list or None: A list of variable substrings extracted from the question corresponding to wildcards,
				  or None if no match is found.
		"""
		## in the case of 'how * *', the mask is split into ['how ', '*', ' ', '*']. This means that these parts must be cycled through. 

		## check to see if the question matches the injected parts. if a wildcard is present, then the question can have any text in that position.
		# e.g. 'how old is Tom Cruise' matches 'how * *' with injected parts ['how ', 'old is', ' ', '*']

		for i, injected_parts in enumerate(self.injected_parts):
			start_of_part = 0
			question_parts = []
			variables = []
			matched = False
			for j, part in enumerate(injected_parts):
				# print(f'Checking part {part} in question {question}')
				next_part_index = self.__find_next_part(question, start_of_part, (i, j))
				if next_part_index is None:
					break
				# print(f'Found part {part} at index {next_part_index}')

				if j == len(injected_parts) - 1:
					matched = True

				if part == '*':
					# If the part is a wildcard, take the substring from the start of the part to the end of the next part
					question_parts.append(question[start_of_part:next_part_index])
					variables.append(question[start_of_part:next_part_index])
				else:
					# If the part is not a wildcard, just append the part
					question_parts.append(part)

				if matched:
					return i, variables

				start_of_part = next_part_index

		return None, None

	def ask_question(self, question: str):
		"""
		Processes a user's question by matching it to a predefined condition and invoking the corresponding function.
		Args:
			question (str): The question to be processed.
		Returns:
			Any: The result of the function associated with the matched condition, or None if no condition matches.
		Side Effects:
			- Prints a warning and injects conditions if they have not been set up.
		"""

		if self.injected_parts is None:
			print('Injected parts are None. Please call inject_conditions() during setup to avoid delays in responses.')
			self.inject_conditions()

		matching_condition, variables = self.__find_matching_condition(question)

		if matching_condition is None:
			return None

		function_to_call = self.conditions[matching_condition][1]

		return function_to_call(*variables)


def GetFromWIKIDATA(query: str):
	url = "https://query.wikidata.org/sparql"
	headers = {
		"Accept": "application/sparql-results+json"
	}

	response = requests.get(url, params={"query": query}, headers=headers)

	if response.status_code != 200:
		print(f"Request failed with status code {response.status_code}")
		return None

	results = response.json().get("results", {}).get("bindings", [])
	
	return results

def GetAgeOf(name: str):
	name = name.strip().title()

	query = f"""
	SELECT ?birthDate WHERE {{
	  ?person rdfs:label "{name}"@en;
			  wdt:P569 ?birthDate.
	}} LIMIT 1
	"""
	results = GetFromWIKIDATA(query)
	if results is None:
		return None

	birth_date_str = results[0]["birthDate"]["value"]
	birth_date = datetime.datetime.strptime(birth_date_str[:10], "%Y-%m-%d")  # Only use YYYY-MM-DD
	today = datetime.datetime.now().date()
	age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
	return str(age)

def GetPopulationOf(area: str):
	area = area.strip().title()

	## check for ambiguity. If if searching for an area that is both a state/county and a city, it it should be made clear we are looking fro the city.
	check_query = f"""
	SELECT ?typeLabel WHERE {{
		?area rdfs:label "{area}"@en.
		?area wdt:P31 ?type.
		SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
	}}
	LIMIT 1
	"""
	check_results = GetFromWIKIDATA(check_query)
	if not check_results or check_results == []:
		# print(f"No results found for {area}. It might not be a recognized city or area in Wikidata.")
		return None
	
	try:
		type_label = check_results[0]['typeLabel']['value'].lower()
	except KeyError:
		# print(f"Unexpected response format for {area}. Could not determine type label.")
		return None
	
	if type_label not in ['city', 'town', 'village']:
		# print(f"Assuming {area} refers to a city due to ambiguity.")
		area = area + " City"

	query = f"""
		SELECT ?population WHERE {{
		  ?area rdfs:label "{area}"@en;
				wdt:P31/wdt:P279* wd:Q515; 
				wdt:P1082 ?population.
		}} LIMIT 1
		"""

	results = GetFromWIKIDATA(query)
	
	try:
		return str(results[0]["population"]["value"])
	except (IndexError, KeyError):
		# print(f"No population data found for {area}. It might not be a recognized city or area in Wikidata.")
		return None

q1 = QUESTION('how * *', [(('old is', '*'), GetAgeOf)])
q2 = QUESTION('what * *', [(('is the population of', '*'), GetPopulationOf)])

q1.add_condition(('big is the population of', '*'), GetPopulationOf)
q1.add_condition(('many people live in', '*'), GetPopulationOf)
q2.add_condition(('is the age of', '*'), GetAgeOf)

q1.inject_conditions()
q2.inject_conditions()

questions = []
questions.append(q1)
questions.append(q2)

def ask(question: str):
	question = question.strip(string.punctuation).lower()

	for _question in questions:
		answer = _question.ask_question(question=question)
		if answer is not None:
			print(f'Answer: {answer}')
			return answer
	print(f'No matching question found for: {question}')
	return None


assert '62' == ask('how old is Tom Cruise')
assert '35' == ask('how old is Taylor Swift')
assert '8799728' == ask('what is the population of London')
assert '8804190' == ask('what is the population of New York?')



