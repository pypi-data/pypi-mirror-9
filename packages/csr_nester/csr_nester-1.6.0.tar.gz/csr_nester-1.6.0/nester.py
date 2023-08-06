def print_new(the_list,indent=False,level=0):
        for each_item in the_list:
                if isinstance(each_item, list):
                        print_new(each_item,indent,level+1)
                else:
                        if indent:
                                print("\t"*level,end='')
#                               for n in range(level):
#                                       print("\t",end='')
                        print(each_item)
