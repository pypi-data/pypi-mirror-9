def print_movie(the_list, level = 0):
    for mov in the_list:
        if isinstance(mov, list):
    	    print_movie(mov,level+1)
    	else:
    		for tab_stop in range(level):
    			print('\t',end = '')
    		print(mov)
	    		