def print_list(the_list,ran):
    for each_item in the_list:
        if isinstance(each_item,list):
            ran=ran+1
            print_list(each_item,ran)
        else:
            for num in range(ran):
                print("\t",end='')
            print(each_item)
