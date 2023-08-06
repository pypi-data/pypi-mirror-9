def print_lol(the_list, tab_list=0):
    for i in the_list:
        if isinstance(i, list):
            print_lol(i, tab_list+1)
        else:
            for j in range(tab_list):
                print("\t", end='')
            print(i)
