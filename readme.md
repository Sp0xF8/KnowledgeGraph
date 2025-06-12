# Knowledge Grpah Guys

> **Note:** To those in charge of hiring. Thank you for giving me this oppertunity. Regardless of progression into the next stage, I had fun designing my solution. I look forward to the potential of hearing back, and being given more fun tasks!

## Task
```python
def ask(question: str, endpoint: str = 'https://query.wikidata.org/sparql'):
     # please complete this method however you wish
     pass

if _name_ == '_main_':
    assert '62' == ask('how old is Tom Cruise')
    assert '35' == ask('how old is Taylor Swift')
    assert '8799728' == ask('what is the population of London')
    assert '8804190' == ask('what is the population of New York?')
```
## Approach

There are many ways to solve the problem above, but two solutions truly stuck out. First impressions of this task is that a function needs to be developed which answers two questions: "How old is a celebrity" and "what is the population of a city"? Whilst on the right track, what this task is really defining is the basic functionality of a chatbot. With this, a simple string equlivancy is possible, given the limited test case, but not optimal. These two possible solutions are discussed at greater detail below. 

The first is simply about finishing the task in as few lines of code as possible: creating a function which handles each query to WikiData, then just call the correct one depending on the question asked. This would work, and there is theoretically nothing stopping this from being made. However, this is the less ideal solution for numerous reasons. The largest being maintainability, and possibility of expansion. Adding new questions which can be answered in this manor would be time consuming and could quickly become complicated to manage. 

A better solution is designing a simple Question nodelling framework. Inspired by AIML, the creaiton of this basic framework allows for base questions to be defined with wildcards. These wildcards are then either replaced by matching "conditional" words, or are kept as wildcards and treated as "variables". For example, the question "how old is tom cruise" could be interperated as "how * *". Here, the first wildcard is matched with the condition "old is", leaving the final wildcard as a variable passed to the "on-true" function. In the case of this specific quesiton, the variable "Tom Cruise" is passed to a function which then gets his age via WikiData. 

Whilst both of these solutions make use of the same `GetPopulationOf(area:str)` and `GetAgeOf(name:str)` functions, thier implimentations are vastly different. I stand behind my decision to exercise creativity in this coding challange, as the given solution is one which is highly adaptable and could lead to the development of a basic chatbot that would facilitate more nuanced discussions than simply using a comparative if statement. 


# Documentation (ordered by what is most worth reading)


## Forward Facing Code

### Creating a Question
***Paramaters***: 
| Parameter   | Type     | Description                |
|-------------|----------|----------------------------|
| question_with_mask | string | Used to map an input to conditional outputs |
| condition_answers | list[tuple[tuple, callable]] | A list holding tuples of conditions and a callable function |

```py
def __init__(self, question_with_mask: str, condition_answers: list[tuple[tuple, callable]]):
    ## e.g. 'how * *', 'what * *'
    self.question_with_mask = question_with_mask 
    ## e.g. 'how * *' becomes ['how ', '*', ' ', '*']
    self.mask_parts = self.__split_mask()  
    self.number_of_conditions = len(question_with_mask.split('*')) - 1

    try:
        ## ensures that the conditions given match the number of wildcards used
        self.__conditins_meet_expectations(condition_answers)
    except ValueError as e:
        print(f'Error in conditions: {e}')
        raise ValueError(f'Error in conditions: {e}')

    ## e.g. [(('old is', '*'), function_on_true), (('is the population of', '*'), function_on_true)]
    self.conditions = condition_answers 
    self.injected_parts = self.__inject_condition_parts()
```


***Example Useage***:
When handling questions like "how old is X", this is broken down into different stages: the base question, matching paramaters, and potential variables. 

Here, "how " becomes the base of the question: followed by "old is", replacing the first wildcard. The second wildcard is identified as a variable by its '*' (astrics) in the conditions section. After the variable text (e.g. "Tom Cruise") has been identified, it is added to a list FIFO list representing the variables in question. These variables are then unpacked and passed to the "on-true" function once a condition has been met. 


```py
how = QUESTION(
    'how * *',  # String mask, used to map inputs to conditional outputs
    [ # List of condition_function pairs
        ( # A condition_function pair
            ('old is', '*') # Conditions which will be emplaced instead of wildcards in the String Mask
            , GetAgeOf # function which will be called when the conditions are true.
        )
    ]
)
```


### Adding a condition
Occasionally, it might be useful to be able to add a condition after an objects creation. With this, the conditions are checked in the same way as the constructor. There is a key difference here though. After adding a new condition, the parts are not re-injected. This is built off the assumption that more conditions may be added. To avoid wasted builds of conditions, responsibility to inject parts after defining additional conditions is handed to the developer. 


***Args:***
| Parameter   | Type     | Description                |
|-------------|----------|----------------------------|
| condition   | tuple    | A tuple containing the condition and a wildcard, e.g. ('old is', '*') |
| function_on_true | callable | A function which will be called when the condition is met, e.g. GetAgeOf |

```py
def add_condition(self, condition: tuple, function_on_true):
    try:
        self.__conditins_meet_expectations([(condition, function_on_true)])
    except ValueError as e:
        print(f'Error in condition: {e}')
        raise ValueError(f'Error in condition: {e}')

    self.conditions.append((condition, function_on_true))

    self.injected_parts = None  # Reset injected parts
```

***Example Useage***:
```py
how.add_condition(('big is the population of', '*'), GetPopulationOf)
how.add_condition(('many people live in', '*'), GetPopulationOf)
```

### Injecting condition parts
The forward-facing code for this function simply calls the private function `__inject_condition_parts()`. This is done to allow for the parts to be injected at any time, without forcing a build every time a condition is added. Loosely speaking, the `__inject_condition_parts()` function is responsible for taking the conditions and injecting them into the string mask, replacing the wildcards with the conditions. All of the possible combinations of conditions are generated and then saved in the `injected_parts` attribute.

```py
def inject_conditions(self):
    if self.injected_parts is None:
        self.injected_parts = self.__inject_condition_parts()
```

***Example Useage***:
```py
how.add_condition(('big is the population of', '*'), GetPopulationOf)
how.add_condition(('many people live in', '*'), GetPopulationOf)

how.inject_conditions()
```

### Asking a question

This is the main function which is called to ask a question. It first checks if the conditions have been injected, and if not, it calls `inject_conditions()`. Then, it finds the matching condition for the question and calls the corresponding function with any variables extracted from the question. If no matching condition is found, it returns `None`.


***Args:***
| Parameter   | Type     | Description                |
|-------------|----------|----------------------------|
| question    | str      | The question to be asked, e.g. "how old is Tom Cruise" |

```py
def ask_question(self, question: str):
    if self.injected_parts is None:
        self.inject_conditions()

    matching_condition, variables = self.__find_matching_condition(question)

    if matching_condition is None:
        return None

    function_to_call = self.conditions[matching_condition][1]

    return function_to_call(*variables)
```



## WikiData Functions

### GetPopulationOf
This function was easy enough to get working for "What is the population of London". However, handling the ambiguity of "What is the population of New York?" was a bit more complex. Origonally, the function would simply search for the population of the given area. However, this would return the population of New York (state) rather than New York City. To handle this, the function first checks if the area is ambiguous by looking for the type of the area in question. If it is not a city, town, or village, it appends "City" to the area name before searching for the population. This aims to remove ambiguity and ensure the correct population is returned.

***Args:***
| Parameter   | Type     | Description                |
|-------------|----------|----------------------------|
| area        | str      | The name of the area to get the population of, e.g. "London" or "New York" |

```py
def GetPopulationOf(area: str):
	area = area.strip().title()

	## check for ambiguity. If searching for an area that is both a state/county and a city, it it should be made clear we are looking from the city.
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
		return None
	
	try:
		type_label = check_results[0]['typeLabel']['value'].lower()
	except KeyError:
		return None
	
    ## if the search is not finding a city, town, or village, we assume ambiguity and append "City" to the area name.
	if type_label not in ['city', 'town', 'village']:
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
		return None
```


### GetAgeOf
This function retrieves the age of a person by their name. It queries Wikidata for the person's birth date and calculates the age based on the current date.

***Args:***
| Parameter   | Type     | Description                |
|-------------|----------|----------------------------|
| name        | str      | The name of the person to get the age of, e.g. "Tom Cruise" |

```py
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
```

### GetFromWIKIDATA
This function is a utility to query Wikidata using SPARQL. It sends a request to the Wikidata SPARQL endpoint and returns the results in JSON format.

***Args:***
| Parameter   | Type     | Description                |
|-------------|----------|----------------------------|
| query       | str      | The SPARQL query to execute |

```py
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
```


## Ask Function
After populating the questions list, the ask function can be called with a question string. It will iterate through the questions and return the answer from the first matching question. This means that quests are checked in the order they were added, and the first match will be returned. If no match is found, it will return `None`.

***Args:***
| Parameter   | Type     | Description                |
|-------------|----------|----------------------------|
| question    | str      | The question to ask, e.g. "how old is Tom Cruise" |

```py
questions = []
def ask(question: str):
	question = question.strip(string.punctuation).lower()

	for _question in questions:
		answer = _question.ask_question(question=question)
		if answer is not None:
			print(f'Answer: {answer}')
			return answer
	print(f'No matching question found for: {question}')
	return None
```


## Main Function
This is the entry point of the script. It initializes the questions and runs the assertions to test the functionality.

```py
if __name__ == '__main__':

	## initialise the questions with the basic conditions
	how = QUESTION('how * *', [(('old is', '*'), GetAgeOf)])
	what = QUESTION('what * *', [(('is the population of', '*'), GetPopulationOf)])

	## add some more proof of concept conditions
	how.add_condition(('big is the population of', '*'), GetPopulationOf)
	how.add_condition(('many people live in', '*'), GetPopulationOf)
	what.add_condition(('is the age of', '*'), GetAgeOf)

	## inject the conditions so that the injected_parts are ready to be used
	how.inject_conditions()
	what.inject_conditions()

	## add the questions to the list of questions
	questions.append(how)
	questions.append(what)

	assert '62' == ask('how old is Tom Cruise') == ask('what is the age of Tom Cruise')
	assert '35' == ask('how old is Taylor Swift') == ask('what is the age of Taylor Swift')
	## these two cannot be demonstrated in the same way as above, 
    # the rate limiting of the Wikidata API prevents repeated calls in a short time frame.
	assert '8799728' == ask('what is the population of London') 
    # == ask('how big is the population of London') == ask('how many people live in London')
	assert '8804190' == ask('what is the population of New York?') 
    # == ask('how big is the population of New York?') == ask('how many people live in New York?')

```