def print_hyb(the_list,level):
	for each_item in the_list:
		if isinstance(each_item,list):
			print_hyb(each_item,level+1)
		else:
			print(each_item)
