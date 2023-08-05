"""  Module nester     Written by Becky Staaden     1/20/2015   """




def print_lol(the_list):
             
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
