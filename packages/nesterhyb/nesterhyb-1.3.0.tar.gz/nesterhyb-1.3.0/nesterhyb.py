def print_hyb(the_list,indent=False,level=0):
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_hyb(each_item,indent,level+1)
                else:
                        if indent:                                
                                for tab_stop in range(level):
                                        print("\t",end='')
                        print(each_item)
