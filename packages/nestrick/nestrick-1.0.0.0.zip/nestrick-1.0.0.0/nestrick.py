""" This Module is used to take an input List and print out its contents in
    nested fashion """
def print_list (arg_list):
    # This function takes in a list argument
    # and prints out its contents in a nested fashion
    # recursively
    for each_elem in arg_list:
        if isinstance(each_elem, list):
            print_list(each_elem)
        else:
            print(each_elem)
