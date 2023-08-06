def print_hyb(the_list):
	for each_item in the_list:
		if isinstance(each_item,list):
			print_hyb(each_item)
		else:
			print(each_item)
