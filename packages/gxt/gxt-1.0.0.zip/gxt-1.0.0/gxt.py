movies = ['a','b','c','d',1977,['m',['q','n','e']]]
def print_movie(the_list):
    for mov in the_list:
        if isinstance(mov, list):
    	    print_movie(mov)
    	else:
    		print(mov)
	    		