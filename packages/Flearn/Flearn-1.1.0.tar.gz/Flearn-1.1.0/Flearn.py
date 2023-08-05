#conding=utf-8

"""this is the 'new.py' module and it provides one function XXX"""

def print_lol(the_list, level):
	"""this function take one xxxx"""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, level + 1)
		else:
                        for tab_stop in range(level):
                                print("\t", end = '')
			print(each_item)
