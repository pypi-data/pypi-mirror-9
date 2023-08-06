""" This Module is used to take an input List and print out its contents in
    nested fashion """
def print_list (arg_list, indent=False, tabs=0):
    # This function takes in a list argument
    # and prints out its contents in a nested fashion
    # recursively.
    # It takes three arguments:
    # arg_list: List that needs to be recursively displayed
    # indent: If you want to indent your nested lists (Default= False)
    # tabs : Indicates the default tabs to be displayed (Default = 0)
    for each_elem in arg_list:
        if isinstance(each_elem, list):
            print_list(each_elem, indent, tabs+1)
        else:
            if indent == True :
                # for tab_level in range(tabs):
                #    print ('\t', end='')
                print ('\t' * tabs, end = ' ')
            print(each_elem)
