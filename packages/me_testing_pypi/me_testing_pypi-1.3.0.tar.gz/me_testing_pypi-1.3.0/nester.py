"""" This is the "nester.py" module and it provides one function called print_lol() 
which prints lists that may or may not include nested lists """

def print_lol(the_list, indent = False, level):
	""" This function takes a positional argument called "the_list", which
	is any python list (of-possibly-nested lists). Each data item in the provided lists is
(recursively) printed to the screen on it's own line. A second argument called
"level" is used to insert tab_stops when a nested list is encountered """
	for each_item in the_list:
		if isinstance(each_item, list):
			#add recursive here
			print_lol(each_item, indent, level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t", end='')
				print(each_item)


			
