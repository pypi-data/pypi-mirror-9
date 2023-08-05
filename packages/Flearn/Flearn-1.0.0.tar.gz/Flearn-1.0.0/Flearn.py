#conding=utf-8

"""this is the 'new.py' module and it provides one function XXX"""

def print_lol(the_list):
	"""this function take one xxxx"""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
