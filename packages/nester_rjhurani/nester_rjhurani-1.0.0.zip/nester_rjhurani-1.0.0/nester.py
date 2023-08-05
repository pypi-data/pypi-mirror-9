"""function to print iterative list items in a list"""
def print_func(item_list):
    for each_item in item_list:
        if isinstance(each_item,list):
            print_func(each_item)
        else:
            print(each_item)

        
