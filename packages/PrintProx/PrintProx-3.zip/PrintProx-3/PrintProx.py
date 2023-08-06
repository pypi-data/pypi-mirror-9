def print_lol(the_list, identidade=False, tab_list=0):
    for i in the_list:
        if isinstance(i, list):
            print_lol(i, identidade, tab_list+1)
        else:
            if identidade:
                for j in range(tab_list):
                    print("\t", end='')
            print(i)
