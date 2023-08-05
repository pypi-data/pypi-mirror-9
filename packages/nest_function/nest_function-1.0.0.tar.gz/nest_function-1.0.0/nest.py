"""print nested list"""

def print_lol(the_list):
	for item in the_list:
		if isinstance(item, list):
			print_lol
		else:
			print(item)